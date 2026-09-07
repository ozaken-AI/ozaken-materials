/* No browser or audio device required: exercise cancellation and late native play promises. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../99_assets/session-audio.js'), 'utf8');

function setup() {
  let now = 0, nextTimer = 0;
  const timers = new Map(), allTimers = new Map(), nodes = [], documentEvents = {}, windowEvents = {};
  class Audio {
    constructor() { this.attrs = {}; this.events = {}; this.paused = true; this.currentTime = 0; this.playCalls = 0; }
    setAttribute(name, value) { this.attrs[name] = value; }
    getAttribute(name) { return this.attrs[name]; }
    addEventListener(name, fn) { this.events[name] = fn; }
    removeEventListener(name, fn) { if (this.events[name] === fn) delete this.events[name]; }
    remove() { nodes.splice(nodes.indexOf(this), 1); }
    pause() { this.paused = true; }
    play() {
      this.playCalls++;
      if (this.throwOnPlay) throw new Error('Unsupported media');
      return new Promise((resolve, reject) => {
        this.resolve = () => { this.paused = false; resolve(); };
        this.reject = reject;
      });
    }
    emit(name) { if (name === 'playing') this.paused = false; if (this.events[name]) this.events[name](); }
  }
  const document = {
    hidden:false,
    currentScript:{src:'https://example.test/materials/99_assets/session-audio.js?v=abc'},
    body:{appendChild(node) { nodes.push(node); }},
    createElement(tag) { assert.equal(tag, 'audio'); return new Audio(); },
    addEventListener(name, fn) { documentEvents[name] = fn; }
  };
  const window = {addEventListener(name, fn) { windowEvents[name] = fn; }};
  vm.runInNewContext(source, {
    document, window, URL, Date:{now:() => now},
    setTimeout(fn, ms) { const id = ++nextTimer; timers.set(id, fn); allTimers.set(id, {fn, ms}); return id; },
    clearTimeout(id) { timers.delete(id); }
  });
  return {
    api:window.ozSessionAudio, nodes, timers, allTimers,
    audio(mode) { return nodes.find(node => node.attrs['data-session-audio'] === mode); },
    time(value) { now = value; },
    hide(value) { document.hidden = value; documentEvents.visibilitychange(); },
    pagehide() { windowEvents.pagehide(); }
  };
}
const state = audio => audio.getAttribute('data-session-state');
const flush = () => Promise.resolve();

(async function () {
  const initial = setup();
  assert.equal(initial.nodes.length, 2);
  for (const mode of ['start', 'end']) {
    const audio = initial.audio(mode);
    assert(audio.hidden && audio.preload === 'auto' && audio.paused);
    assert.equal(audio.src, 'https://example.test/materials/99_assets/audio/session-'+mode+'-v1.wav');
    assert.equal(audio.playCalls, 0);
  }
  initial.api.play('start');
  const started = initial.audio('start');
  assert.equal(started.playCalls, 1, 'native play must run synchronously');
  assert.equal(state(started), 'pending');
  assert.equal([...initial.allTimers.values()][0].ms, 1200);
  started.emit('playing'); started.resolve(); await flush();
  assert.equal(state(started), 'playing'); assert.equal(initial.timers.size, 0);
  started.currentTime = 3;
  initial.api.stop();
  assert(started.paused && started.currentTime === 0); assert.equal(state(started), 'stopped');

  const late = setup(); late.api.play('start');
  const old = late.audio('start'), oldTimeout = [...late.allTimers.values()][0].fn;
  late.api.stop(); late.api.play('start');
  const replacement = late.audio('start');
  assert.notEqual(old, replacement, 'same-mode replay needs an independent audio element');
  replacement.resolve(); await flush(); old.resolve(); await flush(); oldTimeout();
  assert(old.paused && !replacement.paused); assert.equal(state(replacement), 'playing');

  const switchMode = setup(); switchMode.api.play('start');
  const first = switchMode.audio('start');
  switchMode.api.play('end');
  const end = switchMode.audio('end'); end.resolve(); await flush();
  first.reject(new Error('Aborted older play')); await flush();
  assert(first.paused && !end.paused); assert.equal(state(end), 'playing');

  const timeout = setup(); timeout.api.play('end');
  const delayed = timeout.audio('end'); timeout.time(1200);
  [...timeout.timers.values()][0]();
  assert.equal(state(delayed), 'timed-out'); delayed.resolve(); await flush(); assert(delayed.paused);
  const delayedTimer = setup(); delayedTimer.api.play('start'); delayedTimer.time(1201);
  const tooLate = delayedTimer.audio('start'); tooLate.resolve(); await flush();
  assert(tooLate.paused); assert.equal(state(tooLate), 'timed-out');

  const rejected = setup(); rejected.api.play('start');
  const blocked = rejected.audio('start'); blocked.reject(new Error('NotAllowedError')); await flush();
  assert(blocked.paused); assert.equal(state(blocked), 'unavailable'); assert.equal(rejected.timers.size, 0);
  const missing = setup(); missing.api.play('end'); const absent = missing.audio('end'); absent.emit('error');
  absent.resolve(); await flush(); assert(absent.paused); assert.equal(state(absent), 'unavailable');
  const thrown = setup(); thrown.audio('start').throwOnPlay = true;
  assert.doesNotThrow(() => thrown.api.play('start')); assert.equal(state(thrown.audio('start')), 'unavailable');

  const lifecycle = setup(); lifecycle.api.play('start'); const hidden = lifecycle.audio('start');
  lifecycle.hide(true); hidden.resolve(); await flush(); assert(hidden.paused);
  lifecycle.api.play('end'); assert.equal(lifecycle.audio('end').playCalls, 0);
  lifecycle.hide(false); assert(hidden.paused, 'visibility restoration must not restart playback');
  lifecycle.api.play('end'); const exiting = lifecycle.audio('end'); exiting.resolve(); await flush();
  lifecycle.pagehide(); assert(exiting.paused); assert.equal(state(exiting), 'stopped');
  lifecycle.api.stop(); lifecycle.api.stop();

  const ended = setup(); ended.api.play('end'); const complete = ended.audio('end');
  complete.emit('playing'); complete.emit('ended'); complete.resolve(); await flush();
  assert(complete.paused); assert.equal(state(complete), 'ended');
  console.log('PASS: preloading, synchronous play, 1200ms deadline, stop/replay/switch races, late promises/timers, failures, visibility/pagehide, and ended cleanup');
}()).catch(error => { console.error(error); process.exitCode = 1; });
