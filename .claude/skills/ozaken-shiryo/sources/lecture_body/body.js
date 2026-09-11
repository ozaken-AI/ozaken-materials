/* OZ-LECTURE-BODY v1. Only aria-hidden decoration and transient hover styling. */
(() => {
  'use strict';
  const body = document.body;
  if (!body.hasAttribute('data-oz-lecture') || body.dataset.ozLayout === 'pilot') return;
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const visible = new Set();
  let printing = false;
  const sync = () => {
    document.querySelectorAll('.oz-body-running').forEach(el => el.classList.remove('oz-body-running'));
    if (!media.matches && !document.hidden && !printing) visible.forEach(el => el.classList.add('oz-body-running'));
  };
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
    entries.forEach(e => e.isIntersecting ? visible.add(e.target) : visible.delete(e.target));
    sync();
  }, {rootMargin:'60px',threshold:0}) : null;
  const observe = el => {if (observer) observer.observe(el);};
  const pages = [...document.querySelectorAll('[data-oz-page]')];
  pages.forEach(page => {
    const atmosphere = document.createElement('div');
    atmosphere.className = 'oz-body-atmosphere';
    atmosphere.setAttribute('aria-hidden','true');
    page.prepend(atmosphere);
    const resize = () => {
      const count = Math.max(1, Math.ceil(page.clientHeight / 720));
      while (atmosphere.children.length > count) {
        const tile = atmosphere.lastElementChild;
        observer?.unobserve(tile);visible.delete(tile);tile.remove();
      }
      while (atmosphere.children.length < count) {
        const tile = document.createElement('div');
        tile.className = 'lecture-air';tile.style.top = `${atmosphere.children.length * 720}px`;
        tile.append(document.createElement('i'));atmosphere.append(tile);observe(tile);
      }
    };
    resize();
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(page);
  });
  // Keep every original connector complete; a separate highlight travels over it.
  pages.forEach(page => page.querySelectorAll('.figure').forEach(figure => {
    figure.querySelectorAll('path.a-flow,line.a-flow,polyline.a-flow').forEach((base,index) => {
      if (index >= 12 || base.closest('defs') || !base.getTotalLength) return;
      const signal = base.cloneNode(false);
      signal.removeAttribute('id');signal.removeAttribute('style');
      signal.setAttribute('class','oz-body-signal');signal.setAttribute('aria-hidden','true');
      signal.setAttribute('marker-start','none');signal.setAttribute('marker-end','none');
      signal.setAttribute('stroke', getComputedStyle(base).stroke);
      signal.setAttribute('stroke-width',getComputedStyle(base).strokeWidth);
      signal.style.animationDelay = `${-index * .7}s`;
      base.after(signal);
    });
    observe(figure);
  }));
  // Tables remain complete. Hover never changes values or selects a content view.
  document.querySelectorAll('[data-oz-page] .tbl,[data-oz-page] table').forEach(table => {
    const clear = () => table.querySelectorAll('.oz-body-column').forEach(el => el.classList.remove('oz-body-column'));
    table.addEventListener('pointerover', e => {
      if (!fine.matches) return;
      const cell = e.target.closest('.td,.th,td,th');
      if (!cell || !table.contains(cell)) return;
      const index = [...cell.parentElement.children].indexOf(cell);
      clear();
      table.querySelectorAll('.tr,tr').forEach(row => row.children[index]?.classList.add('oz-body-column'));
    });
    table.addEventListener('pointerleave',clear);
  });
  media.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  addEventListener('beforeprint',() => {printing = true;sync();});
  addEventListener('afterprint',() => {printing = false;sync();});
})();
