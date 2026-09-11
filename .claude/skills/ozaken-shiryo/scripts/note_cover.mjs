/* note の見出し画像（1280×670）を作る。
 *
 *   node note_cover.mjs --out cover.png --title "題" [--phrase "短いつかみ"]
 *                       [--fig figs/fig_03.png] [--cat AGENT] [--fonts /tmp/ozaken-ogp-fonts]
 *
 * note公式が「見出し画像の有無で、ビュー数やスキ数に数十パーセントの差がつく」と
 * 言っている。ここは記事の中で、いちばん費用対効果が分かっている場所。
 *
 * 地の色・格子・星座は資料の表紙と同じにしてある。note から資料に来た人が、
 * 同じ人の作ったものだと分かるように。
 *
 * **一覧に並ぶときは小さい。** note のタイムラインでは 320px 幅くらいまで縮む。
 * だから図版は「読ませる」のではなく「図がある記事だ」と伝えるために置き、
 * 文字は短いほど効く。長い題は自動で小さくなるが、小さくなるほど一覧では読めない。
 * `--phrase` に10〜20字のつかみを渡すのが、いちばん強い。
 */
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const flag = (name, def = '') => {
  const i = args.indexOf('--' + name);
  return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : def;
};

const out = flag('out');
const title = flag('title');
const phrase = flag('phrase');
const figPath = flag('fig');
const cat = flag('cat', 'OZAKEN ARCHIVE');
const fontDir = flag('fonts', '/tmp/ozaken-ogp-fonts');
const lead = phrase || title;

if (!out || !lead) {
  console.error('使い方: node note_cover.mjs --out cover.png --title "題" [--phrase "つかみ"] [--fig fig.png]');
  process.exit(1);
}
if (!fs.existsSync(path.join(fontDir, 'ShipporiMinchoB1-Bold.ttf'))) {
  console.error('書体がありません: ' + fontDir + '\n'
    + 'apply_ogp.py の fonts() が取ってくるのと同じもの。先にそれを一度走らせてください');
  process.exit(1);
}

// 図版は data: で埋める。file:// のパスを跨ぐと、環境によって読めないことがある
let figData = '';
if (figPath && fs.existsSync(figPath)) {
  figData = 'data:image/png;base64,' + fs.readFileSync(figPath).toString('base64');
} else if (figPath) {
  console.error('図版が見つかりません（文字だけで作ります）: ' + figPath);
}

