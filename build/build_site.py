# -*- coding: utf-8 -*-
# Generatore statico del portale Salento Case Vacanze — 5 lingue
import json, re, shutil, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
from translations import (LANGS, LANG_NAMES, LANG_FLAGS, HTML_LANG, SLUGS, UI, HOME,
                          CITY_BLURBS, UNIT_SENTENCE, WP_DESC, LOCATIONS, ABOUT, TERMS,
                          UNIT_META, APTS_PAGE_META, LOCS_PAGE_META, CONTACTS_META)
from privacy_i18n import BANNER, PRIVACY

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://salentocasevacanze.com'  # dominio di produzione
PHONE = '+39 339 809 8421'
PHONE_RAW = '+393398098421'
WA_RAW = '393203581118'
EMAIL = 'prenotazionisalentovacanze@gmail.com'
FB = 'https://www.facebook.com/levanteturismosalento'
KROSS_LIST = 'https://salentocasevacanze.kross.travel/it/appartamenti'
ORG = 'Salento Case Vacanze srls'
ADDRESS = 'Via Nazario Sauro, 43 – 73040 Morciano di Leuca (LE)'
VAT = '05262750754'

units = json.load(open(ROOT / 'data' / 'units.json', encoding='utf-8'))

# immagini di riferimento per località (dalle foto WP ottimizzate)
LOC_IMAGES = {
    'leuca': 'assets/img/opt/leuca.webp',
    'torre-vado-e-pescoluse': 'assets/img/opt/pescoluse.webp',
    'gallipoli': 'assets/img/opt/gallipoli.webp',
    'otranto': 'assets/img/opt/otranto.webp',
    'torre-dellorso': 'assets/img/opt/torredellorso.webp',
    'castro': 'assets/img/opt/castro.webp',
}
HERO_IMG = 'assets/img/opt/hero.webp'
LOGO = 'assets/img/opt/logo3-1.png'

# mappa città -> slug località (per collegare unità e guide)
CITY_TO_LOC = {
    'Marina Di Leuca': 'leuca', 'Marina Di Pescoluse': 'torre-vado-e-pescoluse',
    'Lido Marini': 'torre-vado-e-pescoluse', 'Castrignano Del Capo': 'leuca',
    'Barbarano del Capo': 'torre-vado-e-pescoluse', 'Castro Marina': 'castro',
    'Otranto': 'otranto', 'Gallipoli - Rivabella': 'gallipoli', 'Lecce': None,
}
# nomi città visualizzati (normalizzati)
CITY_DISPLAY = {
    'Marina Di Leuca': 'Santa Maria di Leuca', 'Marina Di Pescoluse': 'Pescoluse',
    'Lido Marini': 'Lido Marini', 'Castrignano Del Capo': 'Castrignano del Capo',
    'Barbarano del Capo': 'Barbarano del Capo', 'Castro Marina': 'Castro Marina',
    'Otranto': 'Otranto', 'Gallipoli - Rivabella': 'Gallipoli', 'Lecce': 'Lecce',
}

ICONS = {
    'guests': '👥', 'bed': '🛏️', 'bath': '🛁', 'pin': '📍', 'lock': '🔒',
}


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def lang_root(lang):
    return '' if lang == 'it' else lang + '/'


def rel(lang, depth):
    """prefisso relativo per risalire alla root del sito"""
    d = depth + (0 if lang == 'it' else 1)
    return '../' * d


def page_url(lang, path=''):
    """URL assoluto di una pagina (path senza lingua, es. 'appartamenti/x/')"""
    return f"{SITE}/{lang_root(lang)}{path}"


def loc_path(lang, key, slug=None):
    s = SLUGS[lang]
    if key == 'home':
        return ''
    if key == 'apts':
        return f"{s['apartments']}/" + (f"{slug}/" if slug else '')
    if key == 'locs':
        return f"{s['locations']}/" + (f"{slug}/" if slug else '')
    return f"{s[key]}/"


def hreflang_links(pathmap):
    """pathmap: lang -> path relativo senza lingua"""
    out = []
    for l in LANGS:
        out.append(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{page_url(l, pathmap[l])}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("it", pathmap["it"])}">')
    return '\n'.join(out)


def unit_city(u):
    return CITY_DISPLAY.get(u['city'], u['city'])


def unit_desc(u, lang):
    """descrizione della scheda unità"""
    if u['source'] == 'wp':
        if lang == 'it':
            return u['desc_it']
        return WP_DESC[u['slug']][lang]
    blurb = CITY_BLURBS.get(u['city'], {}).get(lang, '')
    ui = UI[lang]
    g_lbl = ui['guests']
    b_lbl = ui['bedrooms'] if (u['bedrooms'] or 0) != 1 else ui['bedroom']
    ba_lbl = ui['bathrooms'] if (u['bathrooms'] or 0) != 1 else ui['bathroom']
    sent = UNIT_SENTENCE[lang].format(name=u['name'], guests=u['guests'], g_lbl=g_lbl,
                                      bedrooms=u['bedrooms'], b_lbl=b_lbl,
                                      bathrooms=u['bathrooms'], ba_lbl=ba_lbl)
    return blurb + ' ' + sent


