(function () {
  'use strict';
  var home = document.getElementById('materials-home');
  if (!home) return;
  var hero = home.querySelector('.hero');
  var texture = hero.querySelector('.texture svg');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var stages = Array.from(document.querySelectorAll('.thanks, .boot'));
  function isStageOpen() {
    return stages.some(function (stage) {
      return stage.classList.contains('show') || stage.classList.contains('is-on');
    });
  }
  var stageOpen = isStageOpen();
  var heroInView = false, hasEntered = false, enteringTimer = 0;
  var airTiles = new Map();
  var airObserver = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (airTiles.has(entry.target)) airTiles.set(entry.target, entry.isIntersecting);
    });
    syncMotion();
  }) : null;
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
    var canAnimate = !document.hidden && !reduced.matches && !stageOpen;
    var visible = heroInView && canAnimate;
    setHeroMotion(visible);
    if (visible) startEntrance(); else finishEntrance();
    ambientSections.forEach(function (section) {
      section.element.classList.toggle('mh-ambient-active', section.inView && canAnimate);
    });
    airTiles.forEach(function (inView, tile) {
      tile.classList.toggle('is-active', inView && canAnimate);
    });
  }
  // Tile long sections so the archive has movement throughout without one huge animated layer.
  // Decorations never contain information and never take focus or pointer events.
  var airSurfaces = Array.from(home.querySelectorAll(':scope > section, :scope > footer')).map(function (section, sectionIndex) {
    section.classList.add('mh-air-surface');
    var layer = document.createElement('div');
    layer.className = 'mh-air';
    layer.setAttribute('aria-hidden', 'true');
    section.prepend(layer);
    return { element: section, layer: layer, index: sectionIndex, count: 0 };
  });
  function sizeAir(surface) {
    var height = surface.element.clientHeight;
    var count = Math.max(1, Math.ceil(height / 720));
    surface.layer.classList.toggle('mh-air-compact', height < 320);
    while (surface.count > count) {
      var last = surface.layer.lastElementChild;
      if (airObserver) airObserver.unobserve(last);
      airTiles.delete(last);
      last.remove();
      surface.count--;
    }
    while (surface.count < count) {
      var tile = document.createElement('div');
      tile.className = 'mh-air-tile';
      tile.style.top = (surface.count * 720) + 'px';
      tile.style.setProperty('--air-phase', -((surface.index * 7 + surface.count * 5) % 19) + 's');
      for (var i = 0; i < 8; i++) {
        var mote = document.createElement('i');
        mote.className = 'mh-air-mote';
        mote.style.setProperty('--i', i);
        mote.style.left = [5, 18, 36, 59, 73, 87, 94, 47][i] + '%';
        mote.style.top = [32, 74, 17, 86, 43, 22, 69, 55][i] + '%';
        tile.appendChild(mote);
      }
      for (var j = 0; j < 2; j++) {
        var ray = document.createElement('i');
        ray.className = 'mh-air-ray';
        ray.style.setProperty('--i', j);
        tile.appendChild(ray);
      }
      surface.layer.appendChild(tile);
      airTiles.set(tile, false);
      if (airObserver) airObserver.observe(tile);
      surface.count++;
    }
    surface.layer.lastElementChild.style.height = (height - (count - 1) * 720) + 'px';
    // A former last tile must regain its normal size when more content becomes visible.
    Array.from(surface.layer.children).slice(0, -1).forEach(function (tile) { tile.style.height = '720px'; });
  }
  airSurfaces.forEach(sizeAir);
  if ('ResizeObserver' in window) {
    var sizeObserver = new ResizeObserver(function (entries) {
      entries.forEach(function (entry) {
        var surface = airSurfaces.find(function (item) { return item.element === entry.target; });
        if (surface) sizeAir(surface);
      });
    });
    airSurfaces.forEach(function (surface) { sizeObserver.observe(surface.element); });
  } else {
    window.addEventListener('resize', function () { airSurfaces.forEach(sizeAir); });
    window.addEventListener('load', function () { airSurfaces.forEach(sizeAir); });
  }
  document.addEventListener('visibilitychange', syncMotion);
  reduced.addEventListener('change', syncMotion);
  if ('MutationObserver' in window) {
    var stageObserver = new MutationObserver(function () {
      var isOpen = isStageOpen();
      if (isOpen === stageOpen) return;
      stageOpen = isOpen;
      syncMotion();
    });
    stages.forEach(function (stage) { stageObserver.observe(stage, { attributes: true, attributeFilter: ['class'] }); });
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
