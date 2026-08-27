// メール本文の組み立てと、Resend への受け渡し。
//
// メールのHTMLは、Webページと同じようには書けない。
// Outlook や一部の携帯キャリアは <style> ごと捨てるので、
// **table で組んで、CSSは全部 style 属性に直書き**する。
// 資料アーカイブの weekly ページをそのまま貼っても、まず崩れる。

import { esc } from './page.js';
import { unsubscribeUrl, normalize } from './token.js';

const NAVY = '#1f3864';
const AZURE = '#2e5496';
const INK = '#1a1a2e';
const MUTED = '#6b7a99';
const PAPER = '#f8f7f4';
const LINE = '#d8e4f0';
const FONT = "-apple-system,BlinkMacSystemFont,'Hiragino Sans','Hiragino Kaku Gothic ProN','Yu Gothic',Meiryo,sans-serif";

// なぜこのメールが届いているのか。特定電子メール法の表示義務まわりで、
// 「勝手に送ってきた」と受け取られないための一文。取得の経路で言い方を変える。
function reasonLine(source) {
  return source === 'meishi'
    ? 'このメールは、名刺交換などでご連絡先をいただいた方にお送りしています。'
    : 'このメールは、ご本人のお申し込みにもとづいてお送りしています。';
}

export function config(env) {
  const missing = [];
  const need = (k) => {
    const v = env[k];
    if (!v) missing.push(k);
    return v;
  };
  const c = {
    site: env.NEWSLETTER_SITE || 'https://content.ozaken.ai',
    secret: need('NEWSLETTER_SECRET'),
    apiKey: need('RESEND_API_KEY'),
    from: need('NEWSLETTER_FROM'),                      // 例: 小澤健祐（おざけん） <weekly@ozaken.ai>
    senderName: env.NEWSLETTER_SENDER_NAME || '小澤健祐（おざけん）',
    senderAddress: need('NEWSLETTER_SENDER_ADDRESS'),   // 表示義務。住所を省くと違反になる
    replyTo: env.NEWSLETTER_REPLY_TO || null,
    unsubMailto: env.NEWSLETTER_UNSUB_MAILTO || null,
    sendMode: env.NEWSLETTER_SEND_MODE || 'batch',      // batch | single
    missing,
  };
  return c;
}

// ── 本文 ─────────────────────────────────────────────

export function buildEmail({ issue, subscriber, unsubUrl, cfg }) {
  const name = (subscriber.name || '').trim();
  const greeting = name ? `${esc(name)} 様` : 'いつもありがとうございます';
  const items = Array.isArray(issue.items) ? issue.items : [];

  const itemsHtml = items.map((it, i) => `
    <tr><td style="padding:0 0 26px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr><td style="padding:0 0 6px;font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE}">
          ${String(i + 1).padStart(2, '0')}${it.kicker ? `　${esc(it.kicker)}` : ''}
        </td></tr>
        <tr><td style="padding:0 0 8px;font:700 17px/1.55 ${FONT};color:${INK}">
          ${esc(it.title)}
        </td></tr>
        <tr><td style="font:400 15px/1.85 ${FONT};color:${INK}">
          ${esc(it.body || '').replace(/\n/g, '<br>')}
        </td></tr>
        ${it.link ? `<tr><td style="padding:8px 0 0;font:400 14px ${FONT}">
          <a href="${esc(it.link)}" style="color:${AZURE}">${esc(it.linkLabel || '元の記事を読む')} →</a>
        </td></tr>` : ''}
      </table>
    </td></tr>`).join('');

  // 全文は暗号化した週次ページにある。鍵は購読者だけに渡す。
  const ctaHtml = issue.url ? `
    <tr><td style="padding:6px 0 30px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="background:${PAPER};border:1px solid ${LINE};border-radius:4px">
        <tr><td style="padding:24px 26px">
          <div style="font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE};padding-bottom:8px">FULL ISSUE</div>
          <div style="font:400 15px/1.8 ${FONT};color:${INK};padding-bottom:16px">
            図版つきの全文は、こちらで読めます。
          </div>
          <a href="${esc(issue.url)}"
             style="display:inline-block;background:${NAVY};color:#fff;text-decoration:none;
                    border-radius:3px;padding:13px 26px;font:700 15px ${FONT}">今週の全文を読む</a>
          ${issue.passphrase ? `<div style="padding-top:16px;font:400 13px/1.8 ${FONT};color:${MUTED}">
            ひらくときの合言葉：<span style="font:700 14px ${FONT};color:${NAVY};background:#eef1f6;
            border-radius:3px;padding:2px 8px">${esc(issue.passphrase)}</span><br>
            購読いただいている方にだけお渡ししています。
          </div>` : ''}
        </td></tr>
      </table>
    </td></tr>` : '';

  const html = `<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(issue.subject)}</title></head>
<body style="margin:0;padding:0;background:${PAPER};-webkit-text-size-adjust:100%">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(issue.preheader || '')}</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:${PAPER}">
<tr><td align="center" style="padding:28px 12px">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
         style="width:600px;max-width:100%;background:#fff;border:1px solid ${LINE};border-radius:4px">

    <tr><td style="background:${NAVY};padding:26px 34px">
      <div style="font:700 11px ${FONT};letter-spacing:.16em;color:#9fc6f5">OZAKEN WEEKLY</div>
      <div style="padding-top:6px;font:400 13px ${FONT};color:rgba(255,255,255,.72)">${esc(issue.id)}</div>
    </td></tr>

    <tr><td style="padding:34px 34px 0">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr><td style="padding:0 0 4px;width:40px">
          <div style="width:40px;height:2px;background:${AZURE};font-size:0;line-height:0">&nbsp;</div>
        </td></tr>
        <tr><td style="padding:18px 0 14px;font:700 23px/1.5 ${FONT};color:${INK}">
          ${esc(issue.subject)}
        </td></tr>
        <tr><td style="padding:0 0 22px;font:400 14px/1.8 ${FONT};color:${MUTED}">
          ${greeting}
        </td></tr>
        ${issue.lede ? `<tr><td style="padding:0 0 28px;font:400 15px/1.9 ${FONT};color:${INK}">
          ${esc(issue.lede).replace(/\n/g, '<br>')}
        </td></tr>` : ''}
        ${itemsHtml}
        ${ctaHtml}
        ${issue.closing ? `<tr><td style="padding:0 0 30px;font:400 15px/1.9 ${FONT};color:${INK}">
          ${esc(issue.closing).replace(/\n/g, '<br>')}
        </td></tr>` : ''}
      </table>
    </td></tr>

    <tr><td style="padding:0 34px 30px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="border-top:1px solid ${LINE}">
        <tr><td style="padding:20px 0 0;font:400 12px/1.9 ${FONT};color:${MUTED}">
          ${esc(reasonLine(subscriber.source))}<br>
          今後お送りしないほうがよろしければ、こちらから止められます（すぐに反映されます）。<br>
          <a href="${esc(unsubUrl)}" style="color:${AZURE}">配信を停止する</a>
          <br><br>
          発行：${esc(cfg.senderName)}<br>
          所在地：${esc(cfg.senderAddress)}<br>
          ${cfg.replyTo ? `お問い合わせ：<a href="mailto:${esc(cfg.replyTo)}" style="color:${AZURE}">${esc(cfg.replyTo)}</a>` : ''}
        </td></tr>
      </table>
    </td></tr>
  </table>
</td></tr></table>
</body></html>`;

  // 文字だけの版。付けないと迷惑メール判定が厳しくなるし、
  // 携帯キャリアや読み上げ環境ではこちらが読まれる。
  const text = [
    `OZAKEN WEEKLY / ${issue.id}`,
    '',
    issue.subject,
    '',
    name ? `${name} 様` : 'いつもありがとうございます',
    '',
    issue.lede || '',
    '',
    ...items.map((it, i) => [
      `${String(i + 1).padStart(2, '0')}${it.kicker ? ` ${it.kicker}` : ''}`,
      it.title,
      it.body || '',
      it.link ? `→ ${it.link}` : '',
      '',
    ].filter(Boolean).join('\n')),
    issue.url ? `全文：${issue.url}` : '',
    issue.passphrase ? `合言葉：${issue.passphrase}（購読者限定）` : '',
    '',
    issue.closing || '',
    '',
    '--------------------------------------------------',
    reasonLine(subscriber.source),
    `配信停止：${unsubUrl}`,
    '',
    `発行：${cfg.senderName}`,
    `所在地：${cfg.senderAddress}`,
    cfg.replyTo ? `お問い合わせ：${cfg.replyTo}` : '',
  ].filter(l => l !== undefined).join('\n').replace(/\n{3,}/g, '\n\n');

  return { html, text };
}

