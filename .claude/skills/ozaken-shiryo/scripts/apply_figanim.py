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
import oz_root
import lockbox
from domain_fig import _animate

ROOT = oz_root.root(HERE)
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '<!-- OZ-FIGANIM v3 -->'

# キーフレームの名前は oz- で始める。資料ごとに定義が違う figFade などを
# 借りると、その定義を持たない古い資料で「opacity:0 のまま」になり、
# 矢印が丸ごと消える。実際に17本でそれが起きた
CSS_END = '/* /OZ-FIGFLOW */'

CSS = """
/* OZ-FIGFLOW v3 */
/* 出たあとも動き続けるもの。投影中に気が散らないよう、ゆっくり・小さく */
.figanim .figure svg .a-flow, .figanim .hero-glyph svg .a-flow,
.figanim .figure svg .a-breathe, .figanim .hero-glyph svg .a-breathe,
.figanim .figure svg .a-pulse, .figanim .hero-glyph svg .a-pulse { opacity: 0; }
.figanim .figure.anim-on svg .a-flow,
.figanim .hero-glyph.anim-on svg .a-flow {
  stroke-dasharray: 9 5;
  animation: ozFxIn 0.55s ease var(--d,0s) both,
             ozFlow 0.9s linear var(--d,0s) infinite;
}
.figanim .figure.anim-on svg .a-breathe,
.figanim .hero-glyph.anim-on svg .a-breathe {
  animation: ozFxIn 0.55s ease var(--d,0s) both,
             ozBreathe 4.2s ease-in-out calc(var(--d,0s) + 0.6s) infinite;
}
.figanim .figure.anim-on svg .a-pulse,
.figanim .hero-glyph.anim-on svg .a-pulse {
  transform-box: fill-box; transform-origin: center;
  animation: ozFxIn 0.55s ease var(--d,0s) both,
             ozPulse 3.4s ease-in-out calc(var(--d,0s) + 0.6s) infinite;
}
@keyframes ozFxIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes ozFlow { to { stroke-dashoffset: -14; } }
@keyframes ozBreathe { 0%,100% { opacity: 1; } 50% { opacity: 0.62; } }
@keyframes ozPulse {
  0%,100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.06); opacity: 0.84; }
}
/* ── マウスを載せたところが、必ず何かしら返す ────────────────────
   **講演では、話し手がカーソルで図を指す。**
   指したところが少しでも反応すると、聴いている側の目がそこへ付いてくる。
   レーザーポインタの代わりになる。

   反応させるのは、作図側が動きの印を付けた要素だけ。
   図の地や枠まで光ると、どこを指しているのか分からなくなる。

   触れる端末は対象外（`hover:hover`）。指で触れた瞬間に光ると、
   スクロールしているだけで図がちらつく */
@media (hover: hover) and (pointer: fine) {
  .figure svg .a-fade, .figure svg .a-pop, .figure svg .a-rise,
  .figure svg .a-grow, .figure svg .a-draw, .figure svg .a-flow,
  .figure svg .a-pulse, .figure svg .a-breathe,
  .hero-glyph svg .a-fade, .hero-glyph svg .a-pop {
    transform-box: fill-box; transform-origin: center;
    transition: filter .16s ease, transform .16s ease;
  }
  .figure svg .a-fade:hover, .figure svg .a-pop:hover, .figure svg .a-rise:hover,
  .figure svg .a-grow:hover, .figure svg .a-draw:hover, .figure svg .a-flow:hover,
  .figure svg .a-pulse:hover, .figure svg .a-breathe:hover,
  .hero-glyph svg .a-fade:hover, .hero-glyph svg .a-pop:hover {
    filter: brightness(1.16) drop-shadow(0 2px 9px rgba(46,84,150,.38));
  }
  /* 形ごとに、返し方を変える。**箱は浮き、点は膨らみ、棒は少しだけ太る。**
     全部を同じ動きにすると、何を指しているかの手掛かりにならない */
  .figure svg rect.a-rise:hover, .figure svg rect.a-fade:hover { transform: translateY(-2px); }
  .figure svg rect.a-grow:hover { transform: scaleY(1.12); }
  .figure svg circle.a-pop:hover, .figure svg circle.a-fade:hover,
  .figure svg ellipse.a-fade:hover { transform: scale(1.22); }
  .figure svg text.a-fade:hover { transform: scale(1.04); }
  /* すでに動いているもの（流れる矢印・呼吸する丸）は、明るさだけ返す。
     transform を足すと、走っている animation と取り合いになって跳ねる */
  .figure svg .a-flow:hover, .figure svg .a-pulse:hover,
  .figure svg .a-breathe:hover { transform: none; }
}
@media (prefers-reduced-motion: reduce) {
  .figanim .figure svg .a-flow, .figanim .figure svg .a-breathe,
  .figanim .figure svg .a-pulse, .figanim .hero-glyph svg .a-flow,
  .figanim .hero-glyph svg .a-breathe, .figanim .hero-glyph svg .a-pulse {
    opacity: 1; animation: none !important; stroke-dasharray: none !important;
  }
}
/* /OZ-FIGFLOW */
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
  /* **高さで測らない。** threshold は「要素の何割が見えたか」なので、
     要素が画面の何倍も高いと、永久に満たされない。実際、玄関の資料一覧が
     スマートフォンでだけ出てこなくなった */
  }, { threshold: 0, rootMargin: '0px 0px -18% 0px' });
  figs.forEach(function(f){ fo.observe(f); });
})();
</script>
"""


# **属性が続く書き方も拾う。**
# `<div class="figure" data-reveal>` のように class のあとに属性があると、
# 以前の `[^"]*">` では止まって一致しなかった。
# そのせいで、ちゃんと .figure で組んである古い資料が丸ごと外れていた
BLOCK = re.compile(
    r'(<div class="(?:figure|hero-glyph)[^"]*"[^>]*>[\s\S]*?)(<svg[\s\S]*?</svg>)')


def unmark(svg):
    """前の版で振った印を外す。規則が変わったら振り直せるように。
    a-pop は作図関数が意味を持って付けたものなので残す。
    それ以外は _animate が形から振り直すので、いったん全部外す"""
    svg = re.sub(r'\s?class="a-(?:fade|flow|breathe|pulse|rise|draw|grow)"\s?style="--d:[\d.]+s"', '', svg)
    svg = re.sub(r'\s?class="a-(?:flow|breathe|pulse)"', '', svg)
    svg = re.sub(r'class="a-fade ', 'class="', svg)
    svg = re.sub(r'style="--d:[\d.]+s;', 'style="', svg)
    return re.sub(r'\s?style="--d:[\d.]+s"', '', svg)


def patch(html):
    if MARK in html:
        return None
    # 旧版の印とCSSをいったん外してから、いまの規則で入れ直す
    html = re.sub(r'<!-- OZ-FIGANIM v[12] -->\n?', '', html)
    for old in ('/* OZ-FIGFLOW v1 */', '/* OZ-FIGFLOW v2 */'):
        i = html.find(old)
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
    # **分類フォルダは2桁。0 始まりとは限らない。**
    # 分類が10を超えた日に、ここが '0*_*' のままだと新しい分類が丸ごと外れる
    for d in sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in oz_root.BACKSTAGE_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
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
