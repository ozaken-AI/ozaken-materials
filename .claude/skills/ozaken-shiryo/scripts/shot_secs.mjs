// 資料を「面」ごとにPNGで撮る。投影したときにどう見えるかは、絵で見ないと分からない。
//   OZAKEN_PW=マスター node shot_secs.mjs 03_ツール・製品/foo.html [出力先ディレクトリ]
//
// 図版だけを見る shot_figs.mjs と違い、こちらは1画面まるごと。
// 背景色の移り変わり・文字の量・余白の詰まり具合を見るためのもの。
import path from 'path';
import fs from 'fs';

let chromium;
try {
  ({ chromium } = await import('playwright-core'));
} catch (e) {
  console.error('playwright-core が見つかりません。作業ディレクトリで一度だけ:\n  npm i playwright-core\n'
    + '（ブラウザ本体は /opt/pw-browsers/chromium に用意されているので、ダウンロードは不要です）');
  process.exit(1);
}

const rel = process.argv[2];
const outDir = process.argv[3] || '/tmp/secs';
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
  console.error('使い方: OZAKEN_PW=マスター node shot_secs.mjs <資料のパス> [出力先]');
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });

// 投影を想定した比率。会場のスクリーンはたいてい 16:9
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1440, height: 810 } });
p.on('pageerror', e => console.log('PAGEERROR', String(e)));
await p.route(u => !u.protocol.startsWith('file'), r => r.abort());
await p.addInitScript(k => { try { sessionStorage.setItem('ozaken_archive_pw', k); } catch (e) {} }, pw);
await p.goto('file://' + path.join(root, rel));
await p.waitForTimeout(2500);
await p.evaluate(() => {
  document.querySelectorAll('[data-reveal]').forEach(e => e.classList.add('visible'));
  // 図版は画面に入って初めて anim-on が付く。背の高い面を1枚に撮ると、
  // 撮影中に付いても間に合わず、**図が丸ごと真っ白に写る**。先に付けておく
  document.querySelectorAll('.figure').forEach(e => e.classList.add('anim-on'));
});
await p.waitForTimeout(600);

// 表紙は画面いっぱいで1枚
const hero = await p.$('.hero');
if (hero) {
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.waitForTimeout(400);
  await p.screenshot({ path: `${outDir}/00_hero.png` });
}

const secs = await p.$$('section.sec-light, section.sec-navy');
const meta = [];
for (let i = 0; i < secs.length; i++) {
  await secs[i].scrollIntoViewIfNeeded();
  // 図版は描画順に時間差で現れる。落ち着くまで待たないと、薄いまま写る
  await p.waitForTimeout(1500);
  const box = await secs[i].boundingBox();
  await secs[i].screenshot({ path: `${outDir}/${String(i + 1).padStart(2, '0')}.png` });
  const info = await secs[i].evaluate(el => ({
    face: el.className.indexOf('navy') >= 0 ? 'navy' : 'light',
    bg: el.getAttribute('data-bg') || '-',
    head: (el.querySelector('.sec-title') || {}).textContent || '',
  }));
  meta.push({ n: i + 1, h: Math.round((box && box.height) || 0), ...info });
}
// 投影1画面に収まらない面は、送るときに切れる
const tall = meta.filter(m => m.h > 1100).map(m => `${m.n}(${m.h}px)`);
console.log(JSON.stringify({ secs: secs.length, out: outDir }, null, 0));
meta.forEach(m => console.log(`  ${String(m.n).padStart(2)} ${m.face}/${m.bg} ${String(m.h).padStart(5)}px  ${m.head.slice(0, 40)}`));
if (tall.length) console.log('※ 1画面に収まりきらない面: ' + tall.join(' '));
console.log(`面 ${secs.length} 枚（＋表紙）を ${outDir}/ に出力しました。Readツールで1枚ずつ見てください`);
await b.close();
