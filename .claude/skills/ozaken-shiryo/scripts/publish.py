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
        body_foo.html 03_tools/foo.html \\
        --list "Foo入門 ─ 副題" [--backstage] [--to 共有先]

  --backstage を付けると index ではなく裏資料置き場に載せる。
  --list を省くと一覧には載せず、ファイルの生成と台帳登録だけを行う。

  既存資料の本文を作り直すとき:
    OZAKEN_PW=マスター python3 publish.py body_foo.html 05_drive/foo.html --update

  --update は 1〜3 を通したうえで **lockbox.encrypt** で書き戻す。
  鍵は作り直さないので、配布済みのパスワードはそのまま使える。
  ここを通さず build_page.build だけで組み直すと、
  .lede や .mth のCSSが落ちて、見出しのチップが素の文字になる。
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
from page_parts import EXTRA_CSS
from spacing import SPACING_CSS, CARD_COLS_CSS, annotate_cards
from reissue_words import WORDS

TPL = os.path.join(ROOT, '03_tools/cowork.html')   # ロック画面の型として借りる
INDEX = os.path.join(ROOT, 'index.html')
BACKSTAGE = os.path.join(ROOT, 'backstage.html')


def compose(body_path, extra=''):
    """本文フラグメントから、演出の注入まで済んだ完成ページを作る。

    新規公開も、既存資料の作り直しも、必ずここを通す。
    段取りを2か所に書くと、片方だけ直したときに差が出る。
    実際、作り直しのときに page_parts の EXTRA_CSS を渡し忘れて、
    カード見出しのチップ（.mth）と導入文（.lede）の体裁が全部落ちた。
    """
    tmp = os.path.join(HERE, '_build.html')
    page = build(body_path, tmp)
    # 資料ごとのCSS（extra）は最後に置く。共通のものより後ろでないと勝てない。
    # 先に置いたら、AX Table の「持ち帰り3点」が縦積みから3列に戻ってしまった
    page = page.replace('</style>', EXTRA_CSS + SPACING_CSS + CARD_COLS_CSS + extra
                        + '</style>', 1)
    page = annotate_cards(page)
    errs, summary = check(page)
    if errs:
        sys.exit('スタイル検査で止まりました:\n  - ' + '\n  - '.join(errs))

    # **わかりにくさは公開を止めない。ただし必ず目に入るところに出す。**
    # 主語や肩書きの抜けは「直せば良くなる」類なので、止めると直す機会ごと失う。
    # 出さないと気づかれないまま公開されるので、ここで必ず読ませる
    from check_wakaru import check_wakaru
    warn = check_wakaru(page)
    if warn:
        print('⚠ わかりにくさ %d 件（公開は止めません。直せるものは直してください）'
              % len(warn))
        for w in warn:
            print('   ・' + w)

    # **ここに並べ忘れると、作り直すたびに静かに古い見た目へ戻る。**
    # 新しい体裁（normalize_style）と出現の判定の直し（fix_reveal）は、
    # 公開したあとに全資料へ配ったものだった。ところが publish を通していないので、
    # 生成元から作り直した資料だけが、その前の姿で上書きされていた。
    # 実際、経営層向けほか8本が、republish のたびに新デザインを失っていた。
    # **資料に当てるものは、必ずこの列に足す。**
    import apply_spacing, apply_herofx, apply_keynav, apply_bgcycle, apply_figanim
    import apply_home, normalize_style, normalize_hero, apply_stage
    # **normalize_hero がここに無かった。**
    # 扉の大きさを全資料でそろえたCSSは、この列を通らないので、
    # 生成元から作り直すたびに静かに剥がれていた（実際に2本で剥がれた）。
    # 扉の並びを決めるCSSなので、herofx より後ろに積む
    # apply_stage は BODYSTYLE より後ろ。カードの帯の遅延を、札が出たあとに振り直すため
    for mod in (apply_spacing, apply_bgcycle, apply_herofx, apply_keynav, apply_figanim,
                apply_home, normalize_style, normalize_hero, apply_stage):
        got = mod.patch(page)
        if got is None:
            sys.exit('%s の注入に失敗しました' % mod.__name__)
        page = got

    # 出現の判定を、要素の高さに依存しない形に直す（fix_reveal と同じ置き換え）。
    # 背の高い塊が、画面の10倍を超えると永久に出てこなくなる
    import fix_reveal
    page, _ = fix_reveal.patch(page)

    # 暗い地に白字で描かれた古い図版がある面には、白い箱を当てない印を付ける。
    # 生成元から作った図はすべて明るい組みなので、ふつうは何も付かない
    import mark_figdark
    page, _ = mark_figdark.patch(page)
    # 持ち帰りキットと確認テストは、印がある資料にだけ入る（裏資料限定）。
    # 無ければ None が返るので、そのときは何もしない
    import apply_kit, apply_quiz
    page = apply_kit.patch(page) or page
    page = apply_quiz.patch(page) or page
    os.path.exists(tmp) and os.remove(tmp)
    return page, summary


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


