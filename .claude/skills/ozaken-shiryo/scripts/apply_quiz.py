#!/usr/bin/env python3
"""資料の中に、隠しコマンドで開く確認テストを仕込む。──「秘密の確認テスト」

**裏資料（企業講演・法人研修・AX Table）だけの機能。**
表の解説資料は不特定多数が読むので、置かない。

講演の最後に「画面を3回たたいてください」と伝えると、
受講者は自分の端末で確認テストを開ける。研修の理解度が、
その場で本人に返る。**スマートフォンだけで完結する**ように作ってある。

**合言葉は置かない。** 開き方そのものが隠しコマンドなので、
その上にもう一枚パスワードを挟むと、会場での説明が長くなるだけになる。

開き方は3つ。どれもそのままテストが始まる。

  画面を3回たたく   スマートフォン向け。どこでもいい。指で3回
  test と打つ       キーボードのある端末向け。どこにも触れずに打つだけ
  URLに #test       あとからメールで案内するとき用

テストは全画面で出る。1問ずつ、選んだ瞬間に正誤と解説が返り、
最後に点数と「見直すならこのパート」が並ぶ。
点数はブラウザの中（localStorage）だけに残る。どこにも送らない。

書き方（本文フラグメント側）：

    <div class="quiz" data-title="確認テスト"
         data-sub="今日の90分が身についているか、5問で確かめます">
      <div class="qz-q" data-a="2" data-ref="パート1　AIの主語が変わった">
        <div class="qz-t">AIエージェントが、これまでのAIと違うのは？</div>
        <div class="qz-o">答えの精度が上がったこと</div>
        <div class="qz-o">主語がAIに変わり、手順をAIが自分で回すこと</div>
        <div class="qz-o">日本語が使えるようになったこと</div>
        <div class="qz-w">これまでは人が聞いて、AIが答えていました。</div>
      </div>
      <div class="qz-res" data-min="4">よく掴めています。</div>
    </div>

  data-a    正解の選択肢が何番目か（1から数える）
  data-ref  どのパートの話か。間違えたときに「見直す先」として出る
  qz-w      選んだあとに出る一言。なぜそうなのかを短く
  qz-res    点数ごとの講評。data-min 以上のときに出る（高いものが優先）
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
MARK = '<!-- OZ-QUIZ v1 -->'

# 色と書体はトークンから取る。正誤の2色だけ、図版で使っている
# TEAL / RED を画面の中の変数として置く
CSS = """
/* OZ-QUIZ v1 ── 隠しコマンドで開く確認テスト（裏資料限定） */
.quiz{display:none}
.qz{--qz-ok:#2f8f8a;--qz-ng:#ff5d6a;
  position:fixed;inset:0;z-index:9000;display:none;
  font-family:var(--font-ja-sans);color:#fff;
  background:linear-gradient(168deg,#1f3864 0%,#182a52 44%,#141d35 100%);
  overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.qz.on{display:block}
.qz-in{width:min(680px,100%);margin:0 auto;
  padding:0 1.15rem calc(2.4rem + env(safe-area-inset-bottom))}
/* 閉じるボタンは、スマートフォンで下まで進んでも指の届く所に居させる */
.qz-bar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:.7rem;
  padding:calc(1.1rem + env(safe-area-inset-top)) 0 .9rem;
  border-bottom:1px solid rgba(216,228,240,.2);
  /* 面の背景は要素に貼り付いていて動かないので、上端は常にこの色。
     半透明にすると問題文が透けて読みにくくなる（実際そうなった） */
  background:#1f3864}
.qz-tag{font-family:var(--font-en);font-size:.6rem;font-weight:700;letter-spacing:.16em;
  color:var(--navy-deep);background:var(--azure-pale);padding:4px 10px;border-radius:999px}
.qz-step{font-family:var(--font-en);font-size:.78rem;font-weight:600;
  letter-spacing:.08em;color:rgba(216,228,240,.75);margin-left:auto}
.qz-x{flex:none;width:2.5rem;height:2.5rem;margin:-.6rem -.5rem -.6rem .2rem;
  font-size:1.35rem;line-height:1;color:rgba(216,228,240,.8);
  background:transparent;border:0;cursor:pointer}
.qz-dots{display:flex;gap:.34rem;margin:.9rem 0 1.6rem}
.qz-dots i{flex:1;height:3px;border-radius:2px;background:rgba(216,228,240,.22)}
.qz-dots i.ok{background:var(--qz-ok)}
.qz-dots i.ng{background:var(--qz-ng)}
.qz-dots i.now{background:var(--azure-pale)}
.qz-ref{font-family:var(--font-en);font-size:.62rem;font-weight:700;letter-spacing:.14em;
  color:rgba(216,228,240,.6);display:block;margin-bottom:.5rem}
.qz-ask{font-family:var(--font-ja-serif);font-weight:600;
  font-size:clamp(1.12rem,4.6vw,1.42rem);line-height:1.75;margin-bottom:1.4rem}
.qz-opt{display:block;width:100%;text-align:left;
  font-family:var(--font-ja-sans);font-size:.95rem;line-height:1.7;color:#fff;
  background:rgba(255,255,255,.07);border:1px solid rgba(216,228,240,.24);
  border-radius:13px;padding:.92rem 1rem .92rem 3rem;margin-bottom:.62rem;
  position:relative;cursor:pointer;-webkit-tap-highlight-color:transparent;
  transition:background .18s ease,border-color .18s ease}
.qz-opt:hover{background:rgba(255,255,255,.13)}
.qz-opt::before{content:attr(data-n);position:absolute;left:.9rem;top:50%;
  transform:translateY(-50%);width:1.55rem;height:1.55rem;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-family:var(--font-en);font-size:.72rem;font-weight:700;
  background:rgba(216,228,240,.18);color:rgba(216,228,240,.9)}
.qz-opt.ok{border-color:var(--qz-ok);background:rgba(47,143,138,.24)}
.qz-opt.ok::before{content:'✓';background:var(--qz-ok);color:#fff}
.qz-opt.ng{border-color:var(--qz-ng);background:rgba(255,93,106,.18)}
.qz-opt.ng::before{content:'×';background:var(--qz-ng);color:#fff}
.qz-opt.dim{opacity:.45}
.qz-done .qz-opt{cursor:default}
.qz-why{margin-top:1rem;padding:1rem 1.1rem;border-radius:13px;
  background:rgba(20,29,53,.4);border:1px solid rgba(216,228,240,.18)}
.qz-why b{display:block;font-family:var(--font-ja-serif);font-size:.95rem;
  font-weight:600;margin-bottom:.35rem}
.qz-why b.ok{color:var(--qz-ok)}
.qz-why b.ng{color:var(--qz-ng)}
.qz-why p{font-size:.86rem;line-height:1.85;color:rgba(216,228,240,.88)}
.qz-go{display:block;width:100%;margin-top:1.3rem;
  font-family:var(--font-ja-sans);font-size:.92rem;font-weight:700;
  color:var(--navy-deep);background:var(--azure-pale);
  border:0;border-radius:999px;padding:.95em 1.4em;cursor:pointer;
  -webkit-tap-highlight-color:transparent}
.qz-go.ghost{color:rgba(216,228,240,.85);background:transparent;
  border:1px solid rgba(216,228,240,.35);margin-top:.6rem}
.qz-score{font-family:var(--font-en);font-weight:700;line-height:1;
  font-size:clamp(3.4rem,15vw,4.6rem);letter-spacing:-.02em}
.qz-score span{font-size:.34em;font-weight:600;color:rgba(216,228,240,.6);margin-left:.3rem}
.qz-verdict{font-family:var(--font-ja-serif);font-weight:600;
  font-size:clamp(1.1rem,4.4vw,1.35rem);line-height:1.75;margin:.9rem 0 .3rem}
.qz-note{font-size:.85rem;line-height:1.9;color:rgba(216,228,240,.72)}
.qz-back{margin:1.5rem 0 .4rem;padding-top:1.2rem;
  border-top:1px solid rgba(216,228,240,.2)}
.qz-back h4{font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.16em;color:rgba(216,228,240,.6);margin-bottom:.7rem}
.qz-back li{list-style:none;font-size:.86rem;line-height:1.8;
  padding:.55rem .9rem;margin-bottom:.4rem;border-radius:10px;
  background:rgba(255,255,255,.06);border-left:3px solid var(--qz-ng)}
.qz-back li em{display:block;font-style:normal;font-family:var(--font-en);
  font-size:.6rem;font-weight:700;letter-spacing:.12em;
  color:rgba(216,228,240,.6);margin-bottom:.15rem}
/* 会場で投影することもあるので、広い画面では一回り大きく出す */
@media (min-width:900px){
  .qz-in{width:min(820px,100%)}
  .qz-ask{font-size:1.62rem}
  .qz-opt{font-size:1.05rem;padding:1.05rem 1.1rem 1.05rem 3.2rem}
  .qz-why p{font-size:.94rem}
}
body.qz-lock{overflow:hidden}
@media print{.qz{display:none !important}}
/* /OZ-QUIZ */
"""

JS = """
<script>
/* 確認テスト：隠しコマンドで開く。点数はこの端末の中（localStorage）だけに残る */
(function(){
  var src = document.querySelector('.quiz');
  if (!src) return;

  var KEY = 'ozquiz:' + location.pathname;

  var QS = [].slice.call(src.querySelectorAll('.qz-q')).map(function(q){
    return {
      ask: (q.querySelector('.qz-t') || {}).textContent || '',
      opts: [].slice.call(q.querySelectorAll('.qz-o')).map(function(o){ return o.textContent; }),
      ans: (parseInt(q.getAttribute('data-a'), 10) || 1) - 1,
      why: (q.querySelector('.qz-w') || {}).textContent || '',
      ref: q.getAttribute('data-ref') || ''
    };
  });
  var RULES = [].slice.call(src.querySelectorAll('.qz-res')).map(function(r){
    return { min: parseInt(r.getAttribute('data-min'), 10) || 0, text: r.textContent };
  }).sort(function(a, b){ return b.min - a.min; });
  if (!QS.length) return;

  function el(tag, cls, txt){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function best(){
    try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch(e){ return null; }
  }

  /* ── 全画面のテスト ─────────────────────────────────── */
  var qz = el('div', 'qz');
  qz.innerHTML = '<div class="qz-in"></div>';
  var pane = qz.firstChild;
  document.body.appendChild(qz);

  var at = 0, marks = [];

  function open(){
    at = 0; marks = [];
    qz.classList.add('on');
    document.body.classList.add('qz-lock');
    draw();
  }
  function close(){
    qz.classList.remove('on');
    document.body.classList.remove('qz-lock');
  }

  function head(step){
    var bar = el('div', 'qz-bar');
    bar.appendChild(el('span', 'qz-tag', 'CHECK'));
    bar.appendChild(el('span', 'qz-step', step));
    var x = el('button', 'qz-x', '×');
    x.setAttribute('aria-label', '閉じる');
    x.addEventListener('click', close);
    bar.appendChild(x);
    pane.appendChild(bar);

    var dots = el('div', 'qz-dots');
    QS.forEach(function(_, i){
      var d = el('i');
      if (marks[i] === 1) d.className = 'ok';
      else if (marks[i] === 0) d.className = 'ng';
      else if (i === at) d.className = 'now';
      dots.appendChild(d);
    });
    pane.appendChild(dots);
  }

  function draw(){
    pane.innerHTML = '';
    qz.scrollTop = 0;
    if (at >= QS.length) return result();

    var q = QS[at];
    head((at + 1) + ' / ' + QS.length);
    if (q.ref) pane.appendChild(el('span', 'qz-ref', q.ref));
    pane.appendChild(el('h3', 'qz-ask', q.ask));

    var btns = [];
    q.opts.forEach(function(t, i){
      var b = el('button', 'qz-opt', t);
      b.setAttribute('data-n', i + 1);
      b.addEventListener('click', function(){ pick(i, btns, q); });
      pane.appendChild(b);
      btns.push(b);
    });
  }

  function pick(i, btns, q){
    if (pane.classList.contains('qz-done')) return;
    pane.classList.add('qz-done');
    var hit = (i === q.ans);
    marks[at] = hit ? 1 : 0;

    btns.forEach(function(b, k){
      if (k === q.ans) b.classList.add('ok');
      else if (k === i) b.classList.add('ng');
      else b.classList.add('dim');
    });
    // 進捗の点にも即座に反映させる
    var dots = pane.querySelectorAll('.qz-dots i');
    if (dots[at]) dots[at].className = hit ? 'ok' : 'ng';

    var why = el('div', 'qz-why');
    var h = el('b', hit ? 'ok' : 'ng', hit ? '正解' : 'おしい');
    why.appendChild(h);
    if (q.why) why.appendChild(el('p', null, q.why));
    pane.appendChild(why);

    var go = el('button', 'qz-go', at + 1 >= QS.length ? '結果を見る' : '次の問題へ');
    go.addEventListener('click', function(){
      at++; pane.classList.remove('qz-done'); draw();
    });
    pane.appendChild(go);
    go.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  function result(){
    var got = marks.filter(function(m){ return m === 1; }).length;
    pane.classList.remove('qz-done');
    head('RESULT');

    var s = el('div', 'qz-score', String(got));
    s.appendChild(el('span', null, '/ ' + QS.length));
    pane.appendChild(s);

    var v = RULES.filter(function(r){ return got >= r.min; })[0];
    pane.appendChild(el('p', 'qz-verdict', v ? v.text : ''));

    var prev = best();
    if (prev && typeof prev.best === 'number'){
      pane.appendChild(el('p', 'qz-note',
        got > prev.best ? '前回は ' + prev.best + ' 問。伸びています'
                        : 'これまでの最高は ' + prev.best + ' 問'));
    }
    try {
      localStorage.setItem(KEY, JSON.stringify({
        best: Math.max(got, (prev && prev.best) || 0), last: got, n: QS.length }));
    } catch(e){}

    var miss = QS.filter(function(_, i){ return marks[i] === 0; });
    if (miss.length){
      var back = el('div', 'qz-back');
      back.appendChild(el('h4', null, 'REVIEW ── 見直したいところ（' + miss.length + '問）'));
      var ul = document.createElement('ul');
      miss.forEach(function(q){
        var li = document.createElement('li');
        if (q.ref) li.appendChild(el('em', null, q.ref));
        li.appendChild(document.createTextNode(q.ask));
        ul.appendChild(li);
      });
      back.appendChild(ul);
      pane.appendChild(back);
    }

    var again = el('button', 'qz-go', 'もう一度やる');
    again.addEventListener('click', open);
    pane.appendChild(again);
    var out = el('button', 'qz-go ghost', '資料に戻る');
    out.addEventListener('click', close);
    pane.appendChild(out);
  }

  /* ── 開け方は3つ ────────────────────────────────────── */
  // ① 画面を3回たたく（スマートフォン向け。どこでもいい）
  var taps = 0, last = 0;
  document.addEventListener('click', function(e){
    if (qz.classList.contains('on')) return;
    if (e.target.closest('a,button,input,textarea,select,label,.kit,.qrv')) return;
    var now = e.timeStamp || 0;
    taps = (now - last < 900) ? taps + 1 : 1;      // words を選ぶ操作と紛れない程度に短く
    last = now;
    if (taps >= 3){
      taps = 0;
      if (window.getSelection) { try { window.getSelection().removeAllRanges(); } catch(err){} }
      open();
    }
  });

  // ② test と打つ（キーボードのある端末向け）
  //    apply_keynav が st を投影画面のショートカットに使っているので、
  //    そのままだと打っている途中で index へ飛ぶ。keynav 側で
  //    「test / quiz を打ち終えたときは見送る」ようにして避けている
  var buf = '';
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape'){ close(); return; }
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.key.length !== 1) return;
    buf = (buf + e.key.toLowerCase()).slice(-8);
    if (/(test|quiz)$/.test(buf)){ buf = ''; open(); }
  });

  // ③ URLに #test を付けて開く（あとから案内するとき用）
  if (/^#(test|quiz)$/i.test(location.hash)) setTimeout(open, 400);
})();
</script>
"""


CSS_HEAD = CSS.split('\n')[1]          # 差し込んだCSSの先頭行
CSS_TAIL = '/* /OZ-QUIZ */'


def strip(html):
    """入れたぶんを外す。作り直したいときに、いったん綺麗にする"""
    i = html.find(CSS_HEAD)
    if i >= 0:
        j = html.find(CSS_TAIL, i)
        html = html[:i] + html[j + len(CSS_TAIL):] if j >= 0 else html
    i = html.find(MARK)
    if i >= 0:
        k = html.rfind('<script>', 0, i)
        html = html[:k] + html[i + len(MARK) + 1:] if k >= 0 else html
    return html


def patch(html):
    """テストの印が無いページには何もしない（表の資料は対象外）"""
    if MARK in html or 'class="quiz"' not in html:
        return None
    i = html.rfind('</style>')
    if i < 0:
        return None
    out = html[:i] + CSS + html[i:]
    j = out.rfind('</body>')
    if j < 0:
        return None
    return out[:j] + JS + '\n' + MARK + '\n' + out[j:]


def targets():
    for d in oz_root.BACKSTAGE_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f


def listing(pw):
    """どの資料に何問入っているか。仕込み忘れの確認に"""
    out = []
    for f in targets():
        inner = lockbox.decrypt(f, pw)
        n = len(re.findall(r'class="qz-q"', inner))
        if n:
            out.append((os.path.relpath(f, ROOT), n))
    return out


if __name__ == '__main__':
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        for rel, n in listing(pw):
            print('%-40s %d問' % (rel, n))
        sys.exit()

    fresh = len(sys.argv) > 1 and sys.argv[1] == 'refresh'
    done = skip = 0
    for f in targets():
        inner = lockbox.decrypt(f, pw)
        if fresh:
            inner = strip(inner)
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        lockbox.encrypt(f, pw, new)
        assert lockbox.decrypt(f, pw) == new
        done += 1
        print('  確認テストを入れた:', os.path.relpath(f, ROOT))
    print('%d ページ / 対象外 %d' % (done, skip))
