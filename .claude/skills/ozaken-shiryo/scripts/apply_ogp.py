#!/usr/bin/env python3
"""SNSで共有したときに、資料の題と概要が出るようにする。

資料は暗号化されているので、**SNSのクローラーが読むのは鍵のかかった外側**。
そこには全資料が同じ「🔒 資料アーカイブ ─ おざけん」しか持っていなかったため、
どれを貼っても同じ見た目になっていた。

この道具は、内側（暗号の中）から題と概要を取り出して、
**外側の `<head>` に** OGP と description を注ぎ込む。中身は一切触らない。
鍵を作り直さないので、配布済みのパスワードは無事。

  OZAKEN_PW=… python3 apply_ogp.py plan     # 何がどう入るかを見るだけ
  OZAKEN_PW=… python3 apply_ogp.py apply    # 全資料に入れる（冪等）
  OZAKEN_PW=… python3 apply_ogp.py strip    # 剥がす
  OZAKEN_PW=… python3 apply_ogp.py cards    # 共有カードの画像を作り直す

**共有カードの画像**は `99_assets/ogp/` に資料ごとのJPEGとして置く。
作るのは `make_ogp.mjs`（Playwright）。書体は資料と同じものを都度取ってくる。
画像の名前は相対パスのハッシュにしてある。日本語のファイル名をURLに載せると、
クローラーによっては取りに行けないため。対応表は `manifest.json`。
"""
import hashlib
import html as _html
import json
import os
import re
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)
SITE = 'https://ozaken-ai.github.io/ozaken-materials/'
OGP_DIR = os.path.join(ROOT, '99_assets', 'ogp')
MANIFEST = os.path.join(OGP_DIR, 'manifest.json')

MARK = '<!-- OZ-OGP v1 -->'
END = '<!-- /OZ-OGP -->'
LOCK_TITLE = '<title>🔒 資料アーカイブ ─ おざけん</title>'
SITE_NAME = 'おざけん 資料アーカイブ'
DESC_MAX = 120

# 台帳は中身が中身なので、題も概要も出さない
SKIP = {'passwords.html'}

# フォルダ名 → カードに出す小見出し
CATS = {
    '01_concept': 'CONCEPT',
    '02_models': 'TECHNOLOGY',
    '03_tools': 'PRODUCT',
    '04_practice': 'PRACTICE',
    '05_drive': 'ADOPTION',
    '06_people': 'CAREER',
    '07_risk': 'RISK & LAW',
    '08_industry': 'INDUSTRY',
    '09_role': 'FUNCTION',
    'AX_Table': 'AX TABLE',
    'Training': 'CORPORATE TRAINING',
    'Udemy': 'ONLINE COURSE',
    'index.html': 'PROFILE & ARCHIVE',
    'ask.html': 'Q & A',
    'matrix.html': 'MATRIX',
    'backstage.html': 'BACKSTAGE',
}


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def targets():
    """対象の相対パス。鍵つきの資料ぜんぶと、玄関の2枚"""
    out = []
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        # 表の分類フォルダ（01_… 〜 09_…）と、裏資料の置き場だけ
        if not os.path.isdir(p):
            continue
        if not (re.match(r'^0\d_', d) or d in oz_root.BACKSTAGE_DIRS):
            continue
        for f in sorted(os.listdir(p)):
            if f.endswith('.html'):
                out.append('%s/%s' % (d, f))
    out += [f for f in sorted(os.listdir(ROOT)) if f.endswith('.html')]
    return [r for r in out if os.path.basename(r) not in SKIP]


