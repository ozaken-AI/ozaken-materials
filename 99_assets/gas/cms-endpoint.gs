/**
 * おざけん コンテンツ管理システム ── 受け口（Google Apps Script）
 *
 * このスクリプトを貼るスプレッドシートに、次の2枚のシートが自動で用意される。
 *   leads     … 資料ダウンロード時のリード（index.html のゲート）
 *   questions … 質問箱（ask.html）
 *
 * 【設置手順】
 *   1. 受け取り用のスプレッドシートを開く
 *   2. 拡張機能 → Apps Script を開き、このファイルの中身を貼り付けて保存
 *   3. デプロイ → 新しいデプロイ → 種類「ウェブアプリ」
 *        次のユーザーとして実行：自分
 *        アクセスできるユーザー：全員
 *   4. 発行された /exec の URL を、index.html と ask.html の ENDPOINT に設定する
 *
 * ページ側は mode:'no-cors' で投げているので、戻り値は読まれない。
 * それでも 200 を返しておくと、ブラウザの開発者ツールで確認しやすい。
 */

var SHEETS = {
  lead:     { name: 'leads',
              head: ['受信日時', 'お名前', '会社名', 'メール', '対象資料', 'ページ', 'UA'] },
  question: { name: 'questions',
              head: ['受信日時', 'お名前', '質問', '聞いた場（s）', 'ページ', '参照元', 'UA'] }
};

function doPost(e) {
  try {
    var raw = (e && e.postData && e.postData.contents) || '{}';
    var d = JSON.parse(raw);
    var kind = (d.type === 'question') ? 'question' : 'lead';
    var sh = sheetFor(kind);
    var now = new Date();

    if (kind === 'question') {
      sh.appendRow([
        now,
        clip(d.name, 100),
        clip(d.question, 2000),
        clip(d.where, 200),
        clip(d.page, 300),
        clip(d.ref, 300),
        clip(d.ua, 300)
      ]);
    } else {
      sh.appendRow([
        now,
        clip(d.name, 100),
        clip(d.company, 150),
        clip(d.email, 150),
        clip(d.asset, 300),
        clip(d.page, 300),
        clip(d.ua, 300)
      ]);
    }
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return json({ ok: true, service: 'ozaken-cms' });
}

/** 目的のシートを返す。無ければ見出し付きで作る */
function sheetFor(kind) {
  var conf = SHEETS[kind];
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(conf.name);
  if (!sh) {
    sh = ss.insertSheet(conf.name);
    sh.appendRow(conf.head);
    sh.getRange(1, 1, 1, conf.head.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

/** 長すぎる入力でシートが壊れないよう、頭から必要な分だけ取る */
function clip(v, n) {
  if (v === null || v === undefined) return '';
  var s = String(v);
  return s.length > n ? s.slice(0, n) : s;
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
