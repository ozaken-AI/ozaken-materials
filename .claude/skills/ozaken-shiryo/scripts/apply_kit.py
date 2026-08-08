#!/usr/bin/env python3
"""資料の中に、その場で使える道具を埋め込む。──「持ち帰りキット」

**裏資料（AX_Table / Training / 個別に渡す資料）だけの機能。**
表の解説資料は不特定多数が読むので、置かない。
裏資料は渡す相手が決まっているので、その相手の業務に合わせた道具を仕込める。

投影して終わりではなく、**終わったあとにURLを渡すと使い続けられる**。
そこが紙のスライドやPDFとの違いになる。

いまのところ2種類。

  data-kit="prompt"  頼み方を組み立てて、コピーする
                     4つの欄を埋めると依頼文が組み上がる。
                     コピーして、そのまま社内のAIに貼れる。
                     名前を付けて保存すると、次に開いたときも残っている
                     （＝資料が言っている「点を線に」を、その場で体験させる）

  data-kit="check"   チェックして、点数と次の一手を出す
                     項目にチェックを入れると、いま何点で、
                     次に何から手を付けるべきかが出る

保存先はブラウザの中（localStorage）だけ。どこにも送らない。
資料は暗号化されて配られるので、開いた本人の端末に閉じる。

書き方（本文フラグメント側）:

    <div class="kit" data-kit="prompt" data-title="頼み方をつくる"
         data-note="入力はこの端末の中だけに残ります。どこにも送信されません">
      <div class="kit-f" data-label="① あなたは誰か"
           data-ph="法人向け保険の営業担当。中小企業を担当している"></div>
      ...
      <div class="kit-tpl">あなたは{1}です。&#10;相手は{2}です。</div>
    </div>

    <div class="kit" data-kit="check" data-title="自社診断">
      <div class="kit-i" data-w="2">対象部門の6割以上が、週に1回以上使っている</div>
      ...
      <div class="kit-r" data-min="8">仕組みになっています</div>
    </div>
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
MARK = '<!-- OZ-KIT v1 -->'

# 色と書体は必ずトークンから取る。直に書くと check() に弾かれる
CSS = """
/* OZ-KIT v1 ── 持ち帰りキット（裏資料限定） */
.kit{margin:2.4rem 0 0;padding:1.6rem 1.7rem 1.5rem;border-radius:16px;
  border:1px solid var(--azure-pale);background:rgba(46,84,150,.04)}
.sec-navy .kit{border-color:rgba(255,255,255,.18);background:rgba(255,255,255,.05)}
.kit-head{display:flex;align-items:center;gap:.6rem;margin-bottom:.3rem}
.kit-badge{font-family:var(--font-en);font-size:.6rem;font-weight:700;letter-spacing:.16em;
  color:var(--azure);background:var(--azure-pale);padding:3px 9px;border-radius:999px}
