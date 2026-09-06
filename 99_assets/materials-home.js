(function () {
  'use strict';
  var home = document.getElementById('materials-home');
  if (!home) return;
  var hero = home.querySelector('.hero');
  var texture = hero.querySelector('.texture svg');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var profile = document.getElementById('profile-fs');
  var profileOpen = Boolean(profile && profile.classList.contains('show'));
  var heroInView = false, hasEntered = false, enteringTimer = 0;
  var ambientSections = Array.from(home.querySelectorAll('.sec-light, .sec-navy, .sec-download, .nl-band')).map(function (section) {
    section.classList.add('mh-ambient');
    return {
      element: section,
      // The archive is long; animate its bounded backdrop only near the heading.
      target: section.id === 'archive' ? section.querySelector('.mh-archive-top') || section : section,
      inView: false
    };
  });
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
  function syncMotion() {
    var canAnimate = !document.hidden && !reduced.matches && !profileOpen;
    var visible = heroInView && canAnimate;
    setHeroMotion(visible);
    if (visible) startEntrance(); else finishEntrance();
    ambientSections.forEach(function (section) {
      section.element.classList.toggle('mh-ambient-active', section.inView && canAnimate);
    });
  }
  document.addEventListener('visibilitychange', syncMotion);
  reduced.addEventListener('change', syncMotion);
  if (profile && 'MutationObserver' in window) {
    new MutationObserver(function () {
      var isOpen = profile.classList.contains('show');
      if (isOpen === profileOpen) return;
      profileOpen = isOpen;
      syncMotion();
    }).observe(profile, { attributes: true, attributeFilter: ['class'] });
  }
  syncMotion();
  if ('IntersectionObserver' in window) {
    var motionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.target === hero) {
          heroInView = entry.isIntersecting;
          return;
        }
        var section = ambientSections.find(function (item) { return item.target === entry.target; });
        if (section) section.inView = entry.isIntersecting;
      });
      syncMotion();
    });
    motionObserver.observe(hero);
    ambientSections.forEach(function (section) { motionObserver.observe(section.target); });
  } else {
    // Keep section backdrops still when visibility cannot be observed.
    heroInView = true;
    syncMotion();
  }
})();
