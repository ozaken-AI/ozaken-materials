// 配信の実行。/api/send（POST、管理者トークンが要る）
//
// **1回の呼び出しで全員には送らない。** Workers には実行時間の上限があり、
// Resend にもレート制限がある。1回につき limit 件だけ送り、
// 「残り何件か」を返す。呼ぶ側（newsletter/send.sh）が 0 になるまで叩き直す。
//
// 誰に送ったかは deliveries に (号, アドレス) の主キーで記録しているので、
// 途中で落ちても、叩き直しても、同じ人に二度届くことはない。

import { json } from '../_lib/page.js';
import { checkAdmin } from '../_lib/auth.js';
import { config, buildMessage, sendMessages } from '../_lib/mail.js';
import {
  requireDb, upsertIssue, pickRecipients, countRemaining,
  recordDeliveries, listGaveUp, now, HttpError, MAX_ATTEMPTS,
} from '../_lib/db.js';

const DEFAULT_LIMIT = 500;
const MAX_LIMIT = 1000;

function validate(issue) {
  if (!issue || typeof issue !== 'object') throw new HttpError(400, 'issue がありません。');
  if (!issue.id) throw new HttpError(400, 'issue.id（号のID）が要ります。');
  if (!issue.subject) throw new HttpError(400, 'issue.subject（件名）が要ります。');
  if (issue.items && !Array.isArray(issue.items)) throw new HttpError(400, 'issue.items は配列で。');
}

export async function onRequestPost({ request, env }) {
  const auth = checkAdmin(request, env);
  if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);

  try {
    const db = requireDb(env);
    const cfg = config(env);
    if (cfg.missing.length) {
      throw new HttpError(503, `設定が足りません: ${cfg.missing.join(', ')}`);
    }

    const body = await request.json();
    const issue = body.issue;
    validate(issue);

    // 本番前の下見。名簿にも配信ログにも触らない。
    if (body.test_to) {
      const msg = await buildMessage({
        issue,
        subscriber: { email: body.test_to, name: body.test_name || 'テスト', source: 'web' },
        cfg,
      });
      const [r] = await sendMessages(cfg, [msg]);
      return json({ ok: r.status === 'sent', test: true, result: r });
    }

    await upsertIssue(db, issue);

    const limit = Math.min(Number(body.limit) || DEFAULT_LIMIT, MAX_LIMIT);
    const targets = await pickRecipients(db, issue.id, limit);

    if (!targets.length) {
      await db.prepare('UPDATE issues SET finished_at = COALESCE(finished_at, ?) WHERE id = ?')
        .bind(now(), issue.id).run();
      return json({ ok: true, sent: 0, failed: 0, remaining: 0, done: true,
        gave_up: await listGaveUp(db, issue.id) });
    }

    const messages = await Promise.all(
      targets.map(s => buildMessage({ issue, subscriber: s, cfg })));
    const results = await sendMessages(cfg, messages);
    await recordDeliveries(db, issue.id, results);

    const sent = results.filter(r => r.status === 'sent').length;
    const failed = results.length - sent;
    const remaining = await countRemaining(db, issue.id);
    if (remaining === 0) {
      await db.prepare('UPDATE issues SET finished_at = COALESCE(finished_at, ?) WHERE id = ?')
        .bind(now(), issue.id).run();
    }

    return json({
      ok: true,
      sent,
      failed,
      remaining,
      done: remaining === 0,
      // 失敗はここに出す。全部返すと返事が膨れるので先頭だけ。
      // remaining に数え直されているので、次の周回で自動的に拾い直す（最大 MAX_ATTEMPTS 回）。
      errors: results.filter(r => r.status !== 'sent').slice(0, 5).map(r => `${r.email}: ${r.error}`),
      // 上限まで試しても送れなかった相手。ここに出たら手当てが要る。
      gave_up: remaining === 0 ? await listGaveUp(db, issue.id) : undefined,
      max_attempts: MAX_ATTEMPTS,
    });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message || '送信に失敗しました。' }, status);
  }
}

// 名簿と配信の状況を見る。/api/send?issue_id=2026-08-18
export async function onRequestGet({ request, env }) {
  const auth = checkAdmin(request, env);
  if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);

  try {
    const db = requireDb(env);
    const counts = await db.prepare(
      'SELECT status, COUNT(*) AS n FROM subscribers GROUP BY status').all();
    const list = {};
    for (const row of counts.results || []) list[row.status] = row.n;

    const issueId = new URL(request.url).searchParams.get('issue_id');
    let issue = null;
    if (issueId) {
      const meta = await db.prepare(
        'SELECT id, subject, created_at, finished_at FROM issues WHERE id = ?').bind(issueId).first();
      const d = await db.prepare(`
        SELECT status, COUNT(*) AS n FROM deliveries WHERE issue_id = ? GROUP BY status
      `).bind(issueId).all();
      const byStatus = {};
      for (const row of d.results || []) byStatus[row.status] = row.n;
      issue = { ...(meta || { id: issueId }), deliveries: byStatus, remaining: await countRemaining(db, issueId) };
    }
    return json({ ok: true, subscribers: list, issue });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message }, status);
  }
}
