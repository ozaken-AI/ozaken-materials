// メルマガの自己点検。Cloudflareに上げる前に、手元で通す。
//
//   node newsletter/selftest.mjs
//
// D1 のかわりに node:sqlite を同じ形にかぶせて、実際の functions/ をそのまま動かす。
// Resend への fetch は差し替えるので、メールは1通も出ない。
//
// **配信停止まわりは、壊すと相手に迷惑がかかる場所。**
// 直したら必ずここを通す。

import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { sign, verify, unsubscribeUrl } from '../functions/_lib/token.js';
import { config, buildMessage } from '../functions/_lib/mail.js';
import { onRequestGet as unsubGet, onRequestPost as unsubPost } from '../functions/unsubscribe.js';
import { onRequestPost as subscribe } from '../functions/api/subscribe.js';
import { onRequestGet as confirm } from '../functions/api/confirm.js';
import { onRequestPost as send, onRequestGet as sendStat } from '../functions/api/send.js';
import { onRequestPost as hook } from '../functions/api/hooks/resend.js';
import { onRequestPost as importCsv } from '../functions/api/import.js';
import { COLUMNS, parseCsv, detectColumns, parseDate } from '../functions/_lib/meishi.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const SCHEMA = join(HERE, 'schema.sql');
const ISSUE = JSON.parse(readFileSync(join(HERE, 'issues/sample.json'), 'utf8'));

// ── 点検の道具 ───────────────────────────────────────
let pass = 0, fail = 0;
const ok = (label, cond, extra = '') => {
  if (cond) { pass++; console.log(`  ✅ ${label}`); }
  else { fail++; console.log(`  ❌ ${label}${extra ? '  → ' + extra : ''}`); }
};
const head = (t) => console.log(`\n${t}`);

// D1 のふりをする最小の実物
function makeDb() {
  const sq = new DatabaseSync(':memory:');
  sq.exec(readFileSync(SCHEMA, 'utf8'));
  const wrap = (sql, args = []) => ({
    bind: (...a) => wrap(sql, a),
    first: async () => sq.prepare(sql).get(...args) ?? null,
    all: async () => ({ results: sq.prepare(sql).all(...args) }),
    run: async () => ({ meta: { changes: Number(sq.prepare(sql).run(...args).changes) } }),
  });
  return { prepare: (sql) => wrap(sql), batch: async (s) => Promise.all(s.map(x => x.run())), raw: sq };
}

const WHSEC = Buffer.from('super-secret-webhook-key-32bytes').toString('base64');
const BASE = {
  NEWSLETTER_SECRET: 'a'.repeat(48),
  RESEND_API_KEY: 're_test',
  NEWSLETTER_FROM: 'おざけん <weekly@ozaken.ai>',
  NEWSLETTER_SENDER_ADDRESS: '東京都〇〇区〇〇 1-2-3',
  NEWSLETTER_REPLY_TO: 'weekly@ozaken.ai',
  NEWSLETTER_UNSUB_MAILTO: 'unsubscribe@ozaken.ai',
  NEWSLETTER_ADMIN_TOKEN: 'admintoken',
  RESEND_WEBHOOK_SECRET: 'whsec_' + WHSEC,
};
const fresh = () => { const db = makeDb(); return { db, env: { ...BASE, DB: db } }; };
const seed = (db, rows) => {
  const t = new Date().toISOString();
  for (const [e, st] of rows) {
    db.raw.exec(`INSERT INTO subscribers (email,status,source,consent_at,created_at,updated_at)
                 VALUES ('${e}','${st}','meishi','${t}','${t}','${t}')`);
  }
};
const statusOf = (db, e) => (db.raw.prepare('SELECT status FROM subscribers WHERE email=?').get(e) || {}).status;

