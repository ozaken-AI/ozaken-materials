(function () {
  'use strict';
  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var mission = profile.querySelector('.pfv-mission');
  var network = profile.querySelector('.pfv-network');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var running = [];
  var nav = profile.querySelector('.pfv-nav');
  var previousFocus = null;
  var frame = 0;
  profile.setAttribute('aria-modal', 'true');
  function cancelSignals() {
    running.forEach(function (animation) { animation.cancel(); });
    running = [];
    network.querySelectorAll('.pfv-signal').forEach(function (signal) { signal.remove(); });
  }
  function connect() {
    cancelSignals();
    if (reduced.matches || !profile.classList.contains('show')) return;
    var rect = network.getBoundingClientRect();
    if (!rect.width) return;
    network.querySelectorAll('.pfv-endpoint').forEach(function (endpoint, index) {
      var target = endpoint.getBoundingClientRect();
      var x = target.left + target.width / 2 - rect.left - rect.width / 2;
      var y = target.top + target.height / 2 - rect.top - rect.height / 2;
      var signal = document.createElement('i');
      signal.className = 'pfv-signal';
      signal.setAttribute('aria-hidden', 'true');
      network.appendChild(signal);
      var animation = signal.animate([
        { transform:'translate(0,0)', opacity:0 },
        { transform:'translate(0,0)', opacity:1, offset:.08 },
        { transform:'translate(' + x + 'px,' + y + 'px)', opacity:1, offset:.8 },
        { transform:'translate(' + x + 'px,' + y + 'px)', opacity:0 }
      ], { duration:1700, delay:index * 170 + 150, easing:'cubic-bezier(.35,0,.3,1)', fill:'both' });
      running.push(animation);
      animation.onfinish = function () { signal.remove(); };
    });
  }
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting && profile.classList.contains('show')) connect();
    });
  }, { root:profile, threshold:.5 });
  observer.observe(network);
  profile.querySelector('.pfv-replay').addEventListener('click', function () {
    mission.classList.remove('visible');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { mission.classList.add('visible'); connect(); });
    });
  });
  var sections = Array.from(nav.querySelectorAll('[data-pfv-target]')).map(function (button) {
    var section = document.getElementById(button.dataset.pfvTarget);
    button.addEventListener('click', function () {
      if (!section) return;
      profile.scrollTo({ top:section.offsetTop - (section.id === 'pfv-person' ? 0 : 78), behavior:reduced.matches ? 'auto' : 'smooth' });
    });
    return {button:button, section:section};
  });
  function updateNav() {
    frame = 0;
    var selected = sections[0];
    sections.forEach(function (item) { if (item.section && item.section.getBoundingClientRect().top <= profile.clientHeight * .38) selected = item; });
    sections.forEach(function (item) { item.button.setAttribute('aria-current', String(item === selected)); });
  }
  profile.addEventListener('scroll', function () { if (!frame) frame = requestAnimationFrame(updateNav); }, {passive:true});
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Tab' || !profile.classList.contains('show')) return;
    var focusable = Array.from(profile.querySelectorAll('button:not([disabled]),a[href],input,select,textarea')).filter(function (element) { return element.getClientRects().length > 0; });
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || !profile.contains(document.activeElement))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !profile.contains(document.activeElement))) {
      event.preventDefault(); first.focus();
    }
  });
  new MutationObserver(function () {
    if (profile.classList.contains('show')) {
      previousFocus = document.activeElement;
      profile.querySelector('.pf-close').focus({preventScroll:true});
      updateNav();
    } else {
      cancelSignals();
      if (previousFocus && previousFocus.isConnected && !profile.contains(previousFocus)) previousFocus.focus({preventScroll:true});
    }
  }).observe(profile, {attributes:true, attributeFilter:['class']});
  reduced.addEventListener('change', function () { if (reduced.matches) cancelSignals(); });
  updateNav();
})();
