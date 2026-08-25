const { chromium } = await import('playwright-core');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.route('**://fonts.googleapis.com/**', r => r.fulfill({ status: 200, body: '' }));
await p.route('**://fonts.gstatic.com/**', r => r.abort());
await p.goto('file:///home/user/ozaken-materials/index.html#profile', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3200);
const pf = await p.evaluate(() => document.getElementById('profile-fs').classList.contains('show'));
console.log('profile shown:', pf);
const H = await p.evaluate(() => { const el = document.getElementById('profile-fs'); return el.scrollHeight; });
console.log('pf scrollHeight:', H);
let i = 0;
for (let y = 0; y < H && i < 12; y += 850, i++) {
  await p.evaluate(v => { document.getElementById('profile-fs').scrollTop = v; }, y);
  await p.waitForTimeout(700);
  await p.screenshot({ path: `/tmp/pf_${String(i).padStart(2,'0')}.png` });
}
await b.close();
