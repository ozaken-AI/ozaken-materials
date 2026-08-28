// 号の一覧と、名簿の概況。/api/issues（GET、管理者トークンが要る）
//
// 号の中身も結果も、送った時点で D1 に残っている。見る画面が無かっただけ。
//   issues     … 号のID・件名・本文のJSONまるごと
//   deliveries … 誰にいつ送ったか・成否・Resendのメッセージ番号
//   events     … 同意・確認・配信停止・バウンス・苦情
//
//   /api/issues        … 概況ひとまとめ（名簿の内訳・号の一覧・最近の出来事）
//   /api/issues?id=X   … その号の中身。前号を下敷きに次を書くのに使う

import { json } from '../_lib/page.js';
import { checkAdmin } from '../_lib/auth.js';
import { requireDb, HttpError } from '../_lib/db.js';

export async function onRequestGet({ request, env }) {
  const auth = checkAdmin(request, env);
  if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);

  try {
    const db = requireDb(env);
    const id = new URL(request.url).searchParams.get('id');

    // 1本だけ引く（前号を下敷きにするとき）
    if (id) {
      const row = await db.prepare('SELECT id, subject, payload, created_at, finished_at FROM issues WHERE id = ?')
        .bind(id).first();
      if (!row) throw new HttpError(404, `号「${id}」が見つかりません。`);
      let payload = null;
      try { payload = JSON.parse(row.payload); } catch { /* 壊れていても一覧は返す */ }
      return json({ ok: true, issue: { ...row, payload } });
    }

    const counts = await db.prepare(
      'SELECT status, COUNT(*) AS n FROM subscribers GROUP BY status').all();
    const subscribers = {};
    for (const r of counts.results || []) subscribers[r.status] = r.n;

    // 号ごとの成績。1回のクエリで出す（号の数だけ問い合わせると遅くなる）
    const issues = await db.prepare(`
      SELECT i.id, i.subject, i.created_at, i.finished_at,
             SUM(CASE WHEN d.status = 'sent'       THEN 1 ELSE 0 END) AS sent,
             SUM(CASE WHEN d.status = 'failed'     THEN 1 ELSE 0 END) AS failed,
             SUM(CASE WHEN d.status = 'bounced'    THEN 1 ELSE 0 END) AS bounced,
             SUM(CASE WHEN d.status = 'complained' THEN 1 ELSE 0 END) AS complained
      FROM issues i
      LEFT JOIN deliveries d ON d.issue_id = i.id
      GROUP BY i.id
      ORDER BY i.created_at DESC
      LIMIT 50
    `).all();

    // 直近の出来事。**苦情とバウンスは、増え方を目で見ていないと手遅れになる。**
    const events = await db.prepare(`
      SELECT email, kind, detail, at FROM events
      WHERE kind IN ('unsubscribe', 'bounce', 'complaint', 'confirm')
      ORDER BY id DESC LIMIT 30
    `).all();

    // 今日と、直近7日の動き
    const since = new Date(Date.now() - 7 * 86400000).toISOString();
    const recent = await db.prepare(`
      SELECT kind, COUNT(*) AS n FROM events WHERE at > ? GROUP BY kind
    `).bind(since).all();
    const last7 = {};
    for (const r of recent.results || []) last7[r.kind] = r.n;

    return json({
      ok: true,
      subscribers,
      issues: issues.results || [],
      events: events.results || [],
      last7,
    });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message }, status);
  }
}
