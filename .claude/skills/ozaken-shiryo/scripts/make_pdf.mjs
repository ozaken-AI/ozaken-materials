/* 配布用のHTMLを、A4横のPDFに焼く。
 *
 *   node make_pdf.mjs <入力HTMLの絶対パス> <出力PDF>
 *
 * 書体はこの環境に入っていないので file:// で読ませる。
 * そのため **入力HTMLは書体フォルダの中に置く**（make_ogp.mjs と同じ理由）。
 * 書体は apply_ogp.py の fonts() が /tmp/ozaken-ogp-fonts に用意する。
 *
 * HTML側は @page{size:A4 landscape;margin:0} と
 * .page{width:297mm;height:210mm;page-break-after:always} を持たせる。
 * 背景色を出すため printBackground は必須。 */
import { chromium } from 'playwright-core';
const [, , src, out] = process.argv;
if (!src || !out) {
  console.error('使い方: node make_pdf.mjs <入力HTML> <出力PDF>');
  process.exit(1);
}
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium',
  args: ['--allow-file-access-from-files'] });
const p = await b.newPage();
await p.goto('file://' + src, { waitUntil: 'load' });
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(600);
await p.pdf({ path: out, format: 'A4', landscape: true, printBackground: true,
  margin: { top: '0', right: '0', bottom: '0', left: '0' } });
await b.close();
console.log('wrote ' + out);
