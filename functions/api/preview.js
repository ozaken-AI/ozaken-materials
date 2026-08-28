// 号の見え方を確かめる。/api/preview（POST、管理者トークンが要る）
//
// **本文の組み立てを画面側に持たない。** 二重に持つと、必ず片方だけ直して
// 「プレビューでは合っていたのに、届いたものが違う」が起きる。
// ここでは実際に送るのと同じ関数を通して、出来上がったHTMLをそのまま返す。
//
// メールは送らない。名簿にも配信ログにも触らない。

import { json } from '../_lib/page.js';
import { checkAdmin } from '../_lib/auth.js';
import { HttpError } from '../_lib/db.js';
import { config, buildEmail } from '../_lib/mail.js';
import { unsubscribeUrl } from '../_lib/token.js';
import { validate } from './send.js';

export async function onRequestPost({ request, env }) {
  const auth = checkAdmin(request, env);
  if (!auth.ok) return json({ ok: false, error: auth.error }, auth.status);

  try {
    const cfg = config(env);
    if (cfg.missing.length) throw new HttpError(503, `設定が足りません: ${cfg.missing.join(', ')}`);

    const body = await request.json();
    const issue = body.issue;
    validate(issue);

    // 宛名の出方も確かめたいので、受け取る人を仮に置く
    const subscriber = {
      email: body.as_email || 'reader@example.com',
      name: body.as_name || '田中 太郎',
      source: body.as_source || 'download',
    };
    const unsubUrl = await unsubscribeUrl(cfg.site, cfg.secret, subscriber.email);
    const { html, text } = buildEmail({ issue, subscriber, unsubUrl, cfg });

    return json({ ok: true, subject: issue.subject, html, text });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message || '組み立てられませんでした。' }, status);
  }
}
