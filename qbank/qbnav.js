/* qbank/qbnav.js — standalone Question Bank micro-site chrome.
   Replaces the main site's app.js nav. Injects a fixed top bar with a link to
   every question-bank page plus a "back to DP Learning" link, and highlights the
   current page. Shares the main site's light/dark theme via localStorage. */
(function () {
  var pages = [
    { f: 'index.html',       t: 'Search' },
    { f: 'practice.html',    t: 'Practice' },
    { f: 'wrong.html',       t: 'Wrong book' },
    { f: 'knowledge.html',   t: 'Knowledge' },
    { f: 'exams.html',       t: 'Papers' },
    { f: 'collections.html', t: 'Collections' },
    { f: 'progress.html',    t: 'Progress' },
    { f: 'books.html',       t: 'Books' }
  ];
  var file = location.pathname.split('/').pop() || 'index.html';
  var links = pages.map(function (p) {
    var active = (p.f === file) ? ' aria-current="page"' : '';
    return '<a class="qb-nav__link" href="' + p.f + '"' + active + '>' + p.t + '</a>';
  }).join('');

  var nav = document.createElement('header');
  nav.className = 'qb-nav';
  nav.setAttribute('role', 'banner');
  nav.innerHTML =
    '<a class="qb-nav__brand" href="index.html"><span class="qb-nav__logo">Q</span> Question Bank</a>' +
    '<nav class="qb-nav__links" aria-label="Question Bank sections">' + links + '</nav>' +
    '<a class="qb-nav__home" href="../index.html" title="Back to DP Learning">&#8592; DP Learning</a>';

  if (document.body.firstChild) {
    document.body.insertBefore(nav, document.body.firstChild);
  } else {
    document.body.appendChild(nav);
  }

  // Inherit the main site's theme choice (same origin -> shared localStorage).
  try {
    var theme = localStorage.getItem('dp.theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  } catch (e) {}
})();
