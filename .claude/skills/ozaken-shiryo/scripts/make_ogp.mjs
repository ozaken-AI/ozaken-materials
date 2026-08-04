/* SNSの共有カード（1200×630）を資料ごとに書き出す。JPEGなのは、
 * 地のグラデーションがPNGだと1枚500KBになり、78枚で37MBに膨れたため。
 *
 *   node make_ogp.mjs <manifest.json> <出力先> <書体フォルダ>
 *
 * 地の色・格子・星座は資料の表紙と同じ。題は明朝、概要はゴシックで、
 * 資料を開く前から「何の話か」が伝わるようにしている。
 * 書体はこの環境に入っていないので、file:// で読ませる。
 * about:blank に setContent すると file:// の書体を拒まれるため、
 * HTMLをいったん書体と同じ場所に書き出してから開く。 */
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const [, , manifestPath, outDir, fontDir] = process.argv;
const rows = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
fs.mkdirSync(outDir, { recursive: true });

const esc = (s) => s.replace(/[&<>"]/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const page_html = (row) => `<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<style>
@font-face{font-family:'OZ Mincho';src:url('ShipporiMinchoB1-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Medium.ttf');font-weight:500}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ En';src:url('HankenGrotesk.ttf')}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;position:relative;
  background:
    radial-gradient(ellipse 60% 46% at 50% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
    radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
    radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
    linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
  color:#fff;font-family:'OZ Gothic',sans-serif}
.tex{position:absolute;inset:0;opacity:.13}
.bar{position:absolute;left:0;top:0;bottom:0;width:10px;background:#e23744}
.wrap{position:absolute;inset:0;padding:70px 86px 156px 96px;display:flex;
  flex-direction:column;justify-content:center}
.eyebrow{align-self:flex-start;font-family:'OZ En',sans-serif;font-size:19px;font-weight:700;
  letter-spacing:.18em;background:rgba(255,255,255,.15);color:#fff;
  padding:7px 16px;border-radius:4px;margin-bottom:30px}
h1{font-family:'OZ Mincho',serif;font-weight:700;line-height:1.42;
  letter-spacing:.01em;max-height:250px;overflow:hidden}
.desc{margin-top:26px;font-size:23px;line-height:1.85;color:rgba(216,228,240,.76);
  max-height:88px;overflow:hidden}
.foot{position:absolute;left:96px;right:86px;bottom:54px;display:flex;
  align-items:center;justify-content:space-between;
  font-size:19px;color:rgba(216,228,240,.62)}
.foot b{color:#fff;font-weight:700;font-size:21px}
.foot .u{font-family:'OZ En',sans-serif;letter-spacing:.06em;font-size:17px}
.rule{position:absolute;left:96px;right:86px;bottom:104px;height:1px;
  background:rgba(216,228,240,.22)}
</style></head><body>
<svg class="tex" viewBox="0 0 1200 630" preserveAspectRatio="none">
  <defs><pattern id="g" width="46" height="46" patternUnits="userSpaceOnUse">
    <path d="M46 0H0V46" fill="none" stroke="#fff" stroke-width="0.7"/></pattern></defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <circle cx="240" cy="120" r="4" fill="#fff"/><circle cx="560" cy="290" r="4" fill="#fff"/>
  <circle cx="880" cy="150" r="4" fill="#fff"/><circle cx="1060" cy="420" r="4" fill="#fff"/>
  <path d="M240 120L560 290L880 150L1060 420" stroke="#fff" stroke-width="1" fill="none"/>
</svg>
<div class="bar"></div>
<div class="wrap">
  <span class="eyebrow">${esc(row.cat)}</span>
  <h1 id="t">${esc(row.title)}</h1>
  ${row.card ? `<p class="desc">${esc(row.card)}</p>` : ''}
</div>
<div class="rule"></div>
<div class="foot"><span><b>おざけん</b>　小澤健祐</span>
  <span class="u">ozaken-ai.github.io/ozaken-materials</span></div>
</body></html>`;

/* 題は長さがまちまちなので、枠に収まるまで少しずつ小さくする。
 * 文字数で決め打ちにすると、英字まじりの題で行数を読み違える */
const fit = () => {
  const h = document.getElementById('t');
  let s = 64;
  h.style.fontSize = s + 'px';
  while (s > 34 && h.scrollHeight > 250) { s -= 2; h.style.fontSize = s + 'px'; }
};

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--allow-file-access-from-files'],
});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 },
  deviceScaleFactor: 1 });

const tmp = path.join(fontDir, '_card.html');
for (const row of rows) {
  fs.writeFileSync(tmp, page_html(row));
  await page.goto('file://' + tmp);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(fit);
  await page.screenshot({ path: path.join(outDir, row.file),
    type: 'jpeg', quality: 88 });
}
fs.unlinkSync(tmp);
await browser.close();
console.log(rows.length + '枚');
