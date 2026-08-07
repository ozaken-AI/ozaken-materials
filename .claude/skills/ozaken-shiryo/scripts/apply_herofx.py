#!/usr/bin/env python3
"""全資料のファーストビューに、index.html と同じ演出を入れる。

index のヒーローが持っている語彙をそのまま持ち込む：
  走査線が一度抜ける／見出しを左から拭き取る／背景がゆっくり流れる／
  星が瞬き、星座の線が引かれる／四隅のHUD／稼働状況の読み出し／スクロール誘導
資料ページは .hero .inner に data-reveal が付いていて初期状態が opacity:0 のため、
ヒーロー内だけは reveal を解除し、この演出で見せる。
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
import lockbox

ROOT = oz_root.root(HERE)
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '/* OZ-HEROFX v6 */'
MARK_END = '/* /OZ-HEROFX */'

CSS = MARK + """
/* ══ ファーストビューの演出（index.html と同じ語彙） ══ */
/* 地の色は index.html とまったく同じ組み合わせにする。
   単色の紺だと平坦に見えるが、上からの光・右下の赤み・斜めの三段グラデを
   重ねると奥行きが出る。資料ごとに違う紺だと、並べたとき「別のサイト」に見える。
   写真を敷いた AX Table のヒーローだけは、その写真が主役なので触らない */
