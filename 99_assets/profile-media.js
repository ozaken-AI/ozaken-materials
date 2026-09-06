(function () {
  'use strict';

  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var slots = ['portrait', 'lecture', 'community', 'field'];

  function imageURL(source) {
    if (typeof source !== 'string' || !source.trim()) return null;
    source = source.trim();
    if (/^data:/i.test(source)) {
      return /^data:image\/(?:png|jpe?g|webp|gif|avif|bmp|x-icon|vnd\.microsoft\.icon)(?:;[^,]*)?,/i.test(source) ? source : null;
    }
    try {
      var url = new URL(source, document.baseURI);
      if (url.protocol === 'http:' || url.protocol === 'https:') return url.href;
      // Relative assets also work when the standalone preview is opened as a file.
      if (!/^[a-z][a-z0-9+.-]*:/i.test(source) && url.protocol === 'file:' && location.protocol === 'file:') return url.href;
    } catch (error) { /* Leave the designed placeholder visible. */ }
    return null;
  }

  function applyMedia(config) {
    if (!config || typeof config !== 'object') return;
    slots.forEach(function (key) {
      var entry = config[key];
      if (!entry || typeof entry !== 'object') return;
      profile.querySelectorAll('[data-profile-media="' + key + '"]').forEach(function (slot) {
        var img = slot.matches('img') ? slot : slot.querySelector('img');
        var frame = slot.closest('[data-profile-media-frame]');
        if (!img || !frame) return;
        var src = imageURL(entry.src);
        frame.classList.remove('has-media');
        img.hidden = true;
        img.removeAttribute('src');
        if (typeof entry.alt === 'string') img.setAttribute('alt', entry.alt);
        if (typeof entry.objectPosition === 'string') img.style.objectPosition = entry.objectPosition;
        img.onload = function () {
          if (!img.naturalWidth) return;
          img.hidden = false;
          frame.classList.add('has-media');
        };
        img.onerror = function () {
          img.hidden = true;
          frame.classList.remove('has-media');
        };
        if (src) img.src = src;
      });
    });
  }

  if (window.OZAKEN_PROFILE_MEDIA) {
    applyMedia(window.OZAKEN_PROFILE_MEDIA);
  } else {
    fetch('99_assets/profile-media.json')
      .then(function (response) {
        if (!response.ok) throw new Error('Profile media is unavailable');
        return response.json();
      })
      .then(applyMedia)
      .catch(function () { /* Existing portrait and optional placeholders remain. */ });
  }
}());
