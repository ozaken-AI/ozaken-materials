/* Content is complete in HTML. Motion changes only decorative emphasis. */
(() => {
  'use strict';
  const body = document.body;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  function sync() { body.classList.toggle('dp-still', reduce.matches); body.classList.toggle('dp-away', document.hidden); }
  const observer = new IntersectionObserver(entries => entries.forEach(({target,isIntersecting}) => {
    target.classList.toggle('dp-inview', isIntersecting);
  }), {threshold:0.12});
  document.querySelectorAll('main section, body > section').forEach(section => observer.observe(section));
  reduce.addEventListener('change', sync);
  document.addEventListener('visibilitychange', sync);
  sync();
  // No key handlers: pr / st / en / go / qr remain owned by the shared deck.
})();
