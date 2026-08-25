const { chromium } = await import('playwright-core');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const p = await ctx.newPage();
await p.route('**://fonts.googleapis.com/**', r => r.fulfill({ status: 200, body: '' }));
await p.route('**://fonts.gstatic.com/**', r => r.abort());
await p.goto('file:///home/user/ozaken-materials/index.html', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3000);
for (const k of ['1','2','3']) {
  const box = await p.evaluate(k => { const r = document.querySelector(`[data-ozk="${k}"]`).getBoundingClientRect(); return {x:r.x+r.width/2, y:r.y+r.height/2}; }, k);
  await p.touchscreen.tap(box.x, box.y);
  await p.waitForTimeout(350);
}
await p.waitForTimeout(500);
const state = await p.evaluate(() => ({
  bkgate: document.getElementById('bkgate').getAttribute('aria-hidden'),
  anyShow: [...document.querySelectorAll('.show')].map(e=>e.id||e.className).slice(0,4)
}));
console.log(JSON.stringify(state));
await b.close();
