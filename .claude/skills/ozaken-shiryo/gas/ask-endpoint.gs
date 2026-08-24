/**
 * 質問箱の受信ボックス（Google Apps Script）── いいね対応ぶんの追加コード
 * ============================================================================
 *
 * このファイルは **リポジトリの外にある Apps Script に貼るためのもの**です。
 * リポジトリ側（ask.html／index.html／inbox.html）はもう対応済みで、
 * ここを貼って再デプロイすると、いいねが実際に数えられるようになります。
 *
 * 貼らないうちは、こう振る舞います（壊れません）。
 *   ・ask.html の「この会場の質問」は **出ません**（場を名乗らない応答は捨てるため）
 *   ・投影のQ&A画面と受信箱は、いままでどおり動きます（ハートが出ないだけ）
 *
 * ----------------------------------------------------------------------------
 * 入れかた
 *   1. スプレッドシートを開き、拡張機能 → Apps Script
 *   2. このファイルの中身を、既存のコードの **下に** 貼る
 *   3. CONFIG の SHEET_Q を、質問が入っているシート名に直す
 *   4. 既存の doGet / doPost の先頭に、下の「差し込む2行」を入れる
 *   5. デプロイ → デプロイを管理 → 鉛筆 → バージョン「新バージョン」→ デプロイ
 *      （**URLは変わりません。**新しいURLになったら、貼り替えが要ります）
 *
 * 差し込む2行 ── 既存の doGet(e) のいちばん上に：
 *
 *     var r = ozList_(e); if (r) return r;
 *
 * 既存の doPost(e) のいちばん上に：
 *
 *     var r = ozLike_(e); if (r) return r;
 *
 * どちらも「自分の担当ではない呼び出し」には null を返すので、
 * 既存の処理はそのまま素通りします。
 * ----------------------------------------------------------------------------
 *
 * 受け渡しの決めごと（クライアント側と揃えてあります）
 *
 *   GET  ?list=1                → { ok, scope:"", total, items:[{i,t,n,q,w,l}] }
 *   GET  ?list=1&s=york         → { ok, scope:"york", total, items:[...] }
 *   GET  ?list=1&callback=cb    → cb({...})   CORSで弾かれる端末のための逃げ道
 *   POST {type:"like", id, voter, op:"like"|"unlike", s}
 *
 *   **i（質問の見分け方）は、クライアントとまったく同じ式で作ること。**
 *   ずれると、押したいいねが別の質問に付きます。
 *   式： String(時刻ミリ秒) + "." + djb2ハッシュ(本文).toString(36)
 *
 *   **いいねは (i, voter) の組で1票。**同じ端末から何度押しても増えません。
 *   別の端末から押せば別の票になりますが、名乗りを求めない以上ここが限界です。
 */

var CONFIG = {
  SHEET_Q: 'フォームの回答 1',   // ← 質問が入っているシート名に直す
  SHEET_L: 'likes',              // いいねを貯めるシート。無ければ自動で作る
  MAX: 500                       // 一度に返す最大件数（新しいものから）
};

/* ── 列の見つけ方 ────────────────────────────────────────────
   列の並びは触らせないほうがいい（あとで足したときに壊れる）ので、
   1行目の見出しから拾う。見出しの表記ゆれは、候補を並べて吸収する */
var COLS = {
  t: ['タイムスタンプ', 'timestamp', 'time', '日時', 'ts'],
  n: ['name', 'お名前', '名前', 'なまえ'],
  q: ['question', '質問', '本文', 'コメント', 'text'],
  w: ['where', 's', '場', 'session', 'scope'],
  type: ['type', '種別']
};

function ozCol_(head, keys) {
  for (var i = 0; i < head.length; i++) {
    var h = String(head[i] || '').trim().toLowerCase();
    for (var j = 0; j < keys.length; j++) {
      if (h === String(keys[j]).toLowerCase()) return i;
    }
  }
  return -1;
}

/** クライアントと同じ式。**ここを変えたら、3つのHTMLの keyOf も同じに直すこと** */
function ozKey_(t, q) {
  var h = 5381, s = String(q == null ? '' : q);
  for (var i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) >>> 0;
  return String(t || 0) + '.' + h.toString(36);
}

function ozSheet_(name, header) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    if (header) sh.appendRow(header);
  }
  return sh;
}

