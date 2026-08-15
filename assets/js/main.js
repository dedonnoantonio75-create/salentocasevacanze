// Salento Case Vacanze — interazioni
(function () {
  'use strict';

  // header ombra allo scroll
  var header = document.querySelector('.site-header');
  window.addEventListener('scroll', function () {
    header.classList.toggle('scrolled', window.scrollY > 10);
  }, { passive: true });

  // menu mobile
  var burger = document.querySelector('.hamburger');
  var nav = document.querySelector('.main-nav');
  if (burger) {
    burger.addEventListener('click', function () {
      nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', nav.classList.contains('open'));
    });
  }

  // dropdown lingue
  var langBtn = document.querySelector('.lang-btn');
  var langMenu = document.querySelector('.lang-menu');
  if (langBtn) {
    langBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      langMenu.classList.toggle('open');
    });
    document.addEventListener('click', function () { langMenu.classList.remove('open'); });
  }

  // reveal on scroll
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });

  // filtro località nella griglia appartamenti
  var chips = document.querySelectorAll('.chip[data-city]');
  var cards = document.querySelectorAll('.apt-card[data-city]');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      var city = chip.getAttribute('data-city');
      cards.forEach(function (card) {
        card.style.display = (city === '*' || card.getAttribute('data-city') === city) ? '' : 'none';
      });
    });
  });
  // preseleziona il filtro zona se arrivo dal box di ricerca (?zona=...)
  if (chips.length) {
    var zonaParam = new URLSearchParams(location.search).get('zona');
    if (zonaParam) {
      chips.forEach(function (c) {
        if (c.getAttribute('data-city') === zonaParam) c.click();
      });
    }
  }

  // box di ricerca nella hero: date+ospiti -> motore Kross; solo zona -> griglia filtrata
  var hs = document.getElementById('heroSearch');
  if (hs) {
    var hsFrom = document.getElementById('hsFrom');
    var hsTo = document.getElementById('hsTo');
    var oggi = new Date().toISOString().slice(0, 10);
    hsFrom.min = oggi;
    hsTo.min = oggi;
    hsFrom.addEventListener('change', function () { if (hsFrom.value) hsTo.min = hsFrom.value; });
    hs.addEventListener('submit', function (e) {
      e.preventDefault();
      var from = hsFrom.value, to = hsTo.value;
      var guests = document.getElementById('hsGuests').value;
      var zone = document.getElementById('hsZone').value;
      if (from && to) {
        var url = hs.getAttribute('data-kross') + '?from=' + from + '&to=' + to + '&guests=' + guests;
        window.open(url, '_blank', 'noopener');
      } else {
        var dest = hs.getAttribute('data-apts');
        if (zone) dest += '?zona=' + encodeURIComponent(zone);
        window.location.href = dest;
      }
    });
  }

  // lightbox galleria
  var lb = document.querySelector('.lightbox');
  if (lb) {
    var lbImg = lb.querySelector('img');
    var lbCount = lb.querySelector('.lb-count');
    var links = Array.prototype.slice.call(document.querySelectorAll('.gallery a'));
    var idx = 0;
    function show(i) {
      idx = (i + links.length) % links.length;
      lbImg.src = links[idx].getAttribute('href');
      lbImg.alt = links[idx].querySelector('img') ? links[idx].querySelector('img').alt : '';
      lbCount.textContent = (idx + 1) + ' / ' + links.length;
    }
    links.forEach(function (a, i) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        lb.classList.add('open');
        document.body.style.overflow = 'hidden';
        show(i);
      });
    });
    function close() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
  }

  // slideshow hero con dissolvenza + Ken Burns
  var slides = document.querySelectorAll('.hero-slide');
  if (slides.length > 1) {
    var dotsWrap = document.querySelector('.hero-dots');
    var current = 0, timer = null;
    slides.forEach(function (_, i) {
      var d = document.createElement('button');
      d.setAttribute('aria-label', 'Slide ' + (i + 1));
      if (i === 0) d.classList.add('active');
      d.addEventListener('click', function () { goTo(i); restart(); });
      dotsWrap.appendChild(d);
    });
    var dots = dotsWrap.querySelectorAll('button');
    function goTo(i) {
      slides[current].classList.remove('active');
      dots[current].classList.remove('active');
      current = (i + slides.length) % slides.length;
      slides[current].classList.add('active');
      dots[current].classList.add('active');
    }
    function restart() {
      clearInterval(timer);
      timer = setInterval(function () { goTo(current + 1); }, 6500);
    }
    restart();
  }

  // banner privacy/cookie
  // - senza window.SCV_GA: solo informativo (nessun cookie di profilazione)
  // - con window.SCV_GA: banner di consenso; Google Analytics parte SOLO dopo "Accetta"
  var banner = document.getElementById('cookieBanner');
  function loadGA() {
    if (!window.SCV_GA || window.__gaLoaded) return;
    window.__gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', window.SCV_GA, { anonymize_ip: true });
    var sc = document.createElement('script');
    sc.async = true;
    sc.src = 'https://www.googletagmanager.com/gtag/js?id=' + window.SCV_GA;
    document.head.appendChild(sc);
  }
  if (banner) {
    var KEY = window.SCV_GA ? 'scv-consent' : 'scv-privacy-notice';
    var stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) { /* storage bloccato */ }
    if (stored === 'granted') loadGA();
    if (!stored) {
      setTimeout(function () { banner.classList.add('show'); }, 900);
    }
    function choose(value) {
      banner.classList.remove('show');
      try { localStorage.setItem(KEY, value); } catch (e) { /* ignora */ }
      if (value === 'granted') loadGA();
    }
    document.getElementById('cookieOk').addEventListener('click', function () {
      choose(window.SCV_GA ? 'granted' : String(Date.now()));
    });
    var no = document.getElementById('cookieNo');
    if (no) no.addEventListener('click', function () { choose('denied'); });
    var prefs = document.getElementById('cookiePrefs');
    if (prefs) prefs.addEventListener('click', function (e) {
      e.preventDefault();
      try { localStorage.removeItem(KEY); } catch (e2) { /* ignora */ }
      banner.classList.add('show');
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
  }

  // mini-carosello sulle card (cambio foto al passaggio del mouse)
  document.querySelectorAll('.apt-media[data-imgs]').forEach(function (media) {
    var imgs = media.getAttribute('data-imgs').split('|');
    if (imgs.length < 2) return;
    var img = media.querySelector('img');
    var t = null, i = 0;
    media.addEventListener('mouseenter', function () {
      t = setInterval(function () {
        i = (i + 1) % imgs.length;
        img.src = imgs[i];
      }, 1400);
    });
    media.addEventListener('mouseleave', function () {
      clearInterval(t); i = 0; img.src = imgs[0];
    });
  });
})();