def img_alt(u, lang, i):
    city = unit_city(u)
    alts = {
        'it': f"{u['name']} – casa vacanza a {city}, Salento – foto {i}",
        'en': f"{u['name']} – holiday home in {city}, Salento, Italy – photo {i}",
        'fr': f"{u['name']} – location de vacances à {city}, Salento – photo {i}",
        'de': f"{u['name']} – Ferienwohnung in {city}, Salento – Foto {i}",
        'es': f"{u['name']} – casa de vacaciones en {city}, Salento – foto {i}",
    }
    return alts[lang]


def head(lang, title, desc, canonical_path, pathmap, depth, og_img=None, extra_ld=''):
    r = rel(lang, depth)
    og_img = og_img or HERO_IMG
    return f"""<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{page_url(lang, canonical_path)}">
{hreflang_links(pathmap)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Salento Case Vacanze">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{page_url(lang, canonical_path)}">
<meta property="og:image" content="{SITE}/{og_img}">
<meta property="og:locale" content="{HTML_LANG[lang].replace('-', '_')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="icon" type="image/png" href="{r}{LOGO}">
<link rel="stylesheet" href="{r}assets/fonts/fonts.css">
<link rel="stylesheet" href="{r}assets/css/style.css">
{extra_ld}
</head>
<body>
<a class="skip-link" href="#main">{UI[lang]['skip_content']}</a>
"""


def header_nav(lang, depth, active, pathmap):
    r = rel(lang, depth)
    lr = lang_root(lang)
    ui = UI[lang]
    s = SLUGS[lang]
    def cls(k):
        return ' class="active"' if k == active else ''
    lang_items = ''.join(
        f'<a href="{r}{lang_root(l)}{pathmap[l]}"{" class=" + chr(34) + "current" + chr(34) if l == lang else ""}>'
        f'{LANG_FLAGS[l]} {LANG_NAMES[l]}</a>'
        for l in LANGS)
    return f"""<header class="site-header">
<div class="header-inner">
  <a class="brand" href="{r}{lr}" aria-label="Salento Case Vacanze – Home">
    <img src="{r}{LOGO}" alt="Salento Case Vacanze – logo" width="190" height="127">
  </a>
  <nav class="main-nav" aria-label="principale">
    <a href="{r}{lr}"{cls('home')}>{ui['nav_home']}</a>
    <a href="{r}{lr}{s['apartments']}/"{cls('apts')}>{ui['nav_apts']}</a>
    <a href="{r}{lr}{s['locations']}/"{cls('locs')}>{ui['nav_locs']}</a>
    <a href="{r}{lr}{s['about']}/"{cls('about')}>{ui['nav_about']}</a>
    <a href="{r}{lr}{s['contacts']}/"{cls('contacts')}>{ui['nav_contacts']}</a>
    <a class="nav-cta" href="{KROSS_LIST}" target="_blank" rel="noopener">{ui['book_now']}</a>
  </nav>
  <div style="display:flex;align-items:center;gap:10px">
    <div class="lang-switch">
      <button class="lang-btn" aria-haspopup="true" aria-expanded="false">{LANG_FLAGS[lang]} {lang.upper()} ▾</button>
      <div class="lang-menu">{lang_items}</div>
    </div>
    <button class="hamburger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</div>
</header>
<main id="main">
"""


