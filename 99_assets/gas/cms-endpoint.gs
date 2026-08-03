/*** おざけん コンテンツ管理システム ── 受け口（Google Apps Script）*******
 *
 * 既存の「資料ダウンロード → leads シート記録 → 自動返信メール」はそのまま。
 * ask.html（質問箱）からの投稿だけを type で見分け、questions シートへ振り分ける。
 *
 * 【差し替え手順】
 *   1. スプレッドシート → 拡張機能 → Apps Script
 *   2. 既存のコードを全部消して、このファイルの中身を貼り付けて保存
 *   3. デプロイ → デプロイを管理 → 鉛筆アイコン → バージョン「新バージョン」→ デプロイ
 *      （新規デプロイにすると /exec のURLが変わり、既存ページから届かなくなる）
 *   4. 初回のみ、質問通知メールの権限確認が出たら承認する
 *
 * ページ側は mode:'no-cors' で投げるので戻り値は読まれない。
 ***************************************************************************/

/*** 設定 *********************************************************/
var SHEET_NAME  = 'leads';                              // 記録先シート名（既存に合わせる）
var ASK_SHEET   = 'questions';                          // 質問箱の記録先シート名
var SENDER_NAME = '小澤健祐（おざけん）｜AICX協会';        // 差出人の表示名
var REPLY_TO = 'kensuke.ozawa@aicx.jp';       // 返信先（受信者の返信がここに届く）
var SUBJECT     = '資料を手に取っていただき、ありがとうございます ─ 小澤健祐（おざけん）';
var NOTIFY_ASK  = true;                                 // 質問が届いたら REPLY_TO に知らせる
var SS_ID       = '';                                   // 通常は空でよい。スクリプトがシートに
                                                        // 紐づいていない場合だけ、シートのIDを入れる
var CODE_TAG    = '2026-08-03-ask';                     // 動いているコードの版。/exec を開くと出る
var LIST_MAX    = 30;                                   // 投影ページに返す質問の最大件数（新しい順）
var HIDE_COL    = 8;                                    // この列（H）に何か書くと、その質問は投影に出ない

/* 一覧を読むための合言葉。
   このファイルは公開リポジトリに置いてあるので、合言葉はコードに書かない。
   Apps Script の「プロジェクトの設定 → スクリプト プロパティ」で
   LIST_TOKEN という名前で登録する（下の setListToken_() を一度実行してもよい）。
   未設定のあいだは、安全側に倒して一覧を返さない。 */
function listToken_(){
  try { return PropertiesService.getScriptProperties().getProperty('LIST_TOKEN') || ''; }
  catch(e){ return ''; }
}

/* 合言葉を設定する。実行する前に、下の '' の中を書き換えること。
   ここに書いた文字はスクリプトに保存されるだけで、リポジトリには入らない。 */
function setListToken_(){
  var pw = '';                                          // ← ここに合言葉を入れて一度だけ実行
  if (!pw) { Logger.log('合言葉が空です。pw に文字を入れてから実行してください。'); return; }
  PropertiesService.getScriptProperties().setProperty('LIST_TOKEN', pw);
  Logger.log('合言葉を設定しました。');
}

/*** メイン：フォーム受信 → シート記録 → 自動返信メール *********/
function doPost(e){
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch(_){}

  // 質問箱（ask.html）からの投稿は、こちらで処理して終わり
  if (d.type === 'question') return handleQuestion_(d);

  var name    = (d.name||'')+'';
  var company = (d.company||'')+'';
  var email   = (d.email||'')+'';
  var asset   = (d.asset||'')+'';

  // 1) スプレッドシートに記録
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) sh.appendRow(['日時','お名前','会社名','メール','資料','UA']);
    sh.appendRow([new Date(), name, company, email, asset, (d.ua||'')]);
  } catch(_){}

  // 2) ダウンロードした人へ自動返信
  try {
    if (/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      MailApp.sendEmail({
        to: email,
        name: SENDER_NAME,
        replyTo: REPLY_TO,
        subject: SUBJECT,
        htmlBody: buildHtml_(name),
        body: buildText_(name)     // テキスト版フォールバック
      });
    }
  } catch(_){}

  return ok_();
}

