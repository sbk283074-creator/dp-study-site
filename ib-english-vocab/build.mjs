#!/usr/bin/env node
// build.mjs — regenerates site/manifest.json from the days/ folder.
// Run after adding a new day file:  node build.mjs
// It never deletes curated entries; it only APPENDS newly discovered day files.

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DAYS_DIR = join(__dirname, 'days');
const MANIFEST = join(__dirname, 'manifest.json');

const PHASE_NAMES = {
  1: 'Analytical Verbs',
  2: 'Descriptive Precision',
  3: 'Technical Terminology',
  4: 'Mastery & Application',
};

function phaseForDay(day) {
  const idx = Math.min(4, Math.max(1, Math.ceil(day / 28)));
  return `Phase ${idx} · ${PHASE_NAMES[idx]}`;
}

// Read curated manifest (manual edits are preserved).
let manifest = [];
if (existsSync(MANIFEST)) {
  try { manifest = JSON.parse(readFileSync(MANIFEST, 'utf8')); }
  catch { manifest = []; }
}
const knownDays = new Set(manifest.map((d) => d.day));

// Discover day files.
const files = readdirSync(DAYS_DIR).filter((f) => /^day(\d+)\.html$/.test(f));
let added = 0;

for (const f of files) {
  const day = parseInt(f.match(/^day(\d+)\.html$/)[1], 10);
  if (knownDays.has(day)) continue; // already curated — skip

  const html = readFileSync(join(DAYS_DIR, f), 'utf8');

  // date
  const dateM = html.match(/<div class="date">([^<]+)<\/div>/);
  const date = dateM ? dateM[1].trim() : '';

  // today's new words (the .word spans are today's terms; review words use .rword)
  const wordMatches = [...html.matchAll(/<span class="word">([^<]+)<\/span>/g)];
  const words = wordMatches.map((m) => m[1].trim());
  const newWords = words.length;

  // best-effort review count from the spaced-repetition status card
  let reviewWords = 0;
  const revM = html.match(/sr-card review[\s\S]*?sr-count">(\d+)</);
  if (revM) reviewWords = parseInt(revM[1], 10);

  // title / category
  let title = `Day ${day}`;
  const catM = html.match(/class="category-badge[^"]*">([^<]+)</);
  let category = '';
  if (catM) {
    category = catM[1].replace(/NEW CATEGORY\s*—\s*/i, '').trim();
  }
  const badgeM = html.match(/day-badge">Day\s*\d+\s*\/\s*\d+\s*—\s*([^<]+)</);
  if (badgeM) title = badgeM[1].trim();

  manifest.push({
    day,
    file: `days/${f}`,
    title,
    date,
    phase: phaseForDay(day),
    week: Math.ceil(day / 7),
    category,
    newWords,
    reviewWords,
    words,
  });
  added++;
  console.log(`+ Added Day ${day} (${newWords} new words) from ${f}`);
}

manifest.sort((a, b) => a.day - b.day);
writeFileSync(MANIFEST, JSON.stringify(manifest, null, 2) + '\n', 'utf8');

// Generate /day/N/index.html redirect stubs so the short-link works on
// GitHub Pages and any static host (Netlify covers it via its own redirect rule).
for (const d of manifest) {
  const stubDir = join(__dirname, 'day', String(d.day));
  mkdirSync(stubDir, { recursive: true });
  const target = `../days/day${d.day}.html`;
  const stub =
    `<!doctype html>\n` +
    `<html lang="en"><head><meta charset="utf-8">` +
    `<title>Day ${d.day} — IB English Vocabulary</title>` +
    `<meta http-equiv="refresh" content="0; url=${target}">` +
    `<link rel="canonical" href="${target}"></head>` +
    `<body>Redirecting to Day ${d.day}…</body></html>\n`;
  writeFileSync(join(stubDir, 'index.html'), stub, 'utf8');
}
console.log(`Generated ${manifest.length} /day/N/ redirect stubs.`);

const totalNew = manifest.reduce((s, d) => s + (d.newWords || 0), 0);
console.log(`\nmanifest.json updated: ${manifest.length} days, ${totalNew} new words total.`);
if (added === 0) console.log('No new day files discovered — manifest unchanged.');
