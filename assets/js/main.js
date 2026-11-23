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
    var hsFromBtn = document.getElementById('hsFromBtn');
    var hsToBtn = document.getElementById('hsToBtn');
    // calendario a intervallo (come il booking Kross): due mesi affiancati,
    // clic sull'arrivo, poi passando col mouse si colora il periodo, clic sulla partenza
    var lang = (document.documentElement.lang || 'it').slice(0, 2);
    function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
    function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
    var t0 = new Date(); var oggi = iso(new Date(t0.getFullYear(), t0.getMonth(), t0.getDate()));
    var fmtMese = new Intl.DateTimeFormat(lang, { month: 'long', year: 'numeric' });
    var fmtMeseBreve = new Intl.DateTimeFormat(lang, { month: 'short', year: 'numeric' });
    var fmtGiorno =new Intl.DateTimeFormat(lang, { weekday: 'long' });
    var fmtSett = new Intl.DateTimeFormat(lang, { weekday: 'short' });
    var nomiSett = [];
    for (var w = 0; w < 7; w++) nomiSett.push(fmtSett.format(new Date(2024, 0, 1 + w)).replace('.', '').slice(0, 2)); // 1/1/2024 = lunedi'
    var cap = function (s) { return s.charAt(0).toUpperCase() + s.slice(1); };

    var drp = document.createElement('div');
    drp.className = 'drp'; drp.hidden = true;
    drp.setAttribute('role', 'dialog');
    document.body.appendChild(drp);
    var meseVisto = parse(oggi); meseVisto.setDate(1);
    var hoverDay = null;

    function notti() { return hsFrom.value && hsTo.value ? Math.round((parse(hsTo.value) - parse(hsFrom.value)) / 864e5) : 0; }
    function mostraCampo(btn, val) {
      if (!val) { btn.innerHTML = '<span class="hs-ph">' + btn.getAttribute('data-ph') + '</span>'; btn.classList.remove('has'); return; }
      var d = parse(val);
      var mese = window.innerWidth < 520 ? fmtMeseBreve.format(d) : fmtMese.format(d);
      btn.innerHTML = '<span class="hs-dn">' + d.getDate() + '</span><span class="hs-dm"><b>' + cap(mese) + '</b><i>' + fmtGiorno.format(d) + '</i></span>';
      btn.classList.add('has');
    }
    function aggiornaCampi() { mostraCampo(hsFromBtn, hsFrom.value); mostraCampo(hsToBtn, hsTo.value); }

    function disegnaMese(base) {
      var y = base.getFullYear(), m = base.getMonth();
      var h = '<div class="drp-month"><div class="drp-title">' + cap(fmtMese.format(base)) + '</div><div class="drp-grid">';
      nomiSett.forEach(function (n) { h += '<span class="drp-wd">' + n + '</span>'; });
      var vuoti = (new Date(y, m, 1).getDay() + 6) % 7;
      for (var i = 0; i < vuoti; i++) h += '<span></span>';
      var gg = new Date(y, m + 1, 0).getDate();
      var fine = hsTo.value || (hsFrom.value && hoverDay && hoverDay > hsFrom.value ? hoverDay : '');
      for (var g = 1; g <= gg; g++) {
        var s = iso(new Date(y, m, g)), c = 'drp-day';
        if (s < oggi) c += ' past';
        if (s === oggi) c += ' today';
        if (s === hsFrom.value) c += ' start';
        if (s === hsTo.value || (!hsTo.value && s === fine)) c += ' end';
        if (hsFrom.value && fine && s > hsFrom.value && s < fine) c += ' in';
        h += '<button type="button" class="' + c + '" data-d="' + s + '"' + (s < oggi ? ' disabled' : '') + '>' + g + '</button>';
      }
      return h + '</div></div>';
    }
    function disegna() {
      var primo = parse(oggi); primo.setDate(1);
      var prossimo = new Date(meseVisto.getFullYear(), meseVisto.getMonth() + 1, 1);
      var n = notti();
      drp.innerHTML =
        '<button type="button" class="drp-nav prev" aria-label="&lsaquo;"' + (meseVisto <= primo ? ' disabled' : '') + '>&lsaquo;</button>' +
        '<button type="button" class="drp-nav next" aria-label="&rsaquo;">&rsaquo;</button>' +
        '<div class="drp-months">' + disegnaMese(meseVisto) + disegnaMese(prossimo) + '</div>' +
        '<div class="drp-foot"><span>' + (n ? n + ' ' + hs.getAttribute(n === 1 ? 'data-night' : 'data-nights') : '') + '</span>' +
        '<button type="button" class="drp-close">' + hs.getAttribute('data-close') + '</button></div>';
    }
    function posiziona() {
      if (window.innerWidth < 700) { drp.style.top = drp.style.left = ''; return; } // su mobile e' un pannello fisso in basso
      var r = hs.getBoundingClientRect();
      drp.style.top = (r.bottom + window.scrollY + 8) + 'px';
      drp.style.left = Math.max(8, r.left + window.scrollX) + 'px';
    }
    function apri(fase) {
      drp.setAttribute('data-fase', fase);
      var rif = fase === 'to' && hsFrom.value ? hsFrom.value : (hsFrom.value || oggi);
      meseVisto = parse(rif); meseVisto.setDate(1);
      hsFromBtn.classList.toggle('active', fase === 'from');
      hsToBtn.classList.toggle('active', fase === 'to');
      disegna(); drp.hidden = false; posiziona();
    }
    function chiudi() { drp.hidden = true; hoverDay = null; hsFromBtn.classList.remove('active'); hsToBtn.classList.remove('active'); }

    hsFromBtn.addEventListener('click', function (e) { e.stopPropagation(); apri('from'); });
    hsToBtn.addEventListener('click', function (e) { e.stopPropagation(); apri(hsFrom.value ? 'to' : 'from'); });
    drp.addEventListener('click', function (e) {
      e.stopPropagation();
      var b = e.target.closest('button');
      if (!b) return;
      if (b.classList.contains('drp-close')) return chiudi();
      if (b.classList.contains('prev')) { meseVisto.setMonth(meseVisto.getMonth() - 1); return disegna(); }
      if (b.classList.contains('next')) { meseVisto.setMonth(meseVisto.getMonth() + 1); return disegna(); }
      var d = b.getAttribute('data-d');
      if (!d || b.disabled) return;
      if (drp.getAttribute('data-fase') === 'from' || !hsFrom.value || d <= hsFrom.value) {
        // primo clic (o data prima dell'arrivo): nuovo arrivo, si passa a scegliere la partenza
        hsFrom.value = d; hsTo.value = ''; drp.setAttribute('data-fase', 'to');
        hsFromBtn.classList.remove('active'); hsToBtn.classList.add('active');
        aggiornaCampi(); disegna();
      } else {
        hsTo.value = d; aggiornaCampi(); disegna();
        setTimeout(chiudi, 350);
      }
    });
    drp.addEventListener('mouseover', function (e) {
      var b = e.target.closest('.drp-day');
      if (!b || hsTo.value || !hsFrom.value || drp.getAttribute('data-fase') !== 'to') return;
      var d = b.getAttribute('data-d');
      if (d === hoverDay) return;
      hoverDay = d;
      // aggiorno solo le classi, senza ridisegnare (il mouse resta sullo stesso bottone)
      Array.prototype.forEach.call(drp.querySelectorAll('.drp-day'), function (x) {
        var s = x.getAttribute('data-d');
        x.classList.toggle('in', s > hsFrom.value && s < d);
        x.classList.toggle('end', d > hsFrom.value && s === d);
      });
    });
    document.addEventListener('click', function () { if (!drp.hidden) chiudi(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !drp.hidden) chiudi(); });
    window.addEventListener('resize', function () { if (!drp.hidden) posiziona(); });
    aggiornaCampi();
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
