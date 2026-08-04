#!/usr/bin/env python3
"""作った資料を、公開できる状態まで一気に仕上げる。

本文フラグメント（<!--META ...--> 付き）を渡すと、
  1) 完成ページに組む（build_page）
  2) スタイル検査（check）── ここで落ちたら公開しない
  3) 余白・ファーストビュー演出・ショートカットを注入
  4) マスター／共通／個別の3本鍵で暗号化
  5) 個別パスワードを台帳に記録
  6) index.html の資料一覧、または裏資料置き場に載せる
まで面倒を見る。

  使い方:
    OZAKEN_PW=マスター python3 publish.py \\
        body_foo.html 03_ツール・製品/foo.html \\
        --list "Foo入門 ─ 副題" [--backstage] [--to 共有先]

  --backstage を付けると index ではなく裏資料置き場に載せる。
  --list を省くと一覧には載せず、ファイルの生成と台帳登録だけを行う。
"""
import argparse
import os
import re
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
ROOT = oz_root.root(HERE)

import lockbox
import registry
from build_page import build, check
from spacing import SPACING_CSS, CARD_COLS_CSS, annotate_cards
from reissue_words import WORDS

TPL = os.path.join(ROOT, '03_ツール・製品/Cowork.html')   # ロック画面の型として借りる
INDEX = os.path.join(ROOT, 'index.html')
BACKSTAGE = os.path.join(ROOT, '裏資料置き場.html')


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def common():
    """共通パスワードは台帳が持っている。無ければ既定値"""
    try:
        return registry.load(master()).get('_meta', {}).get('common', 'O29daisuki')
    except Exception:
        return 'O29daisuki'


def gen_pw():
    return '-'.join(secrets.choice(WORDS) for _ in range(3))


def add_to_index(rel, label):
    """同じ分類のリストの末尾に足す。分類が無ければ何もしない"""
    cat = rel.split('/')[0]
    s = open(INDEX, encoding='utf-8').read()
    items = re.findall(r'^ *<li><a href="%s/[^"]+">.*?</a></li>$' % re.escape(cat),
                       s, re.M)
    if not items:
        return False
    last = items[-1]
    new = '          <li><a href="%s">%s</a></li>' % (rel, label)
    s = s.replace(last, last + '\n' + new, 1)
    open(INDEX, 'w', encoding='utf-8').write(s)
    return True


def add_to_backstage(rel, label, pw):
    """裏資料置き場のリンク一覧に足す。個別パスワードも併記する"""
    m = master()
    inner = lockbox.decrypt(BACKSTAGE, m)
    hook = '</ul>'
    if hook not in inner:
        return False
    item = ('<li><a href="%s">%s</a><span class="bk-pw">%s</span></li>\n'
            % ('../' + rel if not rel.startswith('..') else rel, label, pw))
    i = inner.rfind(hook)
    inner = inner[:i] + item + inner[i:]
    lockbox.encrypt(BACKSTAGE, m, inner)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('body')          # 本文フラグメント
    ap.add_argument('out')           # リポジトリ相対の出力先
    ap.add_argument('--list', dest='label', default='')
    ap.add_argument('--backstage', action='store_true')
    ap.add_argument('--to', default='')
    ap.add_argument('--extra-css', default='')
    a = ap.parse_args()

    m = master()
    rel = a.out
    out = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # 1) 組む
    tmp = os.path.join(HERE, '_build.html')
    page = build(a.body, tmp)
    extra = open(a.extra_css, encoding='utf-8').read() if a.extra_css else ''
    page = page.replace('</style>', extra + SPACING_CSS + CARD_COLS_CSS + '</style>', 1)
    page = annotate_cards(page)

    # 2) 検査。ここで落ちたら先へ進めない
    errs, summary = check(page)
    if errs:
        sys.exit('スタイル検査で止まりました:\n  - ' + '\n  - '.join(errs))
    print('検査:', summary)
    open(tmp, 'w', encoding='utf-8').write(page)

    # 3) 演出を注入する。平文をリポジトリに書き出さずに済むよう、
    #    ファイル経由ではなくメモリ上で当てる
    import apply_spacing, apply_herofx, apply_keynav, apply_bgcycle
    for mod in (apply_spacing, apply_bgcycle, apply_herofx, apply_keynav):
        got = mod.patch(page)
        if got is None:
            sys.exit('%s の注入に失敗しました' % mod.__name__)
        page = got

    # 4) 3本鍵で暗号化
    pw = gen_pw()
    lockbox.create(TPL, page, out, [m, common(), pw])
    for k in (m, common(), pw):
        assert lockbox.decrypt(out, k) == page, '鍵の確認に失敗: ' + k

    # 5) 台帳に記録
    data = registry.load(m)
    title = re.search(r'<title>(.*?)</title>', page, re.S)
    data[rel] = {'pw': pw, 'keys': 3, 'to': a.to,
                 'title': (title.group(1).split('|')[0].strip() if title else rel),
                 'at': registry.datetime.date.today().isoformat()}
    registry.save(m, data)

    # 6) 一覧へ
    where = '載せていない'
    if a.label:
        if a.backstage:
            where = '裏資料置き場' if add_to_backstage(rel, a.label, pw) else '裏資料置き場（失敗）'
        else:
            where = 'index の資料一覧' if add_to_index(rel, a.label) else 'index（分類が見つからず失敗）'

    os.path.exists(tmp) and os.remove(tmp)
    print('公開: %s\n個別パスワード: %s\n掲載先: %s' % (rel, pw, where))


if __name__ == '__main__':
    main()