/* ?list=1 … 投影ページ用に、新しい順で質問を返す
   それ以外 … 動作確認用。いま動いているコードの版とシート一覧が出る。
   ここに questions が出ていなければ、まだ新しいコードがデプロイされていない。 */
function doGet(e){
  var p = (e && e.parameter) || {};
  if (p.list) return listQuestions_(p.token, p.callback);

  var info = { ok:true, code:CODE_TAG, sheets:[] };
  try {
    book_().getSheets().forEach(function(s){ info.sheets.push(s.getName()); });
  } catch(err){ info.ok = false; info.error = String(err); }
  return reply_(info, p.callback);
}

/* 投影ページへ渡す質問一覧。
   H列（HIDE_COL）に何か書き込むと、その行は返さない。
   登壇中に出したくないものが来たら、シート上でそこに × を打てばすぐ消える。 */
function listQuestions_(token, callback){
  /* 投影ページは会場に映すもので、質問は聴講者にも見える前提。
     そのため既定では合言葉なしで返す。
     限定したくなったときだけ、スクリプト プロパティに LIST_TOKEN を登録すれば
     一致したリクエストにしか返さなくなる。 */
  var want = listToken_();
  if (want && String(token || '') !== want) {
    return reply_({ ok:false, auth:false, code:CODE_TAG }, callback);
  }

  var out = { ok:true, code:CODE_TAG, total:0, items:[] };
  try {
    var sh = book_().getSheetByName(ASK_SHEET);
    if (sh) {
      var last = sh.getLastRow();
      out.total = Math.max(0, last - 1);                 // 見出し行を除く
      var n = Math.min(LIST_MAX, out.total);
      if (n > 0) {
        var rows = sh.getRange(last - n + 1, 1, n, HIDE_COL).getValues();
        for (var i = rows.length - 1; i >= 0; i--) {     // 新しい順に積む
          var r = rows[i];
          if (String(r[HIDE_COL - 1] || '').trim()) continue;
          var q = String(r[2] || '').trim();
          if (!q) continue;
          out.items.push({
            t: r[0] ? new Date(r[0]).getTime() : 0,
            n: clip_(r[1], 40),
            q: clip_(q, 400)
          });
        }
      }
    }
  } catch(err){ out.ok = false; out.error = String(err); }
  return reply_(out, callback);
}

/* callback が付いていれば JSONP で返す。
   Apps Script は script.googleusercontent.com へ転送されるため、
   ブラウザによっては通常の fetch が CORS で弾かれる。script タグ経由なら確実に届く。 */
