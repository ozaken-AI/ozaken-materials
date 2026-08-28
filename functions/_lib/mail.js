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
//
// **心当たりのない人ほど、ここしか読まない。** 経緯が思い出せる言い方にする。
// 曖昧にすると、配信停止ではなく迷惑メール報告に向かう。
const REASONS = {
  meishi:   'このメールは、名刺交換などでご連絡先をいただいた方にお送りしています。',
  download: 'このメールは、資料をダウンロードいただいた際にご連絡先をいただいた方にお送りしています。',
  event:    'このメールは、イベント・講演にご参加いただいた際にご連絡先をいただいた方にお送りしています。',
};

function reasonLine(source) {
  return REASONS[source] || 'このメールは、ご本人のお申し込みにもとづいてお送りしています。';
}

// 購読者に約束していること。subscribe.html と index.html のゲートにも同じ内容がある。
// **片方だけ変えない。** newsletter/selftest.mjs が数字の一致を見張っている。
export const PROMISES = [
  ['前提が動いた論点だけを、数本',
   'ニュースの要約は送りません。「何が変わったから、この発表は効くのか」を書きます。'],
  ['図版つきの全文へのご案内',
   'メールにはあらましを、詳しくは資料アーカイブの該当ページに。読むための合言葉は、購読いただいている方だけにお渡ししています。'],
  ['不定期。月に1〜3通ほど',
   '書くことがあるときだけお送りします。それ以上は送りません。営業のご連絡に転用することもありません。'],
];

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
    from: need('NEWSLETTER_FROM'),                      // 例: 小澤健祐（おざけん） <ozaken@news.ozaken.ai>
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
                    border-radius:3px;padding:13px 26px;font:700 15px ${FONT}">全文を読む</a>
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
      <div style="font:700 11px ${FONT};letter-spacing:.16em;color:#9fc6f5">OZAKEN LETTER</div>
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
    `OZAKEN LETTER / ${issue.id}`,
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


