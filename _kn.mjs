import pw from 'playwright-core';
const { chromium } = pw;
const R='file:///home/user/ozaken-materials/';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const ctx = await b.newContext({ viewport:{width:1280,height:800} });
async function open(path, pass){
  const p = await ctx.newPage();
  await p.route('**://fonts.googleapis.com/**', r=>r.fulfill({status:200,contentType:'text/css',body:''}));
  await p.goto(R+path); await p.waitForTimeout(700);
  const gate = await p.$('input[type=password]');
  if (gate){ await p.fill('input[type=password]', pass); await p.press('input[type=password]','Enter'); await p.waitForTimeout(1800); }
  return p;
}
// ① 資料ページ（深い階層）で ck
let p = await open('09_role/york-union.html','benimaru');
console.log('① 解錠後:', (await p.title()).slice(0,26));
await p.keyboard.type('ck',{delay:70}); await p.waitForTimeout(900);
console.log('   ck →', decodeURI(p.url()).replace(R,''));
await p.close();

// ② test / qr が横取りされていないか
p = await open('09_role/york-union.html','benimaru');
const before = p.url();
await p.keyboard.type('test',{delay:90}); await p.waitForTimeout(900);
console.log('② test:', p.url()===before ? 'ページ遷移なし ✅' : '飛ばされた ❌ '+p.url());
console.log('   確認テストが開いた:', await p.evaluate(()=>{
  const q=document.querySelector('.quiz'); return q ? getComputedStyle(q).display!=='none' : '(この資料にテストなし)'; }));
await p.keyboard.press('Escape'); await p.waitForTimeout(400);
await p.keyboard.type('qr',{delay:90}); await p.waitForTimeout(700);
console.log('   qr:', p.url()===before ? 'ページ遷移なし ✅' : '❌',
            '/ QR画面:', await p.evaluate(()=>{ const q=document.querySelector('.ozqr,#ozqr,.qrpane');
              return q ? getComputedStyle(q).display!=='none' : '(要素名ちがい)'; }));
await p.close();

// ③ ルート直下の資料でも ck が効くか（階層の判定）
p = await open('Udemy/career-strategy.html','yoroi');
await p.keyboard.type('ck',{delay:70}); await p.waitForTimeout(900);
console.log('③ Udemy から ck →', decodeURI(p.url()).replace(R,''));
await p.close();

// ④ stage.html の隠しコマンド
p = await ctx.newPage();
await p.route('**://fonts.googleapis.com/**', r=>r.fulfill({status:200,contentType:'text/css',body:''}));
await p.goto(R+'stage.html'); await p.waitForTimeout(600);
await p.keyboard.type('pt',{delay:70}); await p.waitForTimeout(400);
console.log('④ pt →', await p.evaluate(()=>document.getElementById('pat').classList.contains('on'))?'試験画面 ✅':'❌');
await p.keyboard.press('Escape'); await p.waitForTimeout(400);
for (let i=0;i<3;i++){ await p.mouse.click(450, 700); await p.waitForTimeout(130); }
await p.waitForTimeout(300);
console.log('   3回たたく →', await p.evaluate(()=>document.getElementById('pat').classList.contains('on'))?'開いた ✅':'❌');
await p.keyboard.press('Escape'); await p.waitForTimeout(400);
await p.keyboard.type('st',{delay:70}); await p.waitForTimeout(900);
console.log('   st →', decodeURI(p.url()).replace(R,''));
await p.waitForTimeout(600);
console.log('   待機画面が出た:', await p.evaluate(()=>{ const e=document.getElementById('standby');
  return e ? e.classList.contains('show') : '(要素なし)'; }));
await b.close();