def footer(lang, depth):
    r = rel(lang, depth)
    lr = lang_root(lang)
    ui = UI[lang]
    s = SLUGS[lang]
    wa_svg = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.1.6 4.2 1.6 6L4 29l8.2-1.5c1.2.5 2.5.8 3.8.8 6.6 0 12-5.4 12-12S22.6 3 16 3zm0 21.8c-1.2 0-2.4-.3-3.5-.8l-.6-.3-4.9.9.9-4.7-.3-.6c-.9-1.5-1.4-3.2-1.4-5 0-5.4 4.4-9.8 9.8-9.8s9.8 4.4 9.8 9.8-4.4 9.5-9.8 9.5zm5.4-7.1c-.3-.1-1.7-.9-2-1s-.5-.1-.7.1c-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.2-.5-2.4-1.5-.9-.8-1.5-1.8-1.6-2.1-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5s-.7-1.6-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.7-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.7-.4z"/></svg>')
    return f"""</main>
<a class="wa-float" href="https://wa.me/{WA_RAW}" target="_blank" rel="noopener" aria-label="{ui['whatsapp_msg']}">{wa_svg}</a>
<footer class="site-footer">
<div class="footer-grid">
  <div>
    <img class="footer-logo" src="{r}{LOGO}" alt="Salento Case Vacanze – logo" loading="lazy">
    <p>{ui['footer_tagline']}</p>
    <p style="margin-top:14px;font-size:.9rem">{ORG}<br>{ADDRESS}<br>{ui['vat']} {VAT}</p>
  </div>
  <div>
    <h4>{ui['footer_links']}</h4>
    <ul>
      <li><a href="{r}{lr}{s['apartments']}/">{ui['nav_apts']}</a></li>
      <li><a href="{r}{lr}{s['locations']}/">{ui['nav_locs']}</a></li>
      <li><a href="{r}{lr}{s['about']}/">{ui['nav_about']}</a></li>
      <li><a href="{r}{lr}{s['terms']}/">{TERMS[lang]['title']}</a></li>
      <li><a href="{r}{lr}{s['privacy']}/">{PRIVACY[lang]['title']}</a></li>
      <li><a href="https://salentocasevacanze.kross.travel/" target="_blank" rel="noopener">{ui['manage_booking']}</a></li>
    </ul>
  </div>
  <div>
    <h4>{ui['footer_contacts']}</h4>
    <ul>
      <li>📞 <a href="tel:{PHONE_RAW}">{PHONE}</a></li>
      <li>💬 <a href="https://wa.me/{WA_RAW}" target="_blank" rel="noopener">WhatsApp</a></li>
      <li>✉️ <a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li>👍 <a href="{FB}" target="_blank" rel="noopener">Facebook</a></li>
    </ul>
  </div>
</div>
<div class="footer-bottom"><div class="container">
  <span>© 2026 {ORG} — {ui['rights']}</span>
  <a href="{r}{lr}{s['privacy']}/">{PRIVACY[lang]['title']}</a>
</div></div>
</footer>
<div class="cookie-banner" id="cookieBanner" role="region" aria-label="Cookie">
  <p>🍪 {BANNER[lang]['text']} <a href="{r}{lr}{s['privacy']}/">{BANNER[lang]['more']}</a></p>
  <button class="btn btn-primary" id="cookieOk">{BANNER[lang]['ok']}</button>
</div>
<script src="{r}assets/js/main.js" defer></script>
</body>
</html>
"""


def apt_card(u, lang, depth):
    r = rel(lang, depth)
    lr = lang_root(lang)
    ui = UI[lang]
    s = SLUGS[lang]
    city = unit_city(u)
    imgs = u['images'][:3]
    data_imgs = '|'.join(r + i for i in imgs)
    href = f"{r}{lr}{s['apartments']}/{u['slug']}/"
    specs = []
    if u.get('guests'):
        specs.append(f"<span>{ICONS['guests']} {u['guests']} {ui['guests']}</span>")
    if u.get('bedrooms'):
        lbl = ui['bedrooms'] if u['bedrooms'] != 1 else ui['bedroom']
        specs.append(f"<span>{ICONS['bed']} {u['bedrooms']} {lbl}</span>")
    if u.get('bathrooms'):
        lbl = ui['bathrooms'] if u['bathrooms'] != 1 else ui['bathroom']
        specs.append(f"<span>{ICONS['bath']} {u['bathrooms']} {lbl}</span>")
    return f"""<article class="apt-card reveal" data-city="{esc(u['city'])}">
  <a class="apt-media" href="{href}" data-imgs="{esc(data_imgs)}">
    <img src="{r}{imgs[0]}" alt="{esc(img_alt(u, lang, 1))}" loading="lazy" width="600" height="450">
    <span class="apt-badge">{ICONS['pin']} {esc(city)}</span>
  </a>
  <div class="apt-body">
    <h3><a href="{href}">{esc(u['name'])}</a></h3>
    <div class="apt-specs">{''.join(specs)}</div>
    <div class="apt-actions">
      <a class="btn btn-outline" href="{href}">{ui['discover']}</a>
      <a class="btn btn-sea" href="{u['booking']}" target="_blank" rel="noopener">{ui['book_now']}</a>
    </div>
  </div>
</article>"""


def org_ld(lang):
    return f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"TravelAgency","name":"{ORG}",
