#!/usr/bin/env python3
"""既存の資料の図版に、動きを与える。

スタイル側には a-fade / a-pop / a-grow / a-draw の仕掛けが最初からあり、
画面に入ったら .anim-on が付く仕組みも動いている。
足りていなかったのは、SVGの各要素に印と遅延を振ることだった。

さらに、出たあとも動き続けるもの（矢印・破線が流れる、色帯や点が呼吸する）を
足している。投影中に気が散らないよう、どれもゆっくり・小さく。

新しく作る資料は domain_fig._fig() が自動で振るので、この道具は既存資料向け。
対象は .figure と .hero-glyph の中のSVGだけ。
ファーストビューの背景SVGは別の演出を持っているので触らない。
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
from domain_fig import _animate

ROOT = os.environ.get('OZAKEN_ROOT') or os.path.dirname(os.path.dirname(HERE))
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '<!-- OZ-FIGANIM v2 -->'

CSS = """
/* OZ-FIGFLOW v1 */
/* 出たあとも動き続けるもの。投影中に気が散らないよう、ゆっくり・小さく */
.figanim .figure svg .a-flow, .figanim .hero-glyph svg .a-flow,
.figanim .figure svg .a-breathe, .figanim .hero-glyph svg .a-breathe { opacity: 0; }
.figanim .figure.anim-on svg .a-flow,
.figanim .hero-glyph.anim-on svg .a-flow {
  stroke-dasharray: 9 5;
  animation: figFade 0.55s ease var(--d,0s) both,
             figFlow 0.9s linear var(--d,0s) infinite;
}
.figanim .figure.anim-on svg .a-breathe,
.figanim .hero-glyph.anim-on svg .a-breathe {
  animation: figFade 0.55s ease var(--d,0s) both,
             figBreathe 4.2s ease-in-out calc(var(--d,0s) + 0.6s) infinite;
}
@keyframes figFlow { to { stroke-dashoffset: -14; } }
@keyframes figBreathe { 0%,100% { opacity: 1; } 50% { opacity: 0.62; } }
@media (prefers-reduced-motion: reduce) {
  .figanim .figure svg .a-flow, .figanim .figure svg .a-breathe,
  .figanim .hero-glyph svg .a-flow, .figanim .hero-glyph svg .a-breathe {
    opacity: 1; animation: none !important; stroke-dasharray: none !important;
  }
}
"""

TRIGGER = """
<script>
/* 図版アニメーション：図が画面に入ったら、線が引かれ・バーが伸び・ノードが立ち上がる */
(function(){
  var figs = document.querySelectorAll('.figure, .hero-glyph');
  if (!figs.length) return;
  document.documentElement.classList.add('figanim');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce){
    figs.forEach(function(f){ f.classList.add('anim-on'); });
    return;
  }
  // 線の実長を測って、伏せた状態にしておく
  figs.forEach(function(f){
    f.querySelectorAll('.a-draw').forEach(function(el){
      try {
        var L = el.getTotalLength();
        if (!L) return;
        el.style.strokeDasharray = L;
        el.style.strokeDashoffset = L;
      } catch(e){}
    });
  });
  function play(f){
    f.classList.add('anim-on');
    f.querySelectorAll('.a-draw').forEach(function(el){ el.style.strokeDashoffset = 0; });
  }
  if (!('IntersectionObserver' in window)){
    figs.forEach(play);
    return;
  }
  var fo = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (e.isIntersecting){ play(e.target); fo.unobserve(e.target); }
    });
  }, { threshold: 0.18 });
  figs.forEach(function(f){ fo.observe(f); });
})();
</script>
"""


BLOCK = re.compile(
    r'(<div class="(?:figure|hero-glyph)[^"]*">[\s\S]*?)(<svg[\s\S]*?</svg>)')


def unmark(svg):
    """前の版で振った印を外す。規則が変わったら振り直せるように"""
    svg = re.sub(r'\s?class="a-fade"\s?style="--d:[\d.]+s"', '', svg)
    svg = re.sub(r'class="a-fade ', 'class="', svg)
    svg = re.sub(r'style="--d:[\d.]+s;', 'style="', svg)
    return re.sub(r'\s?style="--d:[\d.]+s"', '', svg)


def patch(html):
    if MARK in html:
        return None
    # 旧版の印とCSSをいったん外してから、いまの規則で入れ直す
    html = re.sub(r'<!-- OZ-FIGANIM v1 -->\n?', '', html)
    i = html.find('/* OZ-FIGFLOW v1 */')
    if i >= 0:
        j = html.find('</style>', i)
        html = html[:i] + html[j:]

    n = [0]

    def one(m):
        head, svg = m.group(1), m.group(2)
        n[0] += 1
        return head + _animate(unmark(svg))

    out = BLOCK.sub(one, html)
    if not n[0]:
        return None
    j = out.rfind('</style>')
    if j > 0:
        out = out[:j] + CSS + out[j:]
    # 古い資料には図版アニメーションの起動スクリプトが無いことがある。
    # 印だけ振っても .figanim が付かないと動かないので、無ければ足す
    if 'figanim' not in out or "classList.add('figanim')" not in out:
        k = out.rfind('</body>')
        if k > 0:
            out = out[:k] + TRIGGER + '\n' + out[k:]
    i = out.rfind('</body>')
    return out[:i] + MARK + '\n' + out[i:] if i > 0 else out + MARK


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, 'AX_Table', '*.html'))):
        yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(f) not in ('index.html', 'ask.html'):
            yield f


if __name__ == '__main__':
    done = skip = flow = breathe = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, PW) if enc else raw
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        flow += new.count('a-flow')
        breathe += new.count('a-breathe')
        if enc:
            lockbox.encrypt(f, PW, new)
            assert lockbox.decrypt(f, PW) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        done += 1
    print('動きを付けた %d ページ / 対象外 %d ／ 流れる線 %d 個・呼吸する要素 %d 個'
          % (done, skip, flow, breathe))
