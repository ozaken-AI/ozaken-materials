const { chromium } = await import('playwright-core');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const p = await ctx.newPage();
p.on('console', m => { if (m.type() === 'error') console.log('JS ERROR:', m.text()); });
p.on('pageerror', e => console.log('PAGE ERROR:', e.message));
await p.route('**://fonts.googleapis.com/**', r => r.fulfill({ status: 200, body: '' }));
await p.route('**://fonts.gstatic.com/**', r => r.abort());
await p.goto('file:///home/user/ozaken-materials/index.html', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
// 右下隅を長押し（CDPでタッチを出し、1.2秒保持）
const x = 390 - 30, y = 844 - 30;
const cdp = await ctx.newCDPSession(p);
await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
await p.waitForTimeout(1200);
await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
await p.waitForTimeout(400);
const shown = await p.evaluate(() => {
  const s = document.getElementById('ozsheet');
  return { exists: !!s, shown: s ? s.classList.contains('show') : false };
});
console.log('ozsheet:', JSON.stringify(shown));
await p.screenshot({ path: '/tmp/touch.png' });
await b.close();