"url":"{SITE}/","logo":"{SITE}/{LOGO}","image":"{SITE}/{HERO_IMG}",
"telephone":"{PHONE_RAW}","email":"{EMAIL}",
"address":{{"@type":"PostalAddress","streetAddress":"Via Nazario Sauro, 43","addressLocality":"Morciano di Leuca","addressRegion":"LE","postalCode":"73040","addressCountry":"IT"}},
"vatID":"IT{VAT}","sameAs":["{FB}"],
"areaServed":{{"@type":"AdministrativeArea","name":"Salento, Puglia, Italia"}}}}
</script>"""


def breadcrumb_ld(lang, crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs, 1):
        items.append(f'{{"@type":"ListItem","position":{i},"name":"{esc(name)}","item":"{url}"}}')
    return ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList",'
            '"itemListElement":[' + ','.join(items) + ']}</script>')


def write_page(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')


sitemap_entries = []  # (pathmap)


def register(pathmap):
    sitemap_entries.append(pathmap)


# ============ HOME ============
def build_home(lang):
    h = HOME[lang]
    ui = UI[lang]
    s = SLUGS[lang]
    lr = lang_root(lang)
    depth = 0
    r = rel(lang, depth)
    pathmap = {l: '' for l in LANGS}
    ld = org_ld(lang) + f"""
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebSite","name":"Salento Case Vacanze","url":"{SITE}/",
"inLanguage":"{HTML_LANG[lang]}"}}
</script>"""
    out = head(lang, h['meta_title'], h['meta_desc'], '', pathmap, depth, extra_ld=ld)
    out += header_nav(lang, depth, 'home', pathmap)
    icons = ['🤝', '⚡', '🏖️', '🧭']
    usps = ''.join(
        f'<div class="usp reveal"><div class="icon">{icons[i]}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
        for i, (t, d) in enumerate(h['usp']))
    # in evidenza: distribuisci tra le località (una unità per città, poi si ricomincia)
    by_city = {}
    for u in units:
        by_city.setdefault(u['city'], []).append(u)
    featured = []
    giro = 0
    while len(featured) < 8 and giro < 10:
        for c in by_city:
            if len(by_city[c]) > giro:
                featured.append(by_city[c][giro])
        giro += 1
    cards = ''.join(apt_card(u, lang, depth) for u in featured[:8])
    loc_cards = ''
    for slug, loc in LOCATIONS.items():
        img = LOC_IMAGES.get(slug, HERO_IMG)
        loc_cards += f"""<a class="loc-card reveal" href="{r}{lr}{s['locations']}/{slug}/">
  <img src="{r}{img}" alt="{esc(loc['name'][lang])} – Salento" loading="lazy">
  <div class="loc-info"><h3>{esc(loc['name'][lang])}</h3>
  <span class="fake-link">{ui['discover']} →</span></div></a>"""
    out += f"""
<section class="hero" style="background-image:url('{r}{HERO_IMG}')">
  <div class="hero-content">
    <h1>{esc(h['hero_title'])}</h1>
    <p>{esc(h['hero_sub'])}</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{r}{lr}{s['apartments']}/">{ui['hero_cta_primary']}</a>
      <a class="btn btn-ghost" href="{r}{lr}{s['locations']}/">{ui['hero_cta_secondary']}</a>
    </div>
  </div>
  <div class="hero-scroll">▾</div>
</section>
<section class="section">
  <div class="container"><div class="usp-grid">{usps}</div></div>
</section>
<section class="section section-alt" id="apts">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">{ui['nav_apts']}</span>
      <h2>{esc(h['apts_title'])}</h2><p>{esc(h['apts_sub'])}</p></div>
    <div class="apt-grid">{cards}</div>
    <p style="text-align:center;margin-top:44px"><a class="btn btn-primary" href="{r}{lr}{s['apartments']}/">{ui['view_all']} ({len(units)})</a></p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">{ui['nav_locs']}</span>
      <h2>{esc(h['locs_title'])}</h2><p>{esc(h['locs_sub'])}</p></div>
    <div class="loc-grid">{loc_cards}</div>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="cta-band reveal">
      <h2>{esc(h['cta_title'])}</h2><p>{esc(h['cta_text'])}</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="{KROSS_LIST}" target="_blank" rel="noopener">{ui['check_availability']}</a>
        <a class="btn btn-ghost" href="https://wa.me/{WA_RAW}" target="_blank" rel="noopener">WhatsApp</a>
      </div>
    </div>
  </div>
