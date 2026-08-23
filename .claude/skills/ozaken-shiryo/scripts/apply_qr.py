#!/usr/bin/env python3
"""資料の中に、会場に見せるQRコードを仕込む。──「QR画面」

**個別パスワードを持つ資料すべてに入る**（表・裏を問わない）。
壇上のパソコンで `qr` と打つと、全画面にQRコードと**個別パスワード**が出る。
聴いている人はスマートフォンのカメラを向けるだけで、その資料を開ける。

表の資料でも、講演で1本だけ見せたいときに「この資料はここです」と渡せる。
裏資料だけに入れていたときは、そのたびにURLを読み上げていた。

URLを読み上げるのは無理があるし、短縮URLは外のサービスに依存する。
パスワードは口頭で言うと必ず聞き返される。**両方まとめて画面に出せば済む。**

QRの升目は `qrgen.py` がビルド時に作り、SVGとして資料の中に焼く。
実行時に何も取りに行かないので、鍵の中から外へ出る通信は起きない。

  qr と打つ         壇上のパソコンで。どこにも触れずに打つだけで出る
  URLに #qr         あとから見せるとき用

  OZAKEN_PW=マスター python3 apply_qr.py          # 入れる（冪等）
  OZAKEN_PW=マスター python3 apply_qr.py refresh  # 見た目を直したとき、当て直す
  OZAKEN_PW=マスター python3 apply_qr.py list     # どの資料に何のURLが入るか
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import qrgen
import registry

ROOT = oz_root.root(HERE)
from oz_site import SITE          # 引っ越すときは oz_site.py だけを直す
BACKSTAGE = os.path.join(ROOT, 'backstage.html')
MARK = '<!-- OZ-QR v1 -->'

CSS = """
/* OZ-QR v1 ── 会場に見せるQR画面（個別パスワードを持つ資料すべて） */
.qrv{position:fixed;inset:0;z-index:9200;display:none;
  font-family:var(--font-ja-sans);color:#fff;
  background:linear-gradient(168deg,#1f3864 0%,#182a52 44%,#141d35 100%);
  overflow-y:auto;-webkit-overflow-scrolling:touch}
.qrv.on{display:block}
.qrv-in{min-height:100%;display:flex;flex-wrap:wrap;align-items:center;
  justify-content:center;gap:clamp(1.4rem,4vw,3.4rem);
  padding:clamp(1.4rem,4vw,3rem) 1.2rem calc(2rem + env(safe-area-inset-bottom))}
.qrv-x{position:absolute;top:.7rem;right:.7rem;width:2.8rem;height:2.8rem;
  font-size:1.5rem;line-height:1;color:rgba(216,228,240,.8);
  background:transparent;border:0;cursor:pointer}
.qrv-card{flex:none;width:clamp(210px,46vmin,460px);padding:1rem;border-radius:18px;
  background:#fff;box-shadow:0 20px 60px rgba(10,15,28,.45)}
.qrv-card svg{display:block;width:100%;height:auto}
.qrv-side{width:min(460px,100%)}
.qrv-tag{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.18em;color:var(--navy-deep);background:var(--azure-pale);
  padding:4px 11px;border-radius:999px;margin-bottom:.9rem}
.qrv-ttl{font-family:var(--font-ja-serif);font-weight:600;line-height:1.6;
  font-size:clamp(1.12rem,3.2vw,1.72rem);margin-bottom:.6rem}
.qrv-url{font-family:var(--font-en);font-size:.76rem;line-height:1.7;
  color:rgba(216,228,240,.65);word-break:break-all;margin-bottom:1.2rem}
.qrv-pw{padding:.9rem 1.1rem;border-radius:14px;
  background:rgba(255,255,255,.07);border:1px solid rgba(216,228,240,.24)}
.qrv-pw span{display:block;font-family:var(--font-en);font-size:.6rem;font-weight:700;
  letter-spacing:.16em;color:rgba(216,228,240,.6);margin-bottom:.25rem}
.qrv-pw b{font-family:var(--font-en);font-weight:700;letter-spacing:.06em;
  font-size:clamp(1.3rem,4.4vw,2.5rem);color:#fff}
.qrv-note{font-size:.8rem;line-height:1.9;color:rgba(216,228,240,.7);margin-top:1rem}
body.qz-lock{overflow:hidden}      /* 確認テストを入れていない資料にも要る */
@media print{.qrv{display:none !important}}
/* /OZ-QR */
"""

JS = """
<script>
/* QR画面：壇上で qr と打つと出る。中身はビルド時に焼いてあるので、何も取りに行かない */
(function(){
  var qrv = document.querySelector('.qrv');
  if (!qrv) return;
  function open(){ qrv.classList.add('on'); document.body.classList.add('qz-lock'); }
  function close(){ qrv.classList.remove('on'); document.body.classList.remove('qz-lock'); }
  qrv.querySelector('.qrv-x').addEventListener('click', close);
  qrv.addEventListener('click', function(e){ if (e.target === qrv) close(); });

  var buf = '';
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape'){ close(); return; }
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.key.length !== 1) return;
    buf = (buf + e.key.toLowerCase()).slice(-8);
    if (buf.indexOf('qr') >= 0){ buf = ''; open(); }
  });
  if (/^#qr$/i.test(location.hash)) setTimeout(open, 400);
})();
</script>
"""


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def targets(pw):
    """個別パスワードを持つ資料すべて。台帳が正。

    道具のページ（台帳・裏資料置き場・資料マトリクス）はマスターだけで開き、
    個別パスワードを持たないので、ここで自然に外れる。

    **板（ダッシュボード）も外す。** QR画面は `qr` と2文字打つと開く仕掛けで、
    それを拾っているのは apply_keynav が入れた仕組みのほう。
    板にはそれが入っていないので、入れても開かない升目が末尾に残るだけになる。
    """
    from crossref_data import NOT_DECKS
    led = registry.load(pw)
    out = []
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        if rel in NOT_DECKS:
            continue
        if (led.get(rel) or {}).get('pw'):
            out.append(rel)
    return sorted(out)


def block(rel, title, pw):
    url = SITE + rel
    e = lambda s: H.escape(s, quote=True)
    return (
        '<div class="qrv">\n'
        '  <div class="qrv-in">\n'
        '    <button class="qrv-x" aria-label="閉じる">×</button>\n'
        '    <div class="qrv-card">%s</div>\n'
        '    <div class="qrv-side">\n'
        '      <span class="qrv-tag">SCAN TO OPEN</span>\n'
        '      <h3 class="qrv-ttl">%s</h3>\n'
        '      <p class="qrv-url">%s</p>\n'
        '      <div class="qrv-pw"><span>PASSWORD</span><b>%s</b></div>\n'
        '      <p class="qrv-note">スマートフォンのカメラを向けると開きます。'
        'このパスワードを入れてご覧ください。</p>\n'
        '    </div>\n  </div>\n</div>\n'
        % (qrgen.svg(url), e(title), e(url), e(pw)))


CSS_HEAD = CSS.split('\n')[1]
CSS_TAIL = '/* /OZ-QR */'


def strip(html):
    """入れたぶんを外す。作り直したいときに、いったん綺麗にする"""
    i = html.find(CSS_HEAD)
    if i >= 0:
        j = html.find(CSS_TAIL, i)
        if j >= 0:
            html = html[:i] + html[j + len(CSS_TAIL):]
    i = html.find(MARK)
    if i >= 0:
        k = html.rfind('<div class="qrv">', 0, i)
        if k >= 0:
            html = html[:k] + html[i + len(MARK) + 1:]
    return html


def patch(html, rel, title, pw):
    if MARK in html:
        return None
    i = html.rfind('</style>')
    j = html.rfind('</body>')
    if i < 0 or j < 0:
        return None
    html = html[:i] + CSS + html[i:]
    j = html.rfind('</body>')
    return html[:j] + block(rel, title, pw) + JS + '\n' + MARK + '\n' + html[j:]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'apply'
    m = master()
    led = registry.load(m)

    if cmd == 'list':
        for rel in targets(m):
            row = led.get(rel, {})
            print('%-44s %-20s %s' % (rel, row.get('pw', '（無し）'), SITE + rel))
        return

    done = 0
    for rel in targets(m):
        row = led.get(rel)
        if not row or not row.get('pw'):
            print('  台帳に個別パスワードが無いので飛ばす:', rel)
            continue
        path = os.path.join(ROOT, rel)
        inner = lockbox.decrypt(path, m)
        if cmd == 'refresh':
            inner = strip(inner)
        new = patch(inner, rel, row.get('title', rel), row['pw'])
        if new is None:
            continue
        lockbox.encrypt(path, m, new)
        assert lockbox.decrypt(path, m) == new
        done += 1
        print('  QR画面を入れた:', rel)
    print('%d ページ' % done)


if __name__ == '__main__':
    main()
