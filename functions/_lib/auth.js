// 管理者トークンの照合。/api/send と /api/import が使う。
//
// **「合っていない」で終わらせない。** サーバー側に鍵が入っていないのか、
// 送った鍵が違うのかで、直す場所がまったく変わる。切り分けて返す。
//
// 前後の空白は落としてから比べる。Cloudflare の変数欄に貼るとき、
// 末尾に改行が紛れ込むことがある。見た目では絶対に気づけない。

export function checkAdmin(request, env) {
  const expected = (env.NEWSLETTER_ADMIN_TOKEN || '').trim();
  if (!expected) {
    return {
      ok: false, status: 503,
      error: 'サーバー側に NEWSLETTER_ADMIN_TOKEN が設定されていません。'
        + 'Cloudflare Pages の Settings → Variables and Secrets（Production）に入れて、'
        + 'そのあと一度デプロイし直してください（変数は、追加したあとのデプロイから効きます）。',
    };
  }

  const raw = request.headers.get('Authorization') || '';
  const given = raw.replace(/^Bearer\s+/i, '').trim();
  if (!given) {
    return { ok: false, status: 401, error: 'トークンが送られていません。' };
  }

  if (given.length !== expected.length || !sameString(given, expected)) {
    return {
      ok: false, status: 401,
      error: `トークンが一致しません（送られた長さ ${given.length} 文字 / `
        + `設定されている長さ ${expected.length} 文字）。`
        + (given.length !== expected.length
          ? '長さが違います。貼り間違いか、ブラウザの自動入力で別の値が入っています。'
          : '長さは合っているので、中身のどこかが違います。'),
    };
  }
  return { ok: true };
}

// 早期returnで抜けると、比較にかかった時間から正解の桁数が漏れる。
function sameString(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
