# IB English Vocabulary Mastery — Netlify Site

A living website that aggregates every daily vocabulary study sheet into one place.
Each new study day is added with **zero restructuring** — just drop a file in and rebuild.

## Structure
```
site/
├── index.html        ← hub page (fetches manifest.json, shows all days + progress)
├── manifest.json     ← source of truth: one entry per study day
├── build.mjs         ← regenerates manifest.json from the days/ folder
├── netlify.toml      ← Netlify build + publish config
├── assets/
│   ├── site.css      ← hub styling
│   └── site.js       ← hub logic (load, render cards, search)
└── days/
    ├── day1.html
    ├── day2.html
    └── … (one self-contained HTML per study day)
```

## Add a new day (the only step you ever repeat)
1. Copy the new study sheet into `days/` as `dayN.html`
   (e.g. `days/day6.html`). The file is fully self-contained.
2. Run the build script to update `manifest.json`:
   ```bash
   cd site
   node build.mjs
   ```
   It auto-detects the new file, extracts the date/words, and appends it.
   Curated entries are never overwritten.
3. Deploy:
   ```bash
   netlify deploy --prod --dir .
   ```
   (First time only: `netlify deploy --prod --dir .` after `netlify login`, or connect the repo in the Netlify dashboard.)

The hub (`index.html`) reads `manifest.json` live, so new days appear immediately —
no manual editing of the homepage required.

## Convenience URL
`https://<your-site>/day/5` redirects to `/days/day5.html`.

## Local preview
```bash
cd site
node build.mjs
npx serve .        # or: python3 -m http.server 8080
```
Open the printed URL. (Opening index.html via file:// will not load manifest.json —
use a local server, which is also how Netlify serves it.)