def check_pw_word(pw, m):
    """個別パスワードに使える形か。会場で読み上げて、スマホで打たれる前提"""
    if not re.fullmatch(r'[a-z]{4,10}', pw):
        sys.exit('個別パスワードは小文字の英字4〜10文字にしてください: ' + pw)
    used = {v.get('pw') for k, v in registry.load(m).items() if k != '_meta'}
    if pw in used:
        sys.exit('その個別パスワードは、すでに別の資料が使っています: ' + pw)
    return pw


# 分類フォルダ → 玄関に出す見出しと説明。**新しい分類はここに足す。**
# 書いていない分類は、フォルダ名から仮の見出しを作って通す（後で直せる）
CATEGORIES = {
    '01_concept':  ('コンセプト', 'AIとは何か。前提を揃えるための土台になる話。'),
    '02_models':   ('モデル・技術', 'モデルの選び方、仕組み、使い分け。'),
    '03_tools':    ('ツール', '実際の製品。料金・機能・向き不向き。'),
    '04_practice': ('実践', '手を動かすための手順。作り方と、書き方。'),
    '05_drive':    ('推進', '組織でAIを進めるための、体制・予算・順番。'),
    '06_people':   ('キャリア・人材', '人と組織。職種、育成、評価、キャリア。'),
    '07_risk':     ('リスク・法務', '事故を起こさないための線引き。'),
    '08_industry': ('業界別', '業界ごとの活用余地と、詰まるところ。'),
    '09_role':     ('職種別', '職種ごとに、1週間の中身がどう入れ替わるか。'),
    '10_policy':   ('政策・国家戦略',
                    '国は何を決め、何を決めなかったか。日本・米国・中国・EUの戦略と、その比較。'),
    '11_stats':    ('統計調査',
                    '数字で見るAI。導入率・雇用・投資・電力。一次情報だけを、確認日つきで。'),
    '12_jobs':     ('雇用・労働',
                    '日本と米国の雇用統計を、同じ物差しで並べる。'
                    '新しい発表が出るたびに差し替えます。'),
}


def add_to_index(rel, label):
    """同じ分類のリストの末尾に足す。

    **分類そのものが無いときは、分類のカードごと作る。**
    以前はここで黙って False を返していたので、新しい分類の1本目は
    毎回「index に載らなかった」となり、手でカードを書いていた。
    手で書くと必ず番号や体裁がずれるので、道具の側で作る。
    """
    cat = rel.split('/')[0]
    s = open(INDEX, encoding='utf-8').read()
    items = re.findall(r'^ *<li><a href="%s/[^"]+">.*?</a></li>$' % re.escape(cat),
                       s, re.M)
    new = '          <li><a href="%s">%s</a></li>' % (rel, label)
    if items:
        s = s.replace(items[-1], items[-1] + '\n' + new, 1)
        open(INDEX, 'w', encoding='utf-8').write(s)
        return True

    # ここから、分類のカードごと作る。**いちばん番号の大きいカードの後ろに置く。**
    cards = list(re.finditer(
        r'      <div class="card">\n'
        r'        <span class="card-tag">(\d+)</span>[\s\S]*?\n      </div>\n', s))
    if not cards:
        return False
    last = max(cards, key=lambda m: int(m.group(1)))
    n = cat.split('_')[0]
    title, note = CATEGORIES.get(
        cat, (cat.split('_', 1)[-1].replace('-', ' '), ''))
    block = ('\n      <div class="card">\n'
             '        <span class="card-tag">%s</span>\n'
             '        <h3>%s</h3>\n'
             '        <p>%s</p>\n'
             '        <ul class="doc-list">\n'
             '%s\n'
             '        </ul>\n'
             '      </div>\n' % (n, title, note, new))
    s = s[:last.end()] + block + s[last.end():]
    open(INDEX, 'w', encoding='utf-8').write(s)
    return True


