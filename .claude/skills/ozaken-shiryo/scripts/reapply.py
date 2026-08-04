#!/usr/bin/env python3
"""注入済みの版を外し、いまの版を入れ直す。

演出やCSSを直したときは、既存の資料にも当て直さないと見た目が揃わない。

  OZAKEN_PW=… python3 reapply.py           # 全部を1回の読み書きで入れ直す（推奨）
  OZAKEN_PW=… python3 reapply.py herofx    # 1つだけ: spacing / bg / herofx / keynav / figanim / xref

**なぜ全部まとめてやるのか。**
注入されたCSSは、どれも同じ `<style>` の末尾に積まれている。
昔は「印から </style> まで」を剥がしていたので、**あとから積まれた他の演出まで
巻き添えで消えていた**（実際に、図版の動きと関連資料チップのCSSが全資料から消えた）。
いまは各ブロックに終わりの印を付け、そこまでで切る。
そのうえで、順番を固定して積み直すのがいちばん安全なので、既定は「全部」。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)

# 積む順番。CSSはこの順で `<style>` の末尾に並ぶ
ORDER = ['spacing', 'bg', 'herofx', 'keynav', 'figanim', 'xref']

# name: (モジュール, CSSの始まりの印, CSSの終わりの印, JSの見出しコメント)
JOBS = {
    'spacing': ('apply_spacing', '/* OZ-SPACING ', '/* /OZ-SPACING */', None),
    'bg':      ('apply_bgcycle', '/* OZ-BG ', '/* /OZ-BG */', None),
    'herofx':  ('apply_herofx', '/* OZ-HEROFX ', '/* /OZ-HEROFX */',
                '/* ファーストビューの演出パーツを組み立てる。'),
    'keynav':  ('apply_keynav', None, None, '/* 資料ページのショートカット。'),
    'figanim': ('apply_figanim', '/* OZ-FIGFLOW ', '/* /OZ-FIGFLOW */', None),
    'xref':    (None, '/* ══ 関連資料チップ', '/* /OZ-XREFCSS */', None),
}


def strip_css(html, mark, end):
    """印から、終わりの印まで。終わりの印を持たない古い版は </style> まで"""
    while True:
        i = html.find(mark)
        if i < 0:
            return html
        j = html.find(end, i) if end else -1
        cut = j + len(end) if j >= 0 else html.find('</style>', i)
        if cut < 0:
            return html
        html = html[:i] + html[cut:]


def strip_js(html, head):
    while True:
        k = html.find(head)
        if k < 0:
            return html
        s = html.rfind('<script>', 0, k)
        e = html.find('</script>', k)
        if s < 0 or e < 0:
            return html
        html = html[:s] + html[e + len('</script>'):]


def strip_one(html, name):
    _, css, css_end, js = JOBS[name]
    if css:
        html = strip_css(html, css, css_end)
    if js:
        html = strip_js(html, js)
    if name == 'figanim':
        html = html.replace('<!-- OZ-FIGANIM v3 -->\n', '') \
                   .replace('<!-- OZ-FIGANIM v3 -->', '')
    if name == 'bg':
        for k in ('1', '2', '3'):
            html = html.replace(' data-bg="%s"' % k, '')
    return html


def patch_one(html, name):
    """入れ直す。入らなかった（対象外だった）ときは元のまま返す"""
    if name == 'xref':
        # チップ本体は本文の中にあり、消えていない。CSSだけを戻す
        import crossref
        if 'xr-chips"' not in html or crossref.CSS_HEAD in html:
            return html
        j = html.rfind('</style>')
        return html[:j] + crossref.CSS + html[j:] if j > 0 else html
    mod = __import__(JOBS[name][0])
    return mod.patch(html) or html


def targets():
    """全部を入れ直すときの対象。各モジュールの対象の和集合"""
    seen, out = set(), []
    for name in ORDER:
        mod = JOBS[name][0]
        if not mod:
            continue
        for f in __import__(mod).targets():
            if f not in seen:
                seen.add(f)
                out.append(f)
    return sorted(out)


def run(names, pw):
    n = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, pw) if enc else raw
        out = inner
        for name in names:
            out = strip_one(out, name)
        for name in names:
            out = patch_one(out, name)
        if out == inner:
            continue
        if enc:
            lockbox.encrypt(f, pw, out)
            assert lockbox.decrypt(f, pw) == out
        else:
            open(f, 'w', encoding='utf-8').write(out)
        n += 1
    print('%s: %d ページを入れ直しました' % (' + '.join(names), n))


if __name__ == '__main__':
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which == 'all':
        run(ORDER, pw)
    elif which in JOBS:
        run([which], pw)
    else:
        sys.exit('対象は all / %s のいずれか' % ' / '.join(ORDER))
