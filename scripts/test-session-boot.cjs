'use strict';

// Execute the actual inline controller against a deterministic DOM/clock.
// The audio adapter has its own tests; this verifies its integration with the 6.8s visual timeline.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]
  .filter(match => /window\.ozBoot\s*=/.test(match[1]));
assert.equal(scripts.length, 1, 'index.html must contain exactly one boot controller');
const source = scripts[0][1];
const bootTag = /<div\b[^>]*\bid="boot"[^>]*>/.exec(html);
assert.ok(bootTag, 'the real boot dialog is present');
const bootHtml = html.slice(bootTag.index, scripts[0].index);
for (const id of ['bootPct', 'bootProc', 'bootVo', 'bootSkip']) {
  assert.ok(bootHtml.includes('id="' + id + '"'), 'the boot markup retains ' + id);
}
const lineCount = [...bootHtml.matchAll(/class="lbl"/g)].length;
assert.equal(lineCount, 6, 'the visual sequence has six status rows');

function makeClock() {
  let now = 0, nextId = 0;
  const timers = new Map();
  function add(callback, delay, kind) {
    const id = ++nextId;
    timers.set(id, { callback, at: now + delay, delay, kind });
    return id;
  }
  return {
    now: () => now,
    timeout: (callback, delay = 0) => add(callback, delay, 'timeout'),
    interval: (callback, delay) => add(callback, delay, 'interval'),
    raf: callback => add(() => callback(now), 16, 'raf'),
    cancel: id => timers.delete(id),
    pending: kind => [...timers.values()].filter(timer => !kind || timer.kind === kind).length,
    advance(milliseconds) {
      const end = now + milliseconds;
      for (let guard = 0; guard < 10000; guard++) {
        const next = [...timers.entries()]
          .filter(([, timer]) => timer.at <= end)
          .sort((a, b) => a[1].at - b[1].at || a[0] - b[0])[0];
        if (!next) { now = end; return; }
        const [id, timer] = next;
        now = timer.at;
        if (timer.kind === 'interval') timer.at += timer.delay;
        else timers.delete(id);
        timer.callback();
      }
      throw new Error('Unexpected timer loop');
    }
  };
}

function fixture({ reduce = false, audioPresent = true } = {}) {
  const clock = makeClock(), events = [];
  class Element {
    constructor(classes = '') {
      this.classes = new Set(classes.split(' ').filter(Boolean));
      this.attributes = {}; this.listeners = {}; this.textContent = '';
      this.classList = {
        contains: name => this.classes.has(name),
        add: (...names) => names.forEach(name => this.classes.add(name)),
        remove: (...names) => names.forEach(name => this.classes.delete(name)),
        toggle: (name, ...force) => {
          const enabled = force.length ? Boolean(force[0]) : !this.classes.has(name);
          if (enabled) this.classes.add(name); else this.classes.delete(name);
          return enabled;
        }
      };
    }
    get offsetWidth() { return 1280; }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return this.attributes[name] ?? null; }
    addEventListener(name, callback) { (this.listeners[name] ??= []).push(callback); }
    fire(name) {
      const event = { propagationStopped: false, stopPropagation() { this.propagationStopped = true; } };
      (this.listeners[name] || []).forEach(callback => callback(event));
      return event;
    }
  }
  const root = new Element(), boot = new Element('boot');
  boot.setAttribute('aria-hidden', 'true');
  const ids = { boot };
  for (const id of ['bootPct', 'bootProc', 'bootVo', 'bootSkip']) ids[id] = new Element();
  const selectors = {};
  for (const selector of ['.boot-tag', '.boot-bar-head span', '.bf-mod', '.bf-lead', '.bf-name', '.bf-sub']) {
    selectors[selector] = new Element();
  }
  selectors['#bootProc'] = ids.bootProc;
  const lines = Array.from({ length: lineCount }, () => new Element());
  boot.querySelector = selector => selectors[selector] || null;
  boot.querySelectorAll = selector => selector === '.boot-term .lbl' ? lines : [];
  let audioPlaying = false;
  const window = { matchMedia: () => ({ matches: reduce }) };
  if (audioPresent) {
    window.ozSessionAudio = {
      play(mode) { audioPlaying = true; events.push({ type: 'play', mode, at: clock.now() }); },
      stop() { audioPlaying = false; events.push({ type: 'stop', at: clock.now() }); }
    };
  }
  vm.runInNewContext(source, {
    window,
    document: { documentElement: root, getElementById: id => ids[id] || null },
    performance: { now: clock.now },
    setTimeout: clock.timeout, clearTimeout: clock.cancel,
    setInterval: clock.interval, clearInterval: clock.cancel,
    requestAnimationFrame: clock.raf, cancelAnimationFrame: clock.cancel
  }, { filename: 'index.html:ozBoot' });
  assert.equal(typeof window.ozBoot, 'function');
  assert.equal(typeof window.ozBootSkip, 'function');
  return { window, root, boot, ids, selectors, lines, clock, events, playing: () => audioPlaying };
}

