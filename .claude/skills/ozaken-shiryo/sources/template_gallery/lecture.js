/* All meaning is in HTML. The runtime only moves decorative light and connectors. */
(() => {
 'use strict';
 const body=document.body,reduce=matchMedia('(prefers-reduced-motion: reduce)');
 function sync(){body.classList.toggle('tl-still',reduce.matches);body.classList.toggle('tl-away',document.hidden);}
 const observer=new IntersectionObserver(entries=>entries.forEach(e=>e.target.classList.toggle('is-inview',e.isIntersecting)),{threshold:0.05});
 document.querySelectorAll('[data-ambient-zone]').forEach(el=>observer.observe(el));
 document.querySelectorAll('.lab-packet[data-travel]').forEach(el=>{
  el.style.offsetPath=`path('${el.dataset.travel}')`;
  el.setAttribute('data-ready','');
 });
 function anchor(){
  const id=location.hash.match(/^#figure=([a-z0-9_-]+)$/)?.[1];
  if(id)document.getElementById('figure-'+id)?.scrollIntoView({behavior:'instant',block:'start'});
 }
 window.addEventListener('hashchange',anchor);
 window.addEventListener('load',anchor);
 document.fonts.ready.then(anchor);
 reduce.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);
 sync();
 // Shared keynav retains the existing hidden commands. No content-toggle handlers.
})();
