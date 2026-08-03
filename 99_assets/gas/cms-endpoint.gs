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

// 動作確認用（ブラウザで /exec を開くと OK が出る）
function doGet(){
  return ContentService.createTextOutput('ok');
}

/*** 質問箱 *******************************************************/
/* ask.html は「お名前（任意）」と「質問」だけを送ってくる。
   ?s=… が付いたURLから開かれた場合は、どの登壇からの質問かも一緒に届く。 */
function handleQuestion_(d){
  var name     = (d.name||'')+'';
  var question = (d.question||'')+'';
  var where    = (d.where||'')+'';

  if (!question.replace(/\s/g,'')) return ok_();   // 空の投稿は捨てる

  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(ASK_SHEET);
    if (!sh) {
      sh = ss.insertSheet(ASK_SHEET);
      sh.appendRow(['日時','お名前','質問','聞いた場','ページ','参照元','UA']);
      sh.getRange(1,1,1,7).setFontWeight('bold');
      sh.setFrozenRows(1);
      sh.setColumnWidth(3, 520);
      sh.getRange('C:C').setWrap(true);
    }
    sh.appendRow([new Date(), clip_(name,100), clip_(question,2000), clip_(where,200),
                  clip_(d.page,300), clip_(d.ref,300), clip_(d.ua,300)]);
  } catch(_){}

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

/*** テスト：質問箱の記録と通知を確認する *************************/
function testQuestion(){
  handleQuestion_({
    type:'question', name:'テスト 太郎',
    question:'製造業です。まず現場の日報からAIに任せたいのですが、最初の一歩は何から着手すべきでしょうか。',
    where:'テスト実行', page:'(テスト)', ref:'', ua:'(テスト)'
  });
}