</section>
"""
    out += footer(lang, depth)
    write_page(f"{lr}index.html", out)


# ============ LISTA APPARTAMENTI ============
def build_apartments_index(lang):
    ui = UI[lang]
    m = APTS_PAGE_META[lang]
    s = SLUGS[lang]
    lr = lang_root(lang)
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'apts') for l in LANGS}
    cities = []
    for u in units:
        if u['city'] not in cities:
            cities.append(u['city'])
    chips = f'<button class="chip active" data-city="*">{ui["all_locations"]}</button>'
    chips += ''.join(f'<button class="chip" data-city="{esc(c)}">{esc(CITY_DISPLAY.get(c, c))}</button>' for c in cities)
    cards = ''.join(apt_card(u, lang, depth) for u in units)
    ld = breadcrumb_ld(lang, [(ui['breadcrumb_home'], page_url(lang)), (m['h1'], page_url(lang, pathmap[lang]))])
    out = head(lang, m['title'], m['desc'], pathmap[lang], pathmap, depth, extra_ld=ld)
    out += header_nav(lang, depth, 'apts', pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {ui['nav_apts']}</nav>
  <div class="page-title"><h1>{esc(m['h1'])}</h1>
  <p style="color:var(--ink-soft);max-width:700px;margin-top:10px">{esc(m['desc'])}</p></div>
</div>
<section class="section" style="padding-top:40px">
  <div class="container">
    <div class="filter-bar">{chips}</div>
    <div class="apt-grid">{cards}</div>
  </div>
</section>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['apartments']}/index.html", out)
    register(pathmap)


# ============ DETTAGLIO UNITÀ ============
def build_unit(u, lang):
    ui = UI[lang]
    s = SLUGS[lang]
    lr = lang_root(lang)
    depth = 2
    r = rel(lang, depth)
    city = unit_city(u)
    pathmap = {l: loc_path(l, 'apts', u['slug']) for l in LANGS}
    m = UNIT_META[lang]
    title = m['title'].format(name=u['name'], city=city)
    desc = m['desc'].format(name=u['name'], city=city, guests=u.get('guests') or '', bedrooms=u.get('bedrooms') or '')
    desc_text = unit_desc(u, lang)
    imgs = u['images']
    og = imgs[0] if imgs else HERO_IMG

    gallery = ''
    for i, im in enumerate(imgs, 1):
        more = ''
        hidden = ' style="display:none"' if i > 5 else ''
        if i == 5 and len(imgs) > 5:
            more = f'<span class="more-count">+{len(imgs) - 5}</span>'
        if i == 2 and len(imgs) > 2:
            more += f'<span class="more-count" style="display:none">+{len(imgs) - 2}</span>'
        gallery += (f'<a href="{r}{im}"{hidden}><img src="{r}{im}" alt="{esc(img_alt(u, lang, i))}" '
                    f'loading="{"eager" if i == 1 else "lazy"}">{more}</a>')

    specs = []
    if u.get('guests'):
        specs.append(f'<span class="spec-pill">{ICONS["guests"]} {u["guests"]} {ui["guests"]}</span>')
    if u.get('bedrooms'):
        lbl = ui['bedrooms'] if u['bedrooms'] != 1 else ui['bedroom']
        specs.append(f'<span class="spec-pill">{ICONS["bed"]} {u["bedrooms"]} {lbl}</span>')
    if u.get('bathrooms'):
        lbl = ui['bathrooms'] if u['bathrooms'] != 1 else ui['bathroom']
        specs.append(f'<span class="spec-pill">{ICONS["bath"]} {u["bathrooms"]} {lbl}</span>')

    services = ''
    if u.get('services'):
        services = ('<h2>' + ui['services'] + '</h2><div class="service-tags">' +
                    ''.join(f'<span>{esc(x)}</span>' for x in u['services']) + '</div>')

    # altre soluzioni nella stessa città
    others = [x for x in units if x['slug'] != u['slug'] and x['city'] == u['city']][:3]
    if len(others) < 3:
        others += [x for x in units if x['slug'] != u['slug'] and x not in others][:3 - len(others)]
    other_cards = ''.join(apt_card(x, lang, depth) for x in others)

    cis = f'<p class="cis-note">{ui["cis_label"]}: {u["cis"]}</p>' if u.get('cis') else ''
    ld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"VacationRental","name":"{esc(u['name'])}",
"url":"{page_url(lang, pathmap[lang])}",
"image":[{','.join(f'"{SITE}/{i}"' for i in imgs[:5])}],
"description":"{esc(desc_text[:300])}",
"address":{{"@type":"PostalAddress","addressLocality":"{esc(city)}","addressRegion":"LE","addressCountry":"IT"}},
"containsPlace":{{"@type":"Accommodation","occupancy":{{"@type":"QuantitativeValue","maxValue":{u.get('guests') or 2}}},"numberOfBedrooms":{u.get('bedrooms') or 1},"numberOfBathroomsTotal":{u.get('bathrooms') or 1}}},
"brand":{{"@type":"Brand","name":"Salento Case Vacanze"}},
"potentialAction":{{"@type":"ReserveAction","target":"{u['booking']}"}}}}
</script>""" + breadcrumb_ld(lang, [
        (ui['breadcrumb_home'], page_url(lang)),
        (ui['nav_apts'], page_url(lang, loc_path(lang, 'apts'))),
        (u['name'], page_url(lang, pathmap[lang]))])

    out = head(lang, title, desc, pathmap[lang], pathmap, depth, og_img=imgs[0] if imgs else None, extra_ld=ld)
    out += header_nav(lang, depth, 'apts', pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › <a href="{r}{lr}{s['apartments']}/">{ui['nav_apts']}</a> › {esc(u['name'])}</nav>
  <div class="detail-head">
    <h1>{esc(u['name'])}</h1>
    <p class="detail-loc">{ICONS['pin']} {esc(city)} · Salento, Puglia</p>
  </div>
  <div class="gallery">{gallery}</div>
  <div class="detail-grid">
    <div class="detail-main">
      <div class="spec-row">{''.join(specs)}</div>
      <h2>{ui['description']}</h2>
      <p>{esc(desc_text)}</p>
      {services}
    </div>
    <aside class="book-box reveal">
      <h3>{ui['check_availability']}</h3>
      <p>{ui['book_direct']}</p>
      <a class="btn btn-sea" href="{u['booking']}" target="_blank" rel="noopener">{ui['book_now']}</a>
      <a class="btn btn-outline" style="border:1.5px solid var(--terra);color:var(--terra)" href="https://wa.me/{WA_RAW}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn btn-outline" style="border:1.5px solid var(--sea);color:var(--sea)" href="tel:{PHONE_RAW}">{ui['call_us']}</a>
      <p class="book-secure">{ICONS['lock']} {ui['book_direct']}</p>
      {cis}
    </aside>
  </div>
  <div class="section-head reveal"><h2 style="font-family:var(--font-display)">{ui['other_apts']}</h2></div>
  <div class="apt-grid" style="margin-bottom:70px">{other_cards}</div>
</div>
<div class="lightbox" role="dialog" aria-modal="true">
  <button class="lb-btn lb-close" aria-label="Chiudi">✕</button>
  <button class="lb-btn lb-prev" aria-label="Prev">‹</button>
  <img alt="">
  <button class="lb-btn lb-next" aria-label="Next">›</button>
  <div class="lb-count"></div>
</div>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['apartments']}/{u['slug']}/index.html", out)
    register(pathmap)


