
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

  // global search on the home page -- carrying the same filters the subject
  // pages already have, so "which Marketing questions have I not done" is
  // answerable from one place instead of by opening four subject pages in turn.
  var g = document.getElementById('g');
  var gr = document.getElementById('gresults');
  if(g && gr && window.CB_INDEX){
    var gSubject = document.getElementById('g-subject');
    var gTopic = document.getElementById('g-topic');
    var gDiff = document.getElementById('g-diff');
    var gDone = document.getElementById('g-done');

    // The topic vocabulary is per subject, so the topic list is rebuilt from
    // whatever the subject filter currently admits. A topic select that still
    // offered "Theme D: Fields" after switching to Business Management would be
    // a filter that can only ever return nothing.
    function topicOptions(){
      if(!gTopic) return;
      var want = gSubject ? gSubject.value : '';
      var seen = {}, out = [];
      window.CB_INDEX.forEach(function(x){
        if(!x.topic) return;
        if(want && x.sub !== want) return;
        if(seen[x.topic]) return;
        seen[x.topic] = 1; out.push(x.topic);
      });
      out.sort();
      var keep = gTopic.value;
      gTopic.innerHTML = '<option value="">All topics</option>' + out.map(function(t){
        return '<option value="' + t.replace(/"/g, '&quot;') + '">' + t + '</option>';
      }).join('');
      // Reset explicitly rather than relying on the browser to drop the old
      // selection when the option it named stops existing: if the subject
      // changed, the old topic is now a filter that can only ever return
      // nothing, and it must not stay quietly applied.
      gTopic.value = (keep && seen[keep]) ? keep : '';
    }

    function runGlobal(){
      var term = (g.value || '').trim().toLowerCase();
      var sub = gSubject ? gSubject.value : '';
      var topic = gTopic ? gTopic.value : '';
      var diff = gDiff ? gDiff.value : '';
      var fd = gDone ? gDone.value : '';
      var filtered = !!(sub || topic || diff || fd);
      // Two characters was the old floor purely to avoid dumping the whole bank
      // on one keystroke. With a filter applied, browsing without typing is the
      // point, so the floor only applies to a bare search.
      if(term.length < 2 && !filtered){ gr.innerHTML = ''; return; }
      var hits = window.CB_INDEX.filter(function(x){
        if(term.length >= 2 && x.s.indexOf(term) === -1) return false;
        if(sub && x.sub !== sub) return false;
        if(topic && x.topic !== topic) return false;
        if(diff && String(x.d) !== diff) return false;
        if(fd){
          var d = isDone(x.id);
          if(fd === 'done' ? !d : d) return false;
        }
        return true;
      });
      var capped = hits.slice(0, 60);
      gr.innerHTML = hits.length ? capped.map(function(x){
        return '<div class="q" data-qid="' + x.id + '"><h3><a href="' + x.u + '">' + x.t + '</a></h3>' +
               '<div class="meta"><span class="chip">' + x.sub + '</span>' +
               (x.topic ? '<span class="chip chip-topic">' + x.topic + '</span>' : '') +
               '<span class="chip">' + x.paper + '</span>' +
               '<span class="chip">' + x.marks + ' marks</span>' +
               '<span class="chip chip-hard">difficulty ' + x.d + '</span></div>' +
               '<button type="button" class="q-done" data-qid="' + x.id + '" aria-pressed="false">Mark done</button></div>';
      }).join('') + (hits.length > capped.length
          ? '<p class="small">' + (hits.length - capped.length) + ' more match -- narrow the search or add a filter.</p>'
          : '')
        : '<p class="empty">No questions match that search.</p>';
      Array.prototype.forEach.call(gr.querySelectorAll('.q-done'), wireToggle);
    }

    if(gSubject) gSubject.addEventListener('change', function(){ topicOptions(); runGlobal(); });
    if(gTopic) gTopic.addEventListener('change', runGlobal);
    if(gDiff) gDiff.addEventListener('change', runGlobal);
    if(gDone) gDone.addEventListener('change', runGlobal);
    g.addEventListener('input', runGlobal);
    // Ticking "Mark done" in a search result has to re-run this filter, not the
    // listing one -- and only one of the two exists on any given page.
    window.__cbRunFilter = runGlobal;
    topicOptions();
  }

  // ---------- "Ask AI": hand each question to the shared assistant ----------
  // There is no second chat implementation here. assets/ai-widget.js already
  // ships the panel -- controls, model pool, usage strip, rendering -- on every
  // page of the site, so this block only says WHICH question to focus on and
  // how to ask it. The item's own text (stem, every part, marks, difficulty)
  // rides along, because the tutor has no access to this bank and a request
  // that sent only "help me" would be answered blind.
  //
  // How each mode is put to the tutor. "Hint" deliberately withholds the answer:
  // a hint that works the question through is not a hint, it is the answer with
  // a preamble, and it removes the practice the question exists to give.
  var AI_MODES = {
    solution: { display:'Full worked solution', depth:'deep', difficulty:'hard', length:'long',
      ask:'Give a full worked solution in IB markscheme style. For each part give the method, the working and the result, and name which marks are earned (M method, A accuracy, R reasoning). Finish with the two errors candidates most often make here.' },
    hint: { display:'Hint only', depth:'quick', difficulty:'medium', length:'short',
      ask:'Give a HINT ONLY. Name the first move and the one thing to watch for. Do not give the answer, do not work any part through to a final value, and do not list the steps.' },
    steps: { display:'Guided steps', depth:'standard', difficulty:'hard', length:'medium',
      ask:'Work through the parts one at a time. For each part give the method and the markscheme logic, but stop short of the final value of the last part so I still have to finish it myself.' },
    mark: { display:'Mark my attempt', depth:'deep', difficulty:'hard', length:'medium',
      ask:'Mark my attempt against IB criteria. Say which marks I earned and which I lost, and exactly why for each. Do not rewrite the whole solution unless I lost a mark on that part.' }
  };

  // The whole item, exactly as the student sees it, behind a one-line header so
  // the tutor knows the subject, the difficulty and what the question is worth.
  function aiContext(panel){
    var src = panel.querySelector('.qai-src');
    var text = src ? src.textContent.trim() : '';
    var subj = panel.getAttribute('data-ai-subject') || 'IB';
    var diff = panel.getAttribute('data-ai-diff') || '';
    var marks = panel.getAttribute('data-ai-marks') || '';
    var ref = panel.getAttribute('data-ai-ref') || '';
    var head = 'IB ' + subj + ' question' + (ref ? ' (' + ref + ')' : '') +
               (diff ? ', difficulty ' + diff + ' of 5' : '') +
               (marks ? ', worth ' + marks + ' marks' : '') + '.';
    return head + '\n\n' + text;
  }

  function aiAsk(panel, mode){
    var conf = AI_MODES[mode] || AI_MODES.solution;
    if(!window.dpAI || typeof window.dpAI.open !== 'function'){
      window.alert('The study assistant has not finished loading. Reload the page and try again.');
      return;
    }
    var marks = parseInt(panel.getAttribute('data-ai-marks'), 10);
    window.dpAI.open({
      ref: panel.getAttribute('data-ai-ref') || 'this question',
      subject: panel.getAttribute('data-ai-subject') || undefined,
      marks: isNaN(marks) ? undefined : marks,
      context: aiContext(panel),
      prompt: conf.ask,
      display: conf.display,
      depth: conf.depth, difficulty: conf.difficulty, length: conf.length,
      // "Mark my attempt" has to wait for the student's working, so it opens the
      // box prefilled instead of firing a request at a blank attempt.
      autoSend: mode !== 'mark'
    });
    if(mode === 'mark'){
      var ta = document.getElementById('dpAiText');
      if(ta){ ta.value += '\n\nMY ATTEMPT:\n'; ta.focus(); }
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-ai]'), function(panel){
    Array.prototype.forEach.call(panel.querySelectorAll('.qai-btn[data-ai-mode]'), function(btn){
      btn.addEventListener('click', function(){
        aiAsk(panel, btn.getAttribute('data-ai-mode'));
      });
    });
  });
})();
