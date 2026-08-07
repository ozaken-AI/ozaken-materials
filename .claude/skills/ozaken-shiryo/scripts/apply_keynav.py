#!/usr/bin/env python3
"""全資料で、index.html と同じショートカットキーを使えるようにする。

投影用の画面（お礼・待機・プロフィール・タイトル・質問箱・星座マップ・
起動演出・裏資料のゲート）は index.html が持っている。
資料側に同じものを複製すると保守が破綻するので、資料でキーを打ったら
index.html の該当画面へ飛ばす。着地の受け口は index 側に用意してある。
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
import lockbox

ROOT = oz_root.root(HERE)
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '/* OZ-KEYNAV v3 */'

JS = """
<script>
""" + MARK + """
/* 資料ページのショートカット。index.html と同じ2文字で、同じ画面が開く。
   全画面の中身は index が持っているので、ここでは行き先を渡すだけ。 */
(function(){
  var GO = { th:'#thanks', st:'#standby', pr:'#profile', ti:'#title',
             qa:'#ask',    ma:'#map',     ur:'#gate',    go:'#boot', en:'#end',
             pw:'#ledger', mx:'#matrix' };
  /* トップへの行き方。フッターのリンクが階層を知っているので、あればそれを借りる。
     無い資料もあるので、その場合は置き場所（01_… / AX_Table / Training）から判断する */
  function home(){
    var a = document.querySelector('a[href$="index.html"]');
    if (a) return a.getAttribute('href');
    var seg = location.pathname.split('/');
    var dir = decodeURIComponent(seg[seg.length - 2] || '');
    return /^(0\\d_|AX_Table|Training)/.test(dir) ? '../index.html' : 'index.html';
  }
  var buf = '';
  document.addEventListener('keydown', function(e){
    var t = e.target;
    if (t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
    if (!e.key || e.key.length !== 1 || e.metaKey || e.ctrlKey || e.altKey) return;
    buf = (buf + e.key.toLowerCase()).slice(-4);
    var k = buf.slice(-2);
    if (GO[k]){ buf = ''; location.href = home() + GO[k]; }
  });
})();
</script>
"""


def patch(html):
    if MARK in html:
        return None
    # 旧版が入っていたら、そっくり外してから入れ直す。
    # 二重に置くと同じキーが2回走る
    html = re.sub(r'\n?<script>\n/\* OZ-KEYNAV v[12] \*/[\s\S]*?</script>\n?', '\n', html)
    i = html.rfind('</body>')
    if i < 0:
        return None
    return html[:i] + JS + html[i:]


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, 'AX_Table', '*.html'))):
    for f in sorted(glob.glob(os.path.join(ROOT, 'Training', '*.html'))):
        yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        b = os.path.basename(f)
        if b not in ('index.html', 'ask.html'):   # この2つは自前で持っている
            yield f


if __name__ == '__main__':
    done = skip = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, PW) if enc else raw
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        if enc:
            lockbox.encrypt(f, PW, new)
            assert lockbox.decrypt(f, PW) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        done += 1
    print('適用 %d ページ / 適用済み %d' % (done, skip))