def locked(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
        return 'OZAKEN-LOCKED2' in fh.read(64)


def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', _html.unescape(s)).strip()


def trim(s, n=DESC_MAX):
    s = s.strip()
    return s if len(s) <= n else s[:n - 1].rstrip('、。 ') + '…'


def meta_of(rel, pw):
    """題と概要。鍵つきなら中身を開いて取り出す。
    概要が書かれていない資料は、表紙のひとことで代える"""
    path = os.path.join(ROOT, rel)
    src = lockbox.decrypt(path, pw) if locked(rel) else open(path, encoding='utf-8').read()

    m = re.search(r'<title>(.*?)</title>', src, re.S)
    title = strip_tags(m.group(1)) if m else ''
    title = re.sub(r'\s*[|｜]\s*おざけん\s*$', '', title)
    title = re.sub(r'\s*[―─\-]\s*おざけん\s*$', '', title)

    d = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
    desc = strip_tags(d.group(1)) if d else ''
    if not desc:
        h = re.search(r'<p class="hero-copy">([\s\S]*?)</p>', src)
        if h:
            desc = trim(strip_tags(h.group(1)))
    if not desc:
        h = re.search(r'<p class="(?:lede|sec-sub)">([\s\S]*?)</p>', src)
        if h:
            desc = trim(strip_tags(h.group(1)))
    return title, desc


def slug(rel):
    return hashlib.sha1(rel.encode('utf-8')).hexdigest()[:10]


def url_of(rel):
    # 玄関は index.html 付きとルートの両方で開けるので、正となる形をルートに寄せる
    return SITE if rel == 'index.html' else SITE + urllib.parse.quote(rel)


def block(rel, title, desc, with_title, with_desc=True):
    """head に差し込むかたまり。og:url と og:image は絶対URLでないと拾われない"""
    e = lambda s: _html.escape(s, quote=True)
    img = SITE + '99_assets/ogp/%s.jpg' % slug(rel)
    out = [MARK]
    if with_title:
        out.append('<title>🔒 %s ─ おざけん</title>' % e(title))
    if with_desc:
        out.append('<meta name="description" content="%s">' % e(desc))
    out += [
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="%s">' % SITE_NAME,
        '<meta property="og:locale" content="ja_JP">',
        '<meta property="og:url" content="%s">' % url_of(rel),
        '<meta property="og:title" content="%s">' % e(title),
        '<meta property="og:description" content="%s">' % e(desc),
        '<meta property="og:image" content="%s">' % img,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % e(title),
        '<meta name="twitter:card" content="summary_large_image">',
        END, '']
    return '\n'.join(out)


def strip_block(src, restore_title):
    """入れたぶんを外す。鍵つきの外側は、共通の題に戻す"""
    while True:
        i = src.find(MARK)
        if i < 0:
            return src
        j = src.find(END, i)
        if j < 0:
            return src
        src = src[:i] + (LOCK_TITLE + '\n' if restore_title else '') + src[j + len(END) + 1:]
        restore_title = False


def patch(rel, pw):
    path = os.path.join(ROOT, rel)
    src = open(path, encoding='utf-8').read()
    is_locked = locked(rel)
    src = strip_block(src, is_locked)

    title, desc = meta_of(rel, pw)
    if not title:
        return None
    # 玄関の2枚は自前の題を持っているので触らない。鍵つきは共通の題を置き換える
    blk = block(rel, title, desc, with_title=is_locked,
                with_desc='<meta name="description"' not in src)
    if is_locked:
        src = src.replace(LOCK_TITLE + '\n', '', 1)
        if LOCK_TITLE in src:
            src = src.replace(LOCK_TITLE, '', 1)
        k = src.find('<meta name="viewport"')
        k = src.find('\n', k) + 1
    else:
        m = re.search(r'<title>.*?</title>\n', src, re.S)
        k = m.end()
    open(path, 'w', encoding='utf-8').write(src[:k] + blk + src[k:])
    return title, desc


# 共有カードに使う書体。この環境には日本語は IPAゴシックしか入っておらず、
# それで刷ると資料と別物の見た目になる。作るときだけ取ってきて、キャッシュに置く
FONT_DIR = '/tmp/ozaken-ogp-fonts'
FONTS = {
    'ShipporiMinchoB1-Bold.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/shipporiminchob1/'
        'ShipporiMinchoB1-Bold.ttf',
    'ZenKakuGothicNew-Medium.ttf':
        'https://raw.githubusercontent.com/googlefonts/zen-kakugothic/main/fonts/ttf/'
        'ZenKakuGothicNew-Medium.ttf',
    'ZenKakuGothicNew-Bold.ttf':
        'https://raw.githubusercontent.com/googlefonts/zen-kakugothic/main/fonts/ttf/'
        'ZenKakuGothicNew-Bold.ttf',
    'HankenGrotesk.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/hankengrotesk/'
        'HankenGrotesk%5Bwght%5D.ttf',
}


def fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    for name, url in FONTS.items():
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p) and os.path.getsize(p) > 50000:
            continue
        subprocess.check_call(['curl', '-sSL', '-o', p, url])
        if os.path.getsize(p) < 50000:
            sys.exit('書体が取得できませんでした: %s' % name)
    return FONT_DIR


def manifest(pw):
    out = []
    for rel in targets():
        title, desc = meta_of(rel, pw)
        if not title:
            continue
        cat = CATS.get(rel.split('/')[0] if '/' in rel else rel, 'ARCHIVE')
        # カードに載る概要は2行で切れるので、切れ味のいいところで詰めておく。
        # og:description には元の長さのまま渡す
        out.append({'rel': rel, 'file': slug(rel) + '.jpg',
                    'title': title, 'desc': desc, 'card': trim(desc, 84),
                    'cat': cat})
    os.makedirs(OGP_DIR, exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    pw = master()

    if cmd == 'plan':
        for rel in targets():
            t, d = meta_of(rel, pw)
            print('%-52s %s' % (rel, t))
            print('%-52s   %s' % ('', d or '（概要なし）'))
        return

    if cmd == 'strip':
        n = 0
        for rel in targets():
            path = os.path.join(ROOT, rel)
            src = open(path, encoding='utf-8').read()
            if MARK not in src:
                continue
            open(path, 'w', encoding='utf-8').write(strip_block(src, locked(rel)))
            n += 1
        print('%d本から外しました。' % n)
        return

    if cmd == 'apply':
        rows = manifest(pw)
        n = 0
        for rel in targets():
            if patch(rel, pw):
                n += 1
        print('%d本に入れました（対応表 %d件）。' % (n, len(rows)))
        return

    if cmd == 'cards':
        rows = manifest(pw)
        node = os.path.join(HERE, 'make_ogp.mjs')
        subprocess.check_call(['node', node, MANIFEST, OGP_DIR, fonts()], cwd=ROOT)
        print('%d枚を書き出しました。' % len(rows))
        return

    sys.exit('plan / apply / strip / cards のどれかを指定してください。')


if __name__ == '__main__':
    main()
