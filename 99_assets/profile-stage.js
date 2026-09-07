(function () {
  'use strict';
  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var chapters = Array.from(profile.querySelectorAll('.pd-chapter'));
  if (!chapters.length) return;
  var deck = profile.querySelector('.pf-doc');
  var overview = profile.querySelector('#pd-overview');
  var grid = overview.querySelector('.pd-overview-grid');
  var count = profile.querySelector('[data-pd-count]');
  var title = profile.querySelector('[data-pd-title]');
  var cue = profile.querySelector('.pd-scroll-cue');
  var progress = profile.querySelector('[data-pd-progress]');
  var reveals = Array.from(profile.querySelectorAll('[data-pd-reveal]'));
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var supportsScrollEnd = 'onscrollend' in deck;
  var active = -1, isOpen = false, previousFocus = null;
  var frame = 0, controlsTimer = 0, scrollTimer = 0;
  var geometry = [], viewport = 1, maxScroll = 0, needsMeasure = true;
  var chapterProgress = [], chapterVisible = [], lastProgress = '', atEnd = null;
  var destination = null, scrolling = false, observedTop = 0, stableChecks = 0;
  function clamp(value,min,max) { return Math.max(min,Math.min(max,value)); }
  function canUpdate() { return isOpen && !document.hidden; }
  function setActive(index) {
    if (index === active) return;
    if (active >= 0) {
      chapters[active].classList.remove('is-active');
      grid.children[active].setAttribute('aria-current','false');
    }
    active = index;
    chapters[active].classList.add('is-active');
    grid.children[active].setAttribute('aria-current','true');
    count.textContent = String(active+1).padStart(2,'0')+' / '+String(chapters.length).padStart(2,'0');
    title.textContent = chapters[active].dataset.title;
  }
  function measure() {
    // Read all geometry together, only on opening or a size change. Scroll frames reuse this cache.
    var top = deck.scrollTop;
    var deckTop = deck.getBoundingClientRect().top + deck.clientTop;
    viewport = Math.max(1,deck.clientHeight);
    maxScroll = Math.max(0,deck.scrollHeight-viewport);
    geometry = chapters.map(function (chapter) {
      var rect = chapter.getBoundingClientRect();
      var start = rect.top-deckTop+top;
      return {top:start,height:rect.height,bottom:start+rect.height};
    });
    if (destination !== null) destination = clamp(destination,0,maxScroll);
    needsMeasure = false;
  }
  function updateView() {
    var top = clamp(deck.scrollTop,0,maxScroll);
    var readingPosition = top+viewport*.35;
    var current = 0;
    geometry.forEach(function (chapter,index) {
      if (chapter.top <= readingPosition) current = index;
      var visible = chapter.bottom > top && chapter.top < top+viewport;
      if (visible !== chapterVisible[index]) {
        chapterVisible[index] = visible;
        chapters[index].classList.toggle('is-visible',visible);
      }
      // 0: chapter top reaches viewport bottom; 1: chapter bottom leaves viewport top.
      var value = clamp((top+viewport-chapter.top)/(chapter.height+viewport),0,1).toFixed(5);
      if (value !== chapterProgress[index]) {
        chapterProgress[index] = value;
        chapters[index].style.setProperty('--pd-progress',value);
      }
    });
    setActive(current);
    var value = (maxScroll ? top/maxScroll : 1).toFixed(5);
    if (progress && value !== lastProgress) {
      progress.style.transform = 'scaleX('+value+')'; lastProgress = value;
    }
    var end = maxScroll-top < 2;
    if (end !== atEnd) {
      atEnd = end;
      cue.textContent = end ? '↑ スクロールで読み返す' : '↓ スクロールで続きを読む';
    }
  }
  function render() {
    frame = 0;
    if (!canUpdate()) return;
    if (needsMeasure) measure();
    updateView();
  }
  function scheduleUpdate(remeasure) {
    if (remeasure) needsMeasure = true;
    if (canUpdate() && !frame) frame = requestAnimationFrame(render);
  }
  function hideControls() {
    clearTimeout(controlsTimer);
    if (!canUpdate()) return;
    controlsTimer = setTimeout(function () {
      if (profile.querySelector('.pd-controls:focus-within') || !overview.hidden) return;
      profile.classList.remove('pd-controls-visible');
    },3200);
  }
  function showControls() {
    if (!canUpdate()) return;
    if (!profile.classList.contains('pd-controls-visible')) profile.classList.add('pd-controls-visible');
    hideControls();
  }
  function beginScroll() {
    if (scrolling) return;
    scrolling = true; profile.classList.add('pd-is-scrolling');
  }
  function finishScroll() {
    if (!canUpdate()) return;
    if (destination !== null && Math.abs(deck.scrollTop-destination) > 2) return;
    clearTimeout(scrollTimer); scrollTimer = 0; destination = null;
    if (scrolling) { scrolling = false; profile.classList.remove('pd-is-scrolling'); }
    scheduleUpdate();
  }
  function checkScroll() {
    scrollTimer = 0;
    if (!canUpdate() || !scrolling) return;
    var top = deck.scrollTop;
    if (Math.abs(top-observedTop) > .5 || (destination !== null && Math.abs(top-destination) > 2)) stableChecks = 0;
    else stableChecks++;
    observedTop = top;
    if (stableChecks >= 2) finishScroll();
    else scrollTimer = setTimeout(checkScroll,200);
  }
  function queueScrollCheck() {
    clearTimeout(scrollTimer); observedTop = deck.scrollTop; stableChecks = 0;
    scrollTimer = setTimeout(checkScroll,200);
  }
  function stopScroll() {
    if (scrolling) deck.scrollTo({top:deck.scrollTop,behavior:'auto'});
    clearTimeout(scrollTimer); scrollTimer = 0; destination = null;
    if (scrolling) { scrolling = false; profile.classList.remove('pd-is-scrolling'); }
  }
  function goTo(top) {
    if (needsMeasure) measure();
    destination = clamp(top,0,maxScroll);
    beginScroll();
    deck.scrollTo({top:destination,behavior:reduced.matches?'auto':'smooth'});
    scheduleUpdate();
    if (reduced.matches || Math.abs(deck.scrollTop-destination) < 2) finishScroll();
    else if (!supportsScrollEnd) queueScrollCheck();
  }
  function goToChapter(index) {
    if (needsMeasure) measure();
    goTo(geometry[index].top);
  }
  deck.addEventListener('scroll',function () {
    if (!canUpdate() || !overview.hidden) return;
    beginScroll(); scheduleUpdate();
    if (!supportsScrollEnd) queueScrollCheck();
  },{passive:true});
  deck.addEventListener('scrollend',finishScroll);
  function manualScroll() {
    destination = null;
    if (canUpdate() && scrolling && !supportsScrollEnd) queueScrollCheck();
  }
  deck.addEventListener('wheel',manualScroll,{passive:true});
  deck.addEventListener('touchstart',manualScroll,{passive:true});
  deck.addEventListener('pointerdown',manualScroll,{passive:true});
  function revealAll() {
    reveals.forEach(function (element) {
      if (!element.classList.contains('is-revealed')) element.classList.add('is-revealed');
    });
  }
  var revealObserver = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    if (!canUpdate()) return;
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      if (!entry.target.classList.contains('is-revealed')) entry.target.classList.add('is-revealed');
      revealObserver.unobserve(entry.target);
    });
  },{root:deck,threshold:0,rootMargin:'0px 0px -6% 0px'}) : null;
  var sizeObserver = 'ResizeObserver' in window ? new ResizeObserver(function () { scheduleUpdate(true); }) : null;
  function observeContent() {
    if (!canUpdate()) return;
    if (sizeObserver) { sizeObserver.observe(deck); chapters.forEach(function (chapter) { sizeObserver.observe(chapter); }); }
    if (reduced.matches || !revealObserver) { profile.classList.remove('pd-reveal-ready'); revealAll(); }
    else {
      profile.classList.add('pd-reveal-ready');
      reveals.forEach(function (element) { if (!element.classList.contains('is-revealed')) revealObserver.observe(element); });
    }
  }
  function pauseUpdates() {
    cancelAnimationFrame(frame); frame = 0; clearTimeout(controlsTimer); stopScroll();
    if (sizeObserver) sizeObserver.disconnect();
    if (revealObserver) revealObserver.disconnect();
  }
  function toggleMenu(open) {
    stopScroll();
    overview.hidden = !open; deck.inert = open;
    if (open) {
      if (needsMeasure) measure();
      updateView(); showControls(); grid.children[active].focus({preventScroll:true});
    } else { profile.focus({preventScroll:true}); hideControls(); }
  }
  chapters.forEach(function (chapter,index) {
    var button = document.createElement('button'); button.type='button'; button.setAttribute('aria-current','false');
    var number = document.createElement('b'); number.textContent=String(index+1).padStart(2,'0');
    var label = document.createElement('span'); label.textContent=chapter.dataset.title;
    button.append(number,label);
    button.addEventListener('click',function () { toggleMenu(false); goToChapter(index); });
    grid.appendChild(button);
  });
  profile.querySelector('[data-pd-menu-close]').addEventListener('click',function () { toggleMenu(false); });
  profile.addEventListener('pointermove',showControls,{passive:true});
  profile.addEventListener('pointerdown',showControls,{passive:true});
  profile.addEventListener('focusin',showControls);
  profile.addEventListener('focusout',hideControls);
  profile.addEventListener('click',function (event) {
    if (event.detail>0 && canUpdate() && overview.hidden && event.target.closest('.pd-controls button')) profile.focus({preventScroll:true});
  });
  document.addEventListener('keydown',function (event) {
    if (!canUpdate() || event.metaKey || event.ctrlKey || event.altKey || event.isComposing) return;
    var target=event.target;
    if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
    var key=event.key;
    if (key==='Tab') {
      showControls();
      var scope=overview.hidden?profile:overview;
      var selector='a[href],button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"]),[contenteditable]:not([contenteditable="false"])';
      var elements=Array.from(scope.querySelectorAll(selector)).filter(function (element) { return element.getClientRects().length>0; });
      var first=elements[0],last=elements[elements.length-1];
      if (!first) { event.preventDefault(); profile.focus({preventScroll:true}); return; }
      if (event.shiftKey && (document.activeElement===first || !elements.includes(document.activeElement))) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement===last || !elements.includes(document.activeElement))) { event.preventDefault(); first.focus(); }
      return;
    }
    if (key==='?') { event.preventDefault(); toggleMenu(overview.hidden); return; }
    if (key==='0' || /^[1-6]$/.test(key)) {
      event.preventDefault(); if (!overview.hidden) toggleMenu(false);
      if (needsMeasure) measure();
      if (key==='0') goTo(maxScroll); else goToChapter(Number(key)-1);
      return;
    }
    if (!overview.hidden) return;
    var next=['ArrowRight','ArrowDown','PageDown'].includes(key);
    var prev=['ArrowLeft','ArrowUp','PageUp'].includes(key);
    if (key===' ' && (!target || target.tagName!=='BUTTON')) { next=!event.shiftKey; prev=event.shiftKey; }
    if (next || prev || key==='Home' || key==='End') {
      event.preventDefault();
      if (needsMeasure) measure();
      var from=destination===null?deck.scrollTop:destination;
      goTo(key==='Home'?0:key==='End'?maxScroll:from+(next?1:-1)*viewport*.85);
    }
  });
  function syncOpen() {
    var open=profile.classList.contains('show');
    if (open===isOpen) return;
    isOpen=open;
    if (open) {
      previousFocus=document.activeElement; overview.hidden=true; deck.inert=false;
      deck.scrollTo({top:0,behavior:'auto'}); setActive(0);
      scheduleUpdate(true); observeContent(); profile.focus({preventScroll:true}); showControls();
    } else {
      pauseUpdates(); overview.hidden=true; deck.inert=false;
      profile.classList.remove('pd-controls-visible');
      chapters.forEach(function (chapter,index) {
        if (chapterVisible[index]) chapter.classList.remove('is-visible');
        chapterVisible[index]=false;
      });
      // Do not steal focus if a secret command has already opened another dialog.
      if (previousFocus && previousFocus.isConnected && !profile.contains(previousFocus) &&
          (profile.contains(document.activeElement) || document.activeElement===document.body)) previousFocus.focus({preventScroll:true});
    }
  }
  new MutationObserver(syncOpen).observe(profile,{attributes:true,attributeFilter:['class']});
  function syncVisibility() {
    profile.classList.toggle('pd-page-hidden',document.hidden);
    if (document.hidden) pauseUpdates();
    else { scheduleUpdate(true); observeContent(); }
  }
  document.addEventListener('visibilitychange',syncVisibility);
  reduced.addEventListener('change',function () {
    if (reduced.matches) { stopScroll(); if (revealObserver) revealObserver.disconnect(); profile.classList.remove('pd-reveal-ready'); revealAll(); }
    else observeContent();
    scheduleUpdate();
  });
  window.addEventListener('resize',function () { scheduleUpdate(true); });
  setActive(0); syncVisibility(); syncOpen();
})();
