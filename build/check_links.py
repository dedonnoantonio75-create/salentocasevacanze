# Verifica link e asset locali di tutte le pagine generate
import re, sys
from pathlib import Path
from urllib.parse import unquote

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
errors = 0
pages = list(ROOT.rglob('index.html'))
ext_links = set()
for page in pages:
    html = page.read_text(encoding='utf-8')
    for m in re.finditer(r'(?:href|src)="([^"#]+)"', html):
        url = m.group(1).split('?')[0]
        if not url:
            continue
        if url.startswith(('http', 'mailto:', 'tel:', 'data:')):
            if url.startswith('http'):
                ext_links.add(url)
            continue
        target = (page.parent / unquote(url)).resolve()
        if url.endswith('/'):
            target = target / 'index.html'
        if not target.exists():
            print(f'ROTTO: {page.relative_to(ROOT)} -> {url}')
            errors += 1
print(f'{len(pages)} pagine controllate, {errors} link rotti')
print('\nLink esterni unici:')
for u in sorted(set(re.sub(r'kross\.travel/[^"]*', 'kross.travel/...', x) for x in ext_links))[:20]:
    print(' -', u)
