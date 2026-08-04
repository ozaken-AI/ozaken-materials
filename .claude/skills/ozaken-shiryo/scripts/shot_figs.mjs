// 資料の図版を1点ずつPNGに撮る。文字のはみ出しは目で見ないと分からない。
//   OZAKEN_PW=マスター node shot_figs.mjs 03_ツール・製品/foo.html [出力先ディレクトリ]
import path from 'path';
import fs from 'fs';

// playwright-core は入っていないことがある。無ければ導入の仕方を伝えて止まる
let chromium;
try {
  ({ chromium } = await import('playwright-core'));
} catch (e) {
  console.error('playwright-core が見つかりません。作業ディレクトリで一度だけ:\n  npm i playwright-core\n'
    + '（ブラウザ本体は /opt/pw-browsers/chromium に用意されているので、ダウンロードは不要です）');
  process.exit(1);
}

const rel = process.argv[2];
const outDir = process.argv[3] || '/tmp/figs';
/* 資料の置き場所は、目印のファイル（index.html と ask.html）を見つけるまで上へ辿る。
   道具の置き場所が変わっても壊れないように */
function findRoot(start){
  let d = start;
  for(;;){
    if (fs.existsSync(path.join(d, 'index.html')) && fs.existsSync(path.join(d, 'ask.html'))) return d;
    const up = path.dirname(d);
    if (up === d) throw new Error('アーカイブの置き場所が見つかりません。OZAKEN_ROOT を設定してください');
    d = up;
  }
}
const root = process.env.OZAKEN_ROOT || findRoot(path.dirname(new URL(import.meta.url).pathname));
const pw = process.env.OZAKEN_PW;
if (!rel || !pw) {
  console.error('使い方: OZAKEN_PW=マスター node shot_figs.mjs <資料のパス> [出力先]');
  process.exit(1);
}

const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
p.on('pageerror', e => console.log('PAGEERROR', String(e)));
await p.route(u => !u.protocol.startsWith('file'), r => r.abort());   // フォント待ちで止めない
await p.addInitScript(k => { try { sessionStorage.setItem('ozaken_archive_pw', k); } catch (e) {} }, pw);
await p.goto('file://' + path.join(root, rel));
await p.waitForTimeout(2500);

// data-reveal は画面に入るまで透明なので、まとめて可視化する
await p.evaluate(() => document.querySelectorAll('[data-reveal]').forEach(e => e.classList.add('visible')));
await p.waitForTimeout(500);

const info = await p.evaluate(() => ({
  title: (document.querySelector('.hero-title') || {}).textContent,
  secs: document.querySelectorAll('section.sec-light, section.sec-navy').length,
  figs: document.querySelectorAll('.figure').length,
  escaped: /&lt;(br|b|span|strong)/.test(document.body.innerHTML),
}));
console.log(JSON.stringify(info));
if (info.escaped) console.log('⚠ タグが文字として出ています。SVGの中で <b> などを使っていないか確認してください');

const figs = await p.$$('.figure');
for (let i = 0; i < figs.length; i++) {
  await figs[i].scrollIntoViewIfNeeded();
  await p.waitForTimeout(300);
  await figs[i].screenshot({ path: `${outDir}/fig_${String(i).padStart(2, '0')}.png` });
}
console.log(`図版 ${figs.length} 点を ${outDir}/ に出力しました。Readツールで1枚ずつ見てください`);
await b.close();