function completed(f) {
  assert.equal(f.root.classList.contains('boot-locked'), false);
  assert.equal(f.playing(), false);
  assert.equal(f.clock.pending('raf'), 0, 'finish cancels the visual counter');
  assert.equal(f.clock.pending('interval'), 0, 'finish cancels subtitle typing');
}

for (const mode of ['start', 'end']) {
  const f = fixture(); let callbacks = 0;
  f.window.ozBoot(() => { callbacks++; f.events.push({ type: 'callback', at: f.clock.now() }); }, mode);
  assert.deepEqual(f.events, [{ type: 'play', mode, at: 0 }], 'mode reaches the audio adapter synchronously');
  assert.equal(f.boot.classList.contains('is-end'), mode === 'end');
  assert.equal(f.boot.classList.contains('is-on'), true);
  assert.equal(f.root.classList.contains('boot-locked'), true);
  assert.equal(f.boot.getAttribute('aria-hidden'), 'false');
  assert.equal(f.selectors['.bf-mod'].textContent, mode === 'end' ? 'SESSION COMPLETE' : 'SESSION START');
  assert.equal(f.lines[0].textContent, mode === 'end' ? 'SESSION COMPLETE' : 'HUMAN PERSPECTIVE');
  f.clock.advance(6799);
  assert.equal(callbacks, 0); assert.equal(f.playing(), true);
  assert.equal(f.boot.classList.contains('is-done'), false, 'the 6.8s sequence must not finish early');
  assert.equal(f.ids.bootPct.textContent, '100%');
  assert.equal(f.ids.bootVo.textContent.replace(/　/g, ' '), mode === 'end'
    ? 'Session complete. Standing by.' : 'Session start in progress. Systems online.');
  f.clock.advance(1);
  assert.equal(callbacks, 1);
  assert.deepEqual(f.events.slice(1), [{ type: 'stop', at: 6800 }, { type: 'callback', at: 6800 }], 'audio stops before the completion callback');
  completed(f);
  assert.equal(f.boot.classList.contains('is-done'), true);
  f.clock.advance(449); assert.equal(f.boot.getAttribute('aria-hidden'), 'false');
  f.clock.advance(1);
  assert.equal(f.boot.classList.contains('is-on'), false);
  assert.equal(f.boot.classList.contains('is-done'), false);
  assert.equal(f.boot.getAttribute('aria-hidden'), 'true');
  assert.equal(f.clock.pending(), 0, 'no timers survive normal completion');
}

for (const route of ['button', 'background', 'skip-api']) {
  const f = fixture(); let callbacks = 0;
  f.window.ozBoot(() => { callbacks++; }, 'end');
  f.clock.advance(180);
  if (route === 'button') assert.equal(f.ids.bootSkip.fire('click').propagationStopped, true);
  else if (route === 'background') f.boot.fire('click');
  else f.window.ozBootSkip(); // The protected common Escape handler invokes this public API.
  assert.equal(callbacks, 1, route + ' preserves the end-screen callback');
  assert.deepEqual(f.events, [{ type: 'play', mode: 'end', at: 0 }, { type: 'stop', at: 180 }]);
  completed(f);
  const caption = f.ids.bootVo.textContent;
  f.window.ozBootSkip(); f.boot.fire('click');
  f.clock.advance(10000);
  assert.equal(callbacks, 1, 'skip is idempotent');
  assert.equal(f.events.filter(event => event.type === 'stop').length, 1);
  assert.equal(f.ids.bootVo.textContent, caption, 'skipped subtitles never resume');
  assert.equal(f.clock.pending(), 0);
}

