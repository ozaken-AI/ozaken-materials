const { chromium } = await import('playwright-core');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const url of ['file:///home/user/ozaken-materials/index.html','file:///tmp/old_index.html']) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const p = await ctx.newPage();
  await p.route('**://fonts.googleapis.com/**', r => r.fulfill({ status: 200, body: '' }));
  await p.route('**://fonts.gstatic.com/**', r => r.abort());
  await p.goto(url, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2000);
  const info = await p.evaluate(() => {
    const el = document.elementFromPoint(360, 814);
    const chain = [];
    let e = el; while (e && chain.length < 5) { chain.push(e.tagName + '.' + (e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className || '').toString().slice(0,40)); e = e.parentElement; }
    // close() が何で呼ばれるかを見る
    const sheet = document.getElementById('ozsheet');
    let log = [];
    sheet.classList.add('show');
    const rec = ev => log.push(ev.type + '@' + (ev.target.id || ev.target.className||'').toString().slice(0,20));
    ['click','touchstart'].forEach(t => sheet.addEventListener(t, rec, true));
    return { at: chain };
  });
  console.log(url.slice(-20), JSON.stringify(info));
  await ctx.close();
}
await b.close();
