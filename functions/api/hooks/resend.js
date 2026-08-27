// Resend からの通知の受け口。/api/hooks/resend（POST）
//
// 宛先不明（バウンス）と迷惑メール報告を放置すると、
// 送信ドメインの評判が落ちて、まともな相手にも届かなくなる。
// Gmail の一括送信者要件は苦情率 0.3% 未満を求めているので、
// ここで自動的に名簿から外す。
//
// Resend の webhook は Svix 形式で署名されている。検証しないと、
// URLを知った誰でも「あの人はバウンスした」と送り込めてしまう。

import { json } from '../../_lib/page.js';
import { requireDb, stopSending, logEvent, emailByProviderId, HttpError } from '../../_lib/db.js';
import { normalize } from '../../_lib/token.js';

const TOLERANCE_SEC = 5 * 60;
const enc = new TextEncoder();

function b64ToBytes(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function bytesToB64(buf) {
  const bytes = new Uint8Array(buf);
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s);
}

function sameString(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

async function verifySvix(secret, headers, payload) {
  const id = headers.get('svix-id') || headers.get('webhook-id');
  const ts = headers.get('svix-timestamp') || headers.get('webhook-timestamp');
  const sigHeader = headers.get('svix-signature') || headers.get('webhook-signature');
  if (!id || !ts || !sigHeader) return false;

  // 古い通知の使い回しを弾く。
  const age = Math.abs(Math.floor(Date.now() / 1000) - Number(ts));
  if (!Number.isFinite(age) || age > TOLERANCE_SEC) return false;

  const raw = secret.startsWith('whsec_') ? secret.slice(6) : secret;
  const key = await crypto.subtle.importKey(
    'raw', b64ToBytes(raw), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const expected = bytesToB64(await crypto.subtle.sign('HMAC', key, enc.encode(`${id}.${ts}.${payload}`)));

  // 鍵の入れ替え中は複数の署名が並ぶので、どれかが合えばよい。
  return sigHeader.split(' ').some((part) => {
    const [version, sig] = part.split(',');
    return version === 'v1' && sig && sameString(sig, expected);
  });
}

export async function onRequestPost({ request, env }) {
  const secret = env.RESEND_WEBHOOK_SECRET;
  if (!secret) return json({ ok: false, error: 'RESEND_WEBHOOK_SECRET が未設定です。' }, 503);

  const payload = await request.text();
  if (!(await verifySvix(secret, request.headers, payload))) {
    return json({ ok: false, error: 'signature mismatch' }, 401);
  }

  let event;
  try {
    event = JSON.parse(payload);
  } catch {
    return json({ ok: false, error: 'bad payload' }, 400);
  }

  try {
    const db = requireDb(env);
    const data = event.data || {};
    let email = Array.isArray(data.to) ? normalize(data.to[0]) : normalize(data.to || '');
    if (!email && data.email_id) email = await emailByProviderId(db, data.email_id);
    if (!email) return json({ ok: true, skipped: 'no recipient' });

    switch (event.type) {
      case 'email.bounced': {
        const kind = (data.bounce && data.bounce.type) || '';
        // 一時的な失敗（受信箱が満杯、相手サーバーの不調）で名簿から外すと、
        // 復旧したはずの相手を永久に失う。恒久的な失敗だけ外す。
        if (/permanent|hard/i.test(kind)) {
          await stopSending(db, email, 'bounced');
          await logEvent(db, email, 'bounce', `permanent: ${(data.bounce && data.bounce.message) || ''}`.slice(0, 300));
        } else {
          await logEvent(db, email, 'bounce', `transient: ${kind}`.slice(0, 300));
        }
        break;
      }
      case 'email.complained':
        // 迷惑メール報告。本人が明確に拒否している。二度と送らない。
        await stopSending(db, email, 'complained');
        await logEvent(db, email, 'complaint', 'spam report');
        break;
      default:
        return json({ ok: true, ignored: event.type });
    }

    if (data.email_id) {
      await db.prepare('UPDATE deliveries SET status = ? WHERE provider_id = ?')
        .bind(event.type === 'email.complained' ? 'complained' : 'bounced', data.email_id).run();
    }
    return json({ ok: true });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message }, status);
  }
}