{
  const f = fixture(); let first = 0, ignored = 0;
  f.window.ozBoot(() => { first++; }, 'start');
  f.clock.advance(200);
  f.window.ozBoot(() => { ignored++; }, 'end');
  f.window.ozBoot(() => { ignored++; }, 'start');
  assert.equal(f.events.filter(event => event.type === 'play').length, 1, 'repeated commands do not overlap audio');
  assert.equal(f.boot.classList.contains('is-end'), false, 'an ignored command cannot switch visual mode');
  f.clock.advance(6599); assert.equal(first, 0);
  f.clock.advance(1); assert.equal(first, 1); assert.equal(ignored, 0, 'ignored commands cannot replace the active callback');
}

{
  const f = fixture(); let first = 0, second = 0;
  f.window.ozBoot(() => { first++; }, 'start');
  f.clock.advance(100); f.window.ozBootSkip();
  f.clock.advance(200); // Restart at 300ms, before the old fade cleanup scheduled for 550ms.
  f.window.ozBoot(() => { second++; }, 'end');
  assert.deepEqual(f.events, [{ type: 'play', mode: 'start', at: 0 }, { type: 'stop', at: 100 }, { type: 'play', mode: 'end', at: 300 }]);
  assert.equal(f.boot.classList.contains('is-done'), false);
  assert.equal(f.boot.classList.contains('is-end'), true);
  assert.equal(f.ids.bootPct.textContent, '0%');
  f.clock.advance(250);
  assert.equal(f.boot.getAttribute('aria-hidden'), 'false', 'old fade cleanup cannot hide the new run');
  assert.equal(f.boot.classList.contains('is-on'), true);
  f.clock.advance(6549); assert.equal(second, 0);
  f.clock.advance(1); assert.equal(first, 1); assert.equal(second, 1);
  assert.deepEqual(f.events.at(-1), { type: 'stop', at: 7100 });
  completed(f);
  f.clock.advance(450); assert.equal(f.clock.pending(), 0);
}

{
  const f = fixture(); let second = 0;
  f.window.ozBoot(() => f.window.ozBoot(() => { second++; }, 'start'), 'end');
  f.clock.advance(6800);
  assert.deepEqual(f.events, [{ type: 'play', mode: 'end', at: 0 }, { type: 'stop', at: 6800 }, { type: 'play', mode: 'start', at: 6800 }]);
  f.clock.advance(450); assert.equal(f.boot.classList.contains('is-on'), true, 'a callback can start the next run safely');
  f.clock.advance(6350); assert.equal(second, 1); completed(f);
}

for (const mode of ['start', 'end']) {
  const f = fixture({ reduce: true }); let callbacks = 0;
  f.window.ozBoot(() => { callbacks++; }, mode);
  f.window.ozBootSkip();
  assert.equal(callbacks, 1, 'reduced motion completes the requested destination immediately');
  assert.deepEqual(f.events, [], 'reduced motion never starts audio');
  assert.equal(f.boot.classList.contains('is-on'), false);
  assert.equal(f.boot.getAttribute('aria-hidden'), 'true');
  assert.equal(f.root.classList.contains('boot-locked'), false);
  assert.equal(f.clock.pending(), 0);
}

{
  const f = fixture({ audioPresent: false }); let callbacks = 0;
  f.window.ozBoot(() => { callbacks++; }, 'end');
  f.clock.advance(6800);
  assert.equal(callbacks, 1, 'missing audio adapter does not block the visual timeline');
  completed(f);
}

console.log('PASS: actual index.html boot controller; start/end audio modes, exact 6.8s stop, all skip routes, duplicate commands, 450ms fade restart, reentrant callback, reduced motion, and missing-audio fallback');
