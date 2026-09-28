/**
 * Fan Hub+ chatbot: async client.
 * - Answers come from POST /chatbot/ask/ (FAQ matching happens on the server).
 * - Suggestion chips come from GET /chatbot/suggestions/ (active FAQs from the database).
 */
(function () {
  'use strict';

  const HISTORY_KEY = 'fanhub_chat_history';
  const TOUR_STEP_KEY = 'fanhub_chat_tour_step';
  const TOUR_DONE_KEY = 'fanhub_chat_tour_done';
  const MAX_HISTORY = 100;
  const MAX_MESSAGE_LENGTH = 255;      // matches ChatbotQuery.message
  const REQUEST_TIMEOUT_MS = 10000;

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    const launcher = document.getElementById('chatbotLauncher');
    const panel = document.getElementById('chatbotPanel');
    const messagesEl = document.getElementById('chatbotMessages');
    const quickChipsEl = document.getElementById('chatbotQuickChips');
    const form = document.getElementById('chatbotForm');
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSendBtn');
    const closeBtn = document.getElementById('chatbotCloseBtn');
    const clearBtn = document.getElementById('chatbotClearBtn');
    const badge = document.getElementById('chatbotBadge');

    if (!launcher || !panel || !messagesEl || !form || !input) return;

    // URLs come from data-* attributes on the panel. Change the defaults if your routes differ.
    const cfg = {
      askUrl: panel.dataset.askUrl,
      exploreUrl: panel.dataset.exploreUrl || '/explore/',
      eventsUrl: panel.dataset.eventsUrl || '/events/',
      dashboardUrl: panel.dataset.dashboardUrl || '/dashboard/',
    };

    // Short guided tour shown to first-time visitors (the SRS's multi-step conversational flow).
    const TOUR = [
      { text: "Hi! I'm the Fan Hub+ assistant. Want a 30-second tour of the site?",
        chips: [{ label: 'Start the tour', action: 'tour-next' }, { label: 'No thanks', action: 'tour-skip' }] },
      { text: 'Explore is where you search and filter content by category, genre, release year and type, and sort by latest, popular or A-Z.',
        chips: [{ label: 'Open Explore', href: cfg.exploreUrl }, { label: 'Next', action: 'tour-next' }] },
      { text: 'With a free account you can bookmark items, rate videos and audio, and see your activity on your dashboard.',
        chips: [{ label: 'My dashboard', href: cfg.dashboardUrl }, { label: 'Next', action: 'tour-next' }] },
      { text: 'Events lists conventions, meetups and screenings, filterable by city, with a map for nearby ones.',
        chips: [{ label: 'See events', href: cfg.eventsUrl }, { label: 'Next', action: 'tour-next' }] },
      { text: "That's the tour! Ask me anything, or tap one of the suggested questions below.", chips: [] },
    ];

    let isOpen = false;
    let pending = false;
    let suggestionsLoaded = false;
    let tourStep = parseInt(localStorage.getItem(TOUR_STEP_KEY) || '0', 10);

    // ---------- helpers ----------
    function timeNow() {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function safeHref(href) {
      // only site-relative links, never javascript: or external URLs
      return typeof href === 'string' && href.startsWith('/') && !href.startsWith('//');
    }

    function csrfToken() {
      const field = form.querySelector('[name=csrfmiddlewaretoken]');
      if (field && field.value) return field.value;
      const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
      return match ? decodeURIComponent(match[1]) : '';
    }

    function loadHistory() {
      try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch (e) { return []; }
    }

    function saveHistory(list) {
      try { localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(-MAX_HISTORY))); } catch (e) { /* storage full or blocked */ }
    }

    // ---------- rendering (textContent only, so nothing typed or returned can inject HTML) ----------
    function makeChip(chip) {
      let el;
      if (chip.href && safeHref(chip.href)) {
        el = document.createElement('a');
        el.href = chip.href;
      } else {
        el = document.createElement('button');
        el.type = 'button';
        if (chip.action) el.dataset.action = chip.action;
        else el.dataset.query = chip.query || chip.label;
      }
      el.className = 'chatbot-chip';
      el.textContent = chip.label;
      return el;
    }

    function renderMessage(msg, animate) {
      const bubble = document.createElement('div');
      bubble.className = 'chat-bubble ' + msg.role;
      if (!animate) bubble.style.animation = 'none';

      const text = document.createElement('div');
      text.textContent = msg.text;
      bubble.appendChild(text);

      if (msg.chips && msg.chips.length) {
        const wrap = document.createElement('div');
        wrap.className = 'chatbot-chips-wrap';
        msg.chips.forEach(function (c) { wrap.appendChild(makeChip(c)); });
        bubble.appendChild(wrap);
      }

      const time = document.createElement('div');
      time.className = 'chat-time';
      time.textContent = msg.time;
      bubble.appendChild(time);

      messagesEl.appendChild(bubble);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return bubble;
    }

    function addMessage(role, text, chips) {
      const msg = { role: role, text: text, time: timeNow(), chips: chips || [] };
      renderMessage(msg, true);
      // tour buttons are not saved, so a reloaded chat never shows dead buttons
      const stored = Object.assign({}, msg, { chips: msg.chips.filter(function (c) { return !c.action; }) });
      const history = loadHistory();
      history.push(stored);
      saveHistory(history);
    }

    function showTyping() {
      return renderMessage({ role: 'bot', text: 'Typing...', time: '', chips: [] }, true);
    }

    function setBusy(busy) {
      pending = busy;
      if (sendBtn) sendBtn.disabled = busy;
      input.disabled = busy;
    }

    // ---------- talking to the backend ----------
    async function askServer(message) {
      const controller = new AbortController();
      const timer = setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT_MS);
      try {
        const res = await fetch(cfg.askUrl, {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
          body: JSON.stringify({ message: message }),
          signal: controller.signal,
        });
        if (res.status === 429) {                       // rate limited: server sends a friendly answer
          const limited = await res.json();
          return { answer: limited.answer, chips: [] };
        }
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        return { answer: data.answer, chips: Array.isArray(data.chips) ? data.chips : [] };
      } catch (err) {
        return { answer: 'Sorry, I could not reach the server. Please try again in a moment.', chips: [] };
      } finally {
        clearTimeout(timer);
      }
    }

    async function sendMessage(raw) {
      const message = (raw || '').trim().slice(0, MAX_MESSAGE_LENGTH);
      if (!message || pending) return;
      setBusy(true);
      addMessage('user', message);
      const typing = showTyping();
      const result = await askServer(message);
      typing.remove();
      addMessage('bot', result.answer, result.chips);
      setBusy(false);
      input.focus();
    }

    async function loadSuggestions() {
      if (suggestionsLoaded || !cfg.suggestionsUrl || !quickChipsEl) return;
      try {
        const res = await fetch(cfg.suggestionsUrl, { credentials: 'same-origin' });
        if (!res.ok) return;
        const data = await res.json();
        suggestionsLoaded = true;
        quickChipsEl.replaceChildren.apply(
          quickChipsEl,
          (data.suggestions || []).map(function (q) { return makeChip({ label: q, query: q }); })
        );
      } catch (err) { /* suggestions are optional, so fail quietly */ }
    }

    // ---------- guided tour ----------
    function showTourStep() {
      if (tourStep >= TOUR.length) { localStorage.setItem(TOUR_DONE_KEY, 'true'); return; }
      const step = TOUR[tourStep];
      addMessage('bot', step.text, step.chips);
      if (tourStep === TOUR.length - 1) localStorage.setItem(TOUR_DONE_KEY, 'true');
    }

    function startConversation() {
      if (messagesEl.children.length > 0) return;
      if (localStorage.getItem(TOUR_DONE_KEY) === 'true') {
        addMessage('bot', "Hi! Ask me about searching, bookmarks, events, or fan submissions, or tap a suggestion below.", []);
      } else {
        showTourStep();
      }
    }

    // ---------- panel open/close ----------
    function openPanel() {
      panel.classList.add('open');
      launcher.classList.add('open');
      launcher.setAttribute('aria-expanded', 'true');
      panel.setAttribute('aria-hidden', 'false');
      isOpen = true;
      if (badge) badge.style.display = 'none';
      startConversation();
      loadSuggestions();
      input.focus();
    }

    function closePanel() {
      panel.classList.remove('open');
      launcher.classList.remove('open');
      launcher.setAttribute('aria-expanded', 'false');
      panel.setAttribute('aria-hidden', 'true');
      isOpen = false;
    }

    // ---------- events ----------
    launcher.addEventListener('click', function () { isOpen ? closePanel() : openPanel(); });
    if (closeBtn) closeBtn.addEventListener('click', closePanel);
    window.addEventListener('keydown', function (e) { if (e.key === 'Escape' && isOpen) closePanel(); });

    form.addEventListener('submit', function (e) {     // fires on Enter and on the send button
      e.preventDefault();
      const value = input.value;
      input.value = '';
      sendMessage(value);
    });

    // one delegated handler for suggestion chips and tour buttons
    panel.addEventListener('click', function (e) {
      const el = e.target.closest('[data-query], [data-action]');
      if (!el) return;
      if (el.dataset.action === 'tour-next') {
        tourStep += 1;
        localStorage.setItem(TOUR_STEP_KEY, String(tourStep));
        el.parentElement.querySelectorAll('button').forEach(function (b) { b.disabled = true; });
        showTourStep();
      } else if (el.dataset.action === 'tour-skip') {
        tourStep = TOUR.length;
        localStorage.setItem(TOUR_DONE_KEY, 'true');
        el.parentElement.querySelectorAll('button').forEach(function (b) { b.disabled = true; });
        addMessage('bot', 'No problem! Ask me anything whenever you like.', []);
      } else if (el.dataset.query) {
        sendMessage(el.dataset.query);
      }
    });

    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (!confirm('Clear your conversation history?')) return;
        localStorage.removeItem(HISTORY_KEY);
        messagesEl.replaceChildren();
        startConversation();
      });
    }

    // ---------- initial state ----------
    loadHistory().forEach(function (msg) { renderMessage(msg, false); });
    if (badge && messagesEl.children.length === 0) badge.style.display = '';
  }
})();