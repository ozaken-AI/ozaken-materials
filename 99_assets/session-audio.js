(function () {
  'use strict';
  var script = document.currentScript;
  var startGrace = 1200;
  var current = null;
  var tracks = {};
  var sources = {
    start: new URL('audio/session-start-v1.wav', script.src).href,
    end: new URL('audio/session-end-v1.wav', script.src).href
  };

  function prepare(mode) {
    var audio = document.createElement('audio');
    audio.hidden = true;
    audio.preload = 'auto';
    audio.setAttribute('aria-hidden', 'true');
    audio.setAttribute('data-session-audio', mode);
    audio.setAttribute('data-session-state', 'ready');
    audio.src = sources[mode];
    document.body.appendChild(audio);
    return {audio:audio, used:false};
  }

  function silence(audio) {
    audio.pause();
    try { audio.currentTime = 0; } catch (error) { /* Metadata may not have loaded yet. */ }
  }

  function finish(attempt, state) {
    attempt.cancelled = true;
    clearTimeout(attempt.timer);
    attempt.audio.removeEventListener('playing', attempt.onPlaying);
    attempt.audio.removeEventListener('ended', attempt.onEnded);
    attempt.audio.removeEventListener('error', attempt.onError);
    silence(attempt.audio);
    attempt.audio.setAttribute('data-session-state', state);
    if (current === attempt) current = null;
  }

  function stop() {
    if (current) finish(current, 'stopped');
  }

  function play(mode) {
    stop();
    if ((mode !== 'start' && mode !== 'end') || document.hidden) return;
    var track = tracks[mode];
    // Never reuse an attempted element: a late play promise can only silence its own audio.
    if (track.used) {
      track.audio.remove();
      track = tracks[mode] = prepare(mode);
    }
    track.used = true;
    var attempt = {audio:track.audio, started:false, cancelled:false, deadline:Date.now()+startGrace, timer:0};
    current = attempt;
    attempt.audio.setAttribute('data-session-state', 'pending');
    attempt.onPlaying = function () {
      if (attempt.cancelled || current !== attempt) { silence(attempt.audio); return; }
      if (attempt.started) return;
      if (Date.now() > attempt.deadline) { finish(attempt, 'timed-out'); return; }
      attempt.started = true;
      clearTimeout(attempt.timer);
      attempt.audio.setAttribute('data-session-state', 'playing');
    };
    attempt.onEnded = function () { finish(attempt, 'ended'); };
    attempt.onError = function () { finish(attempt, 'unavailable'); };
    attempt.audio.addEventListener('playing', attempt.onPlaying);
    attempt.audio.addEventListener('ended', attempt.onEnded);
    attempt.audio.addEventListener('error', attempt.onError);
    attempt.timer = setTimeout(function () {
      if (current === attempt && !attempt.started) finish(attempt, 'timed-out');
    }, startGrace);
    // Keep this native play call in the caller's user-activation turn.
    try {
      var result = attempt.audio.play();
      if (result && typeof result.then === 'function') {
        result.then(attempt.onPlaying, function () {
          if (attempt.cancelled || current !== attempt) { silence(attempt.audio); return; }
          finish(attempt, 'unavailable');
        });
      }
    } catch (error) {
      finish(attempt, 'unavailable');
    }
  }

  tracks.start = prepare('start');
  tracks.end = prepare('end');
  window.ozSessionAudio = {play:play, stop:stop};
  document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); });
  window.addEventListener('pagehide', stop);
}());
