
(function(){
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if(!q || !box) return;
  function hay(card){ return (card.dataset.search || '').toLowerCase(); }
  function run(){
    var term = q.value.trim().toLowerCase();
    var diff = (document.getElementById('f-diff')||{}).value || '';
    var paper = (document.getElementById('f-paper')||{}).value || '';
    var shown = 0;
    Array.prototype.forEach.call(document.querySelectorAll('[data-search]'), function(card){
      var ok = (!term || hay(card).indexOf(term) !== -1)
            && (!diff || card.dataset.diff === diff)
            && (!paper || card.dataset.paper === paper);
      card.style.display = ok ? '' : 'none';
      if(ok) shown++;
    });
    var note = document.getElementById('count');
    if(note) note.textContent = shown + ' question' + (shown === 1 ? '' : 's') + ' shown';
    box.style.display = 'none';
  }
  q.addEventListener('input', run);
  ['f-diff','f-paper'].forEach(function(id){
    var el = document.getElementById(id);
    if(el) el.addEventListener('change', run);
  });

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
               '<span class="chip">' + x.paper + '</span>' +
               '<span class="chip">' + x.marks + ' marks</span>' +
               '<span class="chip chip-hard">difficulty ' + x.d + '</span></div></div>';
      }).join('') : '<p class="empty">No questions match that search.</p>';
    });
  }
})();
