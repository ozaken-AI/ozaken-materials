// D1 への出入り口。SQLを書き散らさないよう、ここに集める。

import { normalize } from './token.js';

// 送信に失敗した相手を、何回まで拾い直すか。
// 無制限にすると、存在しないアドレス1件で配信が終わらなくなる。
export const MAX_ATTEMPTS = 3;

export function now() {
  return new Date().toISOString();
}

// 束ねる先が用意されていないときに、500のスタックトレースを見せない。
// 静的サイト側は無関係に動き続けるので、ここだけが止まる。
export function requireDb(env) {
  if (!env || !env.DB) {
    throw new HttpError(503, 'メルマガの名簿がまだつながっていません（D1 バインディング DB が未設定）。');
  }
  return env.DB;
}

export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export async function getSubscriber(db, email) {
  return db.prepare('SELECT * FROM subscribers WHERE email = ?')
    .bind(normalize(email)).first();
}

// 出来事は消さずに積む（特定電子メール法の記録保存）。
export async function logEvent(db, email, kind, detail, ip) {
  await db.prepare('INSERT INTO events (email, kind, detail, ip, at) VALUES (?, ?, ?, ?, ?)')
    .bind(normalize(email), kind, detail || null, ip || null, now()).run();
}

// Webからの申し込み。すでに配信停止した人が申し込み直した場合は、
// 本人の操作なので pending に戻してよい（確認メールを踏んで初めて active になる）。
export async function upsertPending(db, { email, name, company, source, sourceNote }) {
  const e = normalize(email);
  const t = now();
  await db.prepare(`
    INSERT INTO subscribers (email, name, company, status, source, source_note, consent_at, created_at, updated_at)
    VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
      name        = COALESCE(excluded.name, subscribers.name),
      company     = COALESCE(excluded.company, subscribers.company),
      status      = CASE WHEN subscribers.status = 'active' THEN 'active' ELSE 'pending' END,
      source      = excluded.source,
      source_note = excluded.source_note,
      consent_at  = excluded.consent_at,
      updated_at  = excluded.updated_at
  `).bind(e, name || null, company || null, source, sourceNote || null, t, t, t).run();
}

export async function markConfirmed(db, email) {
  const t = now();
  const r = await db.prepare(`
    UPDATE subscribers SET status = 'active', confirmed_at = ?, updated_at = ?
    WHERE email = ? AND status = 'pending'
  `).bind(t, t, normalize(email)).run();
  return r.meta.changes > 0;
}

// 配信停止・バウンス・苦情。いずれも「もう送らない」に倒す。
// すでに止まっている相手に対しては、状態を上書きしない（最初に止まった理由と日時を残す）。
export async function stopSending(db, email, status) {
  const t = now();
  const r = await db.prepare(`
    UPDATE subscribers SET status = ?, unsubscribed_at = ?, updated_at = ?
    WHERE email = ? AND status IN ('pending', 'active')
  `).bind(status, t, t, normalize(email)).run();
  return r.meta.changes > 0;
}

export async function upsertIssue(db, issue) {
  const t = now();
  await db.prepare(`
    INSERT INTO issues (id, subject, payload, created_at) VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET subject = excluded.subject, payload = excluded.payload
  `).bind(issue.id, issue.subject, JSON.stringify(issue), t).run();
}

// まだ送れていない配信対象を、指定件数だけ取る。
//
// 「送信済み」と「送ろうとして失敗した」を分けているのが肝。
// 失敗したままの相手は、上限回数まで次の周回で拾い直す。
// bounced / complained は拾わない（相手が受け取れない・拒否している）。
const PENDING_CONDITION = `
  s.status = 'active'
  AND (d.email IS NULL OR (d.status = 'failed' AND d.attempts < ?))
`;

export async function pickRecipients(db, issueId, limit) {
  const r = await db.prepare(`
    SELECT s.email, s.name, s.source
    FROM subscribers s
    LEFT JOIN deliveries d ON d.issue_id = ? AND d.email = s.email
    WHERE ${PENDING_CONDITION}
    ORDER BY s.email
    LIMIT ?
  `).bind(issueId, MAX_ATTEMPTS, limit).all();
  return r.results || [];
}

export async function countRemaining(db, issueId) {
  const r = await db.prepare(`
    SELECT COUNT(*) AS n
    FROM subscribers s
    LEFT JOIN deliveries d ON d.issue_id = ? AND d.email = s.email
    WHERE ${PENDING_CONDITION}
  `).bind(issueId, MAX_ATTEMPTS).first();
  return r ? r.n : 0;
}

// 上限まで試して、それでも送れなかった相手。配信のあとに必ず目を通す。
export async function listGaveUp(db, issueId) {
  const r = await db.prepare(`
    SELECT email, error FROM deliveries
    WHERE issue_id = ? AND status = 'failed' AND attempts >= ?
  `).bind(issueId, MAX_ATTEMPTS).all();
  return r.results || [];
}

export async function recordDeliveries(db, issueId, rows) {
  if (!rows.length) return;
  const t = now();
  const stmt = db.prepare(`
    INSERT INTO deliveries (issue_id, email, status, provider_id, error, attempts, sent_at)
    VALUES (?, ?, ?, ?, ?, 1, ?)
    ON CONFLICT(issue_id, email) DO UPDATE SET
      status      = excluded.status,
      provider_id = excluded.provider_id,
      error       = excluded.error,
      attempts    = deliveries.attempts + 1,
      sent_at     = excluded.sent_at
  `);
  await db.batch(rows.map(r =>
    stmt.bind(issueId, normalize(r.email), r.status, r.providerId || null, r.error || null, t)));
}

// Resend の webhook はメッセージIDで届く。誰宛だったかを配信ログから引き直す。
export async function emailByProviderId(db, providerId) {
  const r = await db.prepare('SELECT email FROM deliveries WHERE provider_id = ? LIMIT 1')
    .bind(providerId).first();
  return r ? r.email : null;
}
