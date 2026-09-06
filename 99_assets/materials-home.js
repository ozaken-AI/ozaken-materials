(function () {
  'use strict';
  var home = document.getElementById('materials-home');
  if (!home) return;
  var hero = home.querySelector('.hero');
  var texture = hero.querySelector('.texture svg');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var heroInView = false, hasEntered = false, enteringTimer = 0;
  function setHeroMotion(visible) {
    hero.classList.toggle('is-in-view', visible);
    if (texture && typeof texture.pauseAnimations === 'function') {
      if (visible) texture.unpauseAnimations(); else texture.pauseAnimations();
    }
  }
  function finishEntrance() {
    clearTimeout(enteringTimer);
    enteringTimer = 0;
    hero.classList.remove('is-entering');
  }
  function startEntrance() {
    if (hasEntered) return;
    hasEntered = true;
    hero.classList.add('is-entering');
    enteringTimer = setTimeout(finishEntrance, 3000);
  }
  function syncHeroMotion() {
    var visible = heroInView && !document.hidden && !reduced.matches;
    setHeroMotion(visible);
    if (visible) startEntrance(); else finishEntrance();
  }
  document.addEventListener('visibilitychange', syncHeroMotion);
  reduced.addEventListener('change', syncHeroMotion);
  syncHeroMotion();
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      heroInView = entries[0].isIntersecting;
      syncHeroMotion();
    }).observe(hero);
  } else {
    heroInView = true;
    syncHeroMotion();
  }
})();
