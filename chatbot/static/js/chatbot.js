/**
 * FAN HUB+ Assistant Chatbot Engine
 * Features:
 * - Single-function response engine seam: getBotResponse(userMessage, context)
 * - FAQ keyword matching & scoring
 * - Contextual category recommendations & chips
 * - 5-Step guided onboarding state machine
 * - LocalStorage conversation persistence (fanhub_chat_history)
 */

(function () {
  'use strict';

  const STORAGE_KEY_HISTORY = 'fanhub_chat_history';
  const STORAGE_KEY_CONTEXT = 'fanhub_chat_context';
  const STORAGE_KEY_STEP = 'fanhub_chat_onboarding_step';
  const STORAGE_KEY_COMPLETE = 'fanhub_chat_onboarding_complete';

  function isSubpage() {
    return window.location.pathname.includes('/pages/');
  }

  function getPageUrl(target) {
    if (!target) return '#';
    const sub = isSubpage();
    if (target.startsWith('../') || target.startsWith('http')) return target;
    return sub ? target : 'pages/' + target;
  }

  // Read / Write Storage Helpers
  function getHistory() {
    try {
      const data = localStorage.getItem(STORAGE_KEY_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(messages) {
    // Cap at 100 messages
    if (messages.length > 100) {
      messages = messages.slice(messages.length - 100);
    }
    localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(messages));
  }

  function getChatContext() {
    try {
      const data = localStorage.getItem(STORAGE_KEY_CONTEXT);
      return data ? JSON.parse(data) : { mentionedCategories: [] };
    } catch (e) {
      return { mentionedCategories: [] };
    }
  }

  function saveChatContext(ctx) {
    localStorage.setItem(STORAGE_KEY_CONTEXT, JSON.stringify(ctx));
  }

  // ====================================================================
  // RESPONSE ENGINE SEAM: getBotResponse(userMessage, context)
  // Structure this cleanly so swapping with a backend / LLM endpoint later is trivial.
  // ====================================================================
  function getBotResponse(userMessage, context) {
    const raw = (userMessage || '').toLowerCase();
    const clean = raw.replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
    const data = window.FANHUB_CHATBOT_DATA || { faqs: [], categories: {} };

    // Check if user is asking for a tour
    if (clean.includes('show me around') || clean.includes('how does this work') || clean.includes('take a tour') || clean.includes('guide me')) {
      return {
        text: "Here is a quick tour of Fan Hub+: Use the top navigation or left sidebar to jump between Anime, Gaming, Movies, and Manga hubs. Press '/' anywhere to search instantly. Save shows to your Collection, discuss theories in Community, and grab collectibles in Goodies!",
        chips: [
          { label: 'Explore Anime →', href: getPageUrl('anime.html') },
          { label: 'Community Feed →', href: getPageUrl('community.html') },
          { label: 'Goodies Shop →', href: getPageUrl('goodies.html') }
        ]
      };
    }

    // Category Keyword Tracking
    const categoryKeys = ['anime', 'gaming', 'movies', 'kpop', 'k-pop', 'manga'];
    let detectedCategory = null;

    categoryKeys.forEach(function (cat) {
      const normCat = cat.replace('-', '');
      if (clean.includes(cat) || clean.includes(normCat)) {
        detectedCategory = cat === 'k-pop' ? 'kpop' : cat;
        if (!context.mentionedCategories) context.mentionedCategories = [];
        context.mentionedCategories = context.mentionedCategories.filter(function (c) { return c !== detectedCategory; });
        context.mentionedCategories.unshift(detectedCategory);
        saveChatContext(context);
      }
    });

    // Score FAQ entries
    let bestMatch = null;
    let highestScore = 0;

    data.faqs.forEach(function (faq) {
      let score = 0;
      faq.keywords.forEach(function (kw) {
        if (clean.includes(kw)) {
          score += kw.split(' ').length * 2;
        } else {
          kw.split(' ').forEach(function (w) {
            if (w.length > 2 && clean.includes(w)) score += 1;
          });
        }
      });

      if (score > highestScore) {
        highestScore = score;
        bestMatch = faq;
      }
    });

    // Minimum matching threshold
    if (bestMatch && highestScore >= 2) {
      const chips = (bestMatch.relatedLinks || []).map(function (link) {
        return { label: link.label, href: getPageUrl(link.href) };
      });

      // If user also mentioned a category, append category recommendation
      if (detectedCategory && data.categories[detectedCategory]) {
        const catInfo = data.categories[detectedCategory];
        chips.push({ label: `Visit ${catInfo.title} →`, href: getPageUrl(catInfo.page) });
      }

      return {
        text: bestMatch.answer,
        chips: chips
      };
    }

    // Direct Category Match if no specific FAQ
    if (detectedCategory && data.categories[detectedCategory]) {
      const catInfo = data.categories[detectedCategory];
      return {
        text: `Looking for ${catInfo.title}? You can explore all latest broadcasts, trending titles, and guides right inside the dedicated hub!`,
        chips: [
          { label: `Explore ${catInfo.title} →`, href: getPageUrl(catInfo.page) },
          { label: `Watch: ${catInfo.featured} →`, href: getPageUrl(catInfo.featuredWatch) }
        ]
      };
    }

    // Graceful Fallback
    return {
      text: "I'm not sure about that one — try asking about search shortcuts, collections, offline downloads, convention events, or creator studio uploads!",
      chips: [
        { label: 'How does search work?', query: 'how do i search' },
        { label: 'Tell me about Collections', query: 'what is collection' },
        { label: 'How do Downloads work?', query: 'how do downloads work' }
      ]
    };
  }

  // ====================================================================
  // WIDGET UI & DOM CONTROLLER
  // ====================================================================
  document.addEventListener('DOMContentLoaded', function () {
    const launcher = document.getElementById('chatbotLauncher');
    const panel = document.getElementById('chatbotPanel');
    const closeBtn = document.getElementById('chatbotCloseBtn');
    const clearBtn = document.getElementById('chatbotClearBtn');
    const messagesEl = document.getElementById('chatbotMessages');
    const inputEl = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSendBtn');
    const unreadDot = document.getElementById('chatbotUnreadDot');

    if (!launcher || !panel || !messagesEl) return;

    let isPanelOpen = false;

    function scrollToBottom() {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function renderMessage(role, text, time, chips, shouldAnimate) {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${role}`;
      if (!shouldAnimate) bubble.style.animation = 'none';

      let chipsHtml = '';
      if (chips && chips.length > 0) {
        chipsHtml = '<div class="chatbot-chips-wrap">';
        chips.forEach(function (chip) {
          if (chip.href) {
            chipsHtml += `<a href="${chip.href}" class="chatbot-chip">${chip.label}</a>`;
          } else {
            chipsHtml += `<button type="button" class="chatbot-chip" data-chip-query="${chip.query || chip.value || chip.label}">${chip.label}</button>`;
          }
        });
        chipsHtml += '</div>';
      }

      bubble.innerHTML = `
        <div>${text}</div>
        ${chipsHtml}
        <div class="chat-time">${time}</div>
      `;

      messagesEl.appendChild(bubble);
      scrollToBottom();
    }

    function rehydrateMessages() {
      messagesEl.innerHTML = '';
      const history = getHistory();

      if (history.length === 0) {
        // Check if onboarding is needed
        const onboardingDone = localStorage.getItem(STORAGE_KEY_COMPLETE) === 'true';
        if (!onboardingDone) {
          triggerOnboardingStep(1);
        } else {
          // Default greeting
          const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          const welcomeMsg = {
            role: 'bot',
            text: "Hello! I'm your Fan Hub+ Assistant. How can I help you explore anime, gaming, movies, or fandom goodies today?",
            time: now,
            chips: [
              { label: 'What is Fan Hub+?', query: 'what is fan hub' },
              { label: 'How to watch offline?', query: 'how do downloads work' },
              { label: 'Upcoming Conventions', query: 'how do events work' }
            ]
          };
          saveHistory([welcomeMsg]);
          renderMessage(welcomeMsg.role, welcomeMsg.text, welcomeMsg.time, welcomeMsg.chips, false);
        }
      } else {
        history.forEach(function (msg) {
          renderMessage(msg.role, msg.text, msg.time, msg.chips, false);
        });
      }
    }

    function addMessage(role, text, chips) {
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const msg = { role: role, text: text, time: now, chips: chips || [] };
      const history = getHistory();
      history.push(msg);
      saveHistory(history);
      renderMessage(role, text, now, chips, true);
    }

    function triggerOnboardingStep(stepNum) {
      const data = window.FANHUB_CHATBOT_DATA || {};
      const onboardingData = data.onboarding || [];
      const stepData = onboardingData.find(function (s) { return s.step === stepNum; });

      if (!stepData) return;

      localStorage.setItem(STORAGE_KEY_STEP, stepNum.toString());

      let text = stepData.message;
      let chips = stepData.chips || [];

      if (stepNum === 2) {
        const lastCat = (getChatContext().mentionedCategories || [])[0] || 'anime';
        text = stepData.template ? stepData.template(lastCat) : "Explore the latest releases and universe guides!";
      }

      addMessage('bot', text, chips);
    }

    function handleUserInput(text) {
      if (!text || !text.trim()) return;
      const cleanText = text.trim();

      // Check onboarding state
      const onboardingDone = localStorage.getItem(STORAGE_KEY_COMPLETE) === 'true';
      let currentStep = parseInt(localStorage.getItem(STORAGE_KEY_STEP) || '0', 10);

      addMessage('user', cleanText);

      if (!onboardingDone && currentStep > 0 && currentStep < 5) {
        // Proceed onboarding
        if (currentStep === 1) {
          const cat = cleanText.toLowerCase();
          const ctx = getChatContext();
          ctx.mentionedCategories = [cat];
          saveChatContext(ctx);
          setTimeout(function () { triggerOnboardingStep(2); }, 400);
        } else if (currentStep === 2) {
          setTimeout(function () { triggerOnboardingStep(3); }, 400);
        } else if (currentStep === 3) {
          setTimeout(function () { triggerOnboardingStep(4); }, 400);
        } else if (currentStep === 4) {
          setTimeout(function () { triggerOnboardingStep(5); }, 400);
        }
      } else {
        // Normal FAQ / Recommendation engine
        const context = getChatContext();
        setTimeout(function () {
          const resp = getBotResponse(cleanText, context);
          addMessage('bot', resp.text, resp.chips);
        }, 350);
      }
    }

    // Toggle Panel
    function openPanel() {
      panel.classList.add('open');
      launcher.classList.add('open');
      launcher.setAttribute('aria-expanded', 'true');
      isPanelOpen = true;
      if (unreadDot) unreadDot.style.display = 'none';
      if (inputEl) inputEl.focus();
      scrollToBottom();
    }

    function closePanel() {
      panel.classList.remove('open');
      launcher.classList.remove('open');
      launcher.setAttribute('aria-expanded', 'false');
      isPanelOpen = false;
    }

    launcher.addEventListener('click', function () {
      if (isPanelOpen) {
        closePanel();
      } else {
        openPanel();
      }
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', closePanel);
    }

    // Clear Conversation Action
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (confirm('Clear your conversation history? Your onboarding status and saved fandom categories will be preserved.')) {
          localStorage.removeItem(STORAGE_KEY_HISTORY);
          rehydrateMessages();
          if (window.showToast) window.showToast('Conversation cleared.');
        }
      });
    }

    // Send on click / enter
    if (sendBtn && inputEl) {
      sendBtn.addEventListener('click', function () {
        const val = inputEl.value;
        inputEl.value = '';
        handleUserInput(val);
      });

      inputEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          const val = inputEl.value;
          inputEl.value = '';
          handleUserInput(val);
        }
      });
    }

    // Click on suggestion chip
    document.addEventListener('click', function (e) {
      const chipBtn = e.target.closest('[data-chip-query]');
      if (chipBtn) {
        e.preventDefault();
        const query = chipBtn.getAttribute('data-chip-query');
        if (query === 'finish') {
          localStorage.setItem(STORAGE_KEY_COMPLETE, 'true');
          const lastCat = (getChatContext().mentionedCategories || [])[0] || 'anime';
          const targetPage = (window.FANHUB_CHATBOT_DATA && window.FANHUB_CHATBOT_DATA.categories[lastCat]) ? window.FANHUB_CHATBOT_DATA.categories[lastCat].page : 'anime.html';
          closePanel();
          window.location.href = getPageUrl(targetPage);
        } else {
          handleUserInput(query);
        }
      }
    });

    // Close on Escape
    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isPanelOpen) {
        closePanel();
      }
    });

    // Yield z-index priority: Auto-close chatbot panel if a modal or cart drawer opens
    const observer = new MutationObserver(function () {
      const activeModal = document.querySelector('.modal-overlay.active, .modal-overlay.show, .cart-drawer-overlay.active');
      if (activeModal && isPanelOpen) {
        closePanel();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });

    // Initial rehydration
    rehydrateMessages();
  });
})();
if (res.status === 429) return await res.json();