# ============ LISTA LOCALITÀ ============
def build_locations_index(lang):
    ui = UI[lang]
    m = LOCS_PAGE_META[lang]
    s = SLUGS[lang]
    lr = lang_root(lang)
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'locs') for l in LANGS}
    cards = ''
    for slug, loc in LOCATIONS.items():
        img = LOC_IMAGES.get(slug, HERO_IMG)
        n_units = sum(1 for u in units if CITY_TO_LOC.get(u['city']) == slug)
        count_txt = f"{n_units} {ui['units_count']}" if n_units else ''
        cards += f"""<a class="loc-card reveal" href="{r}{lr}{s['locations']}/{slug}/">
  <img src="{r}{img}" alt="{esc(loc['name'][lang])} – Salento" loading="lazy">
  <div class="loc-info"><h3>{esc(loc['name'][lang])}</h3><p>{count_txt}</p>
  <span class="fake-link">{ui['discover']} →</span></div></a>"""
    ld = breadcrumb_ld(lang, [(ui['breadcrumb_home'], page_url(lang)), (m['h1'], page_url(lang, pathmap[lang]))])
    out = head(lang, m['title'], m['desc'], pathmap[lang], pathmap, depth, extra_ld=ld)
    out += header_nav(lang, depth, 'locs', pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {ui['nav_locs']}</nav>
  <div class="page-title"><h1>{esc(m['h1'])}</h1>
  <p style="color:var(--ink-soft);max-width:700px;margin-top:10px">{esc(m['desc'])}</p></div>
</div>
<section class="section" style="padding-top:40px"><div class="container"><div class="loc-grid">{cards}</div></div></section>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['locations']}/index.html", out)
    register(pathmap)


# ============ DETTAGLIO LOCALITÀ ============
def build_location(slug, lang):
    loc = LOCATIONS[slug]
    ui = UI[lang]
    s = SLUGS[lang]
    lr = lang_root(lang)
    depth = 2
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'locs', slug) for l in LANGS}
    img = LOC_IMAGES.get(slug, HERO_IMG)
    title = loc['title'][lang] + ' | Salento Case Vacanze'
    desc = loc['paras'][lang][0][:158]
    paras = ''.join(f'<p>{esc(p)}</p>' for p in loc['paras'][lang])
    local_units = [u for u in units if CITY_TO_LOC.get(u['city']) == slug]
    unit_cards = ''.join(apt_card(u, lang, depth) for u in local_units[:6])
    units_section = ''
    if unit_cards:
        units_section = f"""<div class="section-head reveal" style="margin-top:60px"><h2 style="font-family:var(--font-display)">{ui['apts_in']} {esc(loc['name'][lang])}</h2></div>
<div class="apt-grid" style="margin-bottom:40px">{unit_cards}</div>"""
    ld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"TouristDestination","name":"{esc(loc['name'][lang])}",
