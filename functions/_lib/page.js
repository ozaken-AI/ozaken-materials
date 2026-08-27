// 配信停止や確認の結果を出す1枚もの。
// 資料アーカイブと同じ紺色基調（ozaken-web-style）に揃えてある。
// 外から見えるのはこの数枚だけなので、雛形を読み込まず、ここで完結させる。

const CSS = `
:root{
  --ink:#1a1a2e; --navy:#1f3864; --navy-deep:#141d35; --azure:#2e5496;
  --azure-pale:#d8e4f0; --paper:#f8f7f4; --white:#fff; --muted:#6b7a99;
  --red:#e23744;
  --font-ja-serif:'Shippori Mincho B1',serif;
  --font-ja-sans:'Zen Kaku Gothic New',sans-serif;
  --font-en:'Hanken Grotesk',sans-serif;
}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:32px 20px;background:var(--paper);color:var(--ink);
  font-family:var(--font-ja-sans);line-height:1.85;
  -webkit-font-smoothing:antialiased}
.card{width:100%;max-width:560px;background:var(--white);border:1px solid var(--azure-pale);
  border-radius:4px;padding:48px 40px;box-shadow:0 1px 3px rgba(31,56,100,.06)}
.rule{width:40px;height:2px;background:var(--azure);margin:0 0 22px}
.eyebrow{font-family:var(--font-en);font-weight:700;font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--azure);margin:0 0 10px}
h1{font-family:var(--font-ja-serif);font-weight:600;font-size:25px;line-height:1.5;
  margin:0 0 18px;letter-spacing:.01em}
p{margin:0 0 16px;font-size:15px}
p:last-child{margin-bottom:0}
.addr{font-family:var(--font-en);font-weight:600;font-size:14px;color:var(--navy);
  background:#eef1f6;border-radius:3px;padding:3px 8px;word-break:break-all}
.muted{color:var(--muted);font-size:13px;line-height:1.8}
.bad{color:var(--red)}
.act{margin:28px 0 0}
button,.btn{font-family:var(--font-ja-sans);font-weight:700;font-size:15px;
  display:inline-block;border:0;border-radius:3px;padding:14px 30px;cursor:pointer;
  background:var(--navy);color:var(--white);text-decoration:none}
button:hover,.btn:hover{background:var(--navy-deep)}
.foot{margin-top:32px;padding-top:20px;border-top:1px solid var(--azure-pale)}
a{color:var(--azure)}
@media(max-width:520px){.card{padding:34px 24px}h1{font-size:21px}}
`;

export function html({ title, eyebrow, heading, body, status = 200 }) {
  const doc = `<!DOCTYPE html><html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} | おざけん</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#1f3864">
<link rel="icon" type="image/png" sizes="32x32" href="/99_assets/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700&family=Shippori+Mincho+B1:wght@600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<style>${CSS}</style></head>
<body><main class="card">
<div class="rule"></div>
${eyebrow ? `<p class="eyebrow">${esc(eyebrow)}</p>` : ''}
<h1>${esc(heading)}</h1>
${body}
</main></body></html>`;
  return new Response(doc, {
    status,
    headers: {
      'Content-Type': 'text/html; charset=UTF-8',
      'Cache-Control': 'no-store',       // 個人のアドレスが載る画面なので、どこにも残さない
      'Referrer-Policy': 'no-referrer',  // 署名つきURLを外部サイトに漏らさない
      'X-Robots-Tag': 'noindex',
    },
  });
}

export function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=UTF-8', 'Cache-Control': 'no-store' },
  });
}

export function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// 署名が合わない・期限切れ・リンクが途中で切れた、をまとめて受ける画面。
// 「あなたのせいではない」と読める言い方にして、問い合わせ先を必ず添える。
export function badLink(reason = 'リンクが正しく読み取れませんでした。') {
  return html({
    status: 400,
    title: 'リンクを確認できませんでした',
    eyebrow: 'Newsletter',
    heading: 'リンクを確認できませんでした',
    body: `<p class="bad">${esc(reason)}</p>
<p>メールソフトがURLを途中で折り返してしまうと、この画面が出ることがあります。
お手数ですが、メール本文のリンクをもう一度、最後まで含めて開いてみてください。</p>
<div class="foot"><p class="muted">うまくいかないときは、配信元のメールにそのまま返信してください。
こちらで配信を止めます。</p></div>`,
  });
}
