(function () {
  'use strict';
  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var slides = Array.from(profile.querySelectorAll('.pd-slide'));
  var overview = profile.querySelector('#pd-overview');
  var grid = overview.querySelector('.pd-overview-grid');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var active = -1, isOpen = false, controlsTimer = 0, previousFocus = null;
  var signals = [], signalFrame = 0, scrollTimer = 0, resizeFrame = 0;
  var destination = null, scrolling = false, stableChecks = 0, observedTop = 0;
  var deck = profile.querySelector('.pf-doc');
  var supportsScrollEnd = 'onscrollend' in deck;
  var count = profile.querySelector('[data-pd-count]');
  var title = profile.querySelector('[data-pd-title]');
  var cue = profile.querySelector('.pd-scroll-cue');
  function clearSignals() {
    cancelAnimationFrame(signalFrame); signalFrame = 0;
    signals.forEach(function (signal) { signal.animation.cancel(); signal.dot.remove(); });
    signals = [];
  }
  function connect() {
    signalFrame = 0;
    if (document.hidden || reduced.matches || !isOpen || scrolling || active !== 1 || !overview.hidden) return;
    var network = slides[active].querySelector('.pd-network');
    var rect = network.getBoundingClientRect();
    // Read every endpoint before adding animated elements to avoid alternating layout reads and writes.
    var endpoints = Array.from(network.querySelectorAll('.pd-node')).map(function (node) {
      var target = node.getBoundingClientRect();
      return {x:target.left + target.width / 2 - rect.left - rect.width / 2,
        y:target.top + target.height / 2 - rect.top - rect.height / 2};
    });
    endpoints.forEach(function (point, index) {
      var dot = document.createElement('i'); dot.className = 'pd-signal'; dot.setAttribute('aria-hidden', 'true');
      network.appendChild(dot);
      var animation = dot.animate([
        {transform:'translate(0,0)',opacity:0},
        {transform:'translate(0,0)',opacity:1,offset:.1},
        {transform:'translate('+point.x+'px,'+point.y+'px)',opacity:1,offset:.85},
        {transform:'translate('+point.x+'px,'+point.y+'px)',opacity:0}
      ], {duration:1450,delay:index*180,easing:'cubic-bezier(.3,0,.25,1)',fill:'both'});
      var signal = {animation:animation,dot:dot};
      animation.onfinish = function () { dot.remove(); signals = signals.filter(function (item) { return item !== signal; }); };
      signals.push(signal);
    });
  }
  function hideControls() {
    clearTimeout(controlsTimer);
    controlsTimer = setTimeout(function () {
      if (profile.querySelector('.pd-controls:focus-within') || !overview.hidden) return;
      profile.classList.remove('pd-controls-visible');
    }, 3200);
  }
  function showControls() {
    if (!isOpen) return;
    if (!profile.classList.contains('pd-controls-visible')) profile.classList.add('pd-controls-visible');
    hideControls();
  }
  function activate(index) {
    index = Math.max(0, Math.min(slides.length-1, index));
    if (index === active) return;
    if (active >= 0) {
      slides[active].classList.remove('is-active');
      grid.children[active].setAttribute('aria-current','false');
    }
    active = index;
    slides[active].classList.add('is-active');
    count.textContent = String(active+1).padStart(2,'0')+' / '+slides.length;
    title.textContent = slides[active].dataset.title;
    cue.textContent = active === slides.length-1 ? '↑ スクロールで前の画面へ' : '↓ スクロールで次の画面へ';
    grid.children[active].setAttribute('aria-current','true');
    if (active === 1 && isOpen && !document.hidden && !reduced.matches && overview.hidden) signalFrame = requestAnimationFrame(connect);
  }
  function nearestSection() {
    var nearest = 0, distance = Infinity;
    slides.forEach(function (slide, index) {
      var delta = Math.abs(slide.offsetTop - deck.scrollTop);
      if (delta < distance) { nearest = index; distance = delta; }
    });
    return nearest;
  }
  function navigationIndex() { return destination === null ? nearestSection() : destination; }
  function beginScroll() {
    if (scrolling) return;
    scrolling = true; clearSignals(); profile.classList.add('pd-is-scrolling');
  }
  function settleScroll() {
    if (!isOpen) return;
    // An older smooth scroll may end after a new key press has selected another destination.
    if (destination !== null && Math.abs(deck.scrollTop-slides[destination].offsetTop) > 2) return;
    clearTimeout(scrollTimer); scrollTimer = 0;
    destination = null;
    if (scrolling) { scrolling = false; profile.classList.remove('pd-is-scrolling'); }
    activate(nearestSection());
  }
  function checkScroll() {
    scrollTimer = 0;
    if (!isOpen || !scrolling) return;
    var top = deck.scrollTop;
    var atDestination = destination === null || Math.abs(top-slides[destination].offsetTop) <= 2;
    if (Math.abs(top-observedTop) > .5 || !atDestination) stableChecks = 0;
    else stableChecks++;
    observedTop = top;
    if (stableChecks >= 2) settleScroll();
    else scrollTimer = setTimeout(checkScroll,200);
  }
  function queueScrollCheck() {
    clearTimeout(scrollTimer); observedTop = deck.scrollTop; stableChecks = 0;
    scrollTimer = setTimeout(checkScroll,200);
  }
  function goToSection(index, instant) {
    index = Math.max(0, Math.min(slides.length-1, index));
    clearTimeout(scrollTimer); destination = index;
    var top = slides[index].offsetTop;
    beginScroll();
    deck.scrollTo({top:top, behavior:instant || reduced.matches ? 'auto' : 'smooth'});
    if (instant || reduced.matches || Math.abs(deck.scrollTop-top) < 2) settleScroll();
    else if (!supportsScrollEnd) queueScrollCheck();
  }
  deck.addEventListener('scroll',function(){
    if (!isOpen) return;
    beginScroll();
    // Modern browsers report the true end; the fallback waits for two stable samples.
    if (!supportsScrollEnd) queueScrollCheck();
  },{passive:true});
  deck.addEventListener('scrollend',settleScroll);
  function manualScroll() {
    destination = null;
    if (scrolling && !supportsScrollEnd) queueScrollCheck();
  }
  deck.addEventListener('wheel',manualScroll,{passive:true});
  deck.addEventListener('touchstart',manualScroll,{passive:true});
  function toggleMenu(open) {
    overview.hidden = !open; deck.inert = open;
    if (open) {
      goToSection(nearestSection(),true); clearSignals(); showControls();
      grid.children[active].focus({preventScroll:true});
    } else { profile.focus({preventScroll:true}); hideControls(); }
  }
  slides.forEach(function (slide, index) {
    var button = document.createElement('button'); button.type='button';
    button.setAttribute('aria-current','false');
    var number = document.createElement('b'); number.textContent=String(index+1).padStart(2,'0');
    var label = document.createElement('span'); label.textContent=slide.dataset.title;
    button.append(number,label);
    button.addEventListener('click', function () { toggleMenu(false); goToSection(index); });
    grid.appendChild(button);
  });
  profile.querySelector('[data-pd-menu-close]').addEventListener('click',function(){ toggleMenu(false); });
  profile.addEventListener('pointermove',showControls,{passive:true});
  profile.addEventListener('pointerdown',showControls,{passive:true});
  profile.addEventListener('focusin',showControls);
  profile.addEventListener('focusout',hideControls);
  profile.addEventListener('click',function(event){
    // Mouse clicks return focus to the stage so controls can fade; Tab focus stays visible.
    if(event.detail>0 && isOpen && overview.hidden && event.target.closest('.pd-controls button')) {
      profile.focus({preventScroll:true});
    }
  });
  // Presentation navigation only. Two-letter stage commands keep their existing handler.
  document.addEventListener('keydown',function(event){
    if (!isOpen || event.metaKey || event.ctrlKey || event.altKey || event.isComposing) return;
    var target=event.target;
    if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
    var key=event.key;
    if (key==='Tab') {
      showControls();
      var scope=overview.hidden?profile:overview;
      var buttons=Array.from(scope.querySelectorAll('button:not(:disabled)')).filter(function(el){return el.getClientRects().length>0;});
      var first=buttons[0], last=buttons[buttons.length-1];
      if (event.shiftKey && (document.activeElement===first || !buttons.includes(document.activeElement))) {event.preventDefault();last.focus();}
      else if (!event.shiftKey && (document.activeElement===last || !buttons.includes(document.activeElement))) {event.preventDefault();first.focus();}
      return;
    }
    if(key==='?'){ event.preventDefault(); toggleMenu(overview.hidden); return; }
    if(/^[0-9]$/.test(key)) { event.preventDefault(); if(!overview.hidden)toggleMenu(false);goToSection(key==='0'?9:Number(key)-1);return; }
    if(!overview.hidden) return;
    var next = ['ArrowRight','ArrowDown','PageDown'].includes(key);
    var prev = ['ArrowLeft','ArrowUp','PageUp'].includes(key);
    // Space on a focused control retains native button activation.
    if(key===' ' && target.tagName!=='BUTTON'){next=!event.shiftKey;prev=event.shiftKey;}
    if(next||prev||key==='Home'||key==='End') {
      event.preventDefault();
      goToSection(key==='Home'?0:key==='End'?slides.length-1:navigationIndex()+(next?1:-1));
    }
  });
  function syncOpen() {
    var open=profile.classList.contains('show');
    if(open===isOpen)return;
    isOpen=open;
    if(open) {
      previousFocus=document.activeElement; overview.hidden=true;deck.inert=false;
      goToSection(0,true); profile.focus({preventScroll:true});showControls();
    } else {
      clearSignals();clearTimeout(controlsTimer);clearTimeout(scrollTimer);cancelAnimationFrame(resizeFrame);destination=null;scrolling=false;overview.hidden=true;deck.inert=false;
      profile.classList.remove('pd-controls-visible','pd-is-scrolling');
      if(previousFocus&&previousFocus.isConnected&&!profile.contains(previousFocus))previousFocus.focus({preventScroll:true});
    }
  }
  new MutationObserver(syncOpen).observe(profile,{attributes:true,attributeFilter:['class']});
  function syncVisibility() {
    profile.classList.toggle('pd-page-hidden',document.hidden);
    if (document.hidden) clearSignals();
  }
  document.addEventListener('visibilitychange',syncVisibility);
  syncVisibility();
  reduced.addEventListener('change',function(){if(reduced.matches)clearSignals();});
  window.addEventListener('resize',function(){
    if (!isOpen) return;
    clearSignals(); cancelAnimationFrame(resizeFrame);
    var index = destination === null ? active : destination;
    resizeFrame = requestAnimationFrame(function(){ goToSection(index,true); });
  });
  activate(0); syncOpen();
})();
