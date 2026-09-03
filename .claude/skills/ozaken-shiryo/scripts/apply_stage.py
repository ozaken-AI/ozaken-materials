#!/usr/bin/env python3
"""面の中身を、話す順番に出す。（全資料・再適用可）

**いちばんの狙いは、講演の「間」に合わせること。**
これまでは面に入った瞬間に、見出し・導入・図版・カードが同じ1フレームで出ていた。
壇上では、見出しを読み上げ、図を指し、カードを1枚ずつ話す。
その順番で出せば、聴いている側の目が話し手の順番についてくる。

  見出しの罫 → 見出し（左から拭き取る） → 副題 → 導入 → 図版
  → カード（1枚ずつ） → ひとこと（左から） → 関連資料

ほかに3つ。
  ・上端に、資料のどこまで来たかの細い帯と「03 / 11」の面番号。
    扉を抜けてから出る。聴講者が「いま何枚目か」を見失わないため
  ・図版の中の赤（要点）が、組み上がったあとに一度だけ静かに光る。
    赤の「かたまり」が3つ以上ある図（壁の連鎖・×の一覧）では光らせない。
    数えるのは要素ではなくかたまり。カードの赤い帯・番号・一言は3要素だが要点は1つ
  ・図版の中身が箱より先に出はじめないよう、組み上がりを箱の出現に合わせて少し遅らせる

**出る動きは transition ではなく animation、動かすのは transform ではなく translate。**
transition に遅延を付けると、その遅延が触れたときの浮き上がりにも掛かり、
カードが1秒遅れて持ち上がる（実際にそうなった）。animation なら触れた反応と分かれる。
ただし animation で transform を動かして both で止めると、その値が触れたときの
translateY(-3px) を永久に上書きして、浮き上がりが死ぬ。
translate プロパティなら transform と別々に効くので、両方が生きる。

**器（.inner）は透明にしない。** これまでは [data-reveal] の器を丸ごと
opacity:0 にしていた。器はそのまま、中身のそれぞれが順に出る形に変える。
図版の中身の組み上がりと、本文ブロック（blocks.py）の伸びる帯は、
これまでどおり .visible を合図に動くので触らない。

どれも prefers-reduced-motion では止まり、印刷では最初から出ている。

  OZAKEN_PW=マスター python3 apply_stage.py          # 全資料に当てる（冪等）
  OZAKEN_PW=マスター python3 reapply.py stage          # 当て直す
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
MARK = '/* OZ-STAGE v1 */'
MARK_END = '/* /OZ-STAGE */'
JS_HEAD = '/* OZ-STAGE: 面の中身を話す順番に出すための、動く部分。'

# 何番目の子が、何秒あとに出るか。sec() の並びは
#   eyebrow(1) → 見出し(2) → 副題(3) → 導入(4) → 図版(5) → カード(6) → ひとこと(7) → 関連資料(8)
# 副題や導入の無い面では、そのぶん図版が前に詰まる。種類ではなく順番で振るのは、
# 手で組んだ古い資料の並びが資料ごとに違っても、崩れずに順に出るようにするため
_BEATS = [0, .09, .18, .28, .38, .50, .64, .76]
_ITEM0, _ITEM = .50, .13            # 並んだ札（カードなど）の、1枚目の間と、1枚ごとの間

S = 'section:not(.hero) [data-reveal]'          # 扉は herofx が自前の演出を持つ


def _beats():
    out = []
    for i, d in enumerate(_BEATS):
        out.append('%s.visible>:nth-child(%d){animation-delay:%.2fs}' % (S, i + 1, d))
    out.append('%s.visible>:nth-child(n+%d){animation-delay:%.2fs}'
               % (S, len(_BEATS) + 1, _BEATS[-1] + .1))
    return '\n'.join(out)


def _items():
    """並んだ札は、器は出しておいて中身を1枚ずつ。下の帯（::before）も札のあとに満ちる"""
    out = []
    for grp, item in (('.cards', '.card'), ('.stats', '.stat'), ('.stepper', '.step'),
                      ('.two-col', '.two-col-item'), ('.vs', '*')):
        for k in range(1, 7):
            d = _ITEM0 + _ITEM * (k - 1)
            out.append('%s.visible %s>%s:nth-child(%d){animation-delay:%.2fs}'
                       % (S, grp, item, k, d))
            if item in ('.card', '.stat', '.step'):
                out.append('%s.visible %s>%s:nth-child(%d)::before{transition-delay:%.2fs}'
                           % (S, grp, item, k, d + .32))
        out.append('%s.visible %s>%s:nth-child(n+7){animation-delay:%.2fs}'
                   % (S, grp, item, _ITEM0 + _ITEM * 6))
    return '\n'.join(out)


# 図版の組み上がりを、箱が出るのと同じ間だけ遅らせる。
# figanim の8つの決まりを、同じ選択子で後ろから上書きする（--d に足すだけ）
_FIG_WAIT = '.42s'
_FIG = '\n'.join([
    '.figanim %s .figure.anim-on svg .a-fade{animation-delay:calc(var(--d,0s) + %s)}' % (S, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-pop{animation-delay:calc(var(--d,0s) + %s)}' % (S, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-grow{animation-delay:calc(var(--d,0s) + %s)}' % (S, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-rise{animation-delay:calc(var(--d,0s) + %s)}' % (S, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-flow{animation-delay:calc(var(--d,0s) + %s),calc(var(--d,0s) + %s)}' % (S, _FIG_WAIT, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-breathe{animation-delay:calc(var(--d,0s) + %s),calc(var(--d,0s) + .6s + %s)}' % (S, _FIG_WAIT, _FIG_WAIT),
    '.figanim %s .figure.anim-on svg .a-pulse{animation-delay:calc(var(--d,0s) + %s),calc(var(--d,0s) + .6s + %s)}' % (S, _FIG_WAIT, _FIG_WAIT),
    '.figanim %s .figure svg .a-draw{transition-delay:calc(var(--d,0s) + %s),calc(var(--d,0s) + .5s + %s)}' % (S, _FIG_WAIT, _FIG_WAIT),
])

CSS = MARK + """
/* ══ 面の中身を、話す順番に出す ══ */
/* 器は透明にしない。中身のそれぞれが、下から順に立ち上がる */
""" + S + """{opacity:1;transform:none;transition:none}
""" + S + """>*{opacity:0}
""" + S + """.visible>*{animation:ozStageUp .62s cubic-bezier(.16,1,.3,1) both}
""" + _beats() + """
/* 見出しは、扉の題と同じく左から拭き取る。「新しい話に入った」が一目で分かる */
""" + S + """.visible>.sec-title{animation:ozStageTitle .85s cubic-bezier(.2,.7,.2,1) both}
/* ひとこと（Ozaken's One Point）は横から。本文の流れとは別の声だと分かる */
""" + S + """.visible>.take{animation:ozStageSide .7s cubic-bezier(.16,1,.3,1) both}
/* 並んだ札は、器を先に出しておき、中身を1枚ずつ */
""" + S + """>.cards,""" + S + """>.stats,""" + S + """>.stepper,
""" + S + """>.two-col,""" + S + """>.vs{opacity:1;animation:none}
""" + S + """ .cards>.card,""" + S + """ .stats>.stat,""" + S + """ .stepper>.step,
""" + S + """ .two-col>.two-col-item,""" + S + """ .vs>*{opacity:0}
""" + S + """.visible .cards>.card,""" + S + """.visible .stats>.stat,
""" + S + """.visible .stepper>.step,""" + S + """.visible .two-col>.two-col-item,
""" + S + """.visible .vs>*{animation:ozStageUp .58s cubic-bezier(.16,1,.3,1) both}
""" + _items() + """
/* 図版の中身は、箱が出てから組み上がる */
""" + _FIG + """
@keyframes ozStageUp{from{opacity:0;translate:0 18px}to{opacity:1;translate:0 0}}
@keyframes ozStageSide{from{opacity:0;translate:-22px 0}to{opacity:1;translate:0 0}}
@keyframes ozStageTitle{
  from{opacity:0;translate:0 12px;clip-path:inset(-12% 108% -12% -6%)}
  to{opacity:1;translate:0 0;clip-path:inset(-12% -8% -12% -6%)}}

