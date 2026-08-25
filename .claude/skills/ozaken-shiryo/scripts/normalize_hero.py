#!/usr/bin/env python3
"""表紙の題とリードの大きさを、全資料でそろえる。

資料は2年ぶんが積み重なっていて、表紙の指定が資料ごとに少しずつ違っていた。

  題    clamp(1.85rem,5vw,2.9rem) が65本、clamp(2rem,5vw,3rem) が15本、
        ほかに 3.1rem / 3.4rem / 4rem が1本ずつ。**2本は指定そのものが無く**、
        ブラウザの既定（h1相当）で出ていた
  リード 1.02rem が65本、1.05rem が15本、0.94rem と 0.98rem が1本ずつ

1本ずつ見ているぶんには気づかないが、続けて開くと題の大きさが跳ねる。
**同じシリーズに見えなくなる。**

各資料のCSSを書き換えるのではなく、`</style>` の直前に上書きの塊を足す。
古い指定は残るが、あとに書いたほうが勝つので結果はそろう。
書き換えだと、資料ごとに違う書式（改行あり・minify済み・グループ化）を
全部相手にすることになり、必ずどれかを壊す。

**題の横幅は、表紙の段そのものを広げて確保する。** 全体の段は本文の読みやすさに
合わせて880pxで、大きな明朝の題にはそこが狭い。長い題の最後の行に1文字だけ残るのは、
たいてい大きさではなく幅が足りていないため。題だけに `max-width` を足しても、
親の段の中に収まっているので効かない。**広げるのは親のほう。**

**題は `text-wrap:balance` で行を均す。** 長い題は最後の行に1文字だけ残ることがあり、
大きさをそろえてもそこだけ貧相に見える。字数に応じて大きさを変えるより、
**全部を同じ大きさにしたうえで、折り返しのほうを均す**ほうが、並べたときにそろう。

**背の低い画面の詰めも、この塊の中で置き直す。** `apply_herofx.py` が
入れている `@media(max-height:560px)` はこれより前にあるので、
基本の指定だけ上書きすると、詰めのほうが効かなくなる。

**わざと外れているもの。**
`01_concept/ax-article.html` は記事の組み、`05_drive/ai-51-master.html` は
1枚もののポスターで、どちらも `.hero-title` を持たない別の作りになっている。
ここを表紙と同じ大きさにすると版が崩れるので、この塊は当たらないままでよい
（当ててもセレクタが一致しないので実害はない）。
`12_jobs/us-jp-employment.html` は板（ダッシュボード）で、そもそも扉が無い。

`02_models/ai-voice.html` は基調講演の扉で、題の右に目次と経歴を置く2段組み。
左そろえ・署名ありという規約は満たしているが、
助走のラベルが `.eyebrow` ではなく `.hero-tag` になっている。
見た目は同じなので、構造だけ直す価値は無いと判断してそのままにしてある。

  OZAKEN_PW=マスター python3 normalize_hero.py          # 当てる（冪等）
  OZAKEN_PW=マスター python3 normalize_hero.py refresh  # 当て直す
  OZAKEN_PW=マスター python3 normalize_hero.py list     # いまの指定を一覧する
"""
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)
MARK = '/* /OZ-HEROSIZE */'
HEAD = '/* ══ OZ-HEROSIZE v4'
# 版が上がっても剥がせるように、頭は版番号の手前まででも探す
HEAD_ANY = '/* ══ OZ-HEROSIZE v'

