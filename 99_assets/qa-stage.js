/* 質問箱のQR投影に、届いた質問を流し込む。
   Apps Script は script.googleusercontent.com へ転送されるため、
   通常の fetch だとブラウザによって CORS で弾かれる。script タグ経由なら確実に届く。
   画面を出しているあいだだけ、一定間隔で読みにいく。 */
(function(){
  var LIST_URL = "https://script.google.com/macros/s/AKfycbwvf6VRQsjfiXulHOPAQ_Uren7ewTS3LTp9sp7XMf3H4yDsMhQIO1f41NPs1FfaTz1P/exec";
  var EVERY = 9000;                       /* 読みにいく間隔 */
  var box = document.getElementById('askqr');
  var list = document.getElementById('aqList');
  var feed = document.querySelector('#askqr .aq-feed');
  var count = document.getElementById('aqCount');
  var rangeBtn = document.getElementById('aqRange');
  if (!box || !list || !count || !feed) return;
  var seq = 0, timer = 0, seen = {}, first = true, latest = null;

  /* 前の講演の質問まで出てこないよう、直近の分だけを映す。
     見出しの表示を押すと範囲が切り替わる。

     **「今日」と「すべて」は外してある。** この画面は会場に投影される。
     同じ日に別の会社の登壇が入っていると、その会社の質問が
     そのままスクリーンに出てしまう。窓を数時間に閉じておけば、
     操作を間違えても他社の分は届かない。
     過去の分を読み返すのは、スプレッドシート側の仕事にする */
  var RANGES = [
    { label:'直近1時間', ms: 3600000 },
    { label:'直近2時間', ms: 2 * 3600000 },
    { label:'直近3時間', ms: 3 * 3600000 }
  ];
  var ri = 2;
  try { var save = parseInt(localStorage.getItem('ozaken_qa_range'), 10);
        if (!isNaN(save) && RANGES[save]) ri = save; } catch(e){}
  if (!RANGES[ri]) ri = RANGES.length - 1;      /* 外した範囲が保存されていたとき */

  function cutoff(){
    var r = RANGES[ri];
    if (!r.ms) return 0;
    if (r.ms === 'today'){ var d = new Date(); d.setHours(0,0,0,0); return d.getTime(); }
    return Date.now() - r.ms;
  }
  function inRange(items){
    var c = cutoff();
    if (!c) return items;
    var out = [];
    for (var i = 0; i < items.length; i++) if (!items[i].t || items[i].t >= c) out.push(items[i]);
    return out;
  }
  if (rangeBtn){
    rangeBtn.textContent = RANGES[ri].label;
    rangeBtn.addEventListener('click', function(ev){
      ev.stopPropagation();
      ri = (ri + 1) % RANGES.length;
      rangeBtn.textContent = RANGES[ri].label;
      try { localStorage.setItem('ozaken_qa_range', String(ri)); } catch(e){}
      seen = {}; first = true;
      if (latest) render(latest.items, latest.total); else pull();
    });
  }

  /* 一覧が出せないときは、黙って空にせず理由を出す */
  function notice(text){
    list.innerHTML = '<li class="aq-empty">' + esc(text) + '</li>';
    count.textContent = '0';
    first = true; seen = {};
    updateOverflow();
  }

  /* まず Cookie を付けずに取りにいく。
     Googleに複数アカウントでログインしていると、Cookie付きのリクエストは
     所有者と違うアカウントで解決され「ファイルは存在しません」のHTMLが返る。
     credentials:'omit' なら匿名扱いになり、この経路を踏まない。
     CORSで弾かれる環境のために、失敗したら script タグ経由へ落とす。 */
  function load(cb){
    var url = LIST_URL + (LIST_URL.indexOf('?') < 0 ? '?' : '&') + 'list=1&_=' + Date.now();
    if (!window.fetch){ jsonp(LIST_URL, cb); return; }
    fetch(url, { method:'GET', mode:'cors', credentials:'omit',
                 redirect:'follow', cache:'no-store' })
      .then(function(r){
        if (!r.ok){ console.warn('[Q&A] fetch の応答が', r.status); return null; }
        return r.json();
      })
      .then(function(d){
        if (d && typeof d.ok !== 'undefined'){ cb(d); return; }
        console.warn('[Q&A] fetch の中身が読めないため script タグへ切り替えます');
        jsonp(LIST_URL, cb);
      })
      .catch(function(err){
        console.warn('[Q&A] fetch に失敗:', err && err.message ? err.message : err);
        jsonp(LIST_URL, cb);
      });
  }

  /* 遅れて届いた応答も捨てない。
     Apps Script は最初の呼び出しに数秒かかることがあり、
     待ちきれずに関数を消してしまうと、返ってきた中身を受け取れなくなる。 */
  function jsonp(url, cb){
    var name = 'ozAq' + (++seq);
    var el = document.createElement('script');
    var fired = false;
    function drop(){
      if (el.parentNode) el.parentNode.removeChild(el);
      setTimeout(function(){ try{ delete window[name]; }catch(e){ window[name] = undefined; } }, 60000);
    }
    window[name] = function(d){ fired = true; drop(); cb(d); };
    el.onerror = function(e){
      if (!fired){ fired = true; console.warn('[Q&A] script タグの読み込みに失敗しました', el.src); drop(); cb(null); }
    };
    el.src = url + (url.indexOf('?') < 0 ? '?' : '&') + 'list=1&callback=' + name
          + '&_=' + Date.now();
    document.head.appendChild(el);
    /* いったん「まだ返ってこない」とだけ伝える。関数は生かしておき、
       あとから届いたらその時点で表示する */
    setTimeout(function(){
      if (!fired){ console.warn('[Q&A] script タグの応答がまだ返っていません'); cb(null); }
    }, 8000);
  }

  function esc(t){ return String(t == null ? '' : t)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  function stamp(ms){
    if (!ms) return '';
    var d = new Date(ms), now = new Date();
    var hm = ('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2);
    /* 今日以外は日付も出す。日をまたいで残っている分と混ざらないように */
    var sameDay = d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth()
               && d.getDate() === now.getDate();
    return sameDay ? hm : ((d.getMonth()+1) + '/' + d.getDate() + ' ' + hm);
  }

  function render(all, total){
    latest = { items: all, total: total };
    var items = inRange(all);
    if (!items.length){
      list.innerHTML = '<li class="aq-empty">'
        + (all.length ? 'この範囲にはまだありません。' : '最初のひとことを待っています。')
        + '</li>';
      count.textContent = '0';
      first = false;
      updateOverflow();
      return;
    }
    var html = '', fresh = false;
    for (var i = 0; i < items.length; i++){
      var it = items[i];
      var key = it.t + '|' + it.q.slice(0, 24);
      var isNew = !first && !seen[key];
      if (isNew) fresh = true;
      seen[key] = 1;
      var who = (it.n ? '<span class="ja">' + esc(it.n) + '</span> ／ ' : '') + stamp(it.t);
      html += '<li' + (isNew ? ' class="is-new"' : '') + '>'
            + '<span class="who">' + who + '</span><p class="aq-message">' + esc(it.q) + '</p></li>';
    }
    /* Keep the visible message at the same offset when a new reply arrives.
       Unchanged polls do not replace nodes or interrupt selection and reading. */
    var oldTop = list.scrollTop, anchor = null, offset = 0;
    var oldItems = Array.prototype.slice.call(list.querySelectorAll('li'));
    for (var j = 0; j < oldItems.length; j++){
      if (oldItems[j].offsetTop + oldItems[j].offsetHeight > oldTop + list.offsetTop){
        anchor = oldItems[j].textContent;
        offset = oldItems[j].offsetTop - list.offsetTop - oldTop;
        break;
      }
    }
    if (list.innerHTML !== html){
      list.innerHTML = html;
      if (oldTop > 4 && anchor){
        var same = Array.prototype.find.call(list.querySelectorAll('li'), function(li){ return li.textContent === anchor; });
        list.scrollTop = same ? same.offsetTop - list.offsetTop - offset : oldTop;
      }
    }
    count.textContent = items.length;
    first = false;
    updateOverflow();
  }

  /* Text stays still during projection. Read the rest by wheel or keyboard. */
  function updateOverflow(){
    feed.classList.toggle('has-more', list.scrollHeight - list.clientHeight > 4);
  }
  feed.addEventListener('click', function(ev){ ev.stopPropagation(); });
  if (window.ResizeObserver) new ResizeObserver(updateOverflow).observe(list);
  else window.addEventListener('resize', updateOverflow);
  if (document.fonts) document.fonts.ready.then(updateOverflow);

  /* ── QRを押したら拡大する。会場の後ろの席からでも読めるように ──
     投影画面はクリックで全画面を切り替えるので、伝播は止めておく */
  (function(){
    var card = box.querySelector('.qr-card');
    var zoom = document.getElementById('aqZoom');
    var slot = document.getElementById('aqZoomQr');
    if (!card || !zoom || !slot) return;
    function open(){
      if (!slot.firstChild){
        var svg = card.querySelector('svg');
        if (svg) slot.appendChild(svg.cloneNode(true));
      }
      zoom.classList.add('on'); zoom.setAttribute('aria-hidden','false');
      zoom.focus({preventScroll:true});
    }
    function close(){
      var wasOpen = zoom.classList.contains('on');
      zoom.classList.remove('on'); zoom.setAttribute('aria-hidden','true');
      if (wasOpen && box.classList.contains('show')) card.focus({preventScroll:true});
    }
    card.setAttribute('title', 'クリックで拡大');
    card.addEventListener('click', function(ev){ ev.stopPropagation(); open(); });
    zoom.addEventListener('click', function(ev){ ev.stopPropagation(); close(); });
    window.ozQrZoomClose = close;
  })();

  var misses = 0, since = 0;
  function pull(){
    if (first){
      if (!since) since = Date.now();
      /* Apps Script は最初の呼び出しに時間がかかることがある。
         黙って待たせず、待っている理由が分かるようにしておく */
      notice(Date.now() - since > 6000 ? '受信中…（初回は少し時間がかかります）' : '受信中…');
    }
    load(function(d){
      if (d && d.ok && d.items){ misses = 0; since = 0; render(d.items, d.total); return; }
      if (d && d.auth === false){
        notice('受信ボックスがまだ公開設定になっていません。');
        return;
      }
      /* 応答が返らなかったとき。一覧がすでに出ているならそのまま残す。
         最初の一回で諦めず、続けて失敗したときだけ理由を出す */
      if (!d && first && ++misses >= 2){
        notice('受信ボックスに接続できません。通信環境をご確認ください。');
      }
    });
  }

  function start(){ if (timer || document.hidden) return; misses = 0; pull(); timer = setInterval(pull, EVERY); }
  function stop(){ clearInterval(timer); timer = 0; }

  /* 投影画面が開いているあいだだけ動かす */
  new MutationObserver(function(){
    document.addEventListener('visibilitychange', function(){
    if (!document.hidden && box.classList.contains('show')) start(); else stop();
  });
  if (box.classList.contains('show')) start();
    else { stop(); if (window.ozQrZoomClose) window.ozQrZoomClose(); }
  }).observe(box, { attributes:true, attributeFilter:['class'] });
  document.addEventListener('visibilitychange', function(){
    if (!document.hidden && box.classList.contains('show')) start(); else stop();
  });
  if (box.classList.contains('show')) start();
})();
