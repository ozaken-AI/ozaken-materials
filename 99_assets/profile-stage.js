(function () {
  'use strict';
  var profile = document.getElementById('profile-fs');
  if (!profile) return;
  var slides = Array.from(profile.querySelectorAll('.pd-slide'));
  var overview = profile.querySelector('#pd-overview');
  var grid = overview.querySelector('.pd-overview-grid');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var active = 0, isOpen = false, controlsTimer = 0, previousFocus = null;
  var signals = [], signalFrame = 0, scrollTimer = 0, resizeFrame = 0;
  var destination = null;
  var deck = profile.querySelector('.pf-doc');
  function clearSignals() {
    cancelAnimationFrame(signalFrame);
    signals.forEach(function (animation) { animation.cancel(); });
    signals = [];
    profile.querySelectorAll('.pd-signal').forEach(function (el) { el.remove(); });
  }
  function connect() {
    if (reduced.matches || !isOpen || active !== 1 || !overview.hidden) return;
    var network = slides[active].querySelector('.pd-network');
    var rect = network.getBoundingClientRect();
    network.querySelectorAll('.pd-node').forEach(function (node, index) {
      var target = node.getBoundingClientRect();
      var x = target.left + target.width / 2 - rect.left - rect.width / 2;
      var y = target.top + target.height / 2 - rect.top - rect.height / 2;
      var dot = document.createElement('i'); dot.className = 'pd-signal'; dot.setAttribute('aria-hidden', 'true');
      network.appendChild(dot);
      var animation = dot.animate([
        {transform:'translate(0,0)',opacity:0},
        {transform:'translate(0,0)',opacity:1,offset:.1},
        {transform:'translate('+x+'px,'+y+'px)',opacity:1,offset:.85},
        {transform:'translate('+x+'px,'+y+'px)',opacity:0}
      ], {duration:1450,delay:index*180,easing:'cubic-bezier(.3,0,.25,1)',fill:'both'});
      animation.onfinish = function () { dot.remove(); };
      signals.push(animation);
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
    profile.classList.add('pd-controls-visible'); hideControls();
  }
  function activate(index, replay) {
    index = Math.max(0, Math.min(slides.length-1, index));
    if (!replay && index === active && slides[index].classList.contains('is-active')) return;
    clearSignals(); active = index;
    slides.forEach(function (slide) {
      slide.classList.remove('is-active','is-replaying');
    });
    void slides[active].offsetWidth;
    slides[active].classList.add('is-active');
    if (replay) slides[active].classList.add('is-replaying');
    profile.querySelector('[data-pd-count]').textContent = String(active+1).padStart(2,'0')+' / '+slides.length;
    profile.querySelector('[data-pd-title]').textContent = slides[active].dataset.title;
    profile.querySelector('.pd-scroll-cue').textContent = active === slides.length-1 ? '↑ スクロールで前の画面へ' : '↓ スクロールで次の画面へ';
    grid.querySelectorAll('button').forEach(function (button,i) { button.setAttribute('aria-current',String(i===active)); });
    signalFrame = requestAnimationFrame(connect);
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
  function settleScroll() {
    clearTimeout(scrollTimer);
    if (!isOpen) return;
    destination = null;
    activate(nearestSection());
  }
  function goToSection(index, instant) {
    index = Math.max(0, Math.min(slides.length-1, index));
    clearTimeout(scrollTimer); clearSignals(); destination = index;
    var top = slides[index].offsetTop;
    deck.scrollTo({top:top, behavior:instant || reduced.matches ? 'auto' : 'smooth'});
    if (instant || reduced.matches || Math.abs(deck.scrollTop-top) < 2) settleScroll();
  }
  deck.addEventListener('scroll',function(){
    if (!isOpen) return;
    clearSignals(); clearTimeout(scrollTimer);
    // scrollend is preferred; the timer also covers browsers without it.
    scrollTimer = setTimeout(settleScroll,160);
  },{passive:true});
  deck.addEventListener('scrollend',settleScroll);
  function manualScroll() { destination = null; }
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
      goToSection(0,true); activate(0,true); profile.focus({preventScroll:true});showControls();
    } else {
      clearSignals();clearTimeout(controlsTimer);clearTimeout(scrollTimer);cancelAnimationFrame(resizeFrame);destination=null;overview.hidden=true;deck.inert=false;
      profile.classList.remove('pd-controls-visible');
      if(previousFocus&&previousFocus.isConnected&&!profile.contains(previousFocus))previousFocus.focus({preventScroll:true});
    }
  }
  new MutationObserver(syncOpen).observe(profile,{attributes:true,attributeFilter:['class']});
  reduced.addEventListener('change',function(){if(reduced.matches)clearSignals();});
  window.addEventListener('resize',function(){
    if (!isOpen) return;
    clearSignals(); cancelAnimationFrame(resizeFrame);
    var index = destination === null ? active : destination;
    resizeFrame = requestAnimationFrame(function(){ goToSection(index,true); });
  });
  activate(0,true); syncOpen();
})();
