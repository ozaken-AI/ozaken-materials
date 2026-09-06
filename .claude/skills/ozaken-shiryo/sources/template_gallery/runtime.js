/* The catalogue owns a single paused, seekable timeline. Only the selected scene animates. */
(function(){
'use strict';
const data=JSON.parse(document.getElementById('tl-data').textContent);
const byId=new Map(data.map(x=>[x.id,x]));
const $=s=>document.querySelector(s);
const canvas=$('#tl-canvas'),studio=$('.tl-studio'),dialog=$('#tl-dialog');
const play=$('#tl-play'),progress=$('#tl-progress'),beats=$('#tl-beats');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const BEAT=1150,ENTER=850;
let current=byId.get('dims'),animations=[],packets=[],time=0,duration=0,playing=false,raf=0,last=0,speed=1,activeCaption=-1;
let category='all',panel='figures',resizeFrame=0,dimension=null,water=null,waterWave=null,lastSize='';
const tabs=[...document.querySelectorAll('.tl-tabs [role=tab]')];
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ease=t=>1-Math.pow(1-t,3);
function pause(){playing=false;cancelAnimationFrame(raf);play.textContent='▶ 再生';play.setAttribute('aria-label','アニメーションを再生');}
function dispose(){pause();animations.forEach(a=>a.cancel());animations=[];packets=[];}
function stageEnd(i){return Math.min(duration,i*BEAT+ENTER+150);}
function motion(el){
 const beat=Number(el.dataset.beat||0),type=el.dataset.motion;
 let frames;
 if(type==='draw'){
  el.removeAttribute('pathLength');
  const length=el.getTotalLength(),matrix=el.getScreenCTM();let px=0,previous=el.getPointAtLength(0).matrixTransform(matrix);
  for(let i=1;i<=80;i++){const point=el.getPointAtLength(length*i/80).matrixTransform(matrix);px+=Math.hypot(point.x-previous.x,point.y-previous.y);previous=point;}
  frames=[{strokeDasharray:px+'px '+px+'px',strokeDashoffset:px+'px'},{strokeDasharray:px+'px '+px+'px',strokeDashoffset:'0px'}];
 }
 else if(type==='growx')frames=[{scale:'0 1'},{scale:'1 1'}];
 else if(type==='growy')frames=[{scale:'1 0'},{scale:'1 1'}];
 else if(type==='scale')frames=[{scale:'.76',opacity:.2},{scale:'1',opacity:1}];
 else if(type==='transfer'){
  const source=canvas.querySelector(el.dataset.from),r=el.getBoundingClientRect(),s=source.getBoundingClientRect();
  frames=[{translate:(s.x+s.width/2-r.x-r.width/2)+'px '+(s.y+s.height/2-r.y-r.height/2)+'px',opacity:0},{translate:'0px 0px',opacity:1}];
 } else frames=[{translate:type==='fromleft'?'-28px 0px':type==='fromright'?'28px 0px':'0px 24px',opacity:.16},{translate:'0px 0px',opacity:1}];
 const a=el.animate(frames,{duration:ENTER,delay:beat*BEAT+100,easing:'cubic-bezier(.2,.65,.25,1)',fill:'both'});a.pause();animations.push(a);
}
function prepare(){
 animations.forEach(a=>a.cancel());animations=[];packets=[];
 if(!reduced.matches){
  canvas.querySelectorAll('[data-motion]').forEach(motion);
  canvas.querySelectorAll('[data-arc]').forEach(el=>{
   const length=Number(el.dataset.arc),circ=Number(el.dataset.circ);
   const a=el.animate([{strokeDasharray:'0 '+circ},{strokeDasharray:length+' '+(circ-length)}],{duration:ENTER,delay:Number(el.dataset.beat)*BEAT+100,easing:'cubic-bezier(.2,.65,.25,1)',fill:'both'});a.pause();animations.push(a);
  });
 }
 canvas.querySelectorAll('[data-travel]').forEach(el=>{
  const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',el.dataset.travel);
  packets.push({el,path:p,length:p.getTotalLength(),beat:Number(el.dataset.beat||0)});
 });
 dimension=canvas.querySelector('[data-dimension]');
 if(dimension&&!dimension.querySelector('circle')){const dot=document.createElementNS('http://www.w3.org/2000/svg','circle');dot.setAttribute('r','5');dot.setAttribute('fill','#9fc6f5');dimension.append(dot);}
 water=canvas.querySelector('[data-water]');waterWave=canvas.querySelector('[data-water-wave]');
 render(time);
}
const forms=[
 [[300,115],[300,115],[300,115],[300,115],[300,115],[300,115]],
 [[175,115],[225,115],[275,115],[325,115],[375,115],[425,115]],
 [[170,125],[220,85],[275,135],[325,85],[380,135],[430,95]],
 [[210,60],[390,60],[390,175],[300,175],[210,175],[210,60]],
 [[300,25],[390,72],[390,168],[300,215],[210,168],[210,72]]
];
function drawDimension(t){
 if(!dimension)return;
 const stage=Math.min(4,Math.floor(t/BEAT)),index=Math.max(0,stage-1),next=stage,mix=stage===0?0:ease(clamp((t-stage*BEAT-100)/ENTER)),pos=index+mix;
 const points=forms[index].map((p,i)=>p.map((v,j)=>v+(forms[next][i][j]-v)*mix));
 const pointText=points.map(p=>p.join(',')).join(' ');
 dimension.querySelector('.dimension-wire').setAttribute('points',pointText);
 const face=dimension.querySelector('.dimension-face');face.setAttribute('points',pointText);face.style.opacity=String(clamp(pos-2));
 const inner=dimension.querySelector('.dimension-inner');inner.setAttribute('points','210,72 300,121 390,72 300,121 300,215');inner.style.opacity=String(clamp(pos-3));
 const dot=dimension.querySelector('circle');dot.setAttribute('cx',String(points[0][0]));dot.setAttribute('cy',String(points[0][1]));dot.style.opacity=String(1-clamp(pos));
 canvas.querySelector('[data-dimension-label]').textContent=['点 / 単発','線 / 前提','連鎖 / 手順','面 / 目的','立体 / 協働'][stage];
}
function render(value){
 time=clamp(value,0,duration);const visualTime=reduced.matches?duration:time;
 animations.forEach(a=>{a.currentTime=visualTime;});
 drawDimension(visualTime);
 if(water){const p=ease(clamp(visualTime/(BEAT*2)));const top=100-p*66.6667;water.style.clipPath='inset('+top+'% 0 0 0)';waterWave.style.top=top+'%';waterWave.style.translate=(Math.sin(visualTime/500)*5)+'% 0px';}
 packets.forEach(({el,path,length,beat})=>{
  const span=current.id==='flow'||current.id==='roles'?BEAT*(current.beats.length-1):BEAT*current.beats.length;
  const p=clamp((visualTime-beat*BEAT)/span);const point=path.getPointAtLength(length*p);
  el.setAttribute('cx',point.x);el.setAttribute('cy',point.y);el.style.opacity=(!reduced.matches&&playing&&p>0&&p<1)?'1':'0';
 });
 const done=time>=duration,active=done?-1:Math.min(current.beats.length-1,Math.floor(time/BEAT));
 canvas.querySelectorAll('[data-beat]').forEach(el=>el.classList.toggle('is-current',Number(el.dataset.beat)===active));
 beats.querySelectorAll('button').forEach((b,i)=>b.setAttribute('aria-current',String(i===active)));
 progress.value=String(Math.round(time/duration*1000));
 progress.setAttribute('aria-valuetext',done?'完成形':current.beats[Math.max(0,active)]);
 $('#tl-time').textContent=done?'完成形':(time/1000).toFixed(1)+' / '+(duration/1000).toFixed(1)+'秒';
 $('#tl-next').textContent=done?'最初の段階 →':'次の段階 →';
 if(active!==activeCaption){activeCaption=active;$('#tl-caption').textContent=reduced.matches?'動きを減らす設定に合わせ、完成形で表示しています。':done?'完成形を表示しています。再生すると、説明の順に変化します。':current.beats[active];}
}
function tick(now){if(!playing)return;const dt=last?Math.min(now-last,80):0;last=now;render(time+dt*speed);if(time>=duration){pause();render(duration);}else raf=requestAnimationFrame(tick);}
function start(restart=false){if(reduced.matches)return;if(restart||time>=duration)time=0;playing=true;last=0;play.textContent='Ⅱ 一時停止';play.setAttribute('aria-label','アニメーションを一時停止');render(time);cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);}
function select(id,scroll=false){
 const item=byId.get(id);if(!item)return;dispose();current=item;duration=BEAT*item.beats.length+100;time=duration;activeCaption=-2;
 canvas.replaceChildren(document.getElementById('scene-'+id).content.cloneNode(true));
 canvas.setAttribute('aria-label',item.name+'の見本');
 $('#tl-stage-title').textContent=item.name;$('#tl-purpose').textContent=item.purpose;$('#tl-best').textContent=item.best;$('#tl-caution').textContent=item.caution;
 $('#tl-stage-category').textContent=({compare:'比較する',sequence:'流れを伝える',structure:'構造をほどく',quantity:'数量を見せる'})[item.category];
 beats.replaceChildren(...item.beats.map((label,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String(i+1).padStart(2,'0')+' '+label;b.addEventListener('click',()=>{pause();render(stageEnd(i));});return b;}));
 document.querySelectorAll('[data-select]').forEach(b=>b.setAttribute('aria-current',String(b.dataset.select===id)));
 prepare();
 const url=new URL(location.href);url.hash='figure='+id;history.replaceState(null,'',url);
 if(scroll){$('#tl-explorer').scrollIntoView({behavior:reduced.matches?'auto':'smooth',block:'start'});$('#tl-stage-title').focus({preventScroll:true});}
}
play.addEventListener('click',()=>playing?pause():start());$('#tl-replay').addEventListener('click',()=>start(true));
$('#tl-next').addEventListener('click',()=>{pause();const next=time>=duration?0:Math.min(current.beats.length-1,Math.floor(time/BEAT)+1);render(stageEnd(next));});
$('#tl-all').addEventListener('click',()=>{pause();render(duration);});
progress.addEventListener('input',()=>{pause();render(Number(progress.value)/1000*duration);});
$('#tl-speed').addEventListener('change',e=>{speed=Number(e.target.value);});
function switchPanel(id,focus=false){
 pause();panel=id;tabs.forEach(b=>{const on=b.dataset.panel===id;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;document.getElementById('panel-'+b.dataset.panel).hidden=!on;if(on&&focus)b.focus();});
 document.querySelectorAll('.tl-part-example [data-reveal]').forEach(el=>el.classList.add('visible'));
 window.dispatchEvent(new Event('resize'));
}
tabs.forEach((button,i)=>{button.addEventListener('click',()=>switchPanel(button.dataset.panel));button.addEventListener('keydown',event=>{let n;if(event.key==='ArrowRight')n=(i+1)%tabs.length;else if(event.key==='ArrowLeft')n=(i+tabs.length-1)%tabs.length;else if(event.key==='Home')n=0;else if(event.key==='End')n=tabs.length-1;else return;event.preventDefault();switchPanel(tabs[n].dataset.panel,true);});});
function filter(){const q=$('#tl-search').value.trim().toLowerCase();let count=0;document.querySelectorAll('[data-select]').forEach(button=>{const item=byId.get(button.dataset.select),match=(category==='all'||item.category===category)&&(!q||[item.name,item.purpose,item.best,item.id,item.caution,...item.beats].join(' ').toLowerCase().includes(q));button.hidden=!match;if(match)count++;});$('#tl-results').textContent=count+'種類';$('#tl-empty').hidden=count!==0;}
document.querySelectorAll('[data-select]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.select,true)));
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{category=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filter();}));
$('#tl-search').addEventListener('input',filter);
document.querySelectorAll('[data-part-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-part-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelectorAll('[data-part]').forEach(part=>part.hidden=button.dataset.partFilter!=='すべて'&&part.dataset.partGroup!==button.dataset.partFilter);}));
const partTimers=new WeakMap();
document.querySelectorAll('[data-replay-part]').forEach(button=>button.addEventListener('click',()=>{const part=button.closest('.tl-part');clearTimeout(partTimers.get(part));part.classList.remove('is-replaying');part.querySelectorAll('[data-reveal]').forEach(x=>x.classList.remove('visible'));void part.offsetWidth;part.classList.add('is-replaying');part.querySelectorAll('[data-reveal]').forEach(x=>x.classList.add('visible'));const count=part.querySelector('[data-count]');if(count)count.click();partTimers.set(part,setTimeout(()=>part.classList.remove('is-replaying'),2600));}));
$('#tl-expand').addEventListener('click',()=>{pause();$('#tl-dialog-mount').append(studio);dialog.showModal();prepare();});
dialog.addEventListener('close',()=>{pause();$('#tl-studio-anchor').after(studio);prepare();$('#tl-expand').focus({preventScroll:true});});
// Native tab semantics for the existing blocks, including arrow-key navigation.
function tabState(root,keyClass,paneClass){const keys=[...root.querySelectorAll(keyClass)],panes=[...root.querySelectorAll(paneClass)];keys.forEach((key,i)=>{const on=key.classList.contains('is-on');key.setAttribute('aria-selected',String(on));key.tabIndex=on?0:-1;const prefix=root.closest('[data-part]').dataset.part;key.id=prefix+'-tab-'+i;key.setAttribute('aria-controls',prefix+'-pane-'+i);panes[i].id=prefix+'-pane-'+i;panes[i].setAttribute('role','tabpanel');panes[i].setAttribute('aria-labelledby',key.id);panes[i].hidden=!on;});}
document.querySelectorAll('[data-tabs],[data-toggle]').forEach(root=>{const keys=root.hasAttribute('data-tabs')?'.tb-k':'.tg-k',panes=root.hasAttribute('data-tabs')?'.tb-p':'.tg-p';tabState(root,keys,panes);new MutationObserver(()=>tabState(root,keys,panes)).observe(root,{subtree:true,attributes:true,attributeFilter:['class']});root.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;const all=[...root.querySelectorAll(keys)],i=all.indexOf(e.target);if(i<0)return;e.preventDefault();const next=e.key==='Home'?0:e.key==='End'?all.length-1:(i+(e.key==='ArrowRight'?1:all.length-1))%all.length;all[next].click();all[next].focus();});});
document.querySelectorAll('[data-flip]').forEach(el=>{const sync=()=>{const open=el.classList.contains('is-open');el.setAttribute('aria-pressed',String(open));el.querySelector('.fl-f').setAttribute('aria-hidden',String(open));el.querySelector('.fl-b').setAttribute('aria-hidden',String(!open));};sync();new MutationObserver(sync).observe(el,{attributes:true,attributeFilter:['class']});});
document.querySelectorAll('.ac-h').forEach(el=>{const sync=()=>el.closest('.ac-i').querySelector('.ac-b').setAttribute('aria-hidden',String(el.getAttribute('aria-expanded')!=='true'));sync();new MutationObserver(sync).observe(el,{attributes:true,attributeFilter:['aria-expanded']});});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)pause();},{threshold:0}).observe(studio);
new IntersectionObserver(entries=>{const state=entries[0].isIntersecting?'running':'paused';document.querySelectorAll('.hero-orbit,.hero-cube').forEach(el=>el.style.animationPlayState=state);},{threshold:0}).observe($('.tl-hero'));
new ResizeObserver(()=>{const r=canvas.getBoundingClientRect(),size=Math.round(r.width)+'x'+Math.round(r.height);if(!r.width||size===lastSize)return;lastSize=size;cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>prepare());}).observe(canvas);
reduced.addEventListener('change',()=>{pause();play.disabled=reduced.matches;$('#tl-replay').disabled=reduced.matches;activeCaption=-2;time=duration;prepare();});
window.addEventListener('beforeprint',()=>{pause();render(duration);});
play.disabled=reduced.matches;$('#tl-replay').disabled=reduced.matches;
const initial=new URLSearchParams(location.hash.slice(1)).get('figure');select(byId.has(initial)?initial:'dims');
})();
