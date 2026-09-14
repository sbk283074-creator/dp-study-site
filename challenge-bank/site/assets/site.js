
(function(){
  // ---------- Mark as done (works on listing + individual question pages) ----------
  var DONE_KEY = 'cb_done_v1';
  function loadDone(){ try { return JSON.parse(localStorage.getItem(DONE_KEY) || '{}'); } catch(e){ return {}; } }
  function saveDone(o){ try { localStorage.setItem(DONE_KEY, JSON.stringify(o)); } catch(e){} }
  function isDone(id){ return !!(id && loadDone()[id]); }
  function setDone(id, val){
    if(!id) return;
    var o = loadDone();
    if(val) o[id] = 1; else delete o[id];
    saveDone(o);
  }
  function wireToggle(btn){
    var id = btn.getAttribute('data-qid');
    if(!id) return;
    function paint(){
      var d = isDone(id);
      btn.setAttribute('aria-pressed', d ? 'true' : 'false');
      btn.textContent = d ? '\u2713 Done' : 'Mark done';
      btn.classList.toggle('on', d);
      var card = btn.closest('.q');
      if(card) card.classList.toggle('is-done', d);
    }
    paint();
    btn.addEventListener('click', function(){
      setDone(id, !isDone(id));
      paint();
      if(typeof window.__cbRunFilter === 'function') window.__cbRunFilter();
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.q-done, .q-done-page'), wireToggle);

  // ---------- Listing filter: search / topic / paper / difficulty / done ----------
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if(q && box){
    function hay(card){ return (card.dataset.search || '').toLowerCase(); }
    window.__cbRunFilter = function(){
      var term = q.value.trim().toLowerCase();
      var diff = (document.getElementById('f-diff')||{}).value || '';
      var paper = (document.getElementById('f-paper')||{}).value || '';
      var topic = (document.getElementById('f-topic')||{}).value || '';
      var fd = (document.getElementById('f-done')||{}).value || '';
      var shown = 0;
      Array.prototype.forEach.call(document.querySelectorAll('[data-search]'), function(card){
        var id = card.getAttribute('data-qid') || '';
        var done = isDone(id);
        var ok = (!term || hay(card).indexOf(term) !== -1)
              && (!diff || card.dataset.diff === diff)
              && (!paper || card.dataset.paper === paper)
              && (!topic || card.dataset.topic === topic)
              && (!fd || (fd === 'done' ? done : !done));
        card.style.display = ok ? '' : 'none';
        if(ok) shown++;
      });
      var note = document.getElementById('count');
      if(note) note.textContent = shown + ' question' + (shown === 1 ? '' : 's') + ' shown';
    };
    q.addEventListener('input', window.__cbRunFilter);
    ['f-diff','f-paper','f-topic','f-done'].forEach(function(id){
      var el = document.getElementById(id);
      if(el) el.addEventListener('change', window.__cbRunFilter);
    });
    window.__cbRunFilter();
  }

  // global search on the home page
  var g = document.getElementById('g');
  var gr = document.getElementById('gresults');
  if(g && gr && window.CB_INDEX){
    g.addEventListener('input', function(){
      var t = g.value.trim().toLowerCase();
      if(t.length < 2){ gr.innerHTML = ''; return; }
      var hits = window.CB_INDEX.filter(function(x){
        return x.s.indexOf(t) !== -1;
      }).slice(0, 20);
      gr.innerHTML = hits.length ? hits.map(function(x){
        return '<div class="q"><h3><a href="' + x.u + '">' + x.t + '</a></h3>' +
               '<div class="meta"><span class="chip">' + x.sub + '</span>' +
               (x.topic ? '<span class="chip chip-topic">' + x.topic + '</span>' : '') +
               '<span class="chip">' + x.paper + '</span>' +
               '<span class="chip">' + x.marks + ' marks</span>' +
               '<span class="chip chip-hard">difficulty ' + x.d + '</span></div></div>';
      }).join('') : '<p class="empty">No questions match that search.</p>';
    });
  }
})();
