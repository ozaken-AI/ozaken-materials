/* OZ-COVER: only decoration changes state; text is complete in the source HTML. */
(() => {
  const covers = [...document.querySelectorAll('[data-oz-cover]')];
  if (!covers.length) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const visible = new Set();
  const sync = () => covers.forEach(cover => cover.classList.toggle('oz-cover-running',
    visible.has(cover) && !document.hidden && !reduce.matches));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target));
      sync();
    }, {threshold: 0});
    covers.forEach(cover => observer.observe(cover));
  } else { covers.forEach(cover => visible.add(cover)); sync(); }
  document.addEventListener('visibilitychange', sync);
  reduce.addEventListener('change', sync);
})();
