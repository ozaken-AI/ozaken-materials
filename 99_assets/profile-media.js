(function () {
  'use strict';

  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var keys = ['portrait', 'lecture', 'community', 'field', 'course', 'public', 'policy'];
  var slides = Array.from(profile.querySelectorAll('.pd-slide'));
  var media = [], ready = false;

  function imageURL(source) {
    if (typeof source !== 'string' || !source.trim()) return null;
    source = source.trim();
    if (/^data:/i.test(source)) {
      return /^data:image\/(?:png|jpe?g|webp|gif|avif|bmp|x-icon|vnd\.microsoft\.icon)(?:;[^,]*)?,/i.test(source) ? source : null;
    }
    try {
      var url = new URL(source, document.baseURI);
      if (url.protocol === 'http:' || url.protocol === 'https:') return url.href;
      // Relative assets also work in a standalone file preview.
      if (!/^[a-z][a-z0-9+.-]*:/i.test(source) && url.protocol === 'file:' && location.protocol === 'file:') return url.href;
    } catch (error) { /* Keep the designed placeholder. */ }
    return null;
  }

  function loadImage(item) {
    if (item.started) return;
    item.started = true;
    if (!item.src) return;
    var img = item.img;
    img.onload = function () {
      if (!img.naturalWidth) return;
      img.hidden = false;
      item.frame.classList.add('has-media');
    };
    img.onerror = function () {
      img.hidden = true;
      item.frame.classList.remove('has-media');
    };
    img.src = item.src;
  }

  function loadNearby() {
    if (!ready || !profile.classList.contains('show')) return;
    var active = slides.findIndex(function (slide) { return slide.classList.contains('is-active'); });
    if (active < 0) active = 0;
    // Start the visible image before the previous and next screen.
    [active, active - 1, active + 1].forEach(function (index) {
      media.forEach(function (item) { if (item.slide === index) loadImage(item); });
    });
  }

  function configure(config) {
    config = config && typeof config === 'object' ? config : {};
    keys.forEach(function (key) {
      var entry = config[key] || {};
      profile.querySelectorAll('[data-profile-media="' + key + '"]').forEach(function (slot) {
        var img = slot.matches('img') ? slot : slot.querySelector('img');
        var frame = slot.closest('[data-profile-media-frame]');
        if (!img || !frame) return;
        var fallback = img.getAttribute('data-profile-src') || img.getAttribute('src');
        var source = typeof entry.src === 'string' ? entry.src : fallback;
        var position = typeof entry.objectPosition === 'string' ? entry.objectPosition : img.getAttribute('data-profile-position');
        if (typeof entry.alt === 'string') img.setAttribute('alt', entry.alt);
        if (position) img.style.objectPosition = position;
        img.hidden = true;
        img.removeAttribute('src');
        frame.classList.remove('has-media');
        media.push({img:img, frame:frame, src:imageURL(source), slide:slides.indexOf(slot.closest('.pd-slide')), started:false});
      });
    });
    ready = true;
    loadNearby();
  }

  new MutationObserver(function (changes) {
    if (changes.some(function (change) { return change.target === profile || change.target.matches('.pd-slide'); })) loadNearby();
  }).observe(profile, {attributes:true, subtree:true, attributeFilter:['class']});

  if (window.OZAKEN_PROFILE_MEDIA) {
    configure(window.OZAKEN_PROFILE_MEDIA);
  } else if (location.protocol === 'file:') {
    configure({});
  } else {
    fetch('99_assets/profile-media.json')
      .then(function (response) {
        if (!response.ok) throw new Error('Profile media settings are unavailable');
        return response.json();
      })
      .then(configure)
      .catch(function () { configure({}); });
  }
}());
