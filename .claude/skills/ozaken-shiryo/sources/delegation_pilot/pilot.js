/* Local scene controls deliberately leave all letter shortcuts to the existing deck. */
(() => {
  'use strict';
  const body = document.body;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const sections = [...body.querySelectorAll('section')];
  const scenes = [...body.querySelectorAll('.dp-figure')];
  const motionButton = body.querySelector('[data-motion]');
  let paused = reduced.matches;
  let index = 0;
  const animations = new Set();
  const pending = new Map();
  const animatedOnce = new WeakSet();
  const myths = [
    ['精度が上がったら任せる', '外れたときの戻し方から決める', '精度だけを待たず、限定した範囲と確認方法を先に設計する。'],
    ['まず全社に入れる', '小さな1業務で、判断基準を育てる', '効く場所と例外を確かめてから、対象を広げる。'],
    ['任せたら楽になる', '作業の代わりに、決めごとを引き受ける', '材料・確認・停止条件を毎回決め直さずに済む形へ。'],
    ['ルールを完璧にしてから', '範囲を絞り、例外から書き足す', 'まずは外に出るか、最終確認は誰か。試せる境界を決める。'],
    ['AIに仕事を取られる', '自分が担う判断を、具体的にする', '作業と判断を分けると、人が引き受ける役割を考えられる。']
  ];
  function animate(el, frames, opts) {
    if (paused || reduced.matches || document.hidden) return;
    const animation = el.animate(frames, opts);
    animations.add(animation);
    animation.onfinish = animation.oncancel = () => animations.delete(animation);
  }
  function setState(scene, state, user = false) {
    if (user) cancelAuto(scene);
    const tasks = [...scene.querySelectorAll('.dp-task')];
    const before = tasks.map(el => el.getBoundingClientRect());
    scene.dataset.state = String(state);
    scene.querySelectorAll('[data-choice]').forEach(el => el.setAttribute('aria-pressed', String(Number(el.dataset.choice) === state)));
    if (scene.dataset.scene === 'shift') {
      scene.querySelector('[data-shift-title]').textContent = state ? '任せる' : '使う';
      scene.querySelectorAll('[data-before]').forEach(el => {
        el.textContent = state ? el.dataset.after : el.dataset.before;
        animate(el, [{opacity:.15, transform:'translateY(10px)'}, {opacity:1, transform:'none'}], {duration:550, easing:'cubic-bezier(.16,1,.3,1)'});
      });
    }
    if (scene.dataset.scene === 'gate') {
      scene.querySelector('[data-gate-request]').textContent = state ? 'お客様への送信' : '社内メモの下書き';
      const dot = scene.querySelector('.dp-gate-line i');
      animate(dot, [{opacity:0}, {opacity:1}], {duration:650});
    }
    if (scene.dataset.scene === 'tasks') {
      scene.querySelector('[data-task-note]').textContent = state ? '作業を分け、実行・確認・判断の担当を決める' : '大きな名前のままでは、任せる境界が見えない';
      tasks.forEach((el, i) => {
        const after = el.getBoundingClientRect();
        animate(el, [{transform:`translate(${before[i].left-after.left}px, ${before[i].top-after.top}px)`}, {transform:'none'}], {duration:850, easing:'cubic-bezier(.16,1,.3,1)'});
      });
    }
    if (scene.dataset.scene === 'myths') {
      ['before','after','note'].forEach((key, i) => { scene.querySelector(`[data-myth-${key}]`).textContent = myths[state][i]; });
      animate(scene.querySelector('.dp-myth'), [{opacity:.2, transform:'translateY(10px)'}, {opacity:1,transform:'none'}], {duration:550});
    }
  }
  function cancelAuto(scene) {
    const item = pending.get(scene);
    if (item) clearTimeout(item.timer);
    pending.delete(scene);
  }
  function schedule(scene, state, delay) {
    cancelAuto(scene);
    const item = {state, remaining:delay, started:0, timer:null};
    pending.set(scene, item);
    arm(scene, item);
  }
  function arm(scene, item) {
    if (paused || reduced.matches || document.hidden || !scene.closest('section').classList.contains('dp-inview')) return;
    item.started = performance.now();
    item.timer = setTimeout(() => {
      pending.delete(scene);
      setState(scene, item.state);
      if (['layers','return'].includes(scene.dataset.scene) && item.state === 1) schedule(scene, 2, 1800);
    }, item.remaining);
  }
  function hold(scene, item) {
    if (item.timer !== null) {
      clearTimeout(item.timer);
      item.remaining = Math.max(0, item.remaining - (performance.now() - item.started));
      item.timer = null;
    }
  }
  function replay(scene, user = false) {
    cancelAuto(scene);
    setState(scene, 0);
    scene.classList.remove('dp-entered');
    void scene.offsetWidth;
    scene.classList.add('dp-entered');
    if (['shift','gate','layers','tasks','return'].includes(scene.dataset.scene)) {
      if (paused || reduced.matches) setState(scene, ['layers','return'].includes(scene.dataset.scene) ? 2 : 1);
      else schedule(scene, 1, user ? 800 : 1800);
    }
  }
  function syncMotion() {
    body.classList.toggle('dp-still', paused);
    motionButton.setAttribute('aria-pressed', String(paused));
    motionButton.disabled = reduced.matches;
    motionButton.textContent = reduced.matches ? '静止表示' : paused ? '動きを再開' : '動きを止める';
    pending.forEach((item, scene) => { if (paused || document.hidden) hold(scene, item); else if (item.timer === null) arm(scene, item); });
    animations.forEach(animation => { if (paused) animation.finish(); else if(document.hidden) animation.pause(); else animation.play(); });
  }
  motionButton.addEventListener('click', () => { paused = !paused; syncMotion(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; if(paused) scenes.forEach(cancelAuto); syncMotion(); });
  document.addEventListener('visibilitychange', () => {body.classList.toggle('dp-away', document.hidden); syncMotion();});
  scenes.forEach(scene => {
    setState(scene, 0);
    scene.querySelectorAll('[data-choice]').forEach(button => button.addEventListener('click', () => setState(scene, Number(button.dataset.choice), true)));
    scene.querySelector('.dp-replay').addEventListener('click', () => replay(scene, true));
  });
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    const section = entry.target;
    section.classList.toggle('dp-inview', entry.isIntersecting);
    const scene = section.querySelector('.dp-figure');
    if (!scene) return;
    if (entry.isIntersecting && !animatedOnce.has(scene)) { animatedOnce.add(scene); replay(scene); }
    else if (pending.has(scene)) { const item = pending.get(scene); if(entry.isIntersecting && item.timer === null) arm(scene,item); else if(!entry.isIntersecting) hold(scene,item); }
  }), {rootMargin:'-12% 0px -25% 0px', threshold:0});
  sections.forEach(section => observer.observe(section));
  let queued = false;
  function updateNavigation() {
    queued = false;
    const y = window.innerHeight * .35;
    index = sections.reduce((best, section, i) => section.getBoundingClientRect().top <= y ? i : best, 0);
    body.querySelector('.dp-page').textContent = `${index === 0 ? '表紙' : index === 10 ? 'まとめ' : String(index).padStart(2,'0')} / 11`;
    body.querySelector('[data-prev]').disabled = index === 0;
    body.querySelector('[data-next]').disabled = index === sections.length - 1;
  }
  function go(delta) { sections[Math.max(0, Math.min(sections.length-1, index+delta))].scrollIntoView({behavior:paused || reduced.matches ? 'instant':'smooth'}); }
  body.querySelector('[data-prev]').addEventListener('click', () => go(-1));
  body.querySelector('[data-next]').addEventListener('click', () => go(1));
  window.addEventListener('scroll', () => { if (!queued) {queued=true;requestAnimationFrame(updateNavigation);} }, {passive:true});
  window.addEventListener('resize', updateNavigation);
  let printedNotes = [];
  window.addEventListener('beforeprint', () => {
    printedNotes = [...document.querySelectorAll('.dp-notes:not([open])')];
    printedNotes.forEach(notes => {notes.open = true;});
  });
  window.addEventListener('afterprint', () => {
    printedNotes.forEach(notes => {notes.open = false;});
    printedNotes = [];
  });
  document.querySelector('.dp-start').addEventListener('click', event => {event.preventDefault(); sections[1].scrollIntoView({behavior:paused || reduced.matches ? 'instant':'smooth'});});
  // The dock uses clicks only, preserving pr / st / en / go / qr and browser keys.
  syncMotion();
  updateNavigation();
})();