.hero:not([data-kabe]){
  background:
    radial-gradient(ellipse 60% 46% at 50% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
    radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
    radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
    linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
}
/* ヒーロー内は reveal を使わず、この演出で出す */
.hero [data-reveal]{opacity:1;transform:none;transition:none}
.hero .inner{position:relative;z-index:3}
/* ファーストビューは画面を占有する。投影したときに1枚目として成立させるため、
   高さの上限を設けない。svh はスマホのアドレスバーで高さが変わるのを避けるため。
   AX Tableの写真ヒーローは自前の組みを持っているので触らない */
.hero:not([data-kabe]){min-height:100vh;min-height:100svh;
  display:flex;flex-direction:column;justify-content:center;
  padding-top:clamp(4rem,9vh,7rem);padding-bottom:clamp(5rem,10vh,7rem)}
/* 写真ヒーローも同じ高さに揃える。組み（左寄せ・覆い）は自前のものを残す */
.hero[data-kabe]{min-height:100vh;min-height:100svh;
  display:flex;flex-direction:column;justify-content:center}
/* 背の低い画面では、詰めてでも1画面に収める */
@media(max-height:560px){
  .hero:not([data-kabe]){padding-top:3.2rem;padding-bottom:3.6rem}
  .hero-title{font-size:clamp(1.5rem,4.4vh,2.4rem)}
  .hero-copy{font-size:.92rem}}
/* 背景がゆっくり流れる */
.hero .texture{animation:ozPan 30s ease-in-out infinite alternate}
@keyframes ozPan{
  from{transform:translate3d(-1.4%,-1%,0) scale(1.05)}
  to{transform:translate3d(1.6%,1.6%,0) scale(1.11)}}
/* 星が瞬く。pattern 内の格子には効かないよう、svg直下だけを狙う */
.hero .texture > svg > circle{animation:ozTwinkle 5.4s ease-in-out infinite}
.hero .texture > svg > circle:nth-of-type(2){animation-delay:1.3s}
.hero .texture > svg > circle:nth-of-type(3){animation-delay:2.7s}
.hero .texture > svg > circle:nth-of-type(4){animation-delay:4s}
@keyframes ozTwinkle{0%,100%{opacity:.3}50%{opacity:1}}
/* 星座の線が引かれる */
.hero .texture > svg > path{stroke-dasharray:1600;stroke-dashoffset:1600;
  animation:ozDraw 2.6s cubic-bezier(.3,.7,.3,1) .35s forwards}
@keyframes ozDraw{to{stroke-dashoffset:0}}
/* 走査線が一度だけ抜ける */
.oz-sweep{position:absolute;left:0;right:0;top:0;height:2px;z-index:2;opacity:0;
  pointer-events:none;background:linear-gradient(90deg,transparent,#9fc6f5,transparent);
  box-shadow:0 0 18px rgba(159,198,245,.75);
  animation:ozSweep 1.7s cubic-bezier(.4,0,.2,1) .05s both}
@keyframes ozSweep{0%{top:0;opacity:0}10%{opacity:1}88%{opacity:1}100%{top:100%;opacity:0}}
/* 見出しは左から拭き取るように、他は下から立ち上がる */
.hero .eyebrow{animation:ozRise .9s .15s both}
.hero-title{animation:ozWipe 1.15s cubic-bezier(.2,.7,.2,1) .3s both}
.hero-copy{animation:ozRise 1s .55s both}
.hero-meta,.hero-tag{animation:ozRise 1s .7s both}
@keyframes ozRise{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
@keyframes ozWipe{
  from{opacity:0;clip-path:inset(0 100% 0 0);transform:translateY(16px)}
  to{opacity:1;clip-path:inset(0 0 0 0);transform:none}}
/* 見出しの赤い強調。index の .hl と同じ振る舞い */
.hero-title .hl{color:var(--red-bright);
  animation:ozGlitch .24s steps(2) 1.25s 3 both,ozHlBlink 9s linear 3s infinite}
@keyframes ozGlitch{0%{opacity:.3;transform:translateX(-3px)}
  50%{opacity:1;transform:translateX(2px)}100%{opacity:1;transform:none}}
@keyframes ozHlBlink{0%,90%{opacity:1;transform:none}
  91%{opacity:.2;transform:translateX(-2px)}92.5%{opacity:1;transform:translateX(2px)}
  94%{opacity:.4;transform:none}95.5%,100%{opacity:1;transform:none}}
/* システム表記バッジ（index と同じ） */
.sys-badge{position:absolute;top:1.6rem;left:1.6rem;z-index:4;
  display:inline-flex;align-items:center;gap:.55rem;
  padding:.5em .95em;border-radius:999px;
  background:rgba(20,29,53,.5);border:1px solid rgba(216,228,240,.22);
  backdrop-filter:blur(6px);
  font-family:var(--font-en);font-size:.66rem;font-weight:600;letter-spacing:.16em;
  color:rgba(216,228,240,.9);text-transform:uppercase;white-space:nowrap;
  animation:ozFadeIn .8s .5s both}
.sys-badge .dot{width:7px;height:7px;border-radius:50%;background:var(--red-bright);
  box-shadow:0 0 8px var(--red-bright);animation:ozSysPulse 2.2s ease-in-out infinite}
.sys-badge .ja{font-family:var(--font-ja-sans);letter-spacing:.06em;font-size:.7rem;color:#fff}
.sys-badge .sep{color:rgba(216,228,240,.35)}
.sys-badge .ver{color:rgba(216,228,240,.55)}
@keyframes ozSysPulse{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes ozFadeIn{from{opacity:0}to{opacity:1}}
/* 画面を囲む枠。光が12秒で一周し、四隅は明滅し続ける。
   これはファーストビューの演出なので、本文に入ったら引っ込める。
   本文を読んでいる間じゅう縁が動いていると、図版の動きと喧嘩する */
.site-frame{position:fixed;inset:0;z-index:60;pointer-events:none;
  opacity:1;transition:opacity .55s ease}
html.past-hero .site-frame{opacity:0}
.sf-edge{position:absolute;overflow:hidden;background:rgba(159,198,245,.13)}
.sf-t{top:18px;left:18px;right:18px;height:1px}
.sf-b{bottom:18px;left:18px;right:18px;height:1px}
.sf-l{left:18px;top:18px;bottom:18px;width:1px}
.sf-r{right:18px;top:18px;bottom:18px;width:1px}
.sf-edge i{position:absolute;display:block;box-shadow:0 0 10px rgba(159,198,245,.75)}
.sf-t i,.sf-b i{top:0;height:1px;width:170px;left:-170px;
  background:linear-gradient(90deg,transparent,#9fc6f5,transparent)}
.sf-l i,.sf-r i{left:0;width:1px;height:170px;top:-170px;
  background:linear-gradient(180deg,transparent,#9fc6f5,transparent)}
.sf-t i{animation:sfT 12s linear infinite}
.sf-r i{animation:sfR 12s linear infinite}
.sf-b i{animation:sfB 12s linear infinite}
.sf-l i{animation:sfL 12s linear infinite}
@keyframes sfT{0%{left:-170px;opacity:1}25%{left:100%;opacity:1}25.01%,100%{opacity:0;left:-170px}}
@keyframes sfR{0%,25%{opacity:0;top:-170px}25.01%{opacity:1}50%{top:100%;opacity:1}50.01%,100%{opacity:0;top:-170px}}
@keyframes sfB{0%,50%{opacity:0;left:100%}50.01%{opacity:1}75%{left:-170px;opacity:1}75.01%,100%{opacity:0;left:100%}}
@keyframes sfL{0%,75%{opacity:0;top:100%}75.01%{opacity:1}100%{top:-170px;opacity:1}}
.sf-c{position:absolute;width:28px;height:28px;border:1px solid rgba(159,198,245,.34);
  animation:sfIn .55s ease both,sfBreathe 4.6s ease-in-out .55s infinite}
.sf-c1{top:14px;left:14px;border-right:0;border-bottom:0}
.sf-c2{top:14px;right:14px;border-left:0;border-bottom:0;animation-delay:.1s,.65s}
.sf-c3{bottom:14px;left:14px;border-right:0;border-top:0;animation-delay:.2s,.75s}
.sf-c4{bottom:14px;right:14px;border-left:0;border-top:0;animation-delay:.3s,.85s}
@keyframes sfIn{from{opacity:0;transform:scale(1.7)}to{opacity:1;transform:none}}
@keyframes sfBreathe{0%,100%{opacity:.38}50%{opacity:.95}}
/* 漂う点と、近い点をつなぐ線 */
.oz-net{position:absolute;inset:0;z-index:1;pointer-events:none;display:block}
/* 稼働状況の読み出し */
.oz-status{position:relative;z-index:3;margin-top:1.9rem;font-family:var(--font-en);
  font-size:.64rem;font-weight:700;letter-spacing:.2em;color:rgba(159,198,245,.82);
  font-variant-numeric:tabular-nums;line-height:1.9;
  display:flex;flex-wrap:wrap;align-items:center;justify-content:center;
  gap:.1rem .2rem;animation:ozRise 1s .8s both}
.hero[data-kabe] .oz-status{justify-content:flex-start}
.oz-live{display:inline-block;width:7px;height:7px;border-radius:50%;background:#46c98a;
  box-shadow:0 0 8px #46c98a;margin-right:.6rem;vertical-align:middle;
  animation:ozPulse 2s ease-in-out infinite}
@keyframes ozPulse{0%,100%{opacity:1}50%{opacity:.32}}
.oz-sep{color:rgba(159,198,245,.4);margin:0 .5rem}
.oz-cur{margin-left:.15em;animation:ozBlink 1.1s steps(1) infinite}
@keyframes ozBlink{0%,50%{opacity:1}50.01%,100%{opacity:0}}
/* スクロール誘導 */
.oz-scroll{position:absolute;bottom:1.9rem;left:50%;transform:translateX(-50%);z-index:3;
  display:flex;flex-direction:column;align-items:center;gap:.35rem;pointer-events:none;
  font-family:var(--font-en);font-size:.6rem;font-weight:600;letter-spacing:.28em;
  color:rgba(216,228,240,.55);animation:ozRise 1s 1.05s both}
.oz-chev{font-size:1.1rem;line-height:.6;animation:ozBob 1.9s ease-in-out infinite}
@keyframes ozBob{0%,100%{transform:translateY(0)}50%{transform:translateY(7px)}}
@media(max-width:640px){
  .oz-status{font-size:.55rem;letter-spacing:.14em}
  .oz-scroll{display:none}
  .sys-badge{top:1rem;left:1rem;font-size:.58rem;padding:.42em .8em;gap:.4rem}
  .sys-badge .ja{font-size:.62rem}
  .sys-badge .ver{display:none}
  .sf-t{top:10px;left:10px;right:10px}.sf-b{bottom:10px;left:10px;right:10px}
  .sf-l{left:10px;top:10px;bottom:10px}.sf-r{right:10px;top:10px;bottom:10px}
  .sf-c{width:18px;height:18px}
  .sf-c1{top:7px;left:7px}.sf-c2{top:7px;right:7px}
  .sf-c3{bottom:7px;left:7px}.sf-c4{bottom:7px;right:7px}}
@media (prefers-reduced-motion: reduce){
  .hero .texture,.hero .texture > svg > circle,.hero .eyebrow,.hero-title,.hero-copy,
  .hero-meta,.hero-tag,.oz-sweep,.oz-status,.oz-scroll,.oz-chev,.oz-live,.oz-cur,
  .hero-title .hl,.sys-badge .dot,.sf-c{animation:none}
  .hero .texture > svg > path{stroke-dashoffset:0}
  .oz-sweep,.sf-edge i,.oz-net{display:none}
  .sf-c{opacity:.5}}/* /OZ-HEROFX */
"""

JS = """
<script>
/* ファーストビューの演出パーツを組み立てる。
   資料の中身から本数を数えるので、加筆しても読み出しは自動で追従する。 */
(function(){
  var hero = document.querySelector('.hero');
  if (!hero || hero.querySelector('.oz-sweep')) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function mk(tag, cls){ var e = document.createElement(tag); if (cls) e.className = cls; return e; }

  /* ── ページ全体を囲む枠（index と同じ） ── */
  if (!document.querySelector('.site-frame')){
    var fr = mk('div','site-frame');
    fr.setAttribute('aria-hidden','true');
    fr.innerHTML = '<span class="sf-edge sf-t"><i></i></span>'
      + '<span class="sf-edge sf-r"><i></i></span>'
      + '<span class="sf-edge sf-b"><i></i></span>'
      + '<span class="sf-edge sf-l"><i></i></span>'
      + '<span class="sf-c sf-c1"></span><span class="sf-c sf-c2"></span>'
      + '<span class="sf-c sf-c3"></span><span class="sf-c sf-c4"></span>';
    document.body.insertBefore(fr, document.body.firstChild);
  }

  /* ファーストビューを抜けたら、縁の演出を引っ込める */
  if ('IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      document.documentElement.classList.toggle('past-hero', !es[0].isIntersecting);
    }, { threshold: 0.02 }).observe(hero);
  }

  /* ── 左上のシステム表記（index と同じ） ── */
  if (!hero.querySelector('.sys-badge')){
    var bd = mk('div','sys-badge');
    bd.setAttribute('aria-label','おざけんコンテンツ管理システム');
    bd.innerHTML = '<span class="dot" aria-hidden="true"></span>'
      + '<span class="ja">おざけん コンテンツ管理システム</span>'
      + '<span class="sep">/</span><span>OZAKEN CMS</span>'
      + '<span class="ver">v2.0</span>';
    hero.insertBefore(bd, hero.firstChild);
  }

  hero.appendChild(mk('div','oz-sweep'));

  /* ── 見出しの一語を赤で強調する。「」の中を最優先、無ければ英字のかたまり ── */
  (function(){
    var t = hero.querySelector('.hero-title');
    if (!t || t.querySelector('.hl')) return;
    var pats = [/「([^」]{1,14})」/, /\\b([A-Za-z][A-Za-z0-9.+#-]{1,17})\\b/];
    var walk = document.createTreeWalker(t, NodeFilter.SHOW_TEXT, null);
    var nodes = [], n;
    while ((n = walk.nextNode())) nodes.push(n);
    for (var p = 0; p < pats.length; p++){
      for (var i = 0; i < nodes.length; i++){
        var m = pats[p].exec(nodes[i].nodeValue);
        if (!m) continue;
        var node = nodes[i];
        var s = m.index + m[0].indexOf(m[1]);
        var tail = node.splitText(s);
        tail.splitText(m[1].length);
        var sp = mk('span','hl');
        sp.textContent = m[1];
        tail.parentNode.replaceChild(sp, tail);
        return;
      }
    }
  })();

  /* ── 稼働状況の読み出し ── */
  var secs = document.querySelectorAll('section.sec-light, section.sec-navy').length;
  var figs = document.querySelectorAll('.figure').length;
  var chars = (document.body.textContent || '').replace(/\\s/g, '').length;
  var min = Math.max(1, Math.round(chars / 520));

  var st = mk('p','oz-status');
  var html = '<span class="oz-live"></span>SYSTEM ONLINE';
  if (secs) html += '<span class="oz-sep">／</span>' + secs + ' SECTIONS';
  if (figs) html += '<span class="oz-sep">／</span>' + figs + ' FIGURES';
  html += '<span class="oz-sep">／</span>EST. ' + min + ' MIN<span class="oz-cur">_</span>';
  st.innerHTML = html;
  (hero.querySelector('.inner') || hero).appendChild(st);

  var sc = mk('div','oz-scroll');
  sc.innerHTML = '<span>SCROLL</span><span class="oz-chev">&#8964;</span>';
  hero.appendChild(sc);

  /* ── 漂う点と、近い点をつなぐ線（index と同じ挙動） ── */
  if (reduce) return;
  var cv = mk('canvas','oz-net');
  cv.setAttribute('aria-hidden','true');
  hero.insertBefore(cv, hero.firstChild);
  var ctx = cv.getContext('2d');
  if (!ctx) return;
  var DPR = Math.min(2, window.devicePixelRatio || 1);
  /* つながる距離。線の本数はこの二乗で効く。index.html と同じ 100 に揃える */
  var LINK = 100, parts = [], W = 0, H = 0, vis = true;
  function resize(){
    var w = hero.clientWidth, h = hero.offsetHeight;
    if (!w || !h) return;
    W = w; H = h;
    cv.width = Math.round(w*DPR); cv.height = Math.round(h*DPR);
    cv.style.width = w+'px'; cv.style.height = h+'px';
    ctx.setTransform(DPR,0,0,DPR,0,0);
    var n = Math.max(12, Math.min(48, Math.round(w*h/26000)));
    if (parts.length !== n){
      parts = [];
      for (var i=0;i<n;i++) parts.push({ x:Math.random()*w, y:Math.random()*h,
        vx:(Math.random()-0.5)*0.24, vy:(Math.random()-0.5)*0.24, r:Math.random()*1.3+1.1 });
    }
  }
  resize();
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(hero);
  if ('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ vis = es[0].isIntersecting; },
      { rootMargin:'140px' }).observe(hero);
  }
  var rt; window.addEventListener('resize', function(){
    clearTimeout(rt); rt = setTimeout(resize, 160); });
  function frame(){
    if (vis && W){
      ctx.clearRect(0,0,W,H);
      for (var i=0;i<parts.length;i++){
        var a = parts[i];
        a.x += a.vx; a.y += a.vy;
        if (a.x < 0 || a.x > W) a.vx *= -1;
        if (a.y < 0 || a.y > H) a.vy *= -1;
        for (var j=i+1;j<parts.length;j++){
          var b = parts[j], dx = a.x-b.x, dy = a.y-b.y, d = Math.sqrt(dx*dx+dy*dy);
          if (d < LINK){
            ctx.strokeStyle = 'rgba(216,228,240,'+((1-d/LINK)*0.5).toFixed(3)+')';
            ctx.lineWidth = 0.7;
            ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
          }
        }
      }
      ctx.fillStyle = 'rgba(216,228,240,0.85)';
      for (var m=0;m<parts.length;m++){
        var q = parts[m];
        ctx.beginPath(); ctx.arc(q.x,q.y,q.r,0,6.2832); ctx.fill();
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
</script>
"""


def patch(html):
    if MARK in html:
        return None
    i = html.rfind('</style>')
    if i < 0:
        return None
    html = html[:i] + CSS + html[i:]
    j = html.rfind('</body>')
    if j < 0:
        return None
    return html[:j] + JS + html[j:]


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in ('AX_Table', 'Training'):        # 裏資料の置き場は2つ
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(f) != 'index.html':   # indexは元から演出を持っている
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
    print('適用 %d ページ / 対象外・適用済み %d' % (done, skip))