CSS = """
/* ══ OZ-HEROSIZE v4 ── 表紙を、全資料で同じ形にそろえる ══ */
/* 表紙の段だけ広げる。中の .hero-copy は自前の max-width を持っているので、
   広げても本文が間延びすることはなく、題だけがゆったり組める。

   **v2：段に width:100% を足す。**
   `.hero` は縦中央そろえのため flex になっていて、`.inner` はその子。
   flex の子は既定で「中身なりの幅」に縮むので、max-width を広げても効かず、
   いちばん広い子である `.hero-copy`（max-width:620px）が段の幅を決めていた。
   つまり**題に使える幅が620pxしかなく**、12文字ほどで折り返していた。
   資料によって段の幅が520〜986pxとばらついていたのも、これが理由。
   width:100% を足すと、段は max-width まで伸びて、全資料で幅がそろう */
.hero > .inner{max-width:min(1160px,94vw);width:100%}
/* **扉は左そろえ。**page_parts.hero の規約そのもの。
   2年ぶんのうち71本が中央そろえで組まれていて、続けて開くと形が跳ねていた。
   投影しても、あとから読んでも、視線は左上から始まる。
   中央に置くと、題・リード文・署名の行頭がそれぞれ違う位置に来るので、
   読み手は毎回その行の始まりを探すことになる。
   中央そろえは `text-align:center` と `margin:0 auto` の2つでできているので、
   両方を戻す */
.hero{text-align:left}
.hero .inner{text-align:left}
.hero .hero-title,.hero .hero-copy,.hero .hero-meta{margin-left:0;margin-right:auto}
/* 扉のCTAボタンは置かない。資料は投影して話すもので、押させる先が無い。
   3本だけ残っていたので、ここで畳む（HTMLからも外してある） */
.hero .btn-primary,.hero .btn-secondary,.hero .hero-cta,.hero .hero-actions{display:none}
/* 題やリードの後ろに置いてある塊（グリフ・数字・タグ）も、左へ寄せる。
   text-align では動かない。`margin:0 auto` と `justify-content:center` の
   2つで中央に置かれているので、両方を戻す */
.hero .hero-glyph,.hero .hero-stats,.hero .hero-tags,.hero .stats,
.hero .phase-stats,.hero .phase-scale{margin-left:0;margin-right:auto;
  justify-content:flex-start}
/* **スクロールの合図だけは、中央のまま。**
   画面のいちばん下に置く目印で、行の始まりを探す種類のものではない */
.hero .hero-scroll,.hero .oz-scroll{margin-left:auto;margin-right:auto}
.hero-title{font-size:clamp(2rem,5.2vw,3.05rem);line-height:1.35;text-wrap:balance;
  max-width:none}     /* 資料ごとに違う幅指定が残っているので、ここで外す */
.hero-copy{font-size:1.02rem;line-height:1.9;text-wrap:pretty}
/* 背の低い画面では詰めて1画面に収める。apply_herofx の指定をここで置き直す
   （あちらはこの塊より前にあるので、基本だけ上書きすると効かなくなる） */
@media(max-height:560px){
  .hero-title{font-size:clamp(1.5rem,4.4vh,2.4rem)}
  .hero-copy{font-size:.92rem}}
@media(max-width:640px){
  .hero-title{font-size:clamp(1.6rem,6.4vw,2.2rem)}
  .hero-copy{font-size:.95rem}}
/* /OZ-HEROSIZE */
"""

BASE_T = re.compile(r'\.hero-title\s*\{\s*[^}]*?font-size:\s*(clamp\([^)]*\)|[\d.]+rem)')
BASE_C = re.compile(r'\.hero-copy\s*\{\s*[^}]*?font-size:\s*(clamp\([^)]*\)|[\d.]+rem)')


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def strip(html):
    i = html.find(HEAD_ANY)
    if i < 0:
        return html
    j = html.find(MARK, i)
    if j < 0:
        return html
    return html[:i] + html[j + len(MARK) + 1:]


def targets():
    """reapply から呼ばれる。台帳に載っている資料が対象。

    これが無かったので reapply の列にも入れられず、
    publish で作り直した資料から静かに剥がれていた
    """
    return registry.docs()


def patch(html):
    if MARK in html:
        return None
    i = html.rfind('</style>')
    if i < 0:
        return None
    return html[:i] + CSS + html[i:]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'apply'
    pw = master()

    if cmd == 'list':
        g = defaultdict(list)
        for f in registry.docs():
            h = lockbox.decrypt(f, pw)
            t = BASE_T.search(strip(h))
            c = BASE_C.search(strip(h))
            g[(t.group(1).replace(' ', '') if t else '（指定なし）',
               c.group(1).replace(' ', '') if c else '（指定なし）')].append(
                   os.path.relpath(f, ROOT))
        for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
            print('題 %-26s リード %-14s %d本' % (k[0], k[1], len(v)))
            if len(v) <= 6:
                for r in v:
                    print('     ', r)
        return

    done = 0
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        h = lockbox.decrypt(f, pw)
        if cmd == 'refresh':
            h = strip(h)
        new = patch(h)
        if new is None:
            continue
        lockbox.encrypt(f, pw, new)
        assert lockbox.decrypt(f, pw) == new
        done += 1
        print('  そろえた:', rel)
    print('%d ページ' % done)


if __name__ == '__main__':
    main()
