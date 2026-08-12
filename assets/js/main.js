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

  // banner privacy/cookie (solo informativo: nessun cookie di profilazione)
  var banner = document.getElementById('cookieBanner');
  if (banner) {
    var KEY = 'scv-privacy-notice';
    var seen = null;
    try { seen = localStorage.getItem(KEY); } catch (e) { /* storage bloccato */ }
    if (!seen) {
      setTimeout(function () { banner.classList.add('show'); }, 900);
    }
    document.getElementById('cookieOk').addEventListener('click', function () {
      banner.classList.remove('show');
      try { localStorage.setItem(KEY, String(Date.now())); } catch (e) { /* ignora */ }
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