"description":"{esc(desc)}","url":"{page_url(lang, pathmap[lang])}",
"containedInPlace":{{"@type":"AdministrativeArea","name":"Salento, Puglia, Italia"}}}}
</script>""" + breadcrumb_ld(lang, [
        (ui['breadcrumb_home'], page_url(lang)),
        (ui['nav_locs'], page_url(lang, loc_path(lang, 'locs'))),
        (loc['name'][lang], page_url(lang, pathmap[lang]))])
    out = head(lang, title, desc, pathmap[lang], pathmap, depth, og_img=img, extra_ld=ld)
    out += header_nav(lang, depth, 'locs', pathmap)
    out += f"""
<section class="loc-hero" style="background-image:url('{r}{img}')">
  <div class="container"><h1>{esc(loc['title'][lang])}</h1></div>
</section>
<section class="section">
  <div class="container">
    <nav class="breadcrumbs" style="padding-bottom:18px"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › <a href="{r}{lr}{s['locations']}/">{ui['nav_locs']}</a> › {esc(loc['name'][lang])}</nav>
    <div class="prose reveal">{paras}</div>
    {units_section}
  </div>
</section>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['locations']}/{slug}/index.html", out)
    register(pathmap)


# ============ CHI SIAMO ============
def build_about(lang):
    a = ABOUT[lang]
    ui = UI[lang]
    lr = lang_root(lang)
    s = SLUGS[lang]
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'about') for l in LANGS}
    paras = ''.join(f'<p>{esc(p)}</p>' for p in a['paras'])
    ld = org_ld(lang)
    out = head(lang, a['title'] + ' | Salento Case Vacanze', a['meta_desc'], pathmap[lang], pathmap, depth, extra_ld=ld)
    out += header_nav(lang, depth, 'about', pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {esc(a['title'])}</nav>
  <div class="page-title"><h1>{esc(a['title'])}</h1></div>
</div>
<section class="section" style="padding-top:34px"><div class="container"><div class="prose reveal">{paras}</div>
<div class="cta-band reveal" style="margin-top:56px">
  <h2>{esc(HOME[lang]['cta_title'])}</h2><p>{esc(HOME[lang]['cta_text'])}</p>
  <a class="btn btn-primary" href="{r}{lr}{s['apartments']}/">{ui['hero_cta_primary']}</a>
</div></div></section>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['about']}/index.html", out)
    register(pathmap)


# ============ CONTATTI ============
def build_contacts(lang):
    ui = UI[lang]
    m = CONTACTS_META[lang]
    lr = lang_root(lang)
    s = SLUGS[lang]
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'contacts') for l in LANGS}
    ld = org_ld(lang)
    out = head(lang, m['title'], m['desc'], pathmap[lang], pathmap, depth, extra_ld=ld)
    out += header_nav(lang, depth, 'contacts', pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {ui['nav_contacts']}</nav>
  <div class="page-title"><h1>{ui['nav_contacts']}</h1></div>
  <div class="contact-grid">
    <div class="contact-card reveal"><div class="icon">📞</div><h3>{ui['call_us']}</h3><a href="tel:{PHONE_RAW}">{PHONE}</a></div>
    <div class="contact-card reveal"><div class="icon">💬</div><h3>WhatsApp</h3><a href="https://wa.me/{WA_RAW}" target="_blank" rel="noopener">+39 320 358 1118</a></div>
    <div class="contact-card reveal"><div class="icon">✉️</div><h3>{ui['write_us']}</h3><a href="mailto:{EMAIL}" style="word-break:break-all">{EMAIL}</a></div>
    <div class="contact-card reveal"><div class="icon">📍</div><h3>{ORG}</h3><p style="font-size:.92rem">{ADDRESS}<br>{ui['vat']} {VAT}</p></div>
  </div>
  <div class="cta-band reveal" style="margin:40px 0 70px">
    <h2>{esc(HOME[lang]['cta_title'])}</h2><p>{esc(HOME[lang]['cta_text'])}</p>
    <a class="btn btn-primary" href="{KROSS_LIST}" target="_blank" rel="noopener">{ui['check_availability']}</a>
  </div>
</div>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['contacts']}/index.html", out)
    register(pathmap)


