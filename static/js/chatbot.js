(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var launcher = document.getElementById('chatbotLauncher');
    var panel = document.getElementById('chatbotPanel');
    var close = document.getElementById('chatbotCloseBtn');
    var form = document.getElementById('chatbotForm');
    var input = document.getElementById('chatbotInput');
    var messages = document.getElementById('chatbotMessages');
    var chips = document.getElementById('chatbotQuickChips');
    if (!launcher || !panel || !form || !input || !messages) return;

    function bubble(role, text) {
      var item = document.createElement('div');
      item.className = 'chat-bubble ' + role;
      item.textContent = text;
      messages.appendChild(item);
      messages.scrollTop = messages.scrollHeight;
    }
    function csrf() {
      var field = form.querySelector('[name="csrfmiddlewaretoken"]');
      if (field) return field.value;
      var match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
      return match ? decodeURIComponent(match[1]) : '';
    }
    function toggle(open) {
      panel.classList.toggle('open', open);
      launcher.classList.toggle('open', open);
      launcher.setAttribute('aria-expanded', String(open));
      panel.setAttribute('aria-hidden', String(!open));
      if (open) input.focus();
    }
    launcher.addEventListener('click', function () { toggle(!panel.classList.contains('open')); });
    if (close) close.addEventListener('click', function () { toggle(false); });
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      var message = input.value.trim();
      if (!message) return;
      input.value = '';
      bubble('user', message);
      var button = form.querySelector('[type="submit"]');
      if (button) button.disabled = true;
      try {
        var response = await fetch(form.dataset.endpoint || form.action, {
          method: 'POST', credentials: 'same-origin',
          headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()},
          body: JSON.stringify({message: message})
        });
        var data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Assistant request failed.');
        bubble('bot', data.answer);
        if (chips) {
          chips.replaceChildren();
          (data.chips || []).forEach(function (chip) {
            var link = document.createElement('a');
            link.className = 'chatbot-chip'; link.href = chip.href; link.textContent = chip.label;
            chips.appendChild(link);
          });
        }
      } catch (error) {
        bubble('bot', 'The assistant is temporarily unavailable. Please try again.');
      } finally {
        if (button) button.disabled = false;
      }
    });
  });
})();