function reply_(obj, callback){
  var body = JSON.stringify(obj);
  if (callback && /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(callback)) {
    return ContentService.createTextOutput(callback + '(' + body + ');')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(body)
    .setMimeType(ContentService.MimeType.JSON);
}

/*** 質問箱 *******************************************************/
/* ask.html は「お名前（任意）」と「質問」だけを送ってくる。
   ?s=… が付いたURLから開かれた場合は、どの登壇からの質問かも一緒に届く。 */
function handleQuestion_(d){
  var name     = (d.name||'')+'';
  var question = (d.question||'')+'';
  var where    = (d.where||'')+'';

  if (!question.replace(/\s/g,'')) return ok_();   // 空の投稿は捨てる

  /* ここは握りつぶさない。失敗したら実行ログに残し、応答にも理由を載せる。
     黙って何も起きないと、原因が追えなくなるため */
  try {
    var ss = book_();
    var sh = ss.getSheetByName(ASK_SHEET);
    if (!sh) {
      sh = ss.insertSheet(ASK_SHEET);
      sh.appendRow(['日時','お名前','質問','聞いた場','ページ','参照元','UA','非表示']);
      sh.getRange(1,1,1,8).setFontWeight('bold');
      sh.setFrozenRows(1);
      sh.setColumnWidth(3, 520);
      sh.getRange('C:C').setWrap(true);
    }
    sh.appendRow([new Date(), clip_(name,100), clip_(question,2000), clip_(where,200),
                  clip_(d.page,300), clip_(d.ref,300), clip_(d.ua,300)]);
    SpreadsheetApp.flush();
  } catch(err){
    Logger.log('質問の記録に失敗: ' + err);
    return ContentService.createTextOutput(JSON.stringify({ ok:false, error:String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // 届いたことに気づけるよう、自分宛に知らせる
  try {
    if (NOTIFY_ASK) {
      MailApp.sendEmail({
        to: REPLY_TO,
        name: SENDER_NAME,
        subject: '【質問箱】' + (name ? name + ' さんから' : '匿名で') + '質問が届きました',
        body: (name ? 'お名前：' + name + '\n' : 'お名前：（未記入）\n')
            + (where ? '聞いた場：' + where + '\n' : '')
            + '\n' + question + '\n\n'
            + '── スプレッドシートの「' + ASK_SHEET + '」シートにも記録されています。'
      });
    }
  } catch(_){}

  return ok_();
}

function ok_(){
  return ContentService.createTextOutput(JSON.stringify({ ok:true }))
    .setMimeType(ContentService.MimeType.JSON);
}

/* 書き込み先のスプレッドシート。
   スタンドアロンのスクリプト（シートに紐づいていない）だと
   getActiveSpreadsheet() が null になるので、その場合は SS_ID を使う。 */
function book_(){
  if (SS_ID) return SpreadsheetApp.openById(SS_ID);
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) throw new Error('スプレッドシートに紐づいていません。SS_ID にシートのIDを設定してください。');
  return ss;
}

/* 長すぎる入力でシートが壊れないよう、頭から必要な分だけ取る */
function clip_(v, n){
  if (v === null || v === undefined) return '';
  var s = String(v);
  return s.length > n ? s.slice(0, n) : s;
}

/*** メール本文 ***************************************************/
function esc_(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function buildHtml_(name){
  var n = name ? esc_(name) : 'ご担当者';
  var P = [
    n + ' 様',
    'この度は資料を手に取っていただき、ありがとうございます。',
    '小澤健祐（おざけん）です。',
    '私は「人間とAIが共存する社会をつくる」ことをビジョンに、これまでに1,500本以上のAI関連記事を書き、年間300回以上の登壇を重ねてきました。',
    'そのすべての根っこにあるのは、「もっと多くの人にAIの可能性を知ってほしい」という、それだけの思いです。',
    '今回の資料も、売るためではなく、一人でも多くの方が最初の一歩を踏み出せるようにという意図でつくりました。',
    'もし一つでも現場で使えるものがあれば、これ以上嬉しいことはありません。',
    '多くの企業の現場を見てきて確信しているのは、AI活用が進むかどうかは技術力では決まらないということです。',
    '完璧な計画を待つよりも、80点で動かして現場で磨く。その思い切りがあるかどうかだけだと思っています。',
    '読んでいただいて「自社の場合はどうか」「ここが難しい」というところがあれば、本メールにそのままご返信ください。',
    '自動送信のメールですが、ご返信は私本人に届きます。',
    'なお、ご必要な場面があれば、下記のような形でもご一緒しています。'
  ].map(function(t){ return '<p style="margin:0 0 14px">'+t+'</p>'; }).join('');

  var LIST = '<ul style="margin:0 0 14px;padding-left:1.1em">'
    + '<li style="margin:4px 0">講演・研修（経営層向けから現場の実践型ワークショップまで）</li>'
    + '<li style="margin:4px 0">顧問・アドバイザー（AI戦略の伴走・継続的な意思決定支援）</li>'
    + '<li style="margin:4px 0">AX（AIトランスフォーメーション）支援（診断から人材育成、定着まで一気通貫）</li>'
    + '</ul>';

  var TAIL = '<p style="margin:0 0 14px">もちろん、まずは情報収集だけという段階でも全く問題ありません。<br>これをご縁に、どこかでお話できる日を楽しみにしています。</p>'
    + '<p style="margin:20px 0 0">おざけん</p>';

  return '<div style="font-family:Hiragino Sans,Meiryo,sans-serif;max-width:600px;margin:auto;color:#1a1a2e;line-height:1.9;font-size:15px">'
    + '<div style="height:4px;background:#1f3864;border-radius:4px;margin-bottom:22px"></div>'
    + P + LIST + TAIL
    + '</div>';
}

function buildText_(name){
  var n = name || 'ご担当者';
  return n + ' 様\n\n'
    + 'この度は資料を手に取っていただき、ありがとうございます。\n\n'
    + '小澤健祐（おざけん）です。\n\n'
    + '私は「人間とAIが共存する社会をつくる」ことをビジョンに、これまでに1,500本以上のAI関連記事を書き、年間300回以上の登壇を重ねてきました。\n\n'
    + 'そのすべての根っこにあるのは、「もっと多くの人にAIの可能性を知ってほしい」という、それだけの思いです。\n\n'
    + '今回の資料も、売るためではなく、一人でも多くの方が最初の一歩を踏み出せるようにという意図でつくりました。\n\n'
    + 'もし一つでも現場で使えるものがあれば、これ以上嬉しいことはありません。\n\n'
    + '多くの企業の現場を見てきて確信しているのは、AI活用が進むかどうかは技術力では決まらないということです。\n\n'
    + '完璧な計画を待つよりも、80点で動かして現場で磨く。その思い切りがあるかどうかだけだと思っています。\n\n'
    + '読んでいただいて「自社の場合はどうか」「ここが難しい」というところがあれば、本メールにそのままご返信ください。\n\n'
    + '自動送信のメールですが、ご返信は私本人に届きます。\n\n'
    + 'なお、ご必要な場面があれば、下記のような形でもご一緒しています。\n'
    + '・講演・研修（経営層向けから現場の実践型ワークショップまで）\n'
    + '・顧問・アドバイザー（AI戦略の伴走・継続的な意思決定支援）\n'
    + '・AX（AIトランスフォーメーション）支援（診断から人材育成、定着まで一気通貫）\n\n'
    + 'もちろん、まずは情報収集だけという段階でも全く問題ありません。\n'
    + 'これをご縁に、どこかでお話できる日を楽しみにしています。\n\n'
    + 'おざけん';
}

/*** テスト送信：自分宛に1通送って見た目を確認する ***************/
function testSend(){
  MailApp.sendEmail({
    to: REPLY_TO,               // 自分宛にテスト
    name: SENDER_NAME,
    replyTo: REPLY_TO,
    subject: '[テスト] ' + SUBJECT,
    htmlBody: buildHtml_('テスト 太郎'),
    body: buildText_('テスト 太郎')
  });
}

/*** 診断：どこで詰まっているかを実行ログに出す *******************/
function diag(){
  Logger.log('コードの版: ' + CODE_TAG);
  try {
    var ss = book_();
    Logger.log('シート名: ' + ss.getName());
    Logger.log('シートID: ' + ss.getId());
    var names = ss.getSheets().map(function(s){ return s.getName(); });
    Logger.log('タブ一覧: ' + names.join(' / '));
    Logger.log('questions タブ: ' + (names.indexOf(ASK_SHEET) >= 0 ? 'あり' : 'なし（未作成）'));
  } catch(err){
    Logger.log('スプレッドシートに到達できません: ' + err);
  }
  Logger.log('通知先: ' + REPLY_TO + ' / 残りメール送信数: ' + MailApp.getRemainingDailyQuota());
}

/*** テスト：質問箱の記録と通知を確認する *************************/
function testQuestion(){
  var res = handleQuestion_({
    type:'question', name:'テスト 太郎',
    question:'製造業です。まず現場の日報からAIに任せたいのですが、最初の一歩は何から着手すべきでしょうか。',
    where:'テスト実行', page:'(テスト)', ref:'', ua:'(テスト)'
  });
  Logger.log('結果: ' + res.getContent());
}
