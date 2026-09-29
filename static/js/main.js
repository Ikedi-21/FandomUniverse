/**
 * FAN HUB+ Core Application Script
 * Handles global search, hotkeys, system theme detection, watch page routing, and toasts.
 */

(function () {
  'use strict';

  // ====================================================================
  // GLOBAL TOAST NOTIFICATION
  // ====================================================================
  let toastTimer = null;

  window.showToast = function (message, isError) {
    if (isError === undefined) isError = false;

    let toastEl = document.getElementById('toastNotice');
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.id = 'toastNotice';
      toastEl.className = 'toast-notice';
      document.body.appendChild(toastEl);
    }

    if (toastTimer) {
      clearTimeout(toastTimer);
    }

    const checkIcon = `
      <svg class="toast-icon success" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
    `;

    const alertIcon = `
      <svg class="toast-icon error" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    `;

    toastEl.innerHTML = `
      ${isError ? alertIcon : checkIcon}
      <span>${message}</span>
    `;

    toastEl.classList.add('show');

    toastTimer = setTimeout(function () {
      toastEl.classList.remove('show');
    }, 3200);
  };

  // ====================================================================
  // THEME & DISPLAY SCALE (With prefers-color-scheme detection)
  // ====================================================================
  const THEME_KEY = 'fanhub_theme';
  const FONTSIZE_KEY = 'fanhub_font_size';

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function savePreference(value) {
    if (document.documentElement.dataset.authenticated !== 'true') return;
    fetch('/accounts/preferences/', {
      method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken()},
      body: JSON.stringify(value)
    }).catch(function () { /* Local preference remains available if the network is offline. */ });
  }

  function applyTheme(themeName, persist) {
    if (!['light', 'dark'].includes(themeName)) themeName = 'light';
    document.documentElement.setAttribute('data-theme', themeName);
    try { localStorage.setItem(THEME_KEY, themeName); } catch (error) { /* Attribute still updates for this page. */ }
    if (persist) savePreference({theme: themeName});
  }

  function applyFontSize(sizeName, persist) {
    if (!['small', 'medium', 'large'].includes(sizeName)) sizeName = 'medium';
    document.documentElement.setAttribute('data-font-size', sizeName);
    try { localStorage.setItem(FONTSIZE_KEY, sizeName); } catch (error) { /* Attribute still updates for this page. */ }
    if (persist) savePreference({font_size: sizeName});
  }

  function initThemeAndFont() {
    let themeBtn = document.getElementById('themeToggleBtn');
    let fontControl = document.getElementById('fontSizeControl');
    if (!themeBtn || !fontControl) {
      const controls = document.createElement('div');
      controls.className = 'fanhub-display-controls';
      if (!themeBtn) {
        themeBtn = document.createElement('button');
        themeBtn.id = 'themeToggleBtn'; themeBtn.type = 'button';
        themeBtn.className = 'btn btn-secondary btn-sm';
        themeBtn.setAttribute('aria-label', 'Toggle color theme');
        themeBtn.textContent = 'Toggle theme'; controls.appendChild(themeBtn);
      }
      if (!fontControl) {
        fontControl = document.createElement('select');
        fontControl.id = 'fontSizeControl'; fontControl.className = 'form-select';
        fontControl.setAttribute('aria-label', 'Text size');
        [['small','Small text'],['medium','Medium text'],['large','Large text']].forEach(function (option) {
          const node = document.createElement('option'); node.value = option[0]; node.textContent = option[1]; fontControl.appendChild(node);
        });
        controls.appendChild(fontControl);
      }
      if (!document.getElementById('themeToggleBtn')) document.body.appendChild(controls);
      else if (!document.getElementById('fontSizeControl')) document.getElementById('themeToggleBtn').after(fontControl);
    }
    const root = document.documentElement;
    applyTheme(root.getAttribute('data-theme') || 'light', false);
    applyFontSize(root.getAttribute('data-font-size') || 'medium', false);
    themeBtn = document.getElementById('themeToggleBtn');
    fontControl = document.getElementById('fontSizeControl');
    if (themeBtn) themeBtn.addEventListener('click', function () {
      applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    });
    if (fontControl) {
      fontControl.value = root.getAttribute('data-font-size') || 'medium';
      fontControl.addEventListener('change', function () { applyFontSize(fontControl.value, true); });
    }
  }

  // ====================================================================
  // GLOBAL SEARCH & HOTKEYS
  // ====================================================================
  function initGlobalSearchAndHotkeys() {
    // Let real Django GET forms handle search; this only provides the slash shortcut.
    const searchInput = document.getElementById('globalSearchInput');
    window.addEventListener('keydown', function (event) {
      if (event.key === '/' && searchInput && document.activeElement !== searchInput && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        event.preventDefault(); searchInput.focus();
      } else if (event.key === 'Escape') closeAllModalsAndDrawers();
    });
  }

  function closeAllModalsAndDrawers() {
    document.querySelectorAll('.modal-overlay').forEach(function (modal) {
      modal.classList.remove('active', 'show');
    });

    document.querySelectorAll('.cart-drawer-overlay').forEach(function (dr) {
      dr.classList.remove('active');
    });
    document.querySelectorAll('.cart-drawer').forEach(function (cd) {
      cd.classList.remove('open');
    });

    document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
      pop.classList.remove('open');
    });

    const sidebar = document.getElementById('sidebarLeft');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('active');
  }

  // ====================================================================
  // SECTION E: DEDICATED WATCH PAGE ROUTING (Off YouTube Modals)
  // ====================================================================
  function initWatchTriggers() {
    // Watch navigation is provided by the real content detail route.
  }

  function initBookmarksAndSharing() {
    document.querySelectorAll('[data-bookmark-toggle]').forEach(function (button) {
      button.addEventListener('click', function () {
        if (document.documentElement.dataset.authenticated !== 'true') {
          window.location.href = button.dataset.loginUrl + '?next=' + encodeURIComponent(window.location.pathname);
          return;
        }
        const body = new URLSearchParams({
          content_type_id: button.dataset.contentTypeId,
          object_id: button.dataset.objectId
        });
        fetch(button.dataset.bookmarkUrl, {
          method: 'POST', credentials: 'same-origin',
          headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken()},
          body: body.toString()
        }).then(function (response) { return response.json(); }).then(function (result) {
          if (!result.ok) throw new Error(result.error || 'Could not update bookmark.');
          button.dataset.bookmarked = result.bookmarked ? 'true' : 'false';
          button.setAttribute('aria-pressed', result.bookmarked ? 'true' : 'false');
          const label = button.querySelector('[data-bookmark-label]');
          if (label) label.textContent = result.bookmarked ? 'Bookmarked' : 'Bookmark';
        }).catch(function (error) { window.showToast(error.message, true); });
      });
    });
    document.querySelectorAll('[data-copy-link]').forEach(function (button) {
      button.addEventListener('click', function () {
        navigator.clipboard.writeText(button.dataset.copyLink || window.location.href)
          .then(function () { window.showToast('Link copied.'); })
          .catch(function () { window.showToast('Could not copy the link.', true); });
      });
    });
  }

  // ====================================================================
  // MODALS, POPOVERS & HEADER MENUS
  // ====================================================================
  function initModalsAndPopovers() {
    document.querySelectorAll('.modal-close-btn, [data-modal-close]').forEach(function (button) {
      button.addEventListener('click', closeAllModalsAndDrawers);
    });
    document.querySelectorAll('.modal-overlay').forEach(function (modal) {
      modal.addEventListener('click', function (event) {
        if (event.target === modal) closeAllModalsAndDrawers();
      });
    });
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebarLeft');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (mobileMenuBtn && sidebar && backdrop) {
      mobileMenuBtn.addEventListener('click', function () { sidebar.classList.add('open'); backdrop.classList.add('active'); });
      backdrop.addEventListener('click', closeAllModalsAndDrawers);
    }
  }

  // Expose helpers globally
  window.closeAllModalsAndDrawers = closeAllModalsAndDrawers;
  window.applyTheme = applyTheme;
  window.applyFontSize = applyFontSize;

  // ====================================================================
  // SIDEBAR NAV TOOLTIPS (for collapsed icon-only state)
  // ====================================================================
  function initSidebarTooltips() {
    document.querySelectorAll('.sidebar-nav-link').forEach(function (link) {
      var span = link.querySelector('span');
      if (span && !link.hasAttribute('title')) {
        link.setAttribute('title', span.textContent.trim());
      }
    });
    // Also add tooltip to the CTA button
    var ctaBtn = document.getElementById('sidebarSubmitBtn');
    if (ctaBtn && !ctaBtn.hasAttribute('title')) {
      var ctaText = ctaBtn.querySelector('.cta-text');
      if (ctaText) {
        ctaBtn.setAttribute('title', ctaText.textContent.trim());
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initThemeAndFont();
    initGlobalSearchAndHotkeys();
    initModalsAndPopovers();
    initBookmarksAndSharing();
    initSidebarTooltips();
  });
})();