// Resend への送信を、実際には出さずに記録だけする
let sent = [];
function stubResend({ httpStatus = 200 } = {}) {
  sent = [];
  globalThis.fetch = async (url, opts) => {
    const body = JSON.parse(opts.body);
    sent.push({ url, body });
    if (httpStatus !== 200) return new Response('{"message":"stub failure"}', { status: httpStatus });
    const n = Array.isArray(body) ? body.length : 1;
    return new Response(JSON.stringify({ data: Array.from({ length: n }, (_, i) => ({ id: 'id' + i })) }), { status: 200 });
  };
}

async function svixHeaders(payload, secretB64 = WHSEC, tsOffset = 0) {
  const id = 'msg_test';
  const ts = String(Math.floor(Date.now() / 1000) + tsOffset);
  const key = await crypto.subtle.importKey('raw', Buffer.from(secretB64, 'base64'),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = Buffer.from(await crypto.subtle.sign('HMAC', key,
    new TextEncoder().encode(`${id}.${ts}.${payload}`))).toString('base64');
  return { 'svix-id': id, 'svix-timestamp': ts, 'svix-signature': `v1,${sig}` };
}

const post = (url, body, headers = {}) => new Request(url, { method: 'POST', headers, body });
const adminPost = (body) => post('https://x/api/send', JSON.stringify(body),
  { Authorization: 'Bearer admintoken', 'Content-Type': 'application/json' });

// ── 1. 署名 ──────────────────────────────────────────
head('1. 配信停止リンクの署名');
{
  const cfg = config(BASE);
  ok('環境変数に不足がない', cfg.missing.length === 0, cfg.missing.join(','));
  const url = new URL(await unsubscribeUrl(cfg.site, cfg.secret, '  Test@Example.COM '));
  const e = url.searchParams.get('e'), s = url.searchParams.get('s');
  ok('アドレスを小文字・空白なしに正規化する', e === 'test@example.com', e);
  ok('正しい署名を通す', await verify(cfg.secret, 'unsub', e, s));
  ok('1文字変えた署名を弾く', !await verify(cfg.secret, 'unsub', e, s.slice(0, -1) + (s.slice(-1) === 'A' ? 'B' : 'A')));
  ok('他人のアドレスへの付け替えを弾く', !await verify(cfg.secret, 'unsub', 'evil@example.com', s));
  ok('用途違い（確認用の署名）を弾く', !await verify(cfg.secret, 'unsub', e, await sign(cfg.secret, 'confirm', e)));
  ok('鍵が違えば通らない', !await verify('b'.repeat(48), 'unsub', e, s));
}

// ── 2. メール本文 ────────────────────────────────────
head('2. メール本文');
{
  const cfg = config(BASE);
  const msg = await buildMessage({ issue: ISSUE, subscriber: { email: 'A@B.co', name: '田中 太郎', source: 'meishi' }, cfg });
  ok('宛先を正規化する', msg.to[0] === 'a@b.co', msg.to[0]);
  ok('List-Unsubscribe を付ける', /^<https:\/\/.+unsubscribe\?e=/.test(msg.headers['List-Unsubscribe']));
  ok('ワンクリック用のヘッダを付ける', msg.headers['List-Unsubscribe-Post'] === 'List-Unsubscribe=One-Click');
  ok('本文にも配信停止リンクがある', msg.html.includes('/unsubscribe?e=') && msg.text.includes('/unsubscribe?e='));
  ok('住所を載せている（表示義務）', msg.html.includes(BASE.NEWSLETTER_SENDER_ADDRESS));
  ok('問い合わせ先を載せている（表示義務）', msg.html.includes(BASE.NEWSLETTER_REPLY_TO));
  ok('名刺の相手には経緯を書く', msg.html.includes('名刺交換'));
  ok('文字だけの版も作る', msg.text.length > 200);
  ok('<style>を使わない（メールで落ちる）', !/<style/i.test(msg.html));

  const web = await buildMessage({ issue: ISSUE, subscriber: { email: 'x@y.co', name: '<img src=x onerror=alert(1)>', source: 'web' }, cfg });
  ok('名簿の名前に混ぜたタグを無害化する', !web.html.includes('<img src=x') && web.html.includes('&lt;img'));
  ok('Web申込者には名刺の文言を出さない', !web.html.includes('名刺交換'));

  // 心当たりのない人ほど、この一文しか読まない。経路ごとに正しく出し分かること。
  for (const [source, needle] of [
    ['download', '資料をダウンロードいただいた際に'],
    ['event', 'イベント・講演にご参加いただいた際に'],
  ]) {
    const m = await buildMessage({ issue: ISSUE, subscriber: { email: 'x@y.co', source }, cfg });
    ok(`${source} の相手にはその経緯を書く`, m.html.includes(needle) && m.text.includes(needle));
    ok(`${source} の相手に名刺の文言を出さない`, !m.html.includes('名刺交換'));
  }
}

// ── 3. 配信停止 ──────────────────────────────────────
head('3. 配信停止');
{
  const { db, env } = fresh();
  seed(db, [['test@example.com', 'active']]);
  const url = await unsubscribeUrl('https://content.ozaken.ai', env.NEWSLETTER_SECRET, 'test@example.com');

  let res = await unsubGet({ request: new Request(url), env });
  ok('GETでは止めない（リンク検査botが踏むため）', statusOf(db, 'test@example.com') === 'active');
  ok('GETは確認画面を返す', res.status === 200 && (await res.clone().text()).includes('配信を停止する'));
  ok('検索避けとキャッシュ禁止が付く',
    res.headers.get('Cache-Control') === 'no-store' && res.headers.get('X-Robots-Tag') === 'noindex');

  res = await unsubGet({ request: new Request(url.replace(/s=./, 's=Z')), env });
  ok('署名の違うリンクを弾く', res.status === 400);

  res = await unsubPost({ request: post(url, ''), env });
  ok('POSTで止まる', statusOf(db, 'test@example.com') === 'unsubscribed');
  ok('完了画面を返す', (await res.clone().text()).includes('配信を停止しました'));

  db.raw.exec("UPDATE subscribers SET status='active' WHERE email='test@example.com'");
  res = await unsubPost({ request: post(url, 'List-Unsubscribe=One-Click',
    { 'Content-Type': 'application/x-www-form-urlencoded' }), env });
  const body = await res.clone().text();
  ok('Gmailのワンクリックで止まる', statusOf(db, 'test@example.com') === 'unsubscribed');
  ok('ワンクリックにはHTMLを返さない', res.status === 200 && !body.includes('<html'));

  const t1 = db.raw.prepare('SELECT unsubscribed_at FROM subscribers WHERE email=?').get('test@example.com').unsubscribed_at;
  res = await unsubPost({ request: post(url, ''), env });
  const t2 = db.raw.prepare('SELECT unsubscribed_at FROM subscribers WHERE email=?').get('test@example.com').unsubscribed_at;
  ok('二度押しで停止日時が書き換わらない', t1 === t2);
  ok('「すでに停止」と伝える', (await res.clone().text()).includes('すでに停止'));

  const ev = db.raw.prepare("SELECT detail FROM events WHERE email=? AND kind='unsubscribe'").all('test@example.com');
  ok('停止の記録が残る（法令上の保存）', ev.length === 3, String(ev.length));
  ok('ワンクリック分を判別できる', ev.some(e => (e.detail || '').includes('one-click')));

  res = await unsubPost({ request: post(url, ''), env: { NEWSLETTER_SECRET: env.NEWSLETTER_SECRET } });
  ok('D1未接続でも事情の分かる画面を返す', res.status === 503 && (await res.text()).includes('D1'));
}

// ── 4. Webからの申し込み ─────────────────────────────
head('4. Webからの申し込み（ダブルオプトイン）');
{
  const { db, env } = fresh();
  stubResend();
  await subscribe({ request: post('https://x/api/subscribe',
    JSON.stringify({ email: ' New@Example.com ', name: '新規' }), { 'Content-Type': 'application/json' }), env });
  ok('申し込んだ直後はまだ配信対象でない', statusOf(db, 'new@example.com') === 'pending', statusOf(db, 'new@example.com'));
  ok('確認メールを1通だけ送る', sent.length === 1);

  // ── 確認メールの中身 ──────────────────────────────
  // この1通は「押してもらう」のが仕事。押す先と、押す理由が両方要る。
  const mail = sent[0].body;
  ok('登録ボタンのリンクが入っている', /https:\/\/[^\s"]*\/api\/confirm\?e=/.test(mail.html));
  ok('本編と同じ名前を出している', mail.html.includes('OZAKEN LETTER') && mail.text.includes('OZAKEN LETTER'));
  ok('何が届くかを書いている', mail.html.includes('これからお送りするもの') && mail.text.includes('これからお送りするもの'));
  for (const needle of ['前提が動いた論点', '合言葉', '1〜3通']) {
    ok(`約束「${needle}」が HTML と文字だけの版の両方にある`,
      mail.html.includes(needle) && mail.text.includes(needle));
  }
  ok('住所と問い合わせ先が入っている（表示義務）',
    mail.html.includes(BASE.NEWSLETTER_SENDER_ADDRESS) && mail.html.includes(BASE.NEWSLETTER_REPLY_TO));
  ok('<style>を使っていない（メールで落ちる）', !/<style/i.test(mail.html));
  ok('ボタンが押せないとき用に、URLも文字で出している',
    mail.html.includes('ボタンが押せないときは'));

  // 約束の数字が3か所で食い違うと、届いた瞬間に信用が減る
  const pageHtml = readFileSync(join(HERE, '../subscribe.html'), 'utf8');
  const indexHtml = readFileSync(join(HERE, '../index.html'), 'utf8');
  ok('購読ページ・資料ゲート・確認メールで、頻度の約束が一致している',
    pageHtml.includes('1〜3通') && indexHtml.includes('1〜3通') && mail.html.includes('1〜3通'));


  const link = sent[0].body.text.match(/https:\/\/\S+/)[0];
  await confirm({ request: new Request(link), env });
  ok('確認リンクで配信対象になる', statusOf(db, 'new@example.com') === 'active');

  db.raw.exec("UPDATE subscribers SET status='unsubscribed' WHERE email='new@example.com'");
  await confirm({ request: new Request(link), env });
  ok('停止後に古い確認リンクを踏んでも復活しない', statusOf(db, 'new@example.com') === 'unsubscribed');

  stubResend();
  const r = await subscribe({ request: post('https://x/api/subscribe',
    JSON.stringify({ email: 'bot@example.com', fax: '埋めた' }), { 'Content-Type': 'application/json' }), env });
  ok('自動投稿を静かに捨てる',
    (await r.json()).ok && sent.length === 0 && !db.raw.prepare('SELECT 1 FROM subscribers WHERE email=?').get('bot@example.com'));

  const bad = await subscribe({ request: post('https://x/api/subscribe',
    JSON.stringify({ email: 'not-an-email' }), { 'Content-Type': 'application/json' }), env });
  ok('形式が違うアドレスを弾く', bad.status === 400);
}

// ── 5. 配信 ──────────────────────────────────────────
head('5. 配信');
{
  const { db, env } = fresh();
  seed(db, [['a@x.co', 'active'], ['b@x.co', 'active'], ['c@x.co', 'pending'], ['d@x.co', 'unsubscribed'], ['e@x.co', 'bounced']]);

  const noAuth = await send({ request: post('https://x/api/send', JSON.stringify({ issue: ISSUE }),
    { Authorization: 'Bearer wrong', 'Content-Type': 'application/json' }), env });
  ok('管理者トークンなしは401', noAuth.status === 401);

  stubResend();
  let out = await (await send({ request: adminPost({ issue: ISSUE }), env })).json();
  ok('配信対象は active だけ', out.sent === 2 && out.done, JSON.stringify(out));
  ok('宛先が正しい', JSON.stringify(sent[0].body.map(m => m.to[0])) === '["a@x.co","b@x.co"]');
  ok('100通ずつ束ねて渡す', sent[0].url.includes('/emails/batch'));
  ok('1通ごとに違う配信停止リンクが入る',
    new Set(sent[0].body.map(m => m.headers['List-Unsubscribe'])).size === 2);

  stubResend();
  out = await (await send({ request: adminPost({ issue: ISSUE }), env })).json();
  ok('同じ号を叩き直しても二重に送らない', out.sent === 0 && out.done && sent.length === 0);

  const stat = await (await sendStat({ request: new Request('https://x/api/send?issue_id=sample',
    { headers: { Authorization: 'Bearer admintoken' } }), env })).json();
  ok('名簿と配信の内訳を返す', stat.subscribers.active === 2 && stat.issue.deliveries.sent === 2);

  stubResend();
  const t = await (await send({ request: adminPost({ issue: ISSUE, test_to: 'me@example.com' }), env })).json();
  ok('テスト送信は名簿にも配信ログにも触らない',
    t.test && sent.length === 1 && !db.raw.prepare('SELECT 1 FROM deliveries WHERE email=?').get('me@example.com'));

  const bad = await (await send({ request: adminPost({ issue: { subject: '件名だけ' } }), env })).json();
  ok('号のIDがなければ受け付けない', !bad.ok);
}

// ── 6. 送信の失敗と再試行 ────────────────────────────
head('6. 送信に失敗したとき');
{
  const { db, env } = fresh();
  seed(db, [['p@x.co', 'active'], ['q@x.co', 'active']]);

  stubResend({ httpStatus: 429 });
  let out = await (await send({ request: adminPost({ issue: ISSUE }), env })).json();
  ok('Resendが落ちた回は「送れていない」と数える',
    out.sent === 0 && out.failed === 2 && out.remaining === 2 && !out.done, JSON.stringify(out));

  stubResend();
  out = await (await send({ request: adminPost({ issue: ISSUE }), env })).json();
  ok('復旧したら拾い直す（取りこぼさない）', out.sent === 2 && out.done);
  ok('取りこぼしの報告は空', (out.gave_up || []).length === 0);

  const d2 = fresh();
  seed(d2.db, [['dead@x.co', 'active']]);
  stubResend({ httpStatus: 422 });
  let rounds = 0;
  while (rounds < 12) {
    rounds++;
    out = await (await send({ request: adminPost({ issue: ISSUE }), env: d2.env })).json();
    if (out.done) break;
  }
  ok('送れない相手がいても配信は終わる（無限ループしない）', out.done, `${rounds}周`);
  ok('あきらめた相手を名指しで報告する',
    (out.gave_up || []).length === 1 && out.gave_up[0].email === 'dead@x.co', JSON.stringify(out.gave_up));
}

// ── 7. バウンス・迷惑メール報告 ──────────────────────
head('7. バウンスと迷惑メール報告');
{
  const { db, env } = fresh();
  seed(db, [['hard@x.co', 'active'], ['soft@x.co', 'active'], ['spam@x.co', 'active']]);
  const fire = async (payload, secret, offset) => hook({
    request: post('https://x/api/hooks/resend', payload, await svixHeaders(payload, secret, offset)), env });

  let p = JSON.stringify({ type: 'email.bounced', data: { to: ['hard@x.co'], bounce: { type: 'Permanent', message: 'no such user' } } });
  await fire(p);
  ok('恒久バウンスは名簿から外す', statusOf(db, 'hard@x.co') === 'bounced');

  p = JSON.stringify({ type: 'email.bounced', data: { to: ['soft@x.co'], bounce: { type: 'Transient', message: 'mailbox full' } } });
  await fire(p);
  ok('一時的なバウンスでは外さない', statusOf(db, 'soft@x.co') === 'active');

  p = JSON.stringify({ type: 'email.complained', data: { to: ['spam@x.co'] } });
  await fire(p);
  ok('迷惑メール報告は即停止', statusOf(db, 'spam@x.co') === 'complained');

  p = JSON.stringify({ type: 'email.complained', data: { to: ['soft@x.co'] } });
  let r = await fire(p, Buffer.from('wrong-key-wrong-key-wrong-key-32').toString('base64'));
  ok('偽の署名を弾く', r.status === 401 && statusOf(db, 'soft@x.co') === 'active');
  r = await fire(p, WHSEC, -600);
  ok('10分前の通知の使い回しを弾く', r.status === 401);
  r = await hook({ request: post('https://x/api/hooks/resend', p, {}), env });
  ok('署名なしを弾く', r.status === 401);
}

// ── 8. 一度止めた人を復活させない ────────────────────
head('8. 一度止めた人を、どこからも復活させない');
{
  const { db, env } = fresh();
  seed(db, [['gone@x.co', 'active']]);
  const url = await unsubscribeUrl('https://content.ozaken.ai', env.NEWSLETTER_SECRET, 'gone@x.co');
  await unsubPost({ request: post(url, ''), env });

  // 名刺CSVの取り込みと同じSQLを流す
  const t = new Date().toISOString();
  db.raw.exec(`INSERT INTO subscribers (email,name,company,status,source,source_note,consent_at,created_at,updated_at)
    VALUES ('gone@x.co','再取り込み','会社','active','meishi','2回目','${t}','${t}','${t}')
    ON CONFLICT(email) DO UPDATE SET
      name = COALESCE(excluded.name, subscribers.name),
      company = COALESCE(excluded.company, subscribers.company),
      updated_at = excluded.updated_at`);
  ok('名簿を取り込み直しても復活しない', statusOf(db, 'gone@x.co') === 'unsubscribed');
  ok('名前と会社名だけは新しくなる',
    db.raw.prepare('SELECT name FROM subscribers WHERE email=?').get('gone@x.co').name === '再取り込み');

  stubResend();
  const out = await (await send({ request: adminPost({ issue: ISSUE }), env })).json();
  ok('配信の宛先に入らない', out.sent === 0 && sent.length === 0);
}

// ── 9. 名刺CSVの取り込み ────────────────────────────
head('9. 名刺CSVの取り込み');
{
  // 引用符の中にカンマ・改行・二重引用符が入った、いやらしい行を混ぜる
  const csv = [
    '姓,名,会社名,部署名,メールアドレス,名刺交換日',
    '小澤,健祐,"株式会社Cinematorico, Inc.",編集部,  A@Example.COM ,2026/06/12',
    '田中,太郎,"改行\nを含む社名",営業,tanaka@example.co.jp,2026年7月3日',
    '重複,太郎,テスト,,a@example.com,',
    '壊れ,行,,,not-an-email,',
    '引用,符,"""カギ""つき社名",,quote@example.co.jp,',
  ].join('\n');

  const rows = parseCsv(csv);
  ok('引用符の中のカンマで列がずれない', rows[1][2] === '株式会社Cinematorico, Inc.', rows[1][2]);
  ok('引用符の中の改行を1行として読む', rows[2][2].includes('\n'), JSON.stringify(rows[2][2]));
  ok('"" を引用符1個として読む', rows[5][2] === '"カギ"つき社名', rows[5][2]);
  const cols = detectColumns(rows[0]);
  ok('姓と名の列を見つける', cols.last === 0 && cols.first === 1);
  ok('年月日つきの日付を読む', parseDate('2026年7月3日', 'x').startsWith('2026-07-03'));
  ok('読めない日付は取り込み日にする', parseDate('いつか', 'FALLBACK') === 'FALLBACK');

  const { db, env } = fresh();
  const imp = (q = '') => importCsv({
    request: post('https://x/api/import' + q, csv,
      { Authorization: 'Bearer admintoken', 'Content-Type': 'text/csv' }), env });

  const noAuth = await importCsv({
    request: post('https://x/api/import', csv, { Authorization: 'Bearer wrong' }), env });
  ok('管理者トークンなしは401', noAuth.status === 401);

  let out = await (await imp('?dry=1&note=下見')).json();
  ok('下見では名簿に書き込まない', db.raw.prepare('SELECT COUNT(*) c FROM subscribers').get().c === 0);
  ok('下見で新規の件数が分かる', out.report.created === 3, JSON.stringify(out.report));
  ok('CSV内の重複を数える', out.report.duplicates === 1);
  ok('形式の違う行を数える', out.report.invalid === 1);
  ok('読み取った列を返す', out.columns.email === 'メールアドレス');

  out = await (await imp('?note=2026年上期')).json();
  ok('本番で名簿に入る',
    db.raw.prepare('SELECT COUNT(*) c FROM subscribers').get().c === 3, JSON.stringify(out.report));
  ok('アドレスを正規化して入れる', statusOf(db, 'a@example.com') === 'active');
  ok('姓と名をつないで名前にする',
    db.raw.prepare('SELECT name FROM subscribers WHERE email=?').get('a@example.com').name === '小澤 健祐');
  ok('取得の場を記録に残す（法令上の根拠）',
    (db.raw.prepare("SELECT detail FROM events WHERE email=? AND kind='import'").get('a@example.com') || {})
      .detail.includes('2026年上期'));

  // 一度止めた人が、CSVの入れ直しで戻らないか
  const url = await unsubscribeUrl('https://content.ozaken.ai', env.NEWSLETTER_SECRET, 'a@example.com');
  await unsubPost({ request: post(url, ''), env });
  out = await (await imp('?note=2回目')).json();
  ok('取り込み直しても配信停止済みは復活しない', statusOf(db, 'a@example.com') === 'unsubscribed');
  ok('復活させなかった件数を報告する', out.report.kept_stopped === 1, JSON.stringify(out.report));
  ok('誰を触らなかったか名指しで返す', (out.kept_examples || []).some(k => k.email === 'a@example.com'));

  // 分割して叩いても、結果が変わらないこと
  const d2 = fresh();
  const imp2 = (q) => importCsv({
    request: post('https://x/api/import' + q, csv,
      { Authorization: 'Bearer admintoken', 'Content-Type': 'text/csv' }), env: d2.env });
  let offset = 0, totals = { created: 0, duplicates: 0 }, rounds = 0;
  while (rounds++ < 20) {
    const r = await (await imp2(`?offset=${offset}&limit=2`)).json();
    totals.created += r.report.created;
    totals.duplicates += r.report.duplicates;
    offset = r.next_offset;
    if (r.done) break;
  }
  ok('分割して叩いても件数が変わらない',
    totals.created === 3 && totals.duplicates === 1, JSON.stringify(totals));
  ok('分割しても名簿の中身は同じ', d2.db.raw.prepare('SELECT COUNT(*) c FROM subscribers').get().c === 3);
}

// ── 10. 端末版とブラウザ版が食い違っていないか ───────
head('10. 端末版（Python）とブラウザ版（JS）の、列の見出しの候補');
{
  const py = readFileSync(join(HERE, 'import_meishi.py'), 'utf8');
  const start = py.indexOf('COLUMNS = {');
  const block = py.slice(start, py.indexOf('}', start));
  for (const [key, list] of Object.entries(COLUMNS)) {
    const line = block.split('\n').find(l => l.trim().startsWith(`"${key}":`)) || '';
    const inPy = [...line.matchAll(/"([^"]+)"/g)].map(m => m[1]).slice(1);
    ok(`${key} の候補が両方で同じ`, JSON.stringify(inPy) === JSON.stringify(list),
      `py=${JSON.stringify(inPy)} js=${JSON.stringify(list)}`);
  }
}

console.log(`\n${'─'.repeat(46)}\n通った ${pass} 件 / 落ちた ${fail} 件\n`);
process.exit(fail === 0 ? 0 : 1);
