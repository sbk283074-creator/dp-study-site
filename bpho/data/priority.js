/* BPhO Round 0 — what the one real paper actually tested.
   =======================================================
   There is exactly one Round 0 past paper in existence (2025). That makes it the only hard
   evidence anyone has about how the 25 marks are really distributed, so this module derives the
   site's priorities from it rather than from anyone's opinion.

   Everything here is computed at load time from the questions tagged `paper:"R0-2025"`, so it
   cannot drift away from the bank: edit the bank and the priorities follow.

   Two counts are kept, and they answer different questions:
     n_main  — questions whose PRIMARY module this is           ("how many marks hang on this")
     n_rel   — questions that also list it under `rel`          ("how often does it turn up")
   A module can have a small n_main but a large n_rel (the toolkit, module A, is the extreme
   case: it underpins almost everything), so both are shown.

   Load order: after questions.js, before guidance.js. */

(function () {
  var PAPER = "R0-2025";

  var qs = (window.BPHO_QUESTIONS || []).filter(function (q) { return q.paper === PAPER; });
  var mods = (window.BPHO_CURRICULUM || { modules: [] }).modules || [];

  /* ---- primary-module counts ---- */
  var main = {}, rel = {}, byModule = {};
  qs.forEach(function (q) {
    main[q.module] = (main[q.module] || 0) + 1;
    (byModule[q.module] = byModule[q.module] || []).push(q.id);
    (q.rel || []).forEach(function (r) { rel[r[0]] = (rel[r[0]] || 0) + 1; });
  });

  /* ---- questions that draw on a module either as primary or via `rel` ---- */
  var drawsOn = {};
  qs.forEach(function (q) {
    var seen = {};
    seen[q.module] = 1;
    (q.rel || []).forEach(function (r) { seen[r[0]] = 1; });
    Object.keys(seen).forEach(function (c) {
      (drawsOn[c] = drawsOn[c] || []).push(q.id);
    });
  });

  /* ---- topic counts (primary topic + every `rel` mention) ---- */
  var topics = {};
  qs.forEach(function (q) {
    var k = q.module + "" + q.topic;
    topics[k] = topics[k] || { module: q.module, topic: q.topic, n: 0, main: 0, qs: [] };
    topics[k].n += 1;
    topics[k].main += 1;
    if (topics[k].qs.indexOf(q.id) < 0) topics[k].qs.push(q.id);
  });
  qs.forEach(function (q) {
    (q.rel || []).forEach(function (r) {
      var k = r[0] + "" + r[1];
      if (!topics[k]) topics[k] = { module: r[0], topic: r[1], n: 0, main: 0, qs: [] };
      if (topics[k].module === q.module && topics[k].topic === q.topic) return; /* already counted */
      topics[k].n += 1;
      if (topics[k].qs.indexOf(q.id) < 0) topics[k].qs.push(q.id);
    });
  });

  var topicList = Object.keys(topics).map(function (k) { return topics[k]; });
  topicList.sort(function (a, b) {
    return (b.main - a.main) || (b.n - a.n) || a.module.localeCompare(b.module);
  });

  /* ---- module table: every module, ranked by marks on the paper ---- */
  var total = qs.length || 1;
  var table = mods.map(function (m) {
    return {
      code: m.code,
      title: m.title,
      short: m.short || m.title,
      priority: m.priority,
      n: main[m.code] || 0,
      rel: rel[m.code] || 0,
      share: Math.round(((main[m.code] || 0) / total) * 100),
      marks: main[m.code] || 0
    };
  });
  table.sort(function (a, b) {
    return (b.n - a.n) || (b.rel - a.rel) || (a.priority - b.priority);
  });
  table.forEach(function (m, i) { m.rank = i + 1; });

  var counts = {}, ranks = {}, order = [];
  table.forEach(function (m) { counts[m.code] = m.n; ranks[m.code] = m.rank; order.push(m.code); });

  window.BPHO_PRIORITY = {
    paper: PAPER,
    label: "2025 Round 0",
    total: qs.length,
    modules: table,
    counts: counts,
    ranks: ranks,
    order: order,                 /* module codes, most-tested first */
    byModule: byModule,           /* code -> ids where it is the primary module */
    drawsOn: drawsOn,             /* code -> ids that use it at all */
    topics: topicList,            /* [{module, topic, n, main, qs}] most-tested first */
    /* how many marks, in total, sit on the modules a given module unlocks — used to justify
       "learn this first" claims */
    forCode: function (code) {
      for (var i = 0; i < table.length; i++) if (table[i].code === code) return table[i];
      return null;
    }
  };
})();
