const { chromium } = await import('playwright-core');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.route('**://fonts.googleapis.com/**', r => r.fulfill({ status: 200, body: '' }));
await p.route('**://fonts.gstatic.com/**', r => r.abort());
p.on('pageerror', e => console.log('PAGE ERROR:', e.message));
await p.goto('file:///home/user/ozaken-materials/index.html', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3000);
const present = await p.evaluate(() => [...document.querySelectorAll('[data-ozk]')].map(e => {
  const r = e.getBoundingClientRect();
  return e.getAttribute('data-ozk') + ':' + (e.className||'') + ' ' + [r.x|0,r.y|0,r.width|0,r.height|0].join(',') + ' vis=' + (r.width>0);
}));
console.log(present.join('\n'));
for (const k of ['1','2','3']) {
  await p.evaluate(k => { const el = document.querySelector(`[data-ozk="${k}"]`); el.dispatchEvent(new MouseEvent('click', {bubbles:true})); }, k);
  await p.waitForTimeout(300);
}
await p.waitForTimeout(600);
const state = await p.evaluate(() => ({
  bkgate: document.getElementById('bkgate').getAttribute('aria-hidden'),
  sheet: document.getElementById('ozsheet').classList.contains('show'),
  anyShow: [...document.querySelectorAll('.show')].map(e=>e.id||e.className).slice(0,4)
}));
console.log(JSON.stringify(state));
await b.close();
