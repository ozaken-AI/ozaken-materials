(function () {
  'use strict';
  var home = document.getElementById('materials-home');
  if (!home) return;
  var finder = home.querySelector('.mh-finder');
  var search = home.querySelector('#mh-search');
  var category = home.querySelector('#mh-category');
  var status = home.querySelector('#mh-results');
  var empty = home.querySelector('.mh-empty');
  var cards = Array.from(home.querySelectorAll('#archive-cards > .card'));
  function normalize(value) { return value.normalize('NFKC').toLocaleLowerCase('ja').trim(); }
  var catalog = cards.map(function (card, index) {
    var title = card.querySelector('h3').textContent;
    var option = document.createElement('option');
    option.value = String(index); option.textContent = title;
    category.appendChild(option);
    return { card: card, category: normalize(title), items: Array.from(card.querySelectorAll('.doc-list li')).map(function (item) {
      return { element: item, text: normalize(item.textContent) };
    }) };
  });
  var total = catalog.reduce(function (sum, entry) { return sum + entry.items.length; }, 0);
  function filter() {
    var words = normalize(search.value).split(/\s+/).filter(Boolean);
    var count = 0, themes = 0;
    catalog.forEach(function (entry, index) {
      var enabled = category.value === 'all' || category.value === String(index);
      var visible = 0;
      entry.items.forEach(function (item) {
        var matches = enabled && words.every(function (word) { return (entry.category + ' ' + item.text).includes(word); });
        item.element.hidden = !matches;
        if (matches) visible++;
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
  var delay;
  search.addEventListener('input', function () { clearTimeout(delay); delay = setTimeout(filter, 120); });
  category.addEventListener('change', filter);
  finder.addEventListener('reset', function () {
    clearTimeout(delay);
    setTimeout(function () { filter(); search.focus(); }, 0);
  });
  filter();
  var hero = home.querySelector('.hero');
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      hero.classList.toggle('is-in-view', entries[0].isIntersecting);
    }).observe(hero);
  } else { hero.classList.add('is-in-view'); }
})();
