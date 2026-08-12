# Salento Case Vacanze — portale statico multilingua

Clone rifatto di salentocasevacanze.com: portale case vacanza in 5 lingue con prenotazione diretta Kross Booking.

## Struttura

- `/` — italiano (lingua predefinita)
- `/en/` `/fr/` `/de/` `/es/` — inglese, francese, tedesco, spagnolo
- 30 appartamenti (24 unità Kross con link di prenotazione diretta + 6 schede storiche del vecchio sito)
- 6 guide località (Leuca, Pescoluse/Torre Vado, Gallipoli, Otranto, Torre dell'Orso, Santa Cesarea/Castro)
- Pagine: chi siamo, contatti, condizioni generali

## SEO / GEO

- Title e meta description ottimizzati per parole chiave in ogni lingua
- hreflang complete (5 lingue + x-default) su ogni pagina e nella sitemap
- JSON-LD: TravelAgency, WebSite, VacationRental (per unità), TouristDestination, BreadcrumbList
- `sitemap.xml` con alternates hreflang, `robots.txt`, `llms.txt` per i motori AI
- Alt text descrittivi e localizzati su tutte le immagini
- Open Graph + Twitter Card

## Come si rigenera

```
python build/build_site.py     # genera le 210 pagine
python build/check_links.py    # verifica link e asset
```

- Dati unità: `data/units.json` (generato da `build/prep_data.py`)
- Testi e traduzioni: `build/translations.py`
- Design: `assets/css/style.css`, interazioni: `assets/js/main.js`

## Deploy su Netlify

Trascinare l'intera cartella su Netlify Drop (o collegare repo). Nessun build command necessario: è già HTML statico. Impostare il dominio e HTTPS. Il valore `SITE` in `build/build_site.py` va aggiornato se il dominio di produzione è diverso da salentocasevacanze.com, poi rigenerare.

## Nota importante

Il vecchio sito WordPress è compromesso: la pagina "Condizioni generali" contiene spam iniettato (casinò online in rumeno). Nel nuovo sito il testo è stato ripulito. Consigliato dismettere il WP o bonificarlo.
