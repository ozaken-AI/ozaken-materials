// Webからの購読申し込み。/api/subscribe（POST）
//
// ここでは名簿に pending で入れるだけで、まだ配信対象にしない。
// 確認メールのリンクを踏んで初めて active になる（ダブルオプトイン）。
// 他人のアドレスを勝手に登録するいたずらを、これで無効化できる。

import { normalize, looksLikeEmail, confirmUrl } from '../_lib/token.js';
import { json, esc } from '../_lib/page.js';
import { requireDb, upsertPending, logEvent, getSubscriber, HttpError } from '../_lib/db.js';
import { config, PROMISES } from '../_lib/mail.js';

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

// 確認メール。**この1通の仕事は、ボタンを押してもらうこと。**
// だからボタンを上に置き、その下で「何が届くか」を見せる。
// 逆にすると、読み物として満足して押さずに閉じられる。
//
// 見た目は本編（OZAKEN LETTER）とそろえてある。次に届いたときに
// 「あのとき登録したやつだ」と分かることが、開いてもらえるかを分ける。
//
// ここに書く約束は subscribe.html と同じ3つ。**片方だけ変えない。**
// newsletter/selftest.mjs が頻度の表記の食い違いを見張っている。

const NAVY = '#1f3864';
const AZURE = '#2e5496';
const INK = '#1a1a2e';
const MUTED = '#6b7a99';
const PAPER = '#f8f7f4';
const LINE = '#d8e4f0';

function confirmHtml(link, cfg) {
  const promises = PROMISES.map(([title, body], i) => `
    <tr><td style="padding:0 0 22px">
      <div style="font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE};padding-bottom:5px">
        ${String(i + 1).padStart(2, '0')}
      </div>
      <div style="font:700 16px/1.6 ${FONT};color:${INK};padding-bottom:5px">${title}</div>
      <div style="font:400 14px/1.85 ${FONT};color:${MUTED}">${body}</div>
    </td></tr>`).join('');

  return `<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:${PAPER};-webkit-text-size-adjust:100%">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">あと1回だけ押していただくと、登録が完了します。</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:${PAPER}">
<tr><td align="center" style="padding:28px 12px">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"
         style="width:100%;max-width:600px;background:#fff;border:1px solid ${LINE};border-radius:4px">

    <tr><td style="background:${NAVY};padding:26px 34px">
      <div style="font:700 11px ${FONT};letter-spacing:.16em;color:#9fc6f5">OZAKEN LETTER</div>
      <div style="padding-top:6px;font:400 13px ${FONT};color:rgba(255,255,255,.72)">登録の確認</div>
    </td></tr>

    <tr><td style="padding:36px 34px 0">
      <div style="width:40px;height:2px;background:${AZURE};font-size:0;line-height:0">&nbsp;</div>
      <div style="padding:18px 0 14px;font:700 23px/1.5 ${FONT};color:${INK}">
        あと1回だけ、押してください
      </div>
      <div style="font:400 15px/1.9 ${FONT};color:${INK};padding-bottom:26px">
        お申し込みを受け付けました。<br>
        下のボタンを押していただくと、登録が完了します。
      </div>
      <a href="${link}" style="display:inline-block;background:${NAVY};color:#fff;text-decoration:none;
         border-radius:3px;padding:15px 34px;font:700 16px ${FONT}">登録を完了する</a>
      <div style="padding:14px 0 0;font:400 12.5px/1.8 ${FONT};color:${MUTED}">
        ボタンが押せないときは、このURLを開いてください。<br>
        <span style="word-break:break-all;color:${AZURE}">${link}</span>
      </div>
    </td></tr>

    <tr><td style="padding:32px 34px 0">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="background:${PAPER};border:1px solid ${LINE};border-radius:4px">
        <tr><td style="padding:26px 26px 8px">
          <div style="font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE};padding-bottom:16px">
            WHAT YOU GET ／ これからお送りするもの
          </div>
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
            ${promises}
          </table>
        </td></tr>
      </table>
    </td></tr>

    <tr><td style="padding:28px 34px 0">
      <div style="font:400 15px/1.95 ${FONT};color:${INK}">
        AIの新着を全部追うのは、もう無理です。だから追いません。<br>
        その代わり、前提が動いたところだけを、なぜ動いたのかまで書いて送ります。
      </div>
      <div style="padding:14px 0 0;font:400 14px ${FONT};color:${MUTED}">── ${esc(cfg.senderName)}</div>
    </td></tr>

    <tr><td style="padding:30px 34px 32px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="border-top:1px solid ${LINE}">
        <tr><td style="padding:20px 0 0;font:400 12px/1.9 ${FONT};color:${MUTED}">
          お心当たりがない場合は、このメールを破棄してください。<br>
          <b>ボタンを押さないかぎり、配信は始まりません。</b><br><br>
          発行：${esc(cfg.senderName)}<br>
          所在地：${esc(cfg.senderAddress)}<br>
          ${cfg.replyTo ? `お問い合わせ：<a href="mailto:${esc(cfg.replyTo)}" style="color:${AZURE}">${esc(cfg.replyTo)}</a>` : ''}
        </td></tr>
      </table>
    </td></tr>
  </table>
</td></tr></table>
</body></html>`;
}

function confirmText(link, cfg) {
  return [
    'OZAKEN LETTER ／ 登録の確認',
    '',
    'あと1回だけ、押してください',
    '',
    'お申し込みを受け付けました。',
    '下のリンクを開いていただくと、登録が完了します。',
    '',
    link,
    '',
    '--------------------------------------------------',
    'これからお送りするもの',
    '',
    ...PROMISES.map(([title, body], i) => `${String(i + 1).padStart(2, '0')} ${title}\n   ${body}\n`),
    '--------------------------------------------------',
    '',
    'AIの新着を全部追うのは、もう無理です。だから追いません。',
    'その代わり、前提が動いたところだけを、なぜ動いたのかまで書いて送ります。',
    `── ${cfg.senderName}`,
    '',
    'お心当たりがない場合は、このメールを破棄してください。',
    'リンクを開かないかぎり、配信は始まりません。',
    '',
    `発行：${cfg.senderName}`,
    `所在地：${cfg.senderAddress}`,
    cfg.replyTo ? `お問い合わせ：${cfg.replyTo}` : '',
  ].filter(l => l !== '').join('\n');
}