// ── 資料ダウンロードのお礼 ───────────────────────────
//
// これが多くの人にとって**最初の1通**になる。ここで「誰から来たのか」が
// 伝わらないと、次に届くお便りが「知らない差出人」になって迷惑メール報告に向かう。
//
// だから、名乗りと差出人アドレスをはっきり出し、
// これから何が届くのかを先に伝えておく。
export async function buildWelcome({ subscriber, asset, cfg }) {
  const unsubUrl = await unsubscribeUrl(cfg.site, cfg.secret, subscriber.email);
  const name = (subscriber.name || '').trim();
  const greeting = name ? `${esc(name)} 様` : 'こんにちは';

  const promiseRows = PROMISES.map(([title], i) => `
    <tr><td style="padding:0 0 9px;font:400 14px/1.7 ${FONT};color:${INK}">
      <span style="font:700 11px ${FONT};letter-spacing:.1em;color:${AZURE}">${String(i + 1).padStart(2, '0')}</span>
      &nbsp;&nbsp;${title}
    </td></tr>`).join('');

  const html = `<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:${PAPER};-webkit-text-size-adjust:100%">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">AI活用が進むかどうかは、技術力では決まりません。</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:${PAPER}">
<tr><td align="center" style="padding:28px 12px">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
         style="width:600px;max-width:100%;background:#fff;border:1px solid ${LINE};border-radius:4px">

    <tr><td style="background:${NAVY};padding:26px 34px">
      <div style="font:700 11px ${FONT};letter-spacing:.16em;color:#9fc6f5">OZAKEN LETTER</div>
      <div style="padding-top:6px;font:400 13px ${FONT};color:rgba(255,255,255,.72)">資料をご覧いただきありがとうございます</div>
    </td></tr>

    <tr><td style="padding:36px 34px 0">
      <div style="width:40px;height:2px;background:${AZURE};font-size:0;line-height:0">&nbsp;</div>
      <div style="padding:18px 0 18px;font:400 14px ${FONT};color:${MUTED}">${greeting}</div>
      <div style="font:400 15px/1.95 ${FONT};color:${INK};padding-bottom:24px">
        この度は資料を手に取っていただき、ありがとうございます。<br>
        小澤健祐（おざけん）です。<br><br>
        ひとつだけ、先にお伝えさせてください。
      </div>
    </td></tr>

    <tr><td style="padding:0 34px 26px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td width="3" style="width:3px;background:${AZURE};font-size:0;line-height:0">&nbsp;</td>
          <td style="padding:4px 0 4px 20px;font:700 19px/1.7 ${FONT};color:${NAVY}">
            AI活用が進むかどうかは、<br>技術力では決まりません。
          </td>
        </tr>
      </table>
    </td></tr>

    <tr><td style="padding:0 34px">
      <div style="font:400 15px/1.95 ${FONT};color:${INK}">
        これまで1,500本以上のAI関連記事を書き、年間300回以上の登壇で、
        たくさんの現場を見てきました。進んでいる会社と、止まっている会社。
        その差は、いつも同じところにありました。<br><br>
        完璧な計画を待たずに、<b>80点で動かして、現場で磨く。</b><br>
        その思い切りがあるかどうか。本当に、それだけです。<br><br>
        今回の資料も、売るためではなく、一人でも多くの方が最初の一歩を
        踏み出せるように、と思ってつくりました。
        もしひとつでも現場で使えるものがあれば、これ以上うれしいことはありません。
      </div>
    </td></tr>

    <tr><td style="padding:26px 34px 0">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="background:${PAPER};border:1px solid ${LINE};border-radius:4px">
        <tr><td style="padding:22px 24px;font:400 14.5px/1.9 ${FONT};color:${INK}">
          読んでいただいて「自社の場合はどうか」「ここが難しい」というところがあれば、
          このメールにそのままご返信ください。<br>
          自動でお送りしているメールですが、<b>ご返信は私本人に届きます。</b>
        </td></tr>
      </table>
    </td></tr>

    <tr><td style="padding:24px 34px 0;font:400 14px ${FONT};color:${MUTED}">
      ── 小澤健祐（おざけん）
    </td></tr>

    <tr><td style="padding:30px 34px 0">
      <div style="font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE};padding-bottom:10px">ARCHIVE</div>
      <div style="font:400 14.5px/1.85 ${FONT};color:${INK};padding-bottom:16px">
        ほかの資料も、まとめて置いてあります。AIを組織で使えるようにするまでの問いを、
        知る → 選ぶ → 動かす の順に並べました。
      </div>
      <a href="${esc(cfg.site)}/" style="display:inline-block;background:${NAVY};color:#fff;
         text-decoration:none;border-radius:3px;padding:13px 26px;font:700 15px ${FONT}">資料アーカイブを見る</a>
    </td></tr>

    <tr><td style="padding:28px 34px 0">
      <div style="font:400 13px/1.9 ${FONT};color:${MUTED}">
        ご必要な場面があれば、<b style="color:${INK}">講演・研修</b>（経営層向けから現場の実践型ワークショップまで）、
        <b style="color:${INK}">顧問・アドバイザー</b>（AI戦略の伴走）、
        <b style="color:${INK}">AX支援</b>（診断から人材育成、定着まで）といった形でもご一緒しています。
        もちろん、まずは情報収集だけという段階でも、まったく問題ありません。
      </div>
    </td></tr>

    <tr><td style="padding:28px 34px 0">
      <div style="font:700 11px ${FONT};letter-spacing:.12em;color:${AZURE};padding-bottom:12px">
        WHAT COMES NEXT ／ これからお送りするもの
      </div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        ${promiseRows}
      </table>
      <div style="padding:10px 0 0;font:400 13px/1.85 ${FONT};color:${MUTED}">
        差出人はこのアドレス（<span style="color:${NAVY}">${esc(fromAddress(cfg.from))}</span>）です。
        <b>連絡先に追加しておいていただけると、迷惑メールに入らず確実に届きます。</b>
      </div>
    </td></tr>

    <tr><td style="padding:30px 34px 32px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
             style="border-top:1px solid ${LINE}">
        <tr><td style="padding:20px 0 0;font:400 12px/1.9 ${FONT};color:${MUTED}">
          ${esc(REASONS.download)}<br>
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

  const text = [
    'OZAKEN LETTER ／ 資料をご覧いただきありがとうございます',
    '',
    name ? `${name} 様` : 'こんにちは',
    '',
    'この度は資料を手に取っていただき、ありがとうございます。',
    '小澤健祐（おざけん）です。',
    '',
    'ひとつだけ、先にお伝えさせてください。',
    '',
    '　AI活用が進むかどうかは、技術力では決まりません。',
    '',
    'これまで1,500本以上のAI関連記事を書き、年間300回以上の登壇で、',
    'たくさんの現場を見てきました。進んでいる会社と、止まっている会社。',
    'その差は、いつも同じところにありました。',
    '',
    '完璧な計画を待たずに、80点で動かして、現場で磨く。',
    'その思い切りがあるかどうか。本当に、それだけです。',
    '',
    '今回の資料も、売るためではなく、一人でも多くの方が最初の一歩を',
    '踏み出せるように、と思ってつくりました。',
    'もしひとつでも現場で使えるものがあれば、これ以上うれしいことはありません。',
    '',
    '読んでいただいて「自社の場合はどうか」「ここが難しい」というところがあれば、',
    'このメールにそのままご返信ください。',
    '自動でお送りしているメールですが、ご返信は私本人に届きます。',
    '',
    '── 小澤健祐（おざけん）',
    '',
    '--------------------------------------------------',
    `ほかの資料もまとめて置いてあります： ${cfg.site}/`,
    '',
    'ご必要な場面があれば、講演・研修、顧問・アドバイザー、AX支援といった',
    '形でもご一緒しています。まずは情報収集だけという段階でも問題ありません。',
    '--------------------------------------------------',
    'これからお送りするもの',
    '',
    ...PROMISES.map(([title], i) => `${String(i + 1).padStart(2, '0')} ${title}`),
    '',
    `差出人はこのアドレス（${fromAddress(cfg.from)}）です。`,
    '連絡先に追加しておいていただけると、迷惑メールに入らず確実に届きます。',
    '--------------------------------------------------',
    '',
    REASONS.download,
    `配信停止：${unsubUrl}`,
    '',
    `発行：${cfg.senderName}`,
    `所在地：${cfg.senderAddress}`,
    cfg.replyTo ? `お問い合わせ：${cfg.replyTo}` : '',
  ].filter(l => l !== '').join('\n');

  const msg = {
    from: cfg.from,
    to: [normalize(subscriber.email)],
    subject: '資料を手に取っていただき、ありがとうございます ─ 小澤健祐（おざけん）',
    html,
    text,
    headers: listHeaders(unsubUrl, cfg.unsubMailto),
  };
  if (cfg.replyTo) msg.reply_to = cfg.replyTo;
  return msg;
}

// "名前 <アドレス>" から、アドレスだけを取り出す。
// 本文で「この差出人を連絡先に追加してください」と言うのに使う。
function fromAddress(from) {
  const m = String(from || '').match(/<([^>]+)>/);
  return m ? m[1] : String(from || '');
}