// ── Resend ───────────────────────────────────────────

// Gmail・Yahoo の一括送信者要件（2024年2月〜）で必須になった2本。
// この2つが揃うと、件名の横に「配信停止」ボタンが出る。
// List-Unsubscribe-Post があると、Gmail は GET ではなく POST を投げてくる。
function listHeaders(unsubUrl, mailto) {
  const value = mailto ? `<${unsubUrl}>, <mailto:${mailto}>` : `<${unsubUrl}>`;
  return {
    'List-Unsubscribe': value,
    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
  };
}

export async function buildMessage({ issue, subscriber, cfg }) {
  const unsubUrl = await unsubscribeUrl(cfg.site, cfg.secret, subscriber.email);
  const { html, text } = buildEmail({ issue, subscriber, unsubUrl, cfg });
  const msg = {
    from: cfg.from,
    to: [normalize(subscriber.email)],
    subject: issue.subject,
    html,
    text,
    headers: listHeaders(unsubUrl, cfg.unsubMailto),
  };
  if (cfg.replyTo) msg.reply_to = cfg.replyTo;
  return msg;
}

async function call(apiKey, path, body) {
  const res = await fetch(`https://api.resend.com${path}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { /* Resendが素のテキストを返すことがある */ }
  return { ok: res.ok, status: res.status, data, text };
}

// 100通ずつ束ねて渡す。1通ずつだと Resend の既定レート（2 req/秒）に張り付いて、
// 1000人に送るのに8分以上かかる ── Workers の実行時間に収まらない。
//
// batch で headers が落ちる構成に当たったら NEWSLETTER_SEND_MODE=single にする。
// そのときも本文フッターの配信停止リンクは常に入っているので、法令上の穴は空かない。
export async function sendMessages(cfg, messages) {
  if (!messages.length) return [];
  if (cfg.sendMode === 'single') {
    const out = [];
    for (const m of messages) {
      const r = await call(cfg.apiKey, '/emails', m);
      out.push(toResult(m, r.ok ? r.data : null, r));
    }
    return out;
  }

  const out = [];
  for (let i = 0; i < messages.length; i += 100) {
    const chunk = messages.slice(i, i + 100);
    const r = await call(cfg.apiKey, '/emails/batch', chunk);
    const ids = r.ok && r.data && Array.isArray(r.data.data) ? r.data.data : [];
    chunk.forEach((m, j) => out.push(toResult(m, ids[j], r)));
  }
  return out;
}

function toResult(msg, idObj, r) {
  const email = msg.to[0];
  if (r.ok) return { email, status: 'sent', providerId: idObj && idObj.id ? idObj.id : null };
  return { email, status: 'failed', error: `${r.status} ${(r.text || '').slice(0, 300)}` };
}
