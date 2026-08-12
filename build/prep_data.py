# Normalizza i dati delle unità (24 Kross + 6 schede WP) in data/units.json
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path(r'C:/Users/dedon/AppData/Local/Temp/claude/C--Users-dedon-Desktop/9e9b014c-967d-4cfa-9923-c356e0c408ab/scratchpad')
kross = json.load(open(SCRATCH / 'kross-properties.json', encoding='utf-8'))
wp = json.load(open(SCRATCH / 'wp-content2.json', encoding='utf-8'))


def first_int(s):
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else None


units = []
for p in kross:
    slug = p['url'].strip('/')
    city = re.sub(r'\s+', ' ', p['city']).strip()
    name = ' '.join(w.capitalize() if w.isupper() or w.islower() else w for w in p['name'].split())
    units.append({
        'slug': slug, 'name': name, 'city': city,
        'guests': first_int(p['max_occupancy_str']),
        'bedrooms': first_int(p['max_n_bedrooms_str']),
        'bathrooms': first_int(p['max_n_bathrooms_str']),
        'address': p.get('address', ''),
        'booking': f'https://salentocasevacanze.kross.travel/{slug}',
        'images': [f'assets/img/kross/{slug}-{i}.webp' for i in range(1, len(p['images']) + 1)],
        'source': 'kross',
    })

WPA = {
    'appartamenti_bellavista-castro': dict(slug='bellavista-castro', name='Bellavista Castro', city='Castro Marina', guests=6, bedrooms=2, bathrooms=2),
    'appartamenti_casa-aragonese': dict(slug='casa-aragonese', name='Casa Aragonese', city='Otranto', guests=6, bedrooms=2, bathrooms=2),
    'appartamenti_casa-leuca-piccola': dict(slug='casa-leuca-piccola', name='Casa Leuca Piccola', city='Barbarano del Capo', guests=5, bedrooms=2, bathrooms=1),
    'appartamenti_casa-orsa-mono': dict(slug='casa-orsa-mono', name='Casa Orsa Mono', city='Gallipoli - Rivabella', guests=2, bedrooms=1, bathrooms=1),
    'appartamenti_villa-orsa-bilo-plus': dict(slug='villa-orsa-bilo-plus', name='Villa Orsa Azzurra', city='Gallipoli - Rivabella', guests=6, bedrooms=2, bathrooms=2),
    'appartamenti_villa-orsa-superior': dict(slug='villa-orsa-superior', name='Villa Orsa Superior', city='Gallipoli - Rivabella', guests=10, bedrooms=2, bathrooms=2),
}
for k, meta in WPA.items():
    v = wp[k]
    desc = next((p for p in v['paragraphs'] if p.startswith('CIS')), '')
    cis = re.match(r'CIS:\s*(\S+)', desc)
    desc_txt = re.sub(r'^CIS:\s*\S+\s*', '', desc)
    extra = [p for p in v['paragraphs'] if not p.startswith('CIS') and len(p) > 60]
    imgs = []
    for u in v['images']:
        stem = re.sub(r'-\d+x\d+$', '', Path(u).stem)
        f = ROOT / 'assets' / 'img' / 'opt' / (stem + '.webp')
        if f.exists() and 'logo' not in stem:
            imgs.append('assets/img/opt/' + stem + '.webp')
    imgs = sorted(set(imgs))
    services = []
    for li in v['list_items']:
        if li.isupper() and 2 < len(li) < 40:
            services.append(li.title())
    u = dict(meta)
    u.update({
        'desc_it': desc_txt + ((' ' + ' '.join(extra)) if extra else ''),
        'cis': cis.group(1) if cis else '',
        'services': sorted(set(services)),
        'booking': 'https://salentocasevacanze.kross.travel/it/appartamenti',
        'images': imgs, 'source': 'wp',
    })
    units.append(u)

json.dump(units, open(ROOT / 'data' / 'units.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cities = {}
for u in units:
    cities[u['city']] = cities.get(u['city'], 0) + 1
print(len(units), 'unita |', cities)
last = units[-1]
print('esempio wp:', last['name'], '| servizi:', last['services'], '|', len(last['images']), 'foto')