SPOT_HEAD = 'スポット講演・セミナー'

# 置き場のフォルダ → 裏資料置き場の節。ここに無いフォルダはスポット講演へ
BACKSTAGE_SECTIONS = {
    'Training': ('法人研修', 'Corporate Training',
                 '企業向けの研修カリキュラム案と、当日の進行資料です。'),
    'Udemy':    ('Udemy講座', 'Online Course',
                 'オンライン講座の教材です。受講者がいつでも開ける前提で組んでいます。'),
}


def retone(inner):
    """節の並びが変わったら、明暗と背景の段を付け直す。

    先頭から light → navy → light … と交互に置き、背景の段は
    それぞれの側で 1→2→3 を回す（`apply_bgcycle.py` と同じ考え方）。
    並べ替えのたびに手で直すと、必ずどこかで色が続く。
    """
    n = {'sec-light': 0, 'sec-navy': 0}
    seen = [0]

    def fix(_m):
        tone = 'sec-light' if seen[0] % 2 == 0 else 'sec-navy'
        seen[0] += 1
        n[tone] = n[tone] % 3 + 1
        return '<section class="%s" data-bg="%d">' % (tone, n[tone])

    return re.sub(r'<section class="sec-(?:light|navy)"[^>]*>', fix, inner)


def renumber(sec):
    """節の中のカード番号を上から振り直す。01 が常にいちばん新しいもの。
    AX Table だけは番号がセッション番号そのものなので、触らない"""
    if 'AX Table' in sec:
        return sec
    c = [0]

    def f(_m):
        c[0] += 1
        return '<span class="card-tag">%d</span>' % c[0]

    return re.sub(r'<span class="card-tag">\d+</span>', f, sec)


