// 配信停止。/unsubscribe?e=<アドレス>&s=<署名>
//
// GET  … 確認画面を出すだけ。**ここで止めてはいけない。**
//        企業のメールセキュリティ製品は、本文中のリンクを勝手に開いて安全確認する。
//        GETで即解除にすると、本人が押していないのに配信が止まる。
// POST … 実際に止める。人がボタンを押した場合と、
//        Gmail の「配信停止」ボタン（ワンクリック）の両方がここに来る。

import { verify, normalize } from './_lib/token.js';
import { html, esc, badLink } from './_lib/page.js';
import { requireDb, stopSending, logEvent, getSubscriber, HttpError } from './_lib/db.js';

function params(request) {
  const url = new URL(request.url);
  return {
    email: normalize(url.searchParams.get('e') || ''),
    sig: url.searchParams.get('s') || '',
  };
}

async function checkLink(env, request) {
  const { email, sig } = params(request);
  if (!email || !sig) return null;
  const ok = await verify(env.NEWSLETTER_SECRET, 'unsub', email, sig);
  return ok ? email : null;
}

export async function onRequestGet({ request, env }) {
  const email = await checkLink(env, request);
  if (!email) return badLink('このリンクの署名を確認できませんでした。');

  const url = new URL(request.url);
  return html({
    title: '配信を停止しますか',
    eyebrow: 'Newsletter',
    heading: '配信を停止しますか',
    body: `<p>次のアドレスへのメールマガジンを停止します。</p>
<p><span class="addr">${esc(email)}</span></p>
<form method="POST" action="${esc(url.pathname + url.search)}" class="act">
  <button type="submit">配信を停止する</button>
</form>
<div class="foot"><p class="muted">停止はすぐに反映されます。ご希望があればいつでも再開できますので、
その際はこのメールにご返信ください。</p></div>`,
  });
}

export async function onRequestPost({ request, env }) {
  const email = await checkLink(env, request);
  if (!email) return badLink('このリンクの署名を確認できませんでした。');

  // Gmail のワンクリックは、本文に List-Unsubscribe=One-Click を入れて POST してくる。
  // 相手はHTMLを読まないので、画面ではなく素の 200 を返す。
  let oneClick = false;
  try {
    const body = await request.text();
    oneClick = body.includes('List-Unsubscribe=One-Click');
  } catch { /* 本文なしのPOSTもある */ }

  try {
    const db = requireDb(env);
    const before = await getSubscriber(db, email);
    const changed = await stopSending(db, email, 'unsubscribed');
    // 記録は「止めた操作があった」ことに対して残す。二度押しの分も残す。
    await logEvent(db, email, 'unsubscribe',
      oneClick ? 'one-click (mail client)' : 'confirmation page',
      request.headers.get('CF-Connecting-IP'));

    if (oneClick) return new Response('unsubscribed', { status: 200 });

    const already = !changed && before && before.status !== 'active' && before.status !== 'pending';
    return html({
      title: '配信を停止しました',
      eyebrow: 'Newsletter',
      heading: already ? 'すでに停止しています' : '配信を停止しました',
      body: `<p>次のアドレスへのメールマガジンは、${already ? 'すでに停止済みです' : '今後お送りしません'}。</p>
<p><span class="addr">${esc(email)}</span></p>
<div class="foot"><p class="muted">これまでお読みいただき、ありがとうございました。<br>
資料アーカイブは引き続き <a href="https://content.ozaken.ai/">content.ozaken.ai</a> でご覧いただけます。</p></div>`,
    });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    if (oneClick) return new Response('error', { status });
    return html({
      status,
      title: '停止できませんでした',
      eyebrow: 'Newsletter',
      heading: 'いま停止の処理ができませんでした',
      body: `<p class="bad">${esc(err.message || 'サーバー側の問題です。')}</p>
<p>お手数ですが、配信元のメールにそのままご返信ください。こちらで確実に止めます。</p>`,
    });
  }
}
