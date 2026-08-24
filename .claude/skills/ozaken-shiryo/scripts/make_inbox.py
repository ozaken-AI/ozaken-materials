#!/usr/bin/env python3
"""受信箱（inbox.html）を組む。

**投影のQ&A画面（index.html の qa）と、この受信箱は別物。**
あちらは会場のスクリーンに映すので、直近数時間しか出さない。
同じ日に別の会社の登壇が入っていると、その会社の質問が
そのままスクリーンに出てしまうからだ。
こちらは登壇者しか開けないので、期間のしぼりを外して全部出す。

  OZAKEN_PW=マスター python3 make_inbox.py

**鍵はマスターだけ。共通鍵は付けない。**
共通パスワードは資料を配るための鍵で、これで受信箱が開くと、
資料を渡した相手に他社の質問まで見えてしまう。

**殻の meta は、台帳（passwords.html）に合わせて空にする。**
lockbox.create は既存ページを殻として流用するので、
何もしないと借りてきた資料の題と共有カードがそのまま残る。
人に渡すページではないので、題は中立な1行だけにして、
og: の一式は落とし、noindex を付ける。
apply_ogp.py の SKIP にも入れてあるので、あとから書き戻されることもない。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)
OUT = os.path.join(ROOT, 'inbox.html')
SHELL = os.path.join(ROOT, '03_tools/cowork.html')   # ロック画面の型として借りる
TITLE = '\U0001f512 資料アーカイブ ─ おざけん'


def neutralize(path):
    """殻に残っている、借りもとの題と共有カードを落とす"""
    h = io.open(path, encoding='utf-8').read()
    h = re.sub(r'<meta (?:property|name)="(?:og|twitter):[^>]*>\s*', '', h)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, h, count=1, flags=re.S)
    if 'name="robots"' not in h:
        h = h.replace('<title>', '<meta name="robots" content="noindex">\n<title>', 1)
    io.open(path, 'w', encoding='utf-8').write(h)


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    if os.path.exists(OUT):
        lockbox.encrypt(OUT, pw, PAGE)          # 鍵は作り直さない
        how = '更新'
    else:
        lockbox.create(SHELL, PAGE, OUT, [pw])
        how = '新規作成'
    neutralize(OUT)
    assert lockbox.decrypt(OUT, pw) == PAGE
    print('受信箱を%sしました（%d バイト）' % (how, os.path.getsize(OUT)))


PAGE = r"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>受信箱 ─ 質問とコメント | おざけん</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#131c33">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Shippori+Mincho+B1:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{--navy:#1f3864;--navy-deep:#131c33;--azure:#2e5496;--azure-pale:#d8e4f0;
  --red:#e23744;--red-bright:#ff5d6a;--amber:#f0b429;--white:#fff;
  --font-ja-sans:'Zen Kaku Gothic New',sans-serif;
  --font-ja-serif:'Shippori Mincho B1',serif;
  --font-en:'Hanken Grotesk',sans-serif}
*{box-sizing:border-box}
html{background:var(--navy-deep)}
body{margin:0;min-height:100vh;
  background:linear-gradient(172deg,#1f3864 0%,#131c33 100%);color:var(--azure-pale);
  font-family:var(--font-ja-sans);line-height:1.9;
  padding:clamp(1.3rem,5vw,3rem) clamp(1.1rem,5vw,2rem) calc(3rem + env(safe-area-inset-bottom));
  -webkit-text-size-adjust:100%}
.wrap{max-width:760px;margin:0 auto}
.eyebrow{display:flex;align-items:center;gap:.7em;font-family:var(--font-en);
  font-size:.6rem;font-weight:700;letter-spacing:.34em;color:var(--amber);margin-bottom:.9rem}
.eyebrow::before{content:"";width:24px;height:1px;background:currentColor;opacity:.7}
h1{font-family:var(--font-ja-sans);font-weight:800;line-height:1.34;
  font-size:clamp(1.5rem,6vw,2.1rem);color:#fff;margin:0 0 .5rem}
.lead{font-size:.86rem;color:rgba(216,228,240,.66);margin:0 0 1.6rem}
.lead b{color:rgba(216,228,240,.86)}

.nums{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;margin-bottom:1.4rem}
.num{border:1px solid rgba(159,198,245,.18);border-radius:10px;
  background:rgba(159,198,245,.06);padding:.7rem .5rem;text-align:center}
.num b{display:block;font-family:var(--font-en);font-size:1.5rem;font-weight:700;
  line-height:1;color:#fff}
.num i{display:block;font-style:normal;font-size:.62rem;letter-spacing:.04em;
  color:rgba(216,228,240,.55);margin-top:.35rem}

/* ── 操作の帯。上に貼りつけておく。件数が多いと、
      しぼり込みのために毎回いちばん上まで戻ることになる ── */
.bar{position:sticky;top:0;z-index:5;margin:0 0 1rem;padding:.7rem 0 .8rem;
  background:linear-gradient(180deg,var(--navy) 72%,rgba(31,56,100,0));
  display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.bar input[type=search]{flex:1 1 200px;min-width:0;font:inherit;font-size:.84rem;
  color:#fff;background:rgba(159,198,245,.09);border:1px solid rgba(159,198,245,.22);
  border-radius:9px;padding:.55rem .8rem;-webkit-appearance:none}
.bar input[type=search]::placeholder{color:rgba(216,228,240,.4)}
.bar input[type=search]:focus{outline:none;border-color:rgba(240,180,41,.55)}
.btn{flex:none;font:inherit;font-size:.72rem;font-weight:700;letter-spacing:.04em;
  color:rgba(216,228,240,.82);background:rgba(159,198,245,.09);
  border:1px solid rgba(159,198,245,.22);border-radius:9px;padding:.55rem .8rem;
  cursor:pointer;-webkit-tap-highlight-color:transparent}
.btn:hover{background:rgba(159,198,245,.16)}
.btn.on{background:rgba(240,180,41,.16);border-color:rgba(240,180,41,.45);color:var(--amber)}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:0 0 1.1rem}
.chip{font-family:var(--font-en);font-size:.64rem;font-weight:700;letter-spacing:.06em;
  color:rgba(216,228,240,.7);background:rgba(159,198,245,.08);
  border:1px solid rgba(159,198,245,.2);border-radius:99px;padding:.3rem .7rem;cursor:pointer}
.chip.on{background:rgba(240,180,41,.16);border-color:rgba(240,180,41,.45);color:var(--amber)}
.chip span{font-family:var(--font-ja-sans);font-weight:500}

.day{display:flex;align-items:center;gap:.7em;margin:1.5rem 0 .6rem;
  font-family:var(--font-en);font-size:.62rem;font-weight:700;letter-spacing:.2em;
  color:rgba(159,198,245,.6)}
.day::after{content:"";flex:1;height:1px;background:rgba(159,198,245,.16)}
.day em{font-style:normal;font-family:var(--font-ja-sans);letter-spacing:.02em;
  color:rgba(216,228,240,.45)}

ul.items{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.55rem}
ul.items li{border:1px solid rgba(159,198,245,.16);border-radius:12px;
  background:rgba(159,198,245,.055);padding:.85rem 1rem}
ul.items li.hit{border-color:rgba(240,180,41,.4)}
.meta{display:flex;flex-wrap:wrap;gap:.5em .8em;align-items:baseline;margin-bottom:.35rem}
.meta .tm{font-family:var(--font-en);font-size:.68rem;font-weight:700;letter-spacing:.08em;
  color:rgba(159,198,245,.75)}
.meta .nm{font-size:.74rem;font-weight:700;color:rgba(216,228,240,.85)}
.meta .wh{font-size:.66rem;color:rgba(216,228,240,.45);
  border:1px solid rgba(159,198,245,.2);border-radius:99px;padding:.05rem .55rem}
.q{font-size:.92rem;line-height:1.85;color:#fff;white-space:pre-wrap;word-break:break-word;margin:0}
mark{background:rgba(240,180,41,.28);color:#fff;border-radius:2px}

.state{border:1px dashed rgba(159,198,245,.24);border-radius:12px;padding:1.4rem 1rem;
  text-align:center;font-size:.8rem;color:rgba(216,228,240,.55)}
.note{margin-top:1.8rem;padding-top:1.2rem;border-top:1px solid rgba(159,198,245,.14);
  font-size:.74rem;line-height:1.9;color:rgba(216,228,240,.5)}
.note b{color:rgba(216,228,240,.78)}
.back{display:inline-flex;align-items:center;gap:.5em;margin-top:1.4rem;
  font-family:var(--font-en);font-size:.66rem;font-weight:700;letter-spacing:.18em;
  color:rgba(159,198,245,.7);text-decoration:none}
.stamp{font-family:var(--font-en);font-size:.58rem;letter-spacing:.2em;
  color:rgba(159,198,245,.35);margin-top:2rem}
@media(max-width:520px){.nums{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="wrap">
  <span class="eyebrow">OZAKEN CMS ／ INBOX ─ RESTRICTED</span>
  <h1>受信箱 ─ 質問とコメント</h1>
  <p class="lead">質問箱に届いたものを、<b>期間を切らずにすべて</b>並べます。
    投影のQ&amp;A画面（<b>qa</b>）は会場に映すので直近数時間しか出しませんが、
    こちらは登壇者用なので全部出します。<b>会場では開かないでください。</b></p>

  <div class="nums">
    <div class="num"><b id="nAll">–</b><i>すべて</i></div>
    <div class="num"><b id="nToday">–</b><i>今日</i></div>
    <div class="num"><b id="nHour">–</b><i>直近1時間</i></div>
    <div class="num"><b id="nShown">–</b><i>表示中</i></div>
  </div>

  <div class="bar">
    <input type="search" id="q" placeholder="本文・名前でしぼる" autocomplete="off" spellcheck="false">
    <button class="btn" id="order" type="button" title="並び順">新しい順</button>
    <button class="btn" id="reload" type="button">更新</button>
    <button class="btn" id="copy" type="button">コピー</button>
  </div>
  <div class="chips" id="chips"></div>

  <div id="state" class="state">受信中…（初回は少し時間がかかります）</div>
  <div id="body"></div>

  <p class="note">この画面は<b>マスターパスワードでしか開きません</b>。
    投影のQ&amp;A画面と同じ受信ボックスを読んでいますが、
    <b>期間のしぼりを外してある</b>のが違いです。
    参加者の質問箱（ask.html）には一覧そのものが無く、
    自分が送った分だけが端末に残ります。<br>
    <b>コピー</b>は、いま表示している分だけを日付つきの文章にして写します。
    議事メモや、あとから回答をまとめるときに。</p>

  <a class="back" href="index.html">← ARCHIVE TOP</a>
  <p class="stamp">OZAKEN ARCHIVE ／ INBOX</p>
</div>

<script>
/* ══ 受信箱 ─ 届いたものを、期間を切らずに全部読む ═══════════════════
   投影のQ&A画面（index.html の qa）と同じ受信ボックスを読むが、
   **あちらは会場に映すので直近数時間に閉じてある**。
   こちらは登壇者しか開けないので、しぼりを外して全部出す。

   Apps Script は script.googleusercontent.com へ転送されるため、
   ふつうの fetch はブラウザによって CORS で弾かれる。
   だから fetch を先に試し、だめなら script タグ経由へ落とす
   （投影画面と同じ二段構え。片方だけ直すと必ず食い違うので、作りは揃えてある）*/
(function(){
  var LIST_URL = "https://script.google.com/macros/s/AKfycbwvf6VRQsjfiXulHOPAQ_Uren7ewTS3LTp9sp7XMf3H4yDsMhQIO1f41NPs1FfaTz1P/exec";
  var EVERY = 30000;                 /* 読み直す間隔。投影より長くていい */
  var seq = 0, items = [], where = '', newest = true, timer = 0, misses = 0, first = true;
  var el = function(id){ return document.getElementById(id); };
  var stateEl = el('state'), bodyEl = el('body'), qEl = el('q'), chipsEl = el('chips');

  function esc(t){ return String(t == null ? '' : t)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  /* 送信側（ask.html）は where / page も一緒に送っているが、
     受信ボックスが何という名前で返してくるかは、こちらからは決められない。
     考えられる名前を順に見て、最初に見つかったものを使う */
  function place(it){
    var v = it.w || it.where || it.s || it.session || '';
    if (v) return String(v);
    var p = it.p || it.page || '';
    if (!p) return '';
    try { p = String(p).split('?')[0].split('#')[0];
          var seg = p.split('/').filter(Boolean);
          return seg.slice(-2).join('/') || p; } catch(e){ return String(p); }
  }

  function dayKey(ms){ var d = new Date(ms); d.setHours(0,0,0,0); return d.getTime(); }
  function dayLabel(ms){
    var d = new Date(ms), t = new Date(); t.setHours(0,0,0,0);
    var diff = Math.round((t.getTime() - dayKey(ms)) / 86400000);
    var w = ['日','月','火','水','木','金','土'][d.getDay()];
    var s = d.getFullYear() + '.' + ('0'+(d.getMonth()+1)).slice(-2) + '.'
          + ('0'+d.getDate()).slice(-2) + ' <em>(' + w + ')</em>';
    if (diff === 0) return s + ' <em>今日</em>';
    if (diff === 1) return s + ' <em>昨日</em>';
    return s;
  }
  function hm(ms){ var d = new Date(ms);
    return ('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2); }

  function match(it, word){
    if (!word) return true;
    var hay = ((it.q||'') + ' ' + (it.n||'') + ' ' + place(it)).toLowerCase();
    return hay.indexOf(word) >= 0;
  }
  function hi(text, word){
    var s = esc(text);
    if (!word) return s;
    try {
      var re = new RegExp(word.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'), 'gi');
      return s.replace(re, function(m){ return '<mark>' + m + '</mark>'; });
    } catch(e){ return s; }
  }

  function visible(){
    var word = qEl.value.trim().toLowerCase();
    var out = [];
    for (var i = 0; i < items.length; i++){
      var it = items[i];
      if (where && place(it) !== where) continue;
      if (!match(it, word)) continue;
      out.push(it);
    }
    out.sort(function(a, b){ return newest ? (b.t||0) - (a.t||0) : (a.t||0) - (b.t||0); });
    return out;
  }

  function chips(){
    var seen = {}, order = [];
    for (var i = 0; i < items.length; i++){
      var p = place(items[i]);
      if (!p) continue;
      if (!seen[p]){ seen[p] = 0; order.push(p); }
      seen[p]++;
    }
    if (!order.length){ chipsEl.innerHTML = ''; return; }
    var html = '<button class="chip' + (where ? '' : ' on') + '" data-w="">すべて '
             + items.length + '</button>';
    order.sort(function(a,b){ return seen[b] - seen[a]; });
    for (var k = 0; k < order.length; k++){
      html += '<button class="chip' + (where === order[k] ? ' on' : '') + '" data-w="'
            + esc(order[k]) + '"><span>' + esc(order[k]) + '</span> ' + seen[order[k]] + '</button>';
    }
    chipsEl.innerHTML = html;
  }

  function draw(){
    var list = visible(), word = qEl.value.trim().toLowerCase();
    el('nShown').textContent = list.length;
    if (!list.length){
      bodyEl.innerHTML = '';
      stateEl.style.display = '';
      stateEl.textContent = items.length ? 'この条件に合うものはありません。' : 'まだ届いていません。';
      return;
    }
    stateEl.style.display = 'none';
    var html = '', day = null;
    for (var i = 0; i < list.length; i++){
      var it = list[i], k = it.t ? dayKey(it.t) : 0;
      if (k !== day){
        if (day !== null) html += '</ul>';
        html += '<div class="day">' + (it.t ? dayLabel(it.t) : '日時なし') + '</div><ul class="items">';
        day = k;
      }
      var p = place(it);
      html += '<li' + (word ? ' class="hit"' : '') + '><div class="meta">'
            + '<span class="tm">' + (it.t ? hm(it.t) : '--:--') + '</span>'
            + (it.n ? '<span class="nm">' + hi(it.n, word) + '</span>' : '')
            + (p ? '<span class="wh">' + esc(p) + '</span>' : '')
            + '</div><p class="q">' + hi(it.q || '', word) + '</p></li>';
    }
    if (day !== null) html += '</ul>';
    bodyEl.innerHTML = html;
  }

  function counts(){
    var t0 = new Date(); t0.setHours(0,0,0,0);
    var today = 0, hour = 0, now = Date.now();
    for (var i = 0; i < items.length; i++){
      var t = items[i].t || 0;
      if (t >= t0.getTime()) today++;
      if (t >= now - 3600000) hour++;
    }
    el('nAll').textContent = items.length;
    el('nToday').textContent = today;
    el('nHour').textContent = hour;
  }

  /* ── 受け取り。fetch → だめなら script タグ ── */
  function load(cb){
    var url = LIST_URL + (LIST_URL.indexOf('?') < 0 ? '?' : '&') + 'list=1&_=' + Date.now();
    if (!window.fetch){ jsonp(cb); return; }
    fetch(url, { method:'GET', mode:'cors', credentials:'omit',
                 redirect:'follow', cache:'no-store' })
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){ if (d && typeof d.ok !== 'undefined'){ cb(d); return; } jsonp(cb); })
      .catch(function(){ jsonp(cb); });
  }
  function jsonp(cb){
    var name = 'ozIn' + (++seq), s = document.createElement('script'), fired = false;
    function drop(){ if (s.parentNode) s.parentNode.removeChild(s);
      setTimeout(function(){ try{ delete window[name]; }catch(e){ window[name] = undefined; } }, 60000); }
    window[name] = function(d){ fired = true; drop(); cb(d); };
    s.onerror = function(){ if (!fired){ fired = true; drop(); cb(null); } };
    s.src = LIST_URL + (LIST_URL.indexOf('?') < 0 ? '?' : '&')
          + 'list=1&callback=' + name + '&_=' + Date.now();
    document.head.appendChild(s);
    /* 遅れて届いた分も捨てない。関数は生かしたまま、いったん報告だけする */
    setTimeout(function(){ if (!fired) cb(null); }, 9000);
  }

  function pull(){
    if (first){ stateEl.style.display = ''; stateEl.textContent = '受信中…（初回は少し時間がかかります）'; }
    load(function(d){
      if (d && d.ok && d.items){
        misses = 0; first = false;
        items = d.items;
        counts(); chips(); draw();
        return;
      }
      if (d && d.auth === false){
        stateEl.style.display = ''; stateEl.textContent = '受信ボックスがまだ公開設定になっていません。';
        return;
      }
      if (!d && first && ++misses >= 2){
        stateEl.style.display = '';
        stateEl.textContent = '受信ボックスに接続できません。通信環境をご確認ください。';
      }
    });
  }

  /* ── 操作 ── */
  var wait = 0;
  qEl.addEventListener('input', function(){
    clearTimeout(wait); wait = setTimeout(draw, 120);
  });
  chipsEl.addEventListener('click', function(e){
    var b = e.target.closest ? e.target.closest('.chip') : null;
    if (!b) return;
    where = b.getAttribute('data-w') || '';
    chips(); draw();
  });
  el('order').addEventListener('click', function(){
    newest = !newest;
    this.textContent = newest ? '新しい順' : '古い順';
    draw();
  });
  el('reload').addEventListener('click', function(){
    this.classList.add('on');
    var b = this;
    pull();
    setTimeout(function(){ b.classList.remove('on'); }, 700);
  });
  el('copy').addEventListener('click', function(){
    var list = visible(), out = [];
    for (var i = 0; i < list.length; i++){
      var it = list[i], d = it.t ? new Date(it.t) : null;
      var head = (d ? (d.getFullYear() + '/' + (d.getMonth()+1) + '/' + d.getDate()
                       + ' ' + hm(it.t)) : '日時なし');
      if (it.n) head += '　' + it.n;
      var p = place(it); if (p) head += '　[' + p + ']';
      out.push(head + '\n' + (it.q || ''));
    }
    var text = out.join('\n\n');
    var btn = this;
    function done(ok){
      btn.textContent = ok ? ('写しました（' + list.length + '件）') : 'コピーできません';
      btn.classList.add('on');
      setTimeout(function(){ btn.textContent = 'コピー'; btn.classList.remove('on'); }, 1800);
    }
    if (navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(function(){ done(true); }, function(){ done(false); });
      return;
    }
    /* clipboard API が使えない端末のために、選択して実行する道も残す */
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    var ok = false; try { ok = document.execCommand('copy'); } catch(e){}
    document.body.removeChild(ta); done(ok);
  });

  /* 隠しているあいだは読みにいかない。壇上でうっかり開いたまま置いても、
     通信を出し続けないように */
  document.addEventListener('visibilitychange', function(){
    if (document.hidden){ clearInterval(timer); timer = 0; }
    else if (!timer){ pull(); timer = setInterval(pull, EVERY); }
  });

  pull();
  timer = setInterval(pull, EVERY);
})();
</script>
</body>
</html>

"""


if __name__ == '__main__':
    main()