def add_to_backstage(rel, label, pw):
    """裏資料置き場に足す。

    このページは箇条書きではなくカードで並んでいる。
    AX Table の一覧に混ぜると別物が同居してしまうので、
    スポット講演用のセクションを持たせ、無ければ作る。

    **新しいものほど上に置く。** 講演の前に開くのはたいてい直近の資料で、
    終わった資料は下に積み上がって一覧として残る。だから新しいカードは
    節の先頭に差し、節ごと作るときはヒーローのすぐ下に置く。
    """
    m = master()
    inner = lockbox.decrypt(BACKSTAGE, m)
    href = rel if rel.startswith('..') else rel
    # **個別パスワードはここに書かない。** この一覧は投影することがあり、
    # 全資料の鍵が一度に映ってしまう。パスワードは資料を開いて qr で出す
    card = ('      <div class="card"><span class="card-tag">1</span>'
            '<h3><a href="%s">%s</a></h3>'
            '<p>開いて <b>qr</b> と打つと、共有用のQRとパスワードが出ます</p></div>\n'
            % (href, label))

    # 置き場所で節を選ぶ。表の分類フォルダに置いたものはスポット講演へ
    d = rel.split('/')[0]
    head, eyebrow, sub = BACKSTAGE_SECTIONS.get(
        d, (SPOT_HEAD, 'Spot Sessions', '単発の講演・セミナー用に組んだ資料です。'))

    if head in inner:
        i = inner.find(head)
        k = inner.find('<div class="cards">', i)
        if k < 0:
            return False
        k = inner.find('\n', k) + 1                    # cards を開いた直後
        e = inner.find('</section>', i)                # この節の終わり
        if e < 0:
            return False
        # 差してから、この節の中だけ番号を振り直す
        inner = inner[:k] + renumber(card + inner[k:e]) + inner[e:]
    else:
        sub += '各ページで qr と打つと、共有用のQRと個別パスワードが出ます。'
        sec = ('<section class="sec-light" data-bg="1">\n  <div class="inner" data-reveal>\n'
               '    <span class="eyebrow">%s</span>\n'
               '    <h2 class="sec-title">%s</h2>\n'
               '    <p class="sec-sub">%s</p>\n'
               '    <div class="cards">\n%s    </div>\n  </div>\n</section>\n\n'
               % (eyebrow, head, sub, card))
        k = inner.find('<section class="sec-')          # ヒーローの次に割り込む
        if k < 0:
            return False
        inner = inner[:k] + sec + inner[k:]
    inner = retone(inner)
    lockbox.encrypt(BACKSTAGE, m, inner)
    assert lockbox.decrypt(BACKSTAGE, m) == inner
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('body')          # 本文フラグメント
    ap.add_argument('out')           # リポジトリ相対の出力先
    ap.add_argument('--list', dest='label', default='')
    ap.add_argument('--backstage', action='store_true')
    ap.add_argument('--to', default='')
    ap.add_argument('--pw', default='',
                    help='個別パスワード。裏資料では必ず資料の芯になる1語を渡す'
                         '（bunkai / soshiki / roadmap のように、小文字の英字だけ）')
    ap.add_argument('--extra-css', default='')
    ap.add_argument('--update', action='store_true',
                    help='既存資料の本文を差し替える（鍵は維持）')
    a = ap.parse_args()

    m = master()
    rel = a.out
    out = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # 1〜3) 組んで、検査して、演出を注入する
    extra = open(a.extra_css, encoding='utf-8').read() if a.extra_css else ''
    page, summary = compose(a.body, extra)
    print('検査:', summary)

    # --update は本文の差し替えだけ。鍵は作り直さない
    if a.update:
        if not os.path.exists(out):
            sys.exit('%s がありません。新規なら --update を外してください。' % rel)
        # 会場に見せるQR画面は本文フラグメントに無いので、組み直すと消える。
        # 台帳に個別パスワードがあるものには、ここで入れ直す（実際に一度消した）
        import apply_qr
        row = registry.load(m).get(rel) or {}
        if row.get('pw'):
            got = apply_qr.patch(page, rel, row.get('title', rel), row['pw'])
            page = got or page
        lockbox.encrypt(out, m, page)
        assert lockbox.decrypt(out, m) == page
        import apply_ogp
        apply_ogp.manifest(m)
        apply_ogp.patch(rel, m)
        print('更新: %s（鍵はそのまま）' % rel)
        print('題や概要を変えたなら: OZAKEN_PW=… python3 apply_ogp.py cards')
        return

    # 4) 3本鍵で暗号化。
    #    **裏資料の個別パスワードは、その資料の芯になる1語にする。**
    #    会場で読み上げ、聴いている人がスマホで打つ。ランダムな文字列だと
    #    必ず聞き返されるし、打ち間違えても本人が気づけない。
    #    1語にしておくと、打つこと自体がその日の主題の復唱になる
    if a.pw:
        pw = check_pw_word(a.pw, m)
    elif a.backstage:
        sys.exit('裏資料には --pw で1語のパスワードを付けてください'
                 '（例: --pw bunkai）。会場で読み上げるためのものです。')
    else:
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

    # 7) 会場に見せるQR画面。表・裏を問わず、個別パスワードを持つ資料すべてに入る。
    #    パスワードを焼き込むので、台帳に記録したあとに回す
    import apply_qr
    inner = lockbox.decrypt(out, m)
    got = apply_qr.patch(inner, rel, data[rel]['title'], pw)
    if got:
        lockbox.encrypt(out, m, got)
        assert lockbox.decrypt(out, m) == got

    # 8) SNSに貼ったときの題と概要。ここを忘れると「🔒 資料アーカイブ」だけが出る
    import apply_ogp
    apply_ogp.manifest(m)
    apply_ogp.patch(rel, m)

    print('公開: %s\n個別パスワード: %s\n掲載先: %s' % (rel, pw, where))
    print('共有カードの画像はまだです: OZAKEN_PW=… python3 apply_ogp.py cards')


if __name__ == '__main__':
    main()