# ============ CONDIZIONI ============
def build_terms(lang):
    t = TERMS[lang]
    ui = UI[lang]
    lr = lang_root(lang)
    s = SLUGS[lang]
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'terms') for l in LANGS}
    items = ''.join(f'<div class="term-item reveal"><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for h, p in t['items'])
    out = head(lang, t['title'] + ' | Salento Case Vacanze', t['meta_desc'], pathmap[lang], pathmap, depth)
    out += header_nav(lang, depth, None, pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {esc(t['title'])}</nav>
  <div class="page-title"><h1>{esc(t['title'])}</h1></div>
  <section class="section" style="padding-top:30px"><div class="terms-list">{items}</div></section>
</div>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['terms']}/index.html", out)
    register(pathmap)


# ============ PRIVACY & COOKIE ============
def build_privacy(lang):
    p = PRIVACY[lang]
    ui = UI[lang]
    lr = lang_root(lang)
    s = SLUGS[lang]
    depth = 1
    r = rel(lang, depth)
    pathmap = {l: loc_path(l, 'privacy') for l in LANGS}
    items = ''.join(f'<div class="term-item reveal"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in p['sections'])
    out = head(lang, p['title'] + ' | Salento Case Vacanze', p['meta_desc'], pathmap[lang], pathmap, depth)
    out += header_nav(lang, depth, None, pathmap)
    out += f"""
<div class="container">
  <nav class="breadcrumbs"><a href="{r}{lr}">{ui['breadcrumb_home']}</a> › {esc(p['title'])}</nav>
  <div class="page-title"><h1>{esc(p['title'])}</h1>
  <p style="color:var(--ink-soft);margin-top:8px">{esc(p['updated'])}</p></div>
  <section class="section" style="padding-top:30px"><div class="terms-list">{items}</div></section>
</div>
"""
    out += footer(lang, depth)
    write_page(f"{lr}{s['privacy']}/index.html", out)
    register(pathmap)


# ============ SITEMAP, ROBOTS, LLMS ============
def build_seo_files():
    register({l: '' for l in LANGS})  # home
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    seen = set()
    for pm in sitemap_entries:
        for l in LANGS:
            url = page_url(l, pm[l])
            if url in seen:
                continue
            seen.add(url)
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{HTML_LANG[x]}" href="{page_url(x, pm[x])}"/>' for x in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("it", pm["it"])}"/>'
            lines.append(f'<url><loc>{url}</loc>{alts}<changefreq>weekly</changefreq></url>')
    lines.append('</urlset>')
    write_page('sitemap.xml', '\n'.join(lines))

    write_page('robots.txt', f"""User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
""")

    # llms.txt per motori AI
    apt_list = '\n'.join(
        f"- [{u['name']}]({page_url('it', loc_path('it', 'apts', u['slug']))}): "
        f"{unit_city(u)}, {u.get('guests') or '?'} ospiti, {u.get('bedrooms') or '?'} camere. "
        f"Prenotazione diretta: {u['booking']}" for u in units)
    write_page('llms.txt', f"""# Salento Case Vacanze

> Case vacanza e appartamenti nel Salento (Puglia, Italia): Santa Maria di Leuca, Pescoluse ("Maldive del Salento"), Lido Marini, Lecce, Castrignano del Capo, Gallipoli, Otranto e Castro. Prenotazione diretta online tramite Kross Booking, senza commissioni di intermediari. Sito in italiano, inglese, francese, tedesco e spagnolo.

Gestito da {ORG}, {ADDRESS}, P.IVA {VAT}. Telefono/WhatsApp: {PHONE} / +39 320 358 1118. Email: {EMAIL}.

## Appartamenti (con link di prenotazione diretta)
{apt_list}

## Località
""" + '\n'.join(f"- [{LOCATIONS[s]['name']['it']}]({page_url('it', loc_path('it', 'locs', s))}): {LOCATIONS[s]['title']['it']}" for s in LOCATIONS) + f"""

## Pagine
- [Chi siamo]({page_url('it', loc_path('it', 'about'))})
- [Contatti]({page_url('it', loc_path('it', 'contacts'))})
- [Condizioni generali]({page_url('it', loc_path('it', 'terms'))})

## Lingue
- Italiano (default): {SITE}/
- English: {SITE}/en/
- Français: {SITE}/fr/
- Deutsch: {SITE}/de/
- Español: {SITE}/es/
""")


# ============ MAIN ============
def main():
    n = 0
    for lang in LANGS:
        build_home(lang)
        build_apartments_index(lang)
        build_locations_index(lang)
        build_about(lang)
        build_contacts(lang)
        build_terms(lang)
        build_privacy(lang)
        for u in units:
            build_unit(u, lang)
            n += 1
        for slug in LOCATIONS:
            build_location(slug, lang)
            n += 1
    build_seo_files()
    total = len(list(ROOT.rglob('index.html')))
    print(f'OK: {total} pagine generate ({len(LANGS)} lingue, {len(units)} unità, {len(LOCATIONS)} località)')


if __name__ == '__main__':
    main()
