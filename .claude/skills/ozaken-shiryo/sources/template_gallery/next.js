/* Template-owned motion. Scene geometry follows the existing seekable player. */
(function(){
'use strict';
const NS='http://www.w3.org/2000/svg', states=new WeakMap();
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>1-Math.pow(1-clamp(x),3);
function make(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
window.TemplateMotion={mount(canvas){
 const root=canvas.querySelector('[data-kinetic]');if(!root)return null;
 let s=states.get(root);if(!s){s={kind:root.dataset.kinetic,gate:'exception',speed:4};states.set(root,s);
  root.addEventListener('click',event=>{const b=event.target.closest('[data-gate]');if(!b)return;s.gate=b.dataset.gate;root.querySelectorAll('[data-gate]').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));canvas.dispatchEvent(new Event('tl-figure-input'));});
  const range=root.querySelector('#nx-speed');if(range)range.addEventListener('input',()=>{s.speed=Number(range.value);root.querySelector('#nx-speed-value').textContent=s.speed+'倍';canvas.dispatchEvent(new Event('tl-figure-input'));});
 }
 const drawing=root.querySelector('.nx-drawing'),w=Math.max(220,drawing.clientWidth),small=w<500;
 const svg=make('svg',{viewBox:`0 0 ${w} ${s.kind==='waiting'?270:s.kind==='gate'?340:420}`,role:'img','aria-label':canvas.getAttribute('aria-label')});drawing.replaceChildren(svg);
 function add(tag,attrs,text,parent=svg){const e=make(tag,attrs,text);parent.append(e);return e;}
 function label(text,x,y,attrs={},parent=svg){return add('text',{x,y,'text-anchor':'middle',...attrs},text,parent);}
 const line=(d,parent=svg)=>add('path',{d,class:'nx-line'},undefined,parent);
 const summary=root.querySelector('.nx-summary');let lastMessage='';
 function message(value){if(lastMessage!==value){summary.textContent=value;lastMessage=value;}}
 let paint;
 if(s.kind==='cutaway'){
  const cx=w*.36,pw=Math.min(350,w*.57),ph=small?49:75,skew=pw*.2,planes=[],leaders=[],labels=[];
  line(`M ${cx-pw*.55} 85 V343 L ${cx} 372 L ${cx+pw*.53} 343 V85`).style.opacity=.3;
  ['目的','計画','モデル','知識','道具','評価'].forEach((name,i)=>{const g=add('g');planes.push(g);add('path',{d:`M ${-pw/2} ${-ph*.25} L ${-pw/2+skew} ${-ph*.75} L ${pw/2} ${ph*.25} L ${pw/2-skew} ${ph*.75} Z`,class:i===2?'nx-plane nx-model':'nx-plane'},undefined,g);line(`M ${-pw/2} ${-ph*.25+5} L ${pw/2-skew} ${ph*.75+5} L ${pw/2} ${ph*.25+5}`,g).style.opacity=.4;leaders.push(line(''));labels.push(label(name,w-57,0,{'text-anchor':'start'}));});
  const title=label('AIエージェント',cx,315);
  paint=t=>{const p=ease((t-1)*1.35),focus=ease((t-2)*1.35);planes.forEach((g,i)=>{const y=201+(i-2.5)*(8+45*p),x=cx+(i-2.5)*3*p;g.setAttribute('transform',`translate(${x} ${y})`);g.style.opacity=i===2?1:1-focus*.35;leaders[i].setAttribute('d',`M ${x+pw/2} ${y+ph*.25} H ${w-67}`);leaders[i].style.opacity=p;labels[i].setAttribute('y',y+ph*.25+5);labels[i].style.opacity=p;});title.style.opacity=1-p;message(t<1?'ひとつのAIを、役割ごとに捉える。':t<2?'同じ全体から、構成する役割を取り出す。':'モデルは構成の一部。目的・知識・道具・評価が支える例。');};
 } else if(s.kind==='rebuild'){
  const names=['調査','要約','構成','草案','判断','合意'],cw=Math.min(small?112:145,w*.42),ch=55,nodes=[];
  const lanes=add('g');[.25,.75].forEach((x,i)=>{add('rect',{x:w*x-w*.225,y:62,width:w*.45,height:326,rx:10,class:'nx-lane'},undefined,lanes);label(i?'人が担う':'AIが担う',w*x,42,{},lanes);});
  const wires=add('g');
  function points(stage){return names.map((_,i)=>{let x,y;if(stage===0){x=w/2+(i-2.5)*2;y=206+(i-2.5)*3;}else if(stage===2){x=w*(i<4?.25:.75);y=i<4?106+i*78:175+(i-4)*115;}else{const cols=small?2:3,row=Math.floor(i/cols),col=stage===3&&row%2?cols-1-i%cols:i%cols;x=w*(small?[.25,.75]:[.2,.5,.8])[col];y=small?108+row*106:160+row*135;}return {x,y};});}
  const end=points(3);end.slice(0,-1).forEach((a,i)=>line(`M ${a.x} ${a.y} L ${end[i+1].x} ${end[i+1].y}`,wires));
  names.forEach((name,i)=>{const g=add('g');nodes.push(g);add('rect',{width:cw,height:ch,rx:i<4?4:23,class:i<4?'nx-task':'nx-task nx-human'},undefined,g);label(String(i+1).padStart(2,'0'),13,17,{class:'nx-minor','text-anchor':'start'},g);label(name,cw/2,36,{},g);});
  const cover=add('g');const coverW=Math.min(285,w-8);add('rect',{x:w/2-coverW/2,y:147,width:coverW,height:117,rx:8,class:'nx-task'},undefined,cover);label('ひとつの業務',w/2,180,{class:'nx-minor'},cover);label('見積り・提案書を作る',w/2,215,{},cover);
  paint=t=>{const stage=Math.min(3,Math.floor(t)),p=ease((t-stage)*1.35),a=points(Math.max(0,stage-1)),b=points(stage);nodes.forEach((g,i)=>{g.setAttribute('transform',`translate(${a[i].x+(b[i].x-a[i].x)*p-cw/2} ${a[i].y+(b[i].y-a[i].y)*p-ch/2})`);g.style.opacity=stage===0?0:stage===1?p:1;});cover.style.opacity=stage===0?1:stage===1?1-p:0;lanes.style.opacity=stage===2?p:stage===3?1-p:0;wires.style.opacity=stage===3?p:0;message(['ひとまとまりの仕事。','同じ6つの作業を、取り出す。','AIは調査・要約・構成・草案、人は判断・合意を担う例。','名前と担当を保ちながら、ひとつの流れへつなぐ。'][stage]);};
 } else if(s.kind==='gate'){
  const gx=w*.45,ew=Math.min(130,w*.38),ex=w-ew-2,end=ex-15,ys=[89,255];
  line(`M 20 166 H ${gx}`);
  const routes=ys.map(y=>line(`M ${gx} 166 C ${gx+18} 166 ${end-22} ${y} ${end} ${y}`));
  add('rect',{x:gx-10,y:65,width:20,height:210,rx:10,fill:'var(--nx-blue)',opacity:.1});add('path',{d:`M ${gx} 65 V140 M ${gx} 191 V275`,stroke:'var(--nx-blue)','stroke-width':2,fill:'none'});
  label('合意した条件',gx,40,{class:'nx-minor'});label('依頼',28,139);
  ys.forEach((y,i)=>{add('rect',{x:ex,y:y-29,width:ew,height:58,rx:i?25:5,class:i?'nx-task nx-human':'nx-task'});label(i?'人の承認を待つ':'実行へ進む',ex+ew/2,y+5,{class:small?'nx-compact':''});});
  const marker=add('rect',{x:-9,y:-9,width:18,height:18,rx:3,fill:'var(--nx-blue)',stroke:'var(--nx-paper)','stroke-width':2});
  paint=t=>{let x=20,y=166;if(t<1)x=20;else if(t<2)x=20+(gx-20)*ease((t-1)*1.35);else{const p=ease((t-2)*1.35),u=1-p,ey=s.gate==='normal'?ys[0]:ys[1];x=u*u*u*gx+3*u*u*p*(gx+18)+3*u*p*p*(end-22)+p*p*p*end;y=(u*u*u+3*u*u*p)*166+(3*u*p*p+p*p*p)*ey;}marker.setAttribute('transform',`translate(${x} ${y})`);marker.setAttribute('fill',s.gate==='normal'?'var(--nx-teal)':'var(--nx-warm)');routes.forEach((p,i)=>p.style.stroke=t>=2&&((s.gate==='normal')===(i===0))?'var(--nx-blue)':'var(--nx-line)');message(t<1?'依頼を受け取る。':t<2?'合意した範囲を、条件と照合する。':s.gate==='normal'?'条件の範囲内なので、実行へ進む。':'上限を超えるため、実行せず人の承認を待つ。');};
 } else {
  const x=49,pw=w-x-8,colors=['var(--nx-blue)','var(--nx-teal)','var(--nx-warm)','var(--nx-muted)'],rects=[],values=[];
  [0,10,20,30].forEach(v=>{const xx=x+pw*v/30;line(`M ${xx} 41 V209`).style.opacity=.35;label(v,xx,231,{'text-anchor':v===0?'start':v===30?'end':'middle',class:'nx-minor'});});
  label('経過時間（時間）',x+pw/2,263,{class:'nx-minor'});
  ['従来','変更後'].forEach((name,row)=>{const yy=60+row*93;label(name,x-10,yy+26,{'text-anchor':'end',class:'nx-compact'});let pos=0;[6,8,12,4].forEach((v,i)=>{const r=add('rect',{x:x+pw*pos/30,y:yy,width:pw*v/30,height:44,fill:colors[i]});const val=label(v+'h',x+pw*(pos+v/2)/30,yy+27,{class:'nx-inverse',style:i===0?'':'fill:#0a0f1c'});if(pw*v/30<27)val.style.opacity=0;if(row){rects.push(r);values.push(val);}pos+=v;});});
  const total=label('24時間',w-8,143,{'text-anchor':'end',class:'nx-minor'});
  paint=t=>{const speed=1+(s.speed-1)*ease((t-1)*1.35),vals=[6,8/speed,12,4];let pos=0;vals.forEach((v,i)=>{const xx=x+pw*pos/30,ww=pw*v/30;rects[i].setAttribute('x',xx);rects[i].setAttribute('width',ww);values[i].setAttribute('x',xx+ww/2);values[i].textContent=Math.round(v*10)/10+'h';values[i].style.opacity=ww<27?0:1;pos+=v;});total.textContent=Math.round(pos*10)/10+'時間';message(t<1?'調査6・草案8・承認待ち12・確認4時間の仮想例。':`草案 8 → ${Math.round(8/s.speed*10)/10} 時間 ／ 全体 30 → ${Math.round((22+8/s.speed)*10)/10} 時間。承認待ちは12時間のまま。`);};
 }
 return {paint};
}};

// Ambient movement is independently pausable. Hidden/offscreen surfaces do no animation work.
const reduce=matchMedia('(prefers-reduced-motion: reduce)'),body=document.body,motionButton=document.getElementById('tl-ambient-toggle');
let still=false;try{still=localStorage.getItem('ozaken-template-still')==='1';}catch{}
function ambient(){body.classList.toggle('tl-still',still||reduce.matches);if(motionButton){motionButton.disabled=reduce.matches;motionButton.setAttribute('aria-pressed',String(!(still||reduce.matches)));motionButton.textContent=reduce.matches?'背景：端末設定で停止':still?'背景の動き：OFF':'背景の動き：ON';}}
if(motionButton)motionButton.addEventListener('click',()=>{still=!still;try{localStorage.setItem('ozaken-template-still',still?'1':'0');}catch{}ambient();});
reduce.addEventListener('change',ambient);ambient();
const ambientObserver=new IntersectionObserver(entries=>entries.forEach(e=>e.target.classList.toggle('is-inview',e.isIntersecting)),{threshold:0});
document.querySelectorAll('[data-ambient-zone]').forEach(el=>ambientObserver.observe(el));
document.addEventListener('visibilitychange',()=>body.classList.toggle('tl-away',document.hidden));

document.querySelectorAll('.nx-reactive').forEach(root=>{const inputs=[...root.querySelectorAll('input')];root.addEventListener('input',()=>{const valid=inputs.every(i=>i.value!==''&&i.validity.valid);root.querySelector('[data-saving]').textContent=valid?(Number(inputs[0].value)*Number(inputs[1].value)*4/60).toLocaleString('ja-JP',{maximumFractionDigits:1}):'—';});});
document.querySelectorAll('.nx-focus').forEach(root=>root.addEventListener('click',event=>{const b=event.target.closest('[data-focus]');if(!b)return;const n=Number(b.dataset.focus);root.querySelectorAll('[data-focus]').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));root.style.setProperty('--focus',n);root.querySelector('p').textContent=['準備：目的・対象・使える情報を揃える。','判断：任せる範囲と、人が確認する条件を決める。','実行：合意した条件に沿って進め、結果を確認する。'][n];}));
document.querySelectorAll('.nx-wipe').forEach(root=>root.querySelector('input').addEventListener('input',e=>{root.style.setProperty('--wipe',e.target.value+'%');root.querySelector('output').textContent=e.target.value+'%';}));
document.querySelectorAll('.nx-decision').forEach(root=>root.addEventListener('click',event=>{const b=event.target.closest('[data-decision]');if(!b)return;root.querySelectorAll('[data-decision]').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));root.querySelector('.nx-decision-answer').textContent=b.dataset.decision==='small'?'1件の低い影響範囲で試し、結果を確認。条件を具体化できます。':'草案作成を任せ、公開・送信の前に人が確認。作成と最終判断を分担できます。';}));
document.querySelectorAll('[data-unit-group]').forEach(b=>b.addEventListener('click',()=>{const grouped=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',String(grouped));b.textContent=grouped?'連続した点に戻す':'10件ずつにまとめる';b.closest('.nx-units').classList.toggle('is-grouped',grouped);}));
document.querySelectorAll('[data-chapter-next]').forEach(b=>b.addEventListener('click',()=>{const root=b.closest('.nx-chapter'),second=!root.classList.contains('is-next');root.classList.toggle('is-next',second);root.querySelector('[data-chapter-label]').textContent=second?'CHAPTER 02 / 任せる':'CHAPTER 01 / 決める';root.querySelector('[data-chapter-text]').textContent=second?'を、AIと共有する。':'を、言葉にする。';root.querySelector('[data-chapter-live]').textContent=second?'第2章：目的を、AIと共有する。':'第1章：目的を、言葉にする。';b.textContent=second?'前の章へ ←':'次の章へ →';}));
})();
