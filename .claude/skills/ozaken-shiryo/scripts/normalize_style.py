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
HEAD = '/* ══ OZ-BODYSTYLE v1'

CSS = """
/* ══ OZ-BODYSTYLE v1 ── 本文の共通部品を、全資料でそろえる ══ */
/* 強調。**雛形に .text-red が無く、83本では赤にならなかった。**
   暗い面では #e23744 が沈むので、表紙の強調と同じ明るい赤に替える */
.text-red{color:var(--red)}
.sec-navy .text-red,.sec-download .text-red{color:var(--red-bright)}
.text-azure{color:var(--azure)}
.sec-navy .text-azure,.sec-download .text-azure{color:var(--azure-pale)}
.fw-bold{font-weight:700}
/* リード文。42本は定義そのものが無く、1本は二重定義で衝突していた */
.lede{font-family:var(--font-ja-serif);font-size:clamp(1.15rem,2.6vw,1.5rem);
  line-height:1.9;margin:.4rem 0 1.6rem}
.sec-navy .lede{color:rgba(255,255,255,.95)}
/* カード見出しの小ラベル */
.mth{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:2px 8px;border-radius:4px;margin-right:.5em;vertical-align:middle}
/* 箱の寸法。地の色や枠線は資料ごとの作りを残し、余白だけをそろえる */
.card{padding:1.4rem 1.6rem}
.figure{padding:1.75rem 1.5rem 1.25rem}
.take{padding:1.55rem 1.75rem}
.sec-title{font-size:clamp(1.6rem,4vw,2.2rem);line-height:1.4}
.eyebrow{font-size:11px;letter-spacing:.12em;padding:3px 10px;margin-bottom:1.1rem}
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
