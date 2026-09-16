const TOTAL_WORDS = 1300;
const TOTAL_DAYS = 112;

const fmt = (n) => n.toLocaleString('en-US');

async function load() {
  let days = [];
  try {
    const res = await fetch('manifest.json', { cache: 'no-cache' });
    days = await res.json();
  } catch (e) {
    document.getElementById('day-grid').innerHTML =
      '<div class="empty">Could not load manifest.json. Make sure you are serving this over HTTP (Netlify or a local server), not opening the file directly.</div>';
    return;
  }
  days.sort((a, b) => a.day - b.day);

  // Totals
  const totalNew = days.reduce((s, d) => s + (d.newWords || 0), 0);
  const totalReview = days.reduce((s, d) => s + (d.reviewWords || 0), 0);
  const lastDay = days.length ? days[days.length - 1].day : 0;
  const phase = days.length ? (days[days.length - 1].phase || 'Phase 1') : 'Phase 1';
  const phaseShort = (phase.match(/Phase\s*(\d+)/i) || [, '1'])[1];

  document.getElementById('hub-badge').textContent =
    `Day ${lastDay} / ${TOTAL_DAYS} — ${phase.replace(/^Phase\s*\d+\s*·\s*/i, '')} Phase`;
  document.getElementById('word-bar').style.width = Math.min(100, (totalNew / TOTAL_WORDS) * 100) + '%';
  document.getElementById('word-num').textContent = `${fmt(totalNew)} / ${fmt(TOTAL_WORDS)}`;
  document.getElementById('day-bar').style.width = Math.min(100, (lastDay / TOTAL_DAYS) * 100) + '%';
  document.getElementById('day-num').textContent = `${lastDay} / ${TOTAL_DAYS}`;
  document.getElementById('stat-days').textContent = days.length;
  document.getElementById('stat-words').textContent = fmt(totalNew);
  document.getElementById('stat-review').textContent = fmt(totalReview);
  document.getElementById('stat-phase').textContent = 'P' + phaseShort;

  const grid = document.getElementById('day-grid');
  const render = (list) => {
    grid.innerHTML = '';
    document.getElementById('empty').style.display = list.length ? 'none' : 'block';
    document.getElementById('result-count').textContent =
      list.length ? `${list.length} of ${days.length} days` : '';
    list.forEach((d) => {
      const words = d.words || [];
      const shown = words.slice(0, 8);
      const extra = words.length - shown.length;
      const chips = shown.map((w) => `<span class="wchip">${w}</span>`).join('');
      const moreChip = extra > 0 ? `<span class="wchip more">+${extra}</span>` : '';
      const card = document.createElement('a');
      card.className = 'day-card';
      card.href = d.file;
      card.innerHTML = `
        <span class="dc-go">→</span>
        <div class="dc-top">
          <span class="dc-day">Day ${d.day}</span>
          <span class="dc-date">${d.date || ''}</span>
        </div>
        <span class="dc-phase">${d.phase || 'Phase 1'}</span>
        <div class="dc-title">${d.title || ('Day ' + d.day)}</div>
        <div class="dc-cat">${d.category || ''}</div>
        <div class="dc-words">${chips}${moreChip}</div>
        <div class="dc-foot">
          <span><strong>${d.newWords || 0}</strong> new</span>
          <span><strong>${d.reviewWords || 0}</strong> review</span>
        </div>`;
      grid.appendChild(card);
    });
  };

  render(days);

  const qEl = document.getElementById('search');
  qEl.addEventListener('input', () => {
    const q = qEl.value.trim().toLowerCase();
    if (!q) return render(days);
    const filtered = days.filter((d) => {
      const hay = [
        'day ' + d.day,
        (d.title || ''),
        (d.phase || ''),
        (d.category || ''),
        (d.date || ''),
        (d.words || []).join(' ')
      ].join(' ').toLowerCase();
      return hay.includes(q);
    });
    render(filtered);
  });
}

load();
