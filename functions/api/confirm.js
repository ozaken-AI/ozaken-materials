// ダブルオプトインの確認。/api/confirm?e=<アドレス>&s=<署名>
// 確認メールのリンクを踏んだ人だけが、ここで active になる。

import { verify, normalize } from '../_lib/token.js';
import { html, esc, badLink } from '../_lib/page.js';
import { requireDb, markConfirmed, logEvent, getSubscriber, HttpError } from '../_lib/db.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const email = normalize(url.searchParams.get('e') || '');
  const sig = url.searchParams.get('s') || '';
  if (!email || !sig) return badLink('リンクに必要な情報が足りません。');
  if (!(await verify(env.NEWSLETTER_SECRET, 'confirm', email, sig))) {
    return badLink('このリンクの署名を確認できませんでした。');
  }

  try {
    const db = requireDb(env);
    const changed = await markConfirmed(db, email);
    if (changed) {
      await logEvent(db, email, 'confirm', 'double opt-in', request.headers.get('CF-Connecting-IP'));
    }
    const current = await getSubscriber(db, email);

    // 配信停止したあとに古い確認リンクを踏んでも、勝手に復活させない。
    if (current && current.status !== 'active') {
      return html({
        title: '登録は完了していません',
        eyebrow: 'Newsletter',
        heading: '登録は完了していません',
        body: `<p>このアドレスは現在、配信の対象外になっています。</p>
<p><span class="addr">${esc(email)}</span></p>
<div class="foot"><p class="muted">改めて受け取りたい場合は、
<a href="https://content.ozaken.ai/subscribe.html">お申し込みページ</a>からもう一度お手続きください。</p></div>`,
      });
    }

    // ここは「押し終えた直後」の画面。お礼だけで終わらせず、
    // (1) 届くまでの行き先 (2) 1通目が迷惑メールに落ちない手当て を渡す。
    // (2) は受け取る側にしかできない、いちばん効く到達率対策。
    return html({
      title: '登録が完了しました',
      eyebrow: 'OZAKEN LETTER',
      heading: changed ? '登録が完了しました' : 'すでに登録されています',
      body: `<p>ありがとうございます。次の号から、こちらのアドレスにお送りします。</p>
<p><span class="addr">${esc(email)}</span></p>
<p>届くまでのあいだは、資料アーカイブをどうぞ。AIを組織で使えるようにするまでの問いを、
<b>知る → 選ぶ → 動かす</b> の順に並べてあります。</p>
<p class="act"><a class="btn" href="https://content.ozaken.ai/">資料アーカイブを見る</a></p>
<div class="foot"><p class="muted">
<b>1通目が迷惑メールに入らないように、いま届いたメールの差出人を連絡先に追加しておいてください。</b>
これがいちばん確実です。<br><br>
配信は各回のメール下部から、いつでもすぐに停止できます。</p></div>`,
    });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return html({
      status,
      title: '処理できませんでした',
      eyebrow: 'Newsletter',
      heading: 'いま処理できませんでした',
      body: `<p class="bad">${esc(err.message || 'サーバー側の問題です。')}</p>
<p>しばらく置いてから、もう一度リンクを開いてみてください。</p>`,
    });
  }
}
