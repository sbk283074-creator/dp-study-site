
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

  // ---------- "Solve with AI": a tutor panel under each question ----------
  // Same worker the global assistant uses. What differs is what is sent: the
  // global assistant gets a bare question, this gets the whole item -- stem,
  // every part, marks, and the item's own difficulty -- because the tutor has no
  // access to this bank, and a panel that sent only "help me" would be answered
  // blind. Nothing leaves the browser until the student presses the button, and
  // the body is built on first click so a page of ninety questions costs ninety
  // buttons rather than ninety textareas.
  var ASK_API = 'https://ib-dp-platform-api.pages.dev/api/ask';
  var ASK_STATUS = 'https://ib-dp-platform-api.pages.dev/api/ask/status';

  // How each mode is put to the tutor. "Hint" deliberately withholds the answer:
  // a hint that works the question through is not a hint, it is the answer with
  // a preamble, and it removes the practice the question exists to give.
  var AI_MODES = {
    solution: { depth:'deep', difficulty:'hard', length:'long',
      ask:'Give a full worked solution in IB markscheme style. For each part give the method, the working and the result, and name which marks are earned (M method, A accuracy, R reasoning). Finish with the two errors candidates most often make here.' },
    hint: { depth:'quick', difficulty:'medium', length:'short',
      ask:'Give a HINT ONLY. Name the first move and the one thing to watch for. Do not give the answer, do not work any part through to a final value, and do not list the steps.' },
    steps: { depth:'standard', difficulty:'hard', length:'medium',
      ask:'Work through the parts one at a time. For each part give the method and the markscheme logic, but stop short of the final value of the last part so I still have to finish it myself.' },
    mark: { depth:'deep', difficulty:'hard', length:'medium',
      ask:'Mark my attempt below against IB criteria. Say which marks I earned and which I lost, and exactly why for each. Do not rewrite the whole solution unless I lost a mark on that part.' }
  };

  function aiEscape(s){
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Markdown-lite, matching the subset the bank's own prose uses. Anything that
  // looks like TeX is left untouched so MathJax can typeset it afterwards.
  function aiFormat(text){
    var t = aiEscape(text);
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    return t.split(/\n{2,}/).map(function(block){
      var lines = block.split('\n');
      var head = lines[0].match(/^\s*(#{1,4})\s+(.*)$/);
      if(head && lines.length === 1){
        var lvl = Math.min(6, head[1].length + 2);
        return '<h' + lvl + '>' + head[2] + '</h' + lvl + '>';
      }
      var isList = lines.length > 1 && lines.every(function(l){
        return /^\s*(?:[-*]|\d+[.)])\s+/.test(l);
      });
      if(isList){
        return '<ul>' + lines.map(function(l){
          return '<li>' + l.replace(/^\s*(?:[-*]|\d+[.)])\s+/, '') + '</li>';
        }).join('') + '</ul>';
      }
      return '<p>' + block.replace(/\n/g, '<br>') + '</p>';
    }).join('');
  }

  function aiTypeset(node){
    if(window.MathJax && typeof window.MathJax.typesetPromise === 'function'){
      window.MathJax.typesetPromise([node]).catch(function(){});
    }
  }

  function aiMessage(panel, mode, attempt){
    var src = panel.querySelector('.qai-src');
    var text = src ? src.textContent.trim() : '';
    var subj = panel.getAttribute('data-ai-subject') || 'IB';
    var diff = panel.getAttribute('data-ai-diff') || '';
    var marks = panel.getAttribute('data-ai-marks') || '';
    var ref = panel.getAttribute('data-ai-ref') || '';
    var head = 'IB ' + subj + ' question' + (ref ? ' (' + ref + ')' : '') +
               (diff ? ', difficulty ' + diff + ' of 5' : '') +
               (marks ? ', worth ' + marks + ' marks' : '') + '.';
    var body = head + '\n\n' + text + '\n\n' + ((AI_MODES[mode] || AI_MODES.solution).ask);
    if(mode === 'mark' && attempt){ body += '\n\nMY ATTEMPT:\n' + attempt; }
    return body;
  }

  function aiBuildBody(panel){
    var body = panel.querySelector('.qai-body');
    if(!body || body.getAttribute('data-built')) return body;
    body.setAttribute('data-built', '1');
    body.innerHTML =
      '<div class="qai-row">' +
        '<label class="qai-lbl">Help me with' +
          '<select data-ai-mode aria-label="How the tutor should help">' +
            '<option value="solution">a full worked solution</option>' +
            '<option value="hint">a hint only, no answer</option>' +
            '<option value="steps">guided steps, one part at a time</option>' +
            '<option value="mark">marking my own attempt</option>' +
          '</select>' +
        '</label>' +
        '<span class="qai-status"></span>' +
      '</div>' +
      '<textarea data-ai-attempt hidden placeholder="Paste your working here, then ask to have it marked." aria-label="Your attempt"></textarea>' +
      '<div class="qai-out" hidden></div>';
    return body;
  }

  function aiSend(panel){
    var btn = panel.querySelector('[data-ai-go]');
    var body = aiBuildBody(panel);
    if(!btn || !body) return;
    var modeSel = body.querySelector('[data-ai-mode]');
    var attemptEl = body.querySelector('[data-ai-attempt]');
    var out = body.querySelector('.qai-out');
    var mode = (modeSel && modeSel.value) || 'solution';
    var conf = AI_MODES[mode] || AI_MODES.solution;
    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Thinking...';
    out.hidden = false;
    out.innerHTML = '<div class="qai-meta">Asking the tutor. A hard question takes a little longer.</div>';
    var controller = (typeof AbortController === 'function') ? new AbortController() : null;
    var timer = controller ? setTimeout(function(){ controller.abort(); }, 90000) : null;
    var payload = {
      message: aiMessage(panel, mode, attemptEl ? attemptEl.value.trim() : ''),
      subject: panel.getAttribute('data-ai-subject') || undefined,
      depth: conf.depth, difficulty: conf.difficulty, length: conf.length
    };
    fetch(ASK_API, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller ? controller.signal : undefined
    })
      .then(function(r){ return r.json().then(function(d){ return { status: r.status, data: d }; }); })
      .then(function(res){
        var d = res.data || {};
        if(res.status === 200 && d.ok){
          var meta = 'via ' + (d.model || 'the tutor');
          if(d.intent){ meta += ' \u00b7 ' + d.intent.depth + ' \u00b7 ' + d.intent.difficulty + ' \u00b7 ' + d.intent.length; }
          var html = '<div class="qai-meta">' + aiEscape(meta) + '</div>' + aiFormat(d.answer || '(no answer)');
          if(d.thinking){
            html += '<details class="qai-think"><summary>Show the reasoning</summary><div class="body">' +
                    aiFormat(d.thinking) + '</div></details>';
          }
          html += '<p class="small">Check this against the markscheme below before you trust it. ' +
                  'The tutor can be wrong; the markscheme cannot.</p>';
          out.innerHTML = html;
          aiTypeset(out);
        } else if(d.error === 'rate_limited' || d.error === 'quota_exceeded'){
          out.innerHTML = '<div class="qai-err">' +
            aiEscape(d.message || 'The tutor is rate-limited right now. Try again in a minute.') + '</div>';
        } else {
          out.innerHTML = '<div class="qai-err">' +
            aiEscape((d && d.message) || ('The tutor could not answer (HTTP ' + res.status + ').')) + '</div>';
        }
      })
      .catch(function(err){
        out.innerHTML = '<div class="qai-err">Could not reach the AI tutor. Check your connection and try again.' +
          (err && err.name === 'AbortError' ? ' (timed out after 90 seconds)' : '') + '</div>';
      })
      .then(function(){
        if(timer) clearTimeout(timer);
        btn.disabled = false;
        btn.textContent = label;
      });
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-ai]'), function(panel){
    var btn = panel.querySelector('[data-ai-go]');
    var body = panel.querySelector('.qai-body');
    if(!btn) return;
    btn.addEventListener('click', function(){
      if(btn.disabled) return;
      if(!body || !body.getAttribute('data-built')){
        aiBuildBody(panel);
        btn.textContent = 'Ask again';
      }
      aiSend(panel);
    });
    if(body){
      body.addEventListener('change', function(ev){
        var t = ev.target;
        if(!t || t.getAttribute('data-ai-mode') === null) return;
        var attempt = body.querySelector('[data-ai-attempt]');
        if(attempt) attempt.hidden = t.value !== 'mark';
      });
    }
  });

  // One status probe for the page, not one per panel.
  if(document.querySelector('[data-ai]')){
    fetch(ASK_STATUS, { method: 'GET', headers: { 'content-type': 'application/json' } })
      .then(function(r){ return r.json(); })
      .then(function(d){
        var line = '';
        if(d && d.configured === false){ line = 'The AI tutor is not configured right now.'; }
        else if(d && d.pool && d.pool.length){
          var up = 0;
          d.pool.forEach(function(m){ if(m.available) up++; });
          line = up + ' of ' + d.pool.length + ' tutor models available';
        }
        if(line){
          Array.prototype.forEach.call(document.querySelectorAll('.qai-status'), function(el){ el.textContent = line; });
        }
      })
      .catch(function(){
        Array.prototype.forEach.call(document.querySelectorAll('.qai-status'), function(el){
          el.textContent = 'AI tutor unreachable from this network';
        });
      });
  }
})();
