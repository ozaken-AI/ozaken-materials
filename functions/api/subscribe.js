// Webからの購読申し込み。/api/subscribe（POST）
//
// ここでは名簿に pending で入れるだけで、まだ配信対象にしない。
// 確認メールのリンクを踏んで初めて active になる（ダブルオプトイン）。
// 他人のアドレスを勝手に登録するいたずらを、これで無効化できる。

import { normalize, looksLikeEmail, confirmUrl } from '../_lib/token.js';
import { json } from '../_lib/page.js';
import { requireDb, upsertPending, logEvent, getSubscriber, HttpError } from '../_lib/db.js';
import { config } from '../_lib/mail.js';

const FONT = "-apple-system,BlinkMacSystemFont,'Hiragino Sans','Yu Gothic',Meiryo,sans-serif";

async function readBody(request) {
  const type = request.headers.get('Content-Type') || '';
  if (type.includes('application/json')) return request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await readBody(request);
  } catch {
    return json({ ok: false, error: '入力を読み取れませんでした。' }, 400);
  }

  // 人間には見えない入力欄。埋まっていたら自動投稿なので、
  // 成功したふりをして静かに捨てる（失敗を返すとやり方を変えて再挑戦してくる）。
  if (body.fax) return json({ ok: true });

  const email = normalize(body.email);
  if (!looksLikeEmail(email)) {
    return json({ ok: false, error: 'メールアドレスの形式をご確認ください。' }, 400);
  }

  try {
    const db = requireDb(env);
    const cfg = config(env);
    if (cfg.missing.length) {
      throw new HttpError(503, `配信の設定が未完了です（${cfg.missing.join(', ')}）。`);
    }

    const before = await getSubscriber(db, email);
    // 一度止めた人が申し込み直すのは本人の意思なので受け付ける。
    // ただし迷惑メール報告をした相手には、こちらから送り直さない。
    if (before && before.status === 'complained') {
      return json({ ok: true });
    }
    if (before && before.status === 'active') {
      return json({ ok: true, already: true });
    }

    await upsertPending(db, {
      email,
      name: (body.name || '').trim() || null,
      company: (body.company || '').trim() || null,
      source: 'web',
      sourceNote: (body.note || '').trim() || null,
    });
    await logEvent(db, email, 'consent', 'web form', request.headers.get('CF-Connecting-IP'));

    const link = await confirmUrl(cfg.site, cfg.secret, email);
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${cfg.apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: cfg.from,
        to: [email],
        subject: '【確認】メールマガジンの登録手続き',
        html: confirmHtml(link, cfg),
        text: confirmText(link, cfg),
        ...(cfg.replyTo ? { reply_to: cfg.replyTo } : {}),
      }),
    });
    if (!res.ok) {
      throw new HttpError(502, '確認メールを送れませんでした。しばらく置いてお試しください。');
    }
    return json({ ok: true });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message || '処理できませんでした。' }, status);
  }
}

function confirmHtml(link, cfg) {
  return `<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:28px 12px;background:#f8f7f4;font-family:${FONT}">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
       style="width:600px;max-width:100%;margin:0 auto;background:#fff;border:1px solid #d8e4f0;border-radius:4px">
  <tr><td style="padding:36px 34px">
    <div style="width:40px;height:2px;background:#2e5496;font-size:0;line-height:0">&nbsp;</div>
    <div style="padding:18px 0 14px;font:700 21px/1.5 ${FONT};color:#1a1a2e">
      あと1回、押してください
    </div>
    <div style="font:400 15px/1.9 ${FONT};color:#1a1a2e;padding-bottom:24px">
      メールマガジンのお申し込みを受け付けました。<br>
      下のボタンを押していただくと、登録が完了します。
    </div>
    <a href="${link}" style="display:inline-block;background:#1f3864;color:#fff;text-decoration:none;
       border-radius:3px;padding:13px 28px;font:700 15px ${FONT}">登録を完了する</a>
    <div style="padding:24px 0 0;font:400 12px/1.9 ${FONT};color:#6b7a99;
                border-top:1px solid #d8e4f0;margin-top:26px">
      お心当たりがない場合は、このメールを破棄してください。<br>
      ボタンを押さないかぎり、配信は始まりません。<br><br>
      発行：${cfg.senderName}<br>所在地：${cfg.senderAddress}
    </div>
  </td></tr>
</table></body></html>`;
}

function confirmText(link, cfg) {
  return [
    'メールマガジンのお申し込みを受け付けました。',
    '下のリンクを開いていただくと、登録が完了します。',
    '',
    link,
    '',
    'お心当たりがない場合は、このメールを破棄してください。',
    'リンクを開かないかぎり、配信は始まりません。',
    '',
    `発行：${cfg.senderName}`,
    `所在地：${cfg.senderAddress}`,
  ].join('\n');
}
