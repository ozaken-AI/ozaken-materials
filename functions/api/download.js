// 資料ダウンロードの受け口。/api/download（POST）
//
// index.html のリードゲートから呼ばれる。以前は Google Apps Script が
// 受けて、スプレッドシートに貯め、aicx.jp からお礼メールを出していた。
// 差出人ドメインが2本になると、次に届くお便りが「知らない相手」に見えるので、
// ここへ寄せて news.ozaken.ai に一本化した。
//
// **ゲートは、この呼び出しが失敗しても資料を出す。** 受け口の不調で
// ダウンロードが止まるのがいちばん困る。だからここは常に ok を返し、
// 失敗の詳細は返さない（呼び出し側は結果を見ていない）。
//
// 質問・コメント（ask.html と投影Q&A）は Apps Script のまま。あちらは別の仕事。

import { json } from '../_lib/page.js';
import { requireDb, now, logEvent, getSubscriber, HttpError } from '../_lib/db.js';
import { normalize, looksLikeEmail } from '../_lib/token.js';
import { config, buildWelcome, sendMessages } from '../_lib/mail.js';

// ゲートの注記。同意の根拠として、文言そのものを記録に残す。
// **画面の文言を変えたら、ここも変える。**
const NOTICE = '小澤健祐（おざけん）およびAICX協会からのメールマガジン・資料・イベント案内の受け取り';

// もう送らないと決まっている人。資料を落とし直しても、こちらから送らない。
const STOPPED = new Set(['unsubscribed', 'bounced', 'complained']);

// 同じ相手への連投を抑える。取りこぼしより、二重送信のほうが印象が悪い。
const DEDUPE_SEC = 60;

async function sentRecently(db, email) {
  const since = new Date(Date.now() - DEDUPE_SEC * 1000).toISOString();
  const r = await db.prepare(
    "SELECT 1 AS hit FROM events WHERE email = ? AND kind = 'download' AND at > ? LIMIT 1")
    .bind(email, since).first();
  return !!r;
}

export async function onRequestPost({ request, env }) {
  let body = {};
  try {
    body = await request.json();
  } catch {
    return json({ ok: true, skipped: 'unreadable' });
  }

  // 人には見えない欄。埋まっていたら自動投稿なので、静かに捨てる。
  if (body.fax) return json({ ok: true });

  const email = normalize(body.email);
  if (!looksLikeEmail(email)) return json({ ok: true, skipped: 'invalid' });

  try {
    const db = requireDb(env);
    const cfg = config(env);
    if (cfg.missing.length) throw new HttpError(503, `設定が足りません: ${cfg.missing.join(', ')}`);

    const before = await getSubscriber(db, email);
    const t = now();
    const asset = String(body.asset || '').slice(0, 300) || null;
    const name = String(body.name || '').trim() || null;
    const company = String(body.company || '').trim() || null;

    // status には触らない。**一度止めた人を、資料の再ダウンロードで戻さない。**
    await db.prepare(`
      INSERT INTO subscribers
        (email, name, company, status, source, source_note, consent_at, created_at, updated_at)
      VALUES (?, ?, ?, 'active', 'download', ?, ?, ?, ?)
      ON CONFLICT(email) DO UPDATE SET
        name       = COALESCE(excluded.name, subscribers.name),
        company    = COALESCE(excluded.company, subscribers.company),
        updated_at = excluded.updated_at
    `).bind(email, name, company, asset, t, t, t).run();

    // 同意の記録。あとから「いつ・どの画面の・どの文言で」を示せるようにする。
    await logEvent(db, email, 'consent',
      `download gate / ${NOTICE}${asset ? ` / asset=${asset}` : ''}`,
      request.headers.get('CF-Connecting-IP'));

    // 止めている相手には送らない。ここを守らないと、配信停止が嘘になる。
    if (before && STOPPED.has(before.status)) {
      return json({ ok: true, mailed: false, reason: 'stopped' });
    }
    if (await sentRecently(db, email)) {
      return json({ ok: true, mailed: false, reason: 'recent' });
    }

    const msg = await buildWelcome({ subscriber: { email, name }, asset, cfg });
    const [r] = await sendMessages({ ...cfg, sendMode: 'single' }, [msg]);
    if (r.status === 'sent') {
      await logEvent(db, email, 'download', asset || 'index.html');
    }
    return json({ ok: true, mailed: r.status === 'sent' });
  } catch (err) {
    // ここで失敗しても、ゲートは資料を出す。原因はログにだけ残す。
    console.log('download endpoint failed:', err && err.message);
    return json({ ok: true, mailed: false });
  }
}