function ozOut_(e, obj) {
  var body = JSON.stringify(obj);
  var cb = e && e.parameter && e.parameter.callback;
  if (cb && /^[A-Za-z_$][\w$]*$/.test(cb)) {
    return ContentService.createTextOutput(cb + '(' + body + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(body)
    .setMimeType(ContentService.MimeType.JSON);
}

/* ── いいねの集計 ───────────────────────────────────────── */
function ozLikeCounts_() {
  var sh = ozSheet_(CONFIG.SHEET_L, ['ts', 'id', 'voter', 'scope']);
  var last = sh.getLastRow();
  var out = {};
  if (last < 2) return out;
  var rows = sh.getRange(2, 1, last - 1, 3).getValues();
  var seen = {};
  for (var i = 0; i < rows.length; i++) {
    var id = String(rows[i][1] || ''), voter = String(rows[i][2] || '');
    if (!id || !voter) continue;
    var pair = id + ' ' + voter;
    if (seen[pair]) continue;          // 同じ人の重ね押しは1票に丸める
    seen[pair] = 1;
    out[id] = (out[id] || 0) + 1;
  }
  return out;
}

/* ── GET：一覧 ─────────────────────────────────────────── */
function ozList_(e) {
  if (!e || !e.parameter || !e.parameter.list) return null;   // 担当外
  var scope = String(e.parameter.s || '');
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_Q);
  if (!sh) return ozOut_(e, { ok: false, error: 'sheet not found', scope: scope });

  var last = sh.getLastRow();
  if (last < 2) return ozOut_(e, { ok: true, scope: scope, total: 0, items: [] });

  var width = sh.getLastColumn();
  var head = sh.getRange(1, 1, 1, width).getValues()[0];
  var ci = {
    t: ozCol_(head, COLS.t), n: ozCol_(head, COLS.n), q: ozCol_(head, COLS.q),
    w: ozCol_(head, COLS.w), type: ozCol_(head, COLS.type)
  };
  if (ci.q < 0) return ozOut_(e, { ok: false, error: 'question column not found', scope: scope });

  var rows = sh.getRange(2, 1, last - 1, width).getValues();
  var likes = ozLikeCounts_();
  var items = [];
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    if (ci.type >= 0 && String(r[ci.type] || '') && String(r[ci.type]) !== 'question') continue;
    var q = String(r[ci.q] || '').trim();
    if (!q) continue;
    var w = ci.w >= 0 ? String(r[ci.w] || '') : '';

    // **場のしぼりは、返す前に落とす。**
    // ここで落とさずクライアントに任せると、他社の分が相手の端末に届いてしまう
    if (scope && w !== scope) continue;

    var t = 0;
    if (ci.t >= 0 && r[ci.t]) { var d = new Date(r[ci.t]); if (!isNaN(d)) t = d.getTime(); }
    var id = ozKey_(t, q);
    items.push({
      i: id, t: t, q: q, w: w,
      n: ci.n >= 0 ? String(r[ci.n] || '') : '',
      l: likes[id] || 0
    });
  }
  items.sort(function (a, b) { return a.t - b.t; });          // 届いた順
  if (items.length > CONFIG.MAX) items = items.slice(-CONFIG.MAX);
  return ozOut_(e, { ok: true, scope: scope, total: items.length, items: items });
}

/* ── POST：いいね ──────────────────────────────────────── */
function ozLike_(e) {
  var raw = e && e.postData && e.postData.contents;
  if (!raw) return null;
  var body;
  try { body = JSON.parse(raw); } catch (err) { return null; }
  if (!body || body.type !== 'like') return null;              // 担当外

  var id = String(body.id || ''), voter = String(body.voter || '');
  var op = body.op === 'unlike' ? 'unlike' : 'like';
  if (!id || !voter) return ozOut_(e, { ok: false, error: 'id and voter are required' });

  // 同時に押されたときに、行が二重に入らないようにする
  var lock = LockService.getScriptLock();
  try { lock.waitLock(8000); } catch (err) { return ozOut_(e, { ok: false, error: 'busy' }); }
  try {
    var sh = ozSheet_(CONFIG.SHEET_L, ['ts', 'id', 'voter', 'scope']);
    var last = sh.getLastRow();
    var found = [];
    if (last >= 2) {
      var rows = sh.getRange(2, 1, last - 1, 3).getValues();
      for (var i = 0; i < rows.length; i++) {
        if (String(rows[i][1]) === id && String(rows[i][2]) === voter) found.push(i + 2);
      }
    }
    if (op === 'like') {
      // **1人1票。**すでに入っていれば、何もしない
      if (!found.length) sh.appendRow([new Date(), id, voter, String(body.s || '')]);
    } else {
      for (var k = found.length - 1; k >= 0; k--) sh.deleteRow(found[k]);
    }
    var n = ozLikeCounts_()[id] || 0;
    return ozOut_(e, { ok: true, id: id, n: n });
  } finally {
    lock.releaseLock();
  }
}
