#!/usr/bin/env python3
"""本文の共通部品を、全資料でそろえる。（表紙は normalize_hero.py）

**いちばん効くのは `.text-red` を足すこと。**
雛形（tpl_style.html）には `.text-azure` と `.fw-bold` しか無く、
`.text-red` はあとから作った6本にしか定義されていなかった。
つまり83本では `class="text-red"` と書いても**黒いまま出る**。
赤が揃っていないのではなく、大半の資料では赤になっていなかった。

**暗い面の赤は、明るい面と同じ色では沈む。**
表紙の強調（`.hero-title .hl`）は最初から `--red-bright` を使っている。
本文でも面の明暗で色を替える。同じ `text-red` と書いて、
明るい面では #e23744、暗い面では #ff5d6a が出るのが正しい。

ほかに、2年ぶんの積み重ねで寸法がばらけていた。

  .card      12通り（余白 1.4/1.5/1.6rem × 1.5/1.6/1.75rem）
  .take      11通り（余白と、地の色の作り方）
  .sec-title  8通り（clamp の上限が 2.1/2.2/2.25rem）
  .eyebrow    8通り（字の大きさ 9.5px/11px、字間）
  .figure     7通り（余白）
  .lede       3通り（**42本は定義そのものが無い**。1本は二重定義で衝突）
  .mth        3通り（61本は未定義）

面の地の色（`.sec-light` / `.sec-navy` と data-bg の巡回）と、
表紙の赤い強調は、調べたところ88本すべて同じだった。ここは触らない。

各資料のCSSを書き換えるのではなく、`</style>` の直前に上書きの塊を足す。
資料ごとに書式（改行あり・minify済み・グループ化）が違うので、
書き換えにすると必ずどれかを壊す。

  OZAKEN_PW=マスター python3 normalize_style.py          # 当てる（冪等）
  OZAKEN_PW=マスター python3 normalize_style.py refresh  # 当て直す
  OZAKEN_PW=マスター python3 normalize_style.py list     # いまのばらつきを一覧する
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)
MARK = '/* /OZ-BODYSTYLE */'
# **印は版を含めない。**v1 と書いてあると、版を上げた日に strip() が
# 古い塊を見つけられず、新旧が二重に積まれる。実際 v1→v2 でそうなりかけた
HEAD = '/* ══ OZ-BODYSTYLE'

CSS = """
/* ══ OZ-BODYSTYLE v2 ── 本文の共通部品を、全資料でそろえる ══ */
/* v1 は寸法をそろえるだけの塊だった。v2 では**新しい版の見た目そのもの**を配る。
   雛形（tpl_style.html）を直しても、既に公開した資料は古いCSSを抱えたままなので、
   ここで後ろから上書きする。資料ごとのCSSを書き換えないのは、
   書式（改行あり・minify済み・グループ化）が資料ごとに違い、必ずどれかを壊すため */

