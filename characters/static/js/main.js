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
  const FONTSIZE_KEY = 'fanhub_fontsize';

  function isSubpage() {
    return window.location.pathname.includes('/pages/');
  }

  function applyTheme(themeName) {
    if (!themeName) themeName = 'light';
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem(THEME_KEY, themeName);

    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    if (sunIcon && moonIcon) {
      if (themeName === 'light') {
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
      } else {
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
      }
    }
  }

  function applyFontSize(sizeName) {
    if (!sizeName) sizeName = 'standard';
    let px = '15px';
    if (sizeName === 'compact') px = '13.5px';
    if (sizeName === 'comfortable') px = '16.5px';
    document.documentElement.style.fontSize = px;
    localStorage.setItem(FONTSIZE_KEY, sizeName);
  }

  function initThemeAndFont() {
    let savedTheme = localStorage.getItem(THEME_KEY);
    // Section C: prefers-color-scheme detection as default on first visit
    if (!savedTheme) {
      savedTheme = 'light';
    }
    applyTheme(savedTheme);

    const savedFont = localStorage.getItem(FONTSIZE_KEY) || 'standard';
    applyFontSize(savedFont);

    // Theme toggle button in header
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.addEventListener('click', function () {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const nextTheme = current === 'light' ? 'dark' : 'light';
        applyTheme(nextTheme);
        window.showToast(`Switched to ${nextTheme} theme`);
      });
    }

    const authThemeBtn = document.getElementById('authThemeBtn');
    if (authThemeBtn) {
      authThemeBtn.addEventListener('click', function () {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = current === 'dark' ? 'light' : 'dark';
        applyTheme(nextTheme);
      });
    }
  }

  // ====================================================================
  // GLOBAL SEARCH & HOTKEYS
  // ====================================================================
  function initGlobalSearchAndHotkeys() {
    const searchInput = document.getElementById('globalSearchInput');

    if (searchInput) {
      searchInput.addEventListener('input', function (e) {
        const term = e.target.value.toLowerCase().trim();
        const searchableSelectors = [
          '.trending-card',
          '.series-card',
          '.event-full-card',
          '.fandom-cat-card',
          '.product-card',
          '.forum-card'
        ];

        const cards = document.querySelectorAll(searchableSelectors.join(', '));
        if (cards.length > 0) {
          cards.forEach(function (card) {
            const text = card.textContent.toLowerCase();
            if (term === '' || text.includes(term)) {
              card.style.display = '';
            } else {
              card.style.display = 'none';
            }
          });
        }
      });

      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          const term = searchInput.value.trim();
          if (term) {
            const sub = isSubpage();
            const discoveryUrl = sub
              ? 'explore.html?q=' + encodeURIComponent(term)
              : 'pages/explore.html?q=' + encodeURIComponent(term);
            window.location.href = discoveryUrl;
          }
        }
      });
    }

    // Keyboard Hotkeys: '/' focuses search, 'Escape' closes all popovers/modals
    window.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== searchInput) {
        const tag = document.activeElement ? document.activeElement.tagName : '';
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
          e.preventDefault();
          if (searchInput) {
            searchInput.focus();
            searchInput.select();
          }
        }
      } else if (e.key === 'Escape') {
        closeAllModalsAndDrawers();
      }
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
    document.addEventListener('click', function (e) {
      const trigger = e.target.closest('[data-video-target], .movie-card-play');
      if (trigger) {
        e.preventDefault();
        const key = trigger.getAttribute('data-video-target') || 'demon-slayer';
        const sub = isSubpage();
        const watchUrl = sub ? `watch.html?title=${encodeURIComponent(key)}` : `pages/watch.html?title=${encodeURIComponent(key)}`;
        window.location.href = watchUrl;
      }
    });
  }

  // ====================================================================
  // MODALS, POPOVERS & HEADER MENUS
  // ====================================================================
  function initModalsAndPopovers() {
    document.querySelectorAll('.modal-close-btn, [data-modal-close]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        closeAllModalsAndDrawers();
      });
    });

    document.querySelectorAll('.modal-overlay').forEach(function (modal) {
      modal.addEventListener('click', function (e) {
        if (e.target === modal) {
          closeAllModalsAndDrawers();
        }
      });
    });

    // Apps dropdown launcher
    const appsBtn = document.getElementById('appsMenuBtn');
    const appsMenu = document.getElementById('appsDropdownMenu');
    if (appsBtn && appsMenu) {
      appsBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = appsMenu.classList.contains('open');
        // Close all header popovers first (C4)
        document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
          pop.classList.remove('open');
        });
        document.querySelectorAll('[aria-expanded="true"]').forEach(function (el) {
          el.setAttribute('aria-expanded', 'false');
        });

        if (!isOpen) {
          appsMenu.classList.add('open');
          appsBtn.setAttribute('aria-expanded', 'true');
        }
      });
    }

    // Notifications popover
    const notifBtn = document.getElementById('notificationsBtn');
    const notifMenu = document.getElementById('notificationsDropdownMenu');
    if (notifBtn && notifMenu) {
      notifBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = notifMenu.classList.contains('open');
        // Close all header popovers first (C4)
        document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
          pop.classList.remove('open');
        });
        document.querySelectorAll('[aria-expanded="true"]').forEach(function (el) {
          el.setAttribute('aria-expanded', 'false');
        });

        if (!isOpen) {
          notifMenu.classList.add('open');
          notifBtn.setAttribute('aria-expanded', 'true');
        }
      });
    }

    const markReadBtn = document.getElementById('btnMarkAllRead');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', function () {
        const notifBadge = document.querySelector('#notificationsBtn .notification-badge');
        if (notifBadge) notifBadge.style.display = 'none';
        window.showToast('All notifications marked as read');
      });
    }

    // Dismiss popovers on click outside (C3)
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.dropdown-popover') && !e.target.closest('.icon-btn') && !e.target.closest('#userProfileBadge')) {
        document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
          pop.classList.remove('open');
        });
        document.querySelectorAll('[aria-expanded="true"]').forEach(function (el) {
          el.setAttribute('aria-expanded', 'false');
        });
      }
    });

    // Dismiss popovers on Escape key and return focus cleanly (C3 & C5)
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' || e.key === 'Esc') {
        const userMenu = document.getElementById('userDropdownMenu');
        const badgeBtn = document.getElementById('userProfileBadge');
        const wasUserMenuOpen = userMenu && userMenu.classList.contains('open');

        const appsMenu = document.getElementById('appsDropdownMenu');
        const appsBtn = document.getElementById('appsMenuBtn');
        const wasAppsOpen = appsMenu && appsMenu.classList.contains('open');

        const notifMenu = document.getElementById('notificationsDropdownMenu');
        const notifBtn = document.getElementById('notificationsBtn');
        const wasNotifOpen = notifMenu && notifMenu.classList.contains('open');

        document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
          pop.classList.remove('open');
        });
        document.querySelectorAll('[aria-expanded="true"]').forEach(function (el) {
          el.setAttribute('aria-expanded', 'false');
        });

        if (wasUserMenuOpen && badgeBtn) {
          badgeBtn.focus();
        } else if (wasAppsOpen && appsBtn) {
          appsBtn.focus();
        } else if (wasNotifOpen && notifBtn) {
          notifBtn.focus();
        }
      }
    });

    // Mobile sidebar drawer
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebarLeft');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (mobileMenuBtn && sidebar && backdrop) {
      mobileMenuBtn.addEventListener('click', function () {
        sidebar.classList.add('open');
        backdrop.classList.add('active');
      });

      backdrop.addEventListener('click', function () {
        sidebar.classList.remove('open');
        backdrop.classList.remove('active');
      });
    }

    // Card heart like toggles
    document.addEventListener('click', function (e) {
      const likeBtn = e.target.closest('.card-like-btn');
      if (likeBtn) {
        e.preventDefault();
        e.stopPropagation();
        likeBtn.classList.toggle('liked');
        if (likeBtn.classList.contains('liked')) {
          window.showToast('Saved to your favorites!');
        }
      }
    });

    // Submit Content Modal (Sidebar trigger)
    const sidebarSubmitBtn = document.getElementById('sidebarSubmitBtn');
    const submitModal = document.getElementById('submitModal');
    if (sidebarSubmitBtn && submitModal) {
      sidebarSubmitBtn.addEventListener('click', function (e) {
        if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname === '') {
          e.preventDefault();
          submitModal.classList.add('active');
        }
      });
    }

    const fandomSubmitForm = document.getElementById('fandomSubmitForm');
    if (fandomSubmitForm) {
      fandomSubmitForm.addEventListener('submit', function (e) {
        e.preventDefault();
        window.showToast('Content submitted to community queue!');
        fandomSubmitForm.reset();
        closeAllModalsAndDrawers();
      });
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
    initWatchTriggers();
    initModalsAndPopovers();
    initSidebarTooltips();
  });
})();
