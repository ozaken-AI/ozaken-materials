import { chromium } from 'playwright-core';
import fs from 'fs';
const DOC = process.argv[2], OUT = process.argv[3], SHOT = process.argv[4]==='shot';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium', args:['--no-sandbox'] });
const p = await b.newPage({viewport:{width:1440,height:900}});
await p.route('**://fonts.googleapis.com/**', r=>r.fulfill({status:200,body:'',contentType:'text/css'}));
await p.route('**://fonts.gstatic.com/**', r=>r.abort());
const errs=[]; p.on('pageerror',x=>errs.push(String(x)));
await p.goto('file:///home/user/ozaken-materials/'+DOC);
await p.waitForTimeout(700);
if (await p.$('#pw')) { await p.fill('#pw','O29tabetai'); await p.keyboard.press('Enter'); }
await p.waitForTimeout(2000);
await p.evaluate(async()=>{ for(let y=0;y<document.body.scrollHeight;y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,55));} window.scrollTo(0,0); });
await p.waitForTimeout(1500);
const r = await p.evaluate(()=>{
  const out={hScroll:document.documentElement.scrollWidth>window.innerWidth+1, over:[]};
  document.querySelectorAll('svg text, svg tspan').forEach(t=>{
    const sv=t.closest('svg'); if(!sv) return;
    const bb=t.getBoundingClientRect(), sb=sv.getBoundingClientRect();
    if(bb.right>sb.right+1||bb.left<sb.left-1) out.over.push((t.textContent||'').slice(0,26));
  });
  return out;
});
console.log('横スクロール:', r.hScroll, '/ 図版はみ出し:', r.over.length);
if(r.over.length) console.log(r.over.slice(0,20));
console.log('エラー:', errs.slice(0,3));
// 語中折れ
const svg = await p.evaluate(()=>{const o=[];document.querySelectorAll('svg text').forEach(t=>{const ts=[...t.querySelectorAll('tspan')].map(x=>x.textContent||'');if(ts.length>1)for(let i=0;i<ts.length-1;i++)o.push([ts[i],ts[i+1]]);});return o;});
const KANJI=/[一-龯]/, KATA=/[ァ-ヺ]/, HEAD_NG=/^[んゃゅょっーぁぃぅぇぉ、。」』）]/;
const OKURI=/^[きくしすちてりるれみめたださけこそとねへほいうえおん]/, PART=/^(は|が|を|に|で|と|も|の|や|へ|から|より|など|まで)/;
const bad=([a,c])=>{const x=a.slice(-1),y=c.slice(0,1);
  if(HEAD_NG.test(y))return'禁則'; if(KATA.test(x)&&KATA.test(y))return'カタカナ語の途中';
  if(KANJI.test(x)&&KANJI.test(y))return'熟語の途中';
  if(KANJI.test(x)&&OKURI.test(y)&&!PART.test(c))return'送り仮名の途中'; return null;};
console.log('=== SVG の切れ目 ('+svg.length+'か所) ===');
let n=0; svg.forEach(pr=>{const v=bad(pr); if(v){n++;console.log('  ['+v+'] …'+pr[0].slice(-8)+' ／ '+pr[1].slice(0,8)+'…');}});
if(!n) console.log('  なし');
if (SHOT) {
  fs.mkdirSync(OUT,{recursive:true});
  const secs = await p.$$('.hero, section');
  for (let i=0;i<secs.length;i++){ await secs[i].scrollIntoViewIfNeeded(); await p.waitForTimeout(1600);
    await secs[i].screenshot({path:`${OUT}/${String(i).padStart(2,'0')}.png`}); }
  console.log('面数:', secs.length);
}
await b.close();
