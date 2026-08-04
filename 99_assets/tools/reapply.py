#!/usr/bin/env python3
"""注入済みの版を外し、いまの版を入れ直す。

演出やCSSを直したときは、既存の資料にも当て直さないと見た目が揃わない。
古い版を丸ごと剥がしてから、新しい版を入れる。

  OZAKEN_PW=マスター python3 reapply.py herofx    # 対象: herofx / keynav / spacing / bg / all
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox

# 剥がすときの目印。CSSは「印から </style> まで」、JSは見出しコメントを含む <script> 全体
JOBS = {
    'spacing': ('apply_spacing', '/* OZ-SPACING ', None),
    'herofx':  ('apply_herofx',  '/* OZ-HEROFX ',  '/* ファーストビューの演出パーツを組み立てる。'),
    'keynav':  ('apply_keynav',  None,             '/* 資料ページのショートカット。'),
    'bg':      ('apply_bgcycle', '/* OZ-BG ',      None),
}


def strip_css(html, mark):
    while True:
        i = html.find(mark)
        if i < 0:
            return html
        j = html.find('</style>', i)
        if j < 0:
            return html
        html = html[:i] + html[j:]


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


def run(name, pw):
    modname, css_mark, js_head = JOBS[name]
    mod = __import__(modname)
    n = 0
    for f in mod.targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, pw) if enc else raw
        base = inner
        if css_mark:
            base = strip_css(base, css_mark)
        if js_head:
            base = strip_js(base, js_head)
        if name == 'bg':
            base = base.replace(' data-bg="1"', '').replace(' data-bg="2"', '') \
                       .replace(' data-bg="3"', '')
        new = mod.patch(base)
        if new is None:
            continue
        if enc:
            lockbox.encrypt(f, pw, new)
            assert lockbox.decrypt(f, pw) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        n += 1
    print('%s: %d ページを入れ直しました' % (name, n))


if __name__ == '__main__':
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for name in (JOBS if which == 'all' else [which]):
        if name not in JOBS:
            sys.exit('対象は %s のいずれか' % ' / '.join(JOBS))
        run(name, pw)