.sec-navy .kit-badge{color:var(--navy-deep);background:var(--azure-pale)}
.kit-ttl{font-family:var(--font-ja-serif);font-size:1.12rem;font-weight:600;color:var(--ink)}
.sec-navy .kit-ttl{color:#fff}
.kit-note{font-size:.76rem;line-height:1.8;color:var(--muted);margin:.2rem 0 1.1rem}
.sec-navy .kit-note{color:rgba(255,255,255,.6)}
.kit-row{margin-bottom:.9rem}
.kit-lb{display:block;font-size:.82rem;font-weight:700;color:var(--azure);margin-bottom:.3rem}
.sec-navy .kit-lb{color:var(--azure-pale)}
.kit input[type=text],.kit textarea{width:100%;box-sizing:border-box;
  font-family:var(--font-ja-sans);font-size:.92rem;line-height:1.7;color:var(--ink);
  background:#fff;border:1px solid var(--azure-pale);border-radius:9px;padding:.6rem .8rem}
.kit textarea{min-height:9.5rem;resize:vertical}
.kit input[type=text]:focus,.kit textarea:focus{outline:2px solid var(--azure);outline-offset:1px}
.kit-out{margin-top:1.1rem}
.kit-bar{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.7rem;align-items:center}
.kit-b{font-family:var(--font-ja-sans);font-size:.8rem;font-weight:700;cursor:pointer;
  color:var(--azure);background:transparent;border:1px solid var(--azure);
  border-radius:999px;padding:.42em 1.1em;transition:background .2s ease,color .2s ease}
.kit-b:hover{background:var(--azure);color:#fff}
.kit-b.on{background:var(--azure);color:#fff}
.sec-navy .kit-b{color:var(--azure-pale);border-color:var(--azure-pale)}
.sec-navy .kit-b:hover,.sec-navy .kit-b.on{background:var(--azure-pale);color:var(--navy-deep)}
.kit-msg{font-size:.78rem;color:var(--muted)}
.sec-navy .kit-msg{color:rgba(255,255,255,.6)}
.kit-saved{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.8rem}
.kit-chip{font-size:.76rem;cursor:pointer;color:var(--ink);background:#fff;
  border:1px solid var(--azure-pale);border-radius:999px;padding:.34em .9em}
.kit-chip:hover{border-color:var(--azure)}
.kit-chip b{color:var(--red);font-weight:700;margin-left:.5em}
.sec-navy .kit-chip{color:var(--ink)}
/* チェック式 */
.kit-ck{display:flex;gap:.7rem;align-items:flex-start;padding:.62rem .8rem;border-radius:10px;
  cursor:pointer;border:1px solid transparent}
.kit-ck:hover{background:rgba(46,84,150,.05)}
.sec-navy .kit-ck:hover{background:rgba(255,255,255,.05)}
.kit-ck input{margin-top:.28rem;width:1rem;height:1rem;accent-color:var(--azure);flex:none}
.kit-ck span{font-size:.9rem;line-height:1.75;color:var(--ink)}
.sec-navy .kit-ck span{color:rgba(255,255,255,.9)}
.kit-ck.done{background:rgba(46,84,150,.07)}
.sec-navy .kit-ck.done{background:rgba(255,255,255,.08)}
.kit-score{font-family:var(--font-en);font-weight:700;font-size:2rem;color:var(--azure);
  line-height:1;margin-right:.5rem}
.sec-navy .kit-score{color:var(--azure-pale)}
.kit-verdict{font-family:var(--font-ja-serif);font-size:1rem;font-weight:600;color:var(--ink)}
.sec-navy .kit-verdict{color:#fff}
.kit-next{font-size:.82rem;line-height:1.8;color:var(--muted);margin-top:.5rem}
.sec-navy .kit-next{color:rgba(255,255,255,.7)}
@media print{.kit-bar,.kit-saved{display:none}}
/* /OZ-KIT */
"""

JS = """
<script>
/* 持ち帰りキット：入力はこの端末の中（localStorage）だけに残る。どこにも送らない */
(function(){
  var kits = document.querySelectorAll('.kit');
  if (!kits.length) return;
  var KEY = 'ozkit:' + location.pathname;

  function store(){
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){ return {}; }
  }
  function save(o){
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch(e){}
  }
  function el(tag, cls, txt){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }

  kits.forEach(function(kit, ki){
    var type = kit.getAttribute('data-kit');
    var head = el('div', 'kit-head');
    head.appendChild(el('span', 'kit-badge', type === 'check' ? 'CHECK' : 'TOOL'));
    head.appendChild(el('span', 'kit-ttl', kit.getAttribute('data-title') || ''));
    kit.insertBefore(head, kit.firstChild);
    var note = kit.getAttribute('data-note');
    if (note){
      var n = el('p', 'kit-note', note);
      kit.insertBefore(n, head.nextSibling);
    }

    if (type === 'prompt') buildPrompt(kit, ki);
    else if (type === 'check') buildCheck(kit, ki);
  });

  /* ── 頼み方を組み立てて、コピーする ───────────────────── */
  function buildPrompt(kit, ki){
    var tplNode = kit.querySelector('.kit-tpl');
    var tpl = tplNode ? tplNode.textContent : '';
    if (tplNode) tplNode.remove();

    var fields = [].slice.call(kit.querySelectorAll('.kit-f'));
    var inputs = [];
    fields.forEach(function(f, i){
      var row = el('div', 'kit-row');
      row.appendChild(el('label', 'kit-lb', f.getAttribute('data-label') || ''));
      var inp = document.createElement('input');
      inp.type = 'text';
      inp.placeholder = f.getAttribute('data-ph') || '';
      row.appendChild(inp);
      f.replaceWith(row);
      inputs.push(inp);
    });

    var out = el('div', 'kit-out');
    out.appendChild(el('label', 'kit-lb', 'できあがった頼み方（そのままコピーして貼れます）'));
    var ta = document.createElement('textarea');
    ta.readOnly = true;
    out.appendChild(ta);
    kit.appendChild(out);

    var bar = el('div', 'kit-bar');
    var bCopy = el('button', 'kit-b', 'コピーする');
    var bSave = el('button', 'kit-b', '名前を付けて保存');
    var msg = el('span', 'kit-msg', '');
    bar.appendChild(bCopy); bar.appendChild(bSave); bar.appendChild(msg);
    kit.appendChild(bar);
    var saved = el('div', 'kit-saved');
    kit.appendChild(saved);

    function compose(){
      var s = tpl;
      inputs.forEach(function(inp, i){
        s = s.split('{' + (i + 1) + '}').join(inp.value || ('（' + (inp.placeholder || '未記入') + '）'));
      });
      ta.value = s;
    }
    inputs.forEach(function(i){ i.addEventListener('input', compose); });
    compose();

    bCopy.addEventListener('click', function(){
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch(e){}
      if (navigator.clipboard) { navigator.clipboard.writeText(ta.value); ok = true; }
      msg.textContent = ok ? 'コピーしました' : 'コピーできませんでした。手で選んでください';
      setTimeout(function(){ msg.textContent = ''; }, 2400);
    });

    function render(){
      var db = store(); var list = (db['p' + ki] || []);
      saved.innerHTML = '';
      list.forEach(function(item, idx){
        var chip = el('span', 'kit-chip', item.name);
        var x = el('b', null, '×');
        chip.appendChild(x);
        chip.addEventListener('click', function(ev){
          if (ev.target === x){
            var d = store(); d['p' + ki].splice(idx, 1); save(d); render(); return;
          }
          item.vals.forEach(function(v, i){ if (inputs[i]) inputs[i].value = v; });
          compose();
        });
        saved.appendChild(chip);
      });
      if (list.length) saved.appendChild(el('span', 'kit-msg', '押すと呼び出せます'));
    }

    bSave.addEventListener('click', function(){
      var name = prompt('この型に名前を付けてください（例：初回訪問の下調べ）');
      if (!name) return;
      var db = store();
      db['p' + ki] = db['p' + ki] || [];
      db['p' + ki].push({ name: name, vals: inputs.map(function(i){ return i.value; }) });
      save(db); render();
      msg.textContent = '保存しました。次に開いたときも残っています';
      setTimeout(function(){ msg.textContent = ''; }, 2800);
    });
    render();
  }

  /* ── チェックして、点数と次の一手を出す ─────────────── */
  function buildCheck(kit, ki){
    var items = [].slice.call(kit.querySelectorAll('.kit-i'));
    var rules = [].slice.call(kit.querySelectorAll('.kit-r')).map(function(r){
      return { min: parseInt(r.getAttribute('data-min'), 10) || 0, text: r.textContent };
    }).sort(function(a, b){ return b.min - a.min; });
    kit.querySelectorAll('.kit-r').forEach(function(r){ r.remove(); });

    var boxes = [], total = 0;
    items.forEach(function(it, i){
      var w = parseInt(it.getAttribute('data-w'), 10) || 1;
      total += w;
      var lab = el('label', 'kit-ck');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      lab.appendChild(cb);
      lab.appendChild(el('span', null, it.textContent));
      it.replaceWith(lab);
      boxes.push({ cb: cb, w: w, lab: lab, text: it.textContent });
    });

    var out = el('div', 'kit-out');
    var line = el('div', 'kit-bar');
    var score = el('span', 'kit-score', '0');
    var verdict = el('span', 'kit-verdict', '');
    line.appendChild(score); line.appendChild(verdict);
    out.appendChild(line);
    var next = el('p', 'kit-next', '');
    out.appendChild(next);
    kit.appendChild(out);

    function calc(){
      var got = 0, first = null;
      boxes.forEach(function(b){
        b.lab.classList.toggle('done', b.cb.checked);
        if (b.cb.checked) got += b.w;
        else if (!first) first = b.text;
      });
      score.textContent = got + ' / ' + total;
      var v = rules.filter(function(r){ return got >= r.min; })[0];
      verdict.textContent = v ? v.text : '';
      next.textContent = first ? '次に手を付けるなら ── ' + first : 'すべて満たしています';
      var db = store();
      db['c' + ki] = boxes.map(function(b){ return b.cb.checked ? 1 : 0; });
      save(db);
    }
    var db = store(), prev = db['c' + ki];
    if (prev) boxes.forEach(function(b, i){ b.cb.checked = !!prev[i]; });
    boxes.forEach(function(b){ b.cb.addEventListener('change', calc); });
    calc();
  }
})();
</script>
"""


def patch(html):
    """キットの印が無いページには何もしない（表の資料は対象外）"""
    if MARK in html or 'class="kit"' not in html:
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
    for d in ('AX_Table', 'Training'):
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f


if __name__ == '__main__':
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    done = skip = 0
    for f in targets():
        inner = lockbox.decrypt(f, pw)
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        lockbox.encrypt(f, pw, new)
        assert lockbox.decrypt(f, pw) == new
        done += 1
        print('  キットを入れた:', os.path.relpath(f, ROOT))
    print('%d ページ / 対象外 %d' % (done, skip))
