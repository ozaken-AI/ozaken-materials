// 配信停止リンクに載せる署名。
//
// メールアドレスだけを ?e= で渡すと、他人のアドレスを打ち込んで
// 勝手に解除できてしまう。HMAC-SHA256 の署名を添えて、
// こちらが発行したリンクだけを受け付ける。
//
// 鍵は環境変数 NEWSLETTER_SECRET（32文字以上のランダム文字列）。

const enc = new TextEncoder();

function b64url(buf) {
  const bytes = new Uint8Array(buf);
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmacKey(secret) {
  return crypto.subtle.importKey(
    'raw', enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false, ['sign'],
  );
}

// purpose を混ぜているので、配信停止用の署名を確認用に使い回せない。
export async function sign(secret, purpose, email) {
  const key = await hmacKey(secret);
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(`${purpose}:${normalize(email)}`));
  return b64url(sig);
}

// 早期returnで抜けると、比較にかかった時間から正解の桁数が漏れる。
// 長さを先に見て、あとは全桁を必ず舐める。
function sameString(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function verify(secret, purpose, email, given) {
  if (!secret || !email || !given) return false;
  return sameString(await sign(secret, purpose, email), given);
}

// 名簿の突き合わせは、すべてこれを通した形で行う。
// 大文字・前後の空白・全角空白が混ざった名刺CSVを何度も見ているので、ここで潰す。
export function normalize(email) {
  return String(email || '').trim().replace(/^[\s　]+|[\s　]+$/g, '').toLowerCase();
}

// ざっくりした形の検査。RFC完全準拠は狙わない（弾きすぎる方が害が大きい）。
export function looksLikeEmail(email) {
  return /^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(email);
}

export async function unsubscribeUrl(site, secret, email) {
  const sig = await sign(secret, 'unsub', email);
  return `${site}/unsubscribe?e=${encodeURIComponent(normalize(email))}&s=${sig}`;
}

export async function confirmUrl(site, secret, email) {
  const sig = await sign(secret, 'confirm', email);
  return `${site}/api/confirm?e=${encodeURIComponent(normalize(email))}&s=${sig}`;
}