const esc = (s) => s.replace(/[&<>"]/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// 図版があるときは文字を左に寄せ、無いときは中央に大きく置く
// 図版の板は right:72 / 幅452 なので、左端は x=756。
// 文字の枠をそこまで広げると、行末が板に触れて窮屈に見える。60px 手前で止める
const W = figData ? 600 : 1040;

const html = `<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<style>
@font-face{font-family:'OZ Mincho';src:url('ShipporiMinchoB1-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Medium.ttf');font-weight:500}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ En';src:url('HankenGrotesk.ttf')}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:670px;overflow:hidden;position:relative;
  background:
    radial-gradient(ellipse 60% 46% at 42% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
    radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
    radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
    linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
  color:#fff;font-family:'OZ Gothic',sans-serif}
.tex{position:absolute;inset:0;opacity:.13}
.bar{position:absolute;left:0;top:0;bottom:0;width:12px;background:#e23744}
.wrap{position:absolute;left:96px;top:0;bottom:0;width:${W}px;display:flex;
  flex-direction:column;justify-content:center;padding-bottom:58px}
.eyebrow{align-self:flex-start;font-family:'OZ En',sans-serif;font-size:20px;font-weight:700;
  letter-spacing:.18em;background:rgba(255,255,255,.15);color:#fff;
  padding:8px 17px;border-radius:4px;margin-bottom:32px}
h1{font-family:'OZ Mincho',serif;font-weight:700;line-height:1.36;
  letter-spacing:.01em;max-height:400px;overflow:hidden}
/* 図版は読ませない。「図のある記事だ」と伝わればいい。
   白geの板に載せて、紺地から浮かせる */
.fig{position:absolute;right:72px;top:50%;transform:translateY(-50%);
  width:452px;height:400px;border-radius:10px;background:#fff;
  box-shadow:0 24px 60px rgba(0,0,0,.42);padding:18px;
  display:flex;align-items:center;justify-content:center;overflow:hidden}
.fig img{max-width:100%;max-height:100%;object-fit:contain}
.foot{position:absolute;left:96px;bottom:48px;display:flex;align-items:center;gap:18px;
  font-size:20px;color:rgba(216,228,240,.66)}
.foot b{color:#fff;font-weight:700;font-size:22px}
.foot .u{font-family:'OZ En',sans-serif;letter-spacing:.06em;font-size:18px}
.rule{position:absolute;left:96px;width:${W}px;bottom:100px;height:1px;
  background:rgba(216,228,240,.22)}
</style></head><body>
<svg class="tex" viewBox="0 0 1280 670" preserveAspectRatio="none">
  <defs><pattern id="g" width="46" height="46" patternUnits="userSpaceOnUse">
    <path d="M46 0H0V46" fill="none" stroke="#fff" stroke-width="0.7"/></pattern></defs>
  <rect width="1280" height="670" fill="url(#g)"/>
  <circle cx="250" cy="118" r="4" fill="#fff"/><circle cx="580" cy="300" r="4" fill="#fff"/>
  <circle cx="900" cy="150" r="4" fill="#fff"/><circle cx="1120" cy="440" r="4" fill="#fff"/>
  <path d="M250 118L580 300L900 150L1120 440" stroke="#fff" stroke-width="1" fill="none"/>
</svg>
<div class="bar"></div>
<div class="wrap">
  <span class="eyebrow">${esc(cat)}</span>
  <h1 id="t">${esc(lead)}</h1>
</div>
${figData ? `<div class="fig"><img src="${figData}"></div>` : ''}
<div class="rule"></div>
<div class="foot"><span><b>おざけん</b>　小澤健祐</span>
  <span class="u">content.ozaken.ai</span></div>
</body></html>`;

/* 題の長さはまちまちなので、収まるまで少しずつ小さくする。
   **高さだけで見ると、最後の1文字が次の行に落ちたまま止まる。**
   「最初の90日で、どこまで進めるか」が3行になり、3行目が「か」だけになった。
   だから行数で詰める。2行に収まる中でいちばん大きい字を選び、
   それが小さくなりすぎるなら3行、4行と譲る。
   一覧では大きい字ほど目に入るので、字を小さくするより行を増やすほうがまし */
const fit = () => {
  const h = document.getElementById('t');
  const lines = (s) => {
    h.style.fontSize = s + 'px';
    return Math.round(h.scrollHeight / parseFloat(getComputedStyle(h).lineHeight));
  };
  for (let max = 2; max <= 4; max++) {
    for (let s = 88; s >= 44; s -= 2) if (lines(s) <= max) return s;
  }
  for (let s = 44; s > 26; s -= 2) { h.style.fontSize = s + 'px'; if (h.scrollHeight <= 400) return s; }
  return 26;
};

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--allow-file-access-from-files'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 670 },
  deviceScaleFactor: 1 });

// 書体と同じ場所に置いてから開く。about:blank に setContent すると file:// の書体が拒まれる
const tmp = path.join(fontDir, '_note_cover.html');
fs.writeFileSync(tmp, html);
await page.goto('file://' + tmp);
await page.evaluate(() => document.fonts.ready);
const size = await page.evaluate(fit);
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
await page.screenshot({ path: out });
fs.unlinkSync(tmp);
await browser.close();

console.log('見出し画像: %s（1280×670 / 文字 %dpx / 図版 %s）',
  out, size, figData ? 'あり' : 'なし');
if (size < 44) {
  console.log('⚠ 文字が %dpx まで小さくなっています。note の一覧では読めません。'
    + '--phrase に10〜20字のつかみを渡してください', size);
}
