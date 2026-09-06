(function () {
  'use strict';
  var home = document.getElementById('materials-home');
  if (!home) return;
  var finder = home.querySelector('.mh-finder');
  var category = home.querySelector('#mh-category');
  var status = home.querySelector('#mh-results');
  var empty = home.querySelector('.mh-empty');
  var cards = Array.from(home.querySelectorAll('#archive-cards > .card'));
  var catalog = cards.map(function (card, index) {
    var title = card.querySelector('h3').textContent;
    var option = document.createElement('option');
    option.value = String(index); option.textContent = title;
    category.appendChild(option);
    return { card: card, items: Array.from(card.querySelectorAll('.doc-list li')) };
  });
  var total = catalog.reduce(function (sum, entry) { return sum + entry.items.length; }, 0);
  function filter() {
    var count = 0, themes = 0;
    catalog.forEach(function (entry, index) {
      var enabled = category.value === 'all' || category.value === String(index);
      var visible = enabled ? entry.items.length : 0;
      entry.items.forEach(function (item) {
        item.hidden = !enabled;
      });
      entry.card.hidden = !visible;
      count += visible;
      if (visible) themes++;
    });
    status.textContent = count + ' / ' + total + '件の資料 · ' + themes + 'テーマ';
    empty.hidden = count > 0;
  }
  finder.hidden = false; status.hidden = false;
  finder.addEventListener('submit', function (event) { event.preventDefault(); });
  category.addEventListener('change', filter);
  finder.addEventListener('reset', function () {
    setTimeout(function () { filter(); category.focus(); }, 0);
  });
  filter();
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
    enteringTimer = setTimeout(finishEntrance, 1800);
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
