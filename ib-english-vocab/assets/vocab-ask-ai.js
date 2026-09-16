/* ============================================================================
   vocab-ask-ai.js — per-word "Ask AI" for the IB English Vocabulary days.
   ----------------------------------------------------------------------------
   Every day page (days/dayN.html) is a self-contained document: its CSS is
   inline and the only shared script is the floating study assistant. This file
   is the second shared script. It walks the page, finds each `.word-card`, and
   adds an "Ask AI" button that scopes the assistant to THAT word only.

   How it scopes: the assistant exposes exactly one integration point —
   window.dpAI.open(). We call it with `ref` + `context` (the word's own data)
   and `autoSend:false`, which pre-fills the question box and focuses it so the
   student can edit the question before sending. Nothing about the chat UI is
   re-implemented here, and the assistant's own logic is never touched.

   Load order matters: this script must come AFTER the ai-widget.js <script>
   tag, because the widget defines window.dpAI while it runs (both are `defer`,
   and deferred scripts execute in document order).
   ========================================================================= */
(function () {
  'use strict';

  var BTN_CLASS = 'askai-btn';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function collapse(s) {
    return String(s == null ? '' : s).replace(/\s+/g, ' ').trim();
  }

  // Text of an element, optionally dropping its little `.label` caption
  // (e.g. the "IB Tip" / "Literary Usage Pattern" chips).
  function textOf(el, dropLabel) {
    if (!el) return '';
    var clone = el.cloneNode(true);
    if (dropLabel) {
      var labels = clone.querySelectorAll('.label');
      for (var i = 0; i < labels.length; i++) {
        if (labels[i].parentNode) labels[i].parentNode.removeChild(labels[i]);
      }
    }
    return collapse(clone.textContent);
  }

  // Pull the whole word entry out of one card.
  function readCard(card) {
    var exEl = card.querySelector('.example');
    var srcEl = exEl ? exEl.querySelector('.source') : null;
    var example = textOf(exEl, false);
    var source = textOf(srcEl, false);
    if (source && example.slice(-source.length) === source) {
      example = collapse(example.slice(0, example.length - source.length));
    }
    return {
      word: textOf(card.querySelector('.word'), false),
      ipa: textOf(card.querySelector('.ipa'), false),
      pos: textOf(card.querySelector('.pos'), false),
      definition: textOf(card.querySelector('.definition'), false),
      usage: textOf(card.querySelector('.usage-box'), true),
      example: example,
      source: source,
      tip: textOf(card.querySelector('.ib-tip'), true),
      collocations: textOf(card.querySelector('.collocations'), false),
      card: card
    };
  }

  // Build the grounding block that travels with the question.
  function contextFor(d) {
    var lines = ['Word: ' + d.word + (d.ipa ? '  ' + d.ipa : '')];
    if (d.pos) lines.push('Part of speech: ' + d.pos);
    if (d.definition) lines.push('Definition (from the study site): ' + d.definition);
    if (d.usage) lines.push('Usage pattern taught: ' + d.usage);
    if (d.example) lines.push('Example given: ' + d.example + (d.source ? ' (' + d.source + ')' : ''));
    if (d.tip) lines.push('IB tip given: ' + d.tip);
    if (d.collocations) lines.push(d.collocations);
    return lines.join('\n');
  }

  function askAi(d) {
    if (!(window.dpAI && typeof window.dpAI.open === 'function')) {
      alert('The study assistant is still loading — give it a moment and try again.');
      return;
    }
    window.dpAI.open({
      ref: d.word,
      subject: 'English Vocabulary',
      topic: 'Literary analysis vocabulary',
      noun: 'word',
      contextLabel: 'Word',
      context: contextFor(d),
      prompt: 'Teach me the word "' + d.word + '". Cover: what it means in plain English, how it is pronounced, ' +
        'the register it belongs to, the collocations I should actually use, and how it differs from the ' +
        'near-synonyms I might reach for instead. Then show me two fresh example sentences of my own to ' +
        'imitate, and one sentence where using it would be WRONG and why.',
      display: 'Ask about "' + d.word + '"',
      intro: 'Focused on "' + d.word + '". Ask me anything about this word \u2014 its meaning, usage, ' +
        'collocations, or how to use it in your own writing.',
      autoSend: false
    });
  }

  function injectStyles() {
    if (document.getElementById('askai-style')) return;
    var css =
      '.word-card .' + BTN_CLASS + '{' +
      'margin-left:auto;align-self:center;font-family:inherit;font-size:12.5px;font-weight:600;' +
      'padding:5px 13px;border-radius:999px;cursor:pointer;white-space:nowrap;transition:.15s;' +
      'border:1px solid #c7d2fe;background:#eef2ff;color:#4338ca;}' +
      '.word-card .' + BTN_CLASS + ':hover{background:#4338ca;border-color:#4338ca;color:#fff;}' +
      '.word-card .' + BTN_CLASS + ':focus-visible{outline:2px solid #4338ca;outline-offset:2px;}';
    var style = document.createElement('style');
    style.id = 'askai-style';
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
  }

  function inject() {
    var cards = document.querySelectorAll('.word-card');
    if (!cards.length) return;
    injectStyles();
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      if (card.querySelector('.' + BTN_CLASS)) continue; // idempotent
      var d = readCard(card);
      if (!d.word) continue;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = BTN_CLASS;
      btn.textContent = '\uD83E\uDD16 Ask AI';
      btn.title = 'Open the assistant focused on "' + d.word + '" only';
      btn.setAttribute('aria-label', 'Ask the study assistant about ' + d.word);
      btn.addEventListener('click', function (entry) {
        return function () { askAi(entry); };
      }(d));
      var header = card.querySelector('.word-header') || card;
      header.appendChild(btn);
    }
  }

  ready(inject);
})();