/* ── 紙の色。生成り（#f8f7f4）から淡い水色へ ── */
:root{--paper:#eef3fa}

/* ── 強調。**雛形に .text-red が無く、83本では赤にならなかった。**
      暗い面では #e23744 が沈むので、表紙の強調と同じ明るい赤に替える ── */
.text-red{color:var(--red)}
.sec-navy .text-red,.sec-download .text-red{color:var(--red-bright)}
.text-azure{color:var(--azure)}
.sec-navy .text-azure,.sec-download .text-azure{color:var(--azure-pale)}
.fw-bold{font-weight:700}

/* ── リード文。42本は定義そのものが無く、1本は二重定義で衝突していた ── */
.lede{font-family:var(--font-ja-serif);font-size:clamp(1.15rem,2.6vw,1.5rem);
  line-height:1.9;margin:.4rem 0 1.6rem}
.sec-navy .lede{color:rgba(255,255,255,.95)}

/* ── カード見出しの小ラベル ── */
.mth{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:2px 8px;border-radius:4px;margin-right:.5em;vertical-align:middle}

/* ── 節の見出しラベル。丸いチップをやめ、罫線を引いた英字にする ── */
.eyebrow{display:inline-flex;align-items:center;gap:.7em;
  font-family:var(--font-en);font-size:.74rem;font-weight:700;
  letter-spacing:.24em;text-transform:uppercase;
  color:var(--azure);background:none;padding:0;margin-bottom:1.1rem}
.eyebrow::before{content:"";width:26px;height:1px;background:currentColor;opacity:.7}
.sec-navy .eyebrow{color:var(--azure-pale);background:none;padding:0}
.hero .eyebrow{color:var(--azure-pale);background:none;padding:0}

/* ── **節の見出しは明朝ではなくゴシックの極太。**
      明朝の見出しは、投影すると細く沈んで読まれない ── */
.sec-title{font-family:var(--font-ja-sans);font-size:clamp(1.6rem,3.4vw,2.35rem);
  font-weight:800;line-height:1.34;letter-spacing:.01em;margin-bottom:.5rem}

/* ── 箱の寸法。地の色や枠線は資料ごとの作りを残し、余白だけをそろえる ── */
.card{padding:1.4rem 1.6rem}
.take{padding:1.55rem 1.75rem}

/* ── **濃い面の上でも、図版の箱は白。**
      箱まで濃くすると図の中まで暗くなり、薄い塗りが濁って読めなくなる。
      紙の資料でも、濃い扉の上に置く図版は白い紙のまま刷る。

      ただし**手で組んだ古い図は、暗い地の上に白い字で描かれている**。
      そこへ一律に白い箱を当てると、白に白が乗って図が消える。
      `mark_figdark.py` が付けた印のある面だけは、箱を濃いままにする ── */
.figure{padding:2.1rem 2.1rem 1.5rem}
.sec-navy:not([data-figdark]) .figure{background:var(--white);color:var(--ink);
  box-shadow:0 22px 52px -20px rgba(10,15,28,.55);
  border-color:rgba(46,84,150,.10)}
.sec-navy:not([data-figdark]) .figure-cap{color:var(--muted)}
.sec-navy:not([data-figdark]) .fig-title{color:var(--ink);
  border-bottom-color:var(--azure-pale)}
.sec-navy:not([data-figdark]) .legend-item{color:var(--muted)}
.sec-light .figure{color:var(--ink)}
@media(max-width:640px){.figure{padding:1.4rem 1.1rem 1rem}}

/* ── 図番号だけ、明朝のイタリックへ逃がす。
      番号と題が同じ強さだと、投影したときに題のほうが読まれない ── */
.fig-no{font-family:var(--font-ja-serif);font-style:italic;font-weight:600;
  color:var(--azure);margin-right:.7em}
.sec-navy .fig-no{color:var(--azure)}

/* ── カードの番号を、主役にする ── */
.card-tag{display:block;font-family:var(--font-en);font-size:1.55rem;font-weight:700;
  letter-spacing:.02em;line-height:1;color:var(--azure);background:none;padding:0;
  margin-bottom:.7rem}
.sec-navy .card-tag{color:var(--azure-pale);background:none}
/* /OZ-BODYSTYLE */
"""

SELS = ('.lede', '.text-red', '.text-azure', '.fw-bold', '.mth',
        '.card', '.figure', '.take', '.sec-title', '.eyebrow')


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def strip(html):
    i = html.find(HEAD)
    if i < 0:
        return html
    j = html.find(MARK, i)
    if j < 0:
        return html
    return html[:i] + html[j + len(MARK) + 1:]


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
        # **ここが出すのは、上書きを外した「素の状態」。**
        # 実際の見た目は下の塊が揃えているので、通り数が多くても崩れてはいない。
        # 素の状態を見せるのは、雛形のほうを直すべきものを見つけるため
        on = sum(1 for f in registry.docs() if MARK in lockbox.decrypt(f, pw))
        print('そろえる塊が当たっている資料: %d 本' % on)
        print('（以下は、その塊を外したときの素の指定。実際の見た目は揃っている）\n')
        for sel in SELS:
            c = Counter()
            for f in registry.docs():
                h = re.sub(r'/\*[\s\S]*?\*/', '', strip(lockbox.decrypt(f, pw)))
                m = re.search(re.escape(sel) + r'\s*\{([^}]*)\}', h)
                c[re.sub(r'\s+', '', m.group(1)) if m else '（定義なし）'] += 1
            print('%-12s %d通り' % (sel, len(c)))
            for v, n in c.most_common(4):
                print('    %3d本  %s' % (n, v[:88]))
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