/* ── 上端の進み具合と、面番号。扉を抜けてから出る ── */
.oz-progress{position:fixed;top:0;left:0;right:0;z-index:70;height:3px;pointer-events:none;
  opacity:0;transition:opacity .5s ease}
.oz-progress.is-on{opacity:1}
.oz-progress i{position:absolute;left:0;top:0;height:3px;width:100%;
  transform-origin:0 50%;transform:scaleX(0);
  background:linear-gradient(90deg,var(--azure),#9fc6f5);
  box-shadow:0 0 10px rgba(159,198,245,.55)}
.oz-progress b{position:absolute;top:11px;right:16px;
  font-family:var(--font-en);font-weight:700;font-size:.66rem;letter-spacing:.18em;
  font-variant-numeric:tabular-nums;color:rgba(216,228,240,.9);
  background:rgba(20,29,53,.58);border:1px solid rgba(216,228,240,.22);border-radius:999px;
  padding:.34em .85em;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}
.oz-progress .oz-pg-s{margin:0 .35em;opacity:.45}
.oz-progress .oz-pg-n{display:inline-block}
.oz-progress .oz-pg-n.is-tick{animation:ozStageTick .45s cubic-bezier(.16,1,.3,1)}
@keyframes ozStageTick{from{translate:0 -7px;opacity:0}to{translate:0 0;opacity:1}}
@media(max-width:640px){.oz-progress b{top:8px;right:10px;font-size:.58rem;padding:.3em .7em}}

/* ── 図版の中の赤（要点）が、組み上がったあとに一度だけ光る ── */
.figure svg .oz-key-armed{transition:filter .9s ease}
.figure svg .oz-key{filter:drop-shadow(0 0 6px rgba(226,55,68,.9)) drop-shadow(0 0 16px rgba(226,55,68,.55)) brightness(1.18)}

@media (prefers-reduced-motion: reduce){
  """ + S + """>*,""" + S + """ .cards>.card,""" + S + """ .stats>.stat,
  """ + S + """ .stepper>.step,""" + S + """ .two-col>.two-col-item,""" + S + """ .vs>*{
    opacity:1;animation:none !important;translate:none;clip-path:none}
  .oz-progress i{transition:none}
  .oz-progress .oz-pg-n.is-tick{animation:none}
  .figure svg .oz-key{filter:none}}
@media print{
  """ + S + """>*,""" + S + """ .cards>.card,""" + S + """ .stats>.stat,
  """ + S + """ .stepper>.step,""" + S + """ .two-col>.two-col-item,""" + S + """ .vs>*{
    opacity:1 !important;animation:none !important;translate:none;clip-path:none}
  .oz-progress{display:none}}
""" + MARK_END + """
"""

JS = """
<script>
""" + JS_HEAD + """
   進み具合の帯・面番号・要点の光。どれも読み上げの邪魔をしない大きさで。 */
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var secs = [].slice.call(document.querySelectorAll('section.sec-light, section.sec-navy'));

  /* ── 上端の進み具合と面番号 ── */
  if (secs.length && !document.querySelector('.oz-progress')){
    var pad = function(n){ return (n < 10 ? '0' : '') + n; };
    var bar = document.createElement('div');
    bar.className = 'oz-progress'; bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = '<i></i><b><span class="oz-pg-n">01</span>'
      + '<span class="oz-pg-s">/</span><span class="oz-pg-t">' + pad(secs.length) + '</span></b>';
    document.body.appendChild(bar);
    var fill = bar.querySelector('i'), num = bar.querySelector('.oz-pg-n');
    var cur = -1, tick = false;
    function update(){
      tick = false;
      var h = document.documentElement, max = h.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      fill.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      /* いま画面の上から4割の線をまたいでいる面が、現在地 */
      var line = window.innerHeight * 0.4, best = -1;
      for (var i = 0; i < secs.length; i++){
        var r = secs[i].getBoundingClientRect();
        if (r.top <= line && r.bottom > line){ best = i; break; }
      }
      if (best < 0 || best === cur) return;
      cur = best;
      num.textContent = pad(best + 1);
      if (!reduce){ num.classList.remove('is-tick'); void num.offsetWidth; num.classList.add('is-tick'); }
    }
    window.addEventListener('scroll', function(){
      if (!tick){ tick = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
    /* 扉のあいだは出さない。扉には扉の演出がある */
    var hero = document.querySelector('.hero');
    if (hero && 'IntersectionObserver' in window){
      new IntersectionObserver(function(es){
        bar.classList.toggle('is-on', !es[0].isIntersecting);
      }, { threshold: 0.02 }).observe(hero);
    } else {
      bar.classList.add('is-on');
    }
  }

  /* ── 図版の中の赤（要点）が、組み上がったあとに一度だけ光る ──
     赤が3つ以上ある図（壁の連鎖・×の一覧）は光らせない。全部光ると要点でなくなる */
  if (reduce || !('IntersectionObserver' in window)) return;
  var RED = { '#e23744': 1, '#ff5d6a': 1 };
  var figs = [].slice.call(document.querySelectorAll('section:not(.hero) .figure'));
  if (!figs.length) return;
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var svg = e.target.querySelector('svg');
      if (!svg) return;
      var reds = [].slice.call(svg.querySelectorAll('[fill],[stroke]')).filter(function(el){
        return RED[(el.getAttribute('fill') || '').toLowerCase()]
            || RED[(el.getAttribute('stroke') || '').toLowerCase()];
      });
      if (!reds.length) return;
      /* 数えるのは要素ではなく「かたまり」。カードの赤い帯・番号・一言は3要素だが要点は1つ。
         近い箱同士（24単位以内）をつないで、かたまりが3つ以上なら光らせない */
      var boxes = reds.map(function(el){
        try { var r = el.getBBox(); return [r.x - 24, r.y - 24, r.x + r.width + 24, r.y + r.height + 24]; }
        catch (err){ return null; }
      });
      var grp = [], seen = [];
      for (var a = 0; a < boxes.length; a++){
        if (seen[a] || !boxes[a]) continue;
        var stack = [a]; seen[a] = 1; grp.push(1);
        while (stack.length){
          var i = stack.pop(), bi = boxes[i];
          for (var j = 0; j < boxes.length; j++){
            var bj = boxes[j];
            if (seen[j] || !bj) continue;
            if (bi[0] < bj[2] && bj[0] < bi[2] && bi[1] < bj[3] && bj[1] < bi[3]){ seen[j] = 1; stack.push(j); }
          }
        }
      }
      if (grp.length > 2) return;
      setTimeout(function(){
        reds.forEach(function(el){ el.classList.add('oz-key-armed'); el.classList.add('oz-key'); });
      }, 2000);
      setTimeout(function(){
        reds.forEach(function(el){ el.classList.remove('oz-key'); });
      }, 3900);
    });
  }, { threshold: 0, rootMargin: '0px 0px -18% 0px' });
  figs.forEach(function(f){ io.observe(f); });
})();
</script>
"""


def strip(html):
    i = html.find(MARK)
    if i >= 0:
        j = html.find(MARK_END, i)
        cut = j + len(MARK_END) if j >= 0 else html.find('</style>', i)
        if cut > 0:
            html = html[:i] + html[cut:]
    k = html.find(JS_HEAD)
    if k >= 0:
        s = html.rfind('<script>', 0, k)
        e = html.find('</script>', k)
        if s >= 0 and e >= 0:
            html = html[:s] + html[e + len('</script>'):]
    return html


def patch(html):
    if MARK in html:
        return None
    html = strip(html)
    i = html.rfind('</style>')
    if i < 0:
        return None
    html = html[:i] + CSS + html[i:]
    j = html.rfind('</body>')
    if j < 0:
        return None
    return html[:j] + JS + html[j:]


def targets():
    # **分類フォルダは2桁。0 始まりとは限らない。**
    for d in sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in oz_root.BACKSTAGE_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(f) not in ('index.html', 'ask.html'):   # 玄関は自前の演出を持つ
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
    print('話す順番に出す演出を適用 %d ページ / 適用済み %d' % (done, skip))
