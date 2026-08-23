// 図版の箱から、文字がはみ出していないかを全資料で見る。
//
// **SVGは自動で折り返さない。** 上限を超えた文字は箱から出て、
// 隣の行に重なるか、図版の外へ消える。コードからは見えないので、
// 実際に描画して、text ひとつずつの位置を測るしかない。
//
//   OZAKEN_PW=マスター python3 dump_all.py /tmp/oz      # 復号して並べる
//   node check_overflow.mjs /tmp/oz
//
// 出力は「資料 / はみ出した文字 [向き と 何px]」。
// 2px までは字形の丸めなので見逃す。
import pw from 'playwright-core';
const { chromium } = pw;
import fs from 'node:fs';
(async () => {
  const dir = process.argv[2];
  const files = fs.readdirSync(dir).sort();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.route('**://fonts.googleapis.com/**', r => r.fulfill({status:200,contentType:'text/css',body:''}));
  await p.route('**://fonts.gstatic.com/**', r => r.abort());
  let total = 0;
  for (const f of files) {
    await p.goto('file://' + dir + '/' + f);
    await p.waitForTimeout(120);
    await p.evaluate(() => {
      document.querySelectorAll('[data-reveal]').forEach(e => e.classList.add('visible'));
      document.querySelectorAll('.figure,.hero-glyph').forEach(e => e.classList.add('anim-on'));
    });
    const bad = await p.evaluate(() => {
      const out = [];
      document.querySelectorAll('.figure svg').forEach(svg => {
        const S = svg.getBoundingClientRect();
        svg.querySelectorAll('text').forEach(t => {
          const r = t.getBoundingClientRect();
          if (r.width === 0) return;
          const o = { 左: S.left - r.left, 上: S.top - r.top, 右: r.right - S.right, 下: r.bottom - S.bottom };
          const e = Object.entries(o).filter(([k, v]) => v > 2);
          if (e.length) out.push(t.textContent.slice(0, 14) + ' [' +
            e.map(([k, v]) => k + Math.round(v)).join(',') + ']');
        });
      });
      return out;
    });
    if (bad.length) { total += bad.length; console.log(f.replace(/__/g, '/') + '  ' + bad.join(' / ')); }
  }
  console.log('---'); console.log('はみ出し ' + total + ' 箇所 / ' + files.length + ' 本を確認');
  await b.close();
})();
