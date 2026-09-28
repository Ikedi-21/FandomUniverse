/**
 * FAN HUB+ Authentication Context
 * Single source of truth for auth state across all pages.
 * Handles DOM synchronization, guest flow, route protection, and auth-change events.
 */

(function () {
  'use strict';

  const STORAGE_KEY_SESSION = 'fanhub_auth_session';
  const STORAGE_KEY_LOGGED_IN = 'fanhub_logged_in';
  const STORAGE_KEY_USER = 'fanhub_user';
  const REDIRECT_KEY = 'fanhub_redirect_after_login';

  const PROTECTED_ROUTES = [
    'dashboard.html',
    'profile.html',
    'submissions.html',
    'collection.html',
    'settings.html'
  ];

  let listeners = [];

  const AuthContext = {
    getUser: function () {
      try {
        const raw = localStorage.getItem(STORAGE_KEY_SESSION);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },

    getUserProfile: function () {
      try {
        const raw = localStorage.getItem(STORAGE_KEY_USER);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },

    isAuthenticated: function () {
      const loggedIn = localStorage.getItem(STORAGE_KEY_LOGGED_IN);
      const session = this.getUser();
      return loggedIn === 'true' && session !== null;
    },

    login: function (sessionData) {
      const defaultUser = {
        token: 'fh_token_' + Math.random().toString(36).substring(2, 10),
        username: (sessionData && sessionData.username) || 'alex_prime',
        firstName: (sessionData && sessionData.firstName) || 'Alex',
        lastName: (sessionData && sessionData.lastName) || 'Vance',
        email: (sessionData && sessionData.email) || 'alex@fanhub.com',
        avatar: (sessionData && sessionData.avatar) || (this.isSubpage() ? '../images/avatars/alex.jpg' : 'images/avatars/alex.jpg'),
        tier: (sessionData && sessionData.tier) || 'Gold VIP',
        role: (sessionData && sessionData.username === 'admin') ? 'admin' : 'user',
        loginTime: new Date().toISOString()
      };

      const finalSession = Object.assign({}, defaultUser, sessionData);
      localStorage.setItem(STORAGE_KEY_SESSION, JSON.stringify(finalSession));
      localStorage.setItem(STORAGE_KEY_LOGGED_IN, 'true');

      this.dispatchChange(true, finalSession);
      this.syncDOM();
      return finalSession;
    },

    logout: function () {
      localStorage.removeItem(STORAGE_KEY_SESSION);
      localStorage.setItem(STORAGE_KEY_LOGGED_IN, 'false');

      this.dispatchChange(false, null);
      this.syncDOM();

      if (window.showToast) {
        window.showToast('You have been signed out.');
      }

      // Redirect to login.html
      const loginUrl = this.isSubpage() ? 'login.html' : 'pages/login.html';
      setTimeout(function () {
        window.location.href = loginUrl;
      }, 350);
    },

    subscribe: function (callback) {
      if (typeof callback === 'function') {
        listeners.push(callback);
      }
    },

    dispatchChange: function (isAuthenticated, user) {
      const detail = { isAuthenticated: isAuthenticated, user: user };
      const event = new CustomEvent('fanhub:auth-change', { detail: detail });
      window.dispatchEvent(event);

      listeners.forEach(function (cb) {
        try {
          cb(detail);
        } catch (err) {
          console.error('Auth listener error:', err);
        }
      });
    },

    isSubpage: function () {
      return window.location.pathname.includes('/pages/');
    },

    getCurrentPageName: function () {
      const path = window.location.pathname;
      return path.substring(path.lastIndexOf('/') + 1) || 'index.html';
    },

    checkRouteGuard: function () {
      const currentPage = this.getCurrentPageName();
      if (PROTECTED_ROUTES.includes(currentPage)) {
        if (!this.isAuthenticated()) {
          const currentUrl = window.location.href;
          sessionStorage.setItem(REDIRECT_KEY, currentUrl);

          const loginUrl = this.isSubpage()
            ? 'login.html?next=' + encodeURIComponent(currentPage) + '&notice=login_required'
            : 'pages/login.html?next=' + encodeURIComponent(currentPage) + '&notice=login_required';

          window.location.href = loginUrl;
        }
      }
    },

    // Single source of truth DOM synchronizer (Section A & B)
    syncDOM: function () {
      const isAuth = this.isAuthenticated();
      const user = this.getUser();
      const sub = this.isSubpage();
      const prefix = sub ? '' : 'pages/';
      const imgPrefix = sub ? '../' : '';

      // 1. Sync #headerAuthSlot
      const headerAuthSlot = document.getElementById('headerAuthSlot');
      if (headerAuthSlot) {
        if (isAuth && user) {
          headerAuthSlot.innerHTML = `
            <div class="user-profile-badge-wrap" style="position: relative;">
              <button class="user-profile-badge btn-ghost" id="userProfileBadge" style="display:flex; align-items:center; gap:8px; padding:4px 8px; border-radius:8px;" aria-expanded="false" aria-label="User Profile Menu">
                <img src="${imgPrefix}images/avatars/alex.jpg" alt="${user.username}" style="width:34px; height:34px; border-radius:50%; object-fit:cover; border:2px solid var(--accent-red); flex-shrink:0;" />
                <span class="user-profile-username" style="font-size:var(--font-sm); font-weight:var(--fw-bold); max-width:90px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${user.username}</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="user-profile-chevron"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </button>
              <div class="dropdown-popover user-popover-content" id="userDropdownMenu">
                <div class="user-popover-header">
                  <img src="${imgPrefix}images/avatars/alex.jpg" alt="Avatar" style="width:40px; height:40px; border-radius:50%; object-fit:cover; flex-shrink:0;" />
                  <div style="min-width:0; overflow:hidden;">
                    <div style="font-weight:var(--fw-bold); font-size:var(--font-sm); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.firstName || 'Alex'} ${user.lastName || ''}</div>
                    <div style="font-size:var(--font-xs); color:var(--text-dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">@${user.username}</div>
                    <div style="font-size:0.75rem; color:var(--accent-red); font-weight:bold;">${user.tier || 'Gold VIP'}</div>
                  </div>
                </div>
                <a href="${prefix}dashboard.html" class="user-popover-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                  Dashboard
                </a>
                <a href="${prefix}profile.html" class="user-popover-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                  Profile & Preferences
                </a>
                <a href="${prefix}submit-content.html" class="user-popover-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                  Submit Fan Content
                </a>
                <a href="${prefix}feedback.html" class="user-popover-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                  Feedback & Help
                </a>
                <button type="button" class="user-popover-link logout" id="btnLogoutAction" style="width:100%; border:none; background:none; text-align:left; cursor:pointer;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                  Sign Out
                </button>
              </div>
            </div>
          `;

          const badgeBtn = document.getElementById('userProfileBadge');
          const userMenu = document.getElementById('userDropdownMenu');
          if (badgeBtn && userMenu) {
            badgeBtn.onclick = function (e) {
              e.stopPropagation();
              const isOpen = userMenu.classList.contains('open');

              // Close all header popovers first (C4: mutual exclusivity)
              document.querySelectorAll('.dropdown-popover').forEach(function (pop) {
                pop.classList.remove('open');
              });
              document.querySelectorAll('[aria-expanded="true"]').forEach(function (el) {
                el.setAttribute('aria-expanded', 'false');
              });

              if (!isOpen) {
                userMenu.classList.add('open');
                badgeBtn.setAttribute('aria-expanded', 'true');
              } else {
                userMenu.classList.remove('open');
                badgeBtn.setAttribute('aria-expanded', 'false');
              }
            };
          }

          const btnLogout = document.getElementById('btnLogoutAction');
          if (btnLogout) {
            btnLogout.onclick = function () {
              AuthContext.logout();
            };
          }
        } else {
          headerAuthSlot.innerHTML = `
            <div style="display:flex; align-items:center; gap:8px;">
              <a href="${prefix}login.html" class="btn btn-ghost btn-sm" id="btnNavSignIn">Sign In</a>
              <a href="${prefix}register.html" class="btn btn-primary btn-sm" id="btnNavRegister">Register</a>
            </div>
          `;
        }
      }

      // 2. Sync sidebar footer
      const sidebarFooterSlot = document.getElementById('sidebarFooterSlot');
      if (sidebarFooterSlot) {
        if (isAuth && user) {
          sidebarFooterSlot.innerHTML = `
            <div class="sidebar-user-block" title="${user.firstName || 'Alex'} ${user.lastName || ''} (@${user.username})">
              <img src="${imgPrefix}images/avatars/alex.jpg" alt="${user.username}" class="sidebar-user-avatar" />
              <div class="sidebar-user-info">
                <div class="sidebar-user-name">${user.firstName || 'Alex'} ${user.lastName || ''}</div>
                <div class="sidebar-user-tier">${user.tier || 'VIP'}</div>
              </div>
            </div>
            <button type="button" class="sidebar-nav-link" id="sidebarLogoutBtn" title="Sign Out" style="border:none; background:none; text-align:left; cursor:pointer; color:#ef4444; width:100%;">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
              <span>Sign Out</span>
            </button>
          `;

          const sidebarLogout = document.getElementById('sidebarLogoutBtn');
          if (sidebarLogout) {
            sidebarLogout.onclick = function () {
              AuthContext.logout();
            };
          }
        } else {
          sidebarFooterSlot.innerHTML = `
            <a href="${prefix}submit-content.html" class="sidebar-cta-btn" id="sidebarSubmitBtn" title="Submit Content">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              <span class="cta-text">Submit Content</span>
            </a>
          `;
        }
      }

      // 3. Sync Right Sidebar User Widget (#sidebarUserWidget) — FIX SECTION A
      const sidebarUserWidget = document.getElementById('sidebarUserWidget');
      if (sidebarUserWidget) {
        if (isAuth && user) {
          sidebarUserWidget.innerHTML = `
            <div style="display:flex; align-items:center; gap:12px;">
              <img src="${imgPrefix}images/avatars/alex.jpg" alt="User Profile" style="width:48px; height:48px; border-radius:50%; object-fit:cover; border:2px solid var(--accent-red);" />
              <div>
                <div style="font-size:var(--font-xs); color:var(--text-dim); text-transform:uppercase; font-weight:bold;">Welcome Explorer</div>
                <div style="font-size:var(--font-lg); font-weight:var(--fw-bold);">${user.firstName || 'Alex'} ${user.lastName || 'Vance'}</div>
              </div>
            </div>
            <p style="font-size:var(--font-sm); color:var(--text-muted); line-height:1.4;">
              ${user.tier || 'Gold VIP'} Explorer • 3 new simulcast broadcasts ready in your watchlist.
            </p>
            <a href="${prefix}dashboard.html" class="btn btn-view-dashboard">View Dashboard</a>
          `;
        } else {
          sidebarUserWidget.innerHTML = `
            <div style="display:flex; align-items:center; gap:12px;">
              <div class="brand-badge" style="width:44px; height:44px; font-size:1.4rem;">F</div>
              <div>
                <div style="font-size:var(--font-xs); color:var(--accent-red); text-transform:uppercase; font-weight:bold;">Join The Community</div>
                <div style="font-size:var(--font-lg); font-weight:var(--fw-bold);">Explore Fan Hub+</div>
              </div>
            </div>
            <p style="font-size:var(--font-sm); color:var(--text-muted); line-height:1.4;">
              Create your free account to track watchlist progress, download episodes offline, and share discussions.
            </p>
            <div style="display:flex; gap:8px;">
              <a href="${prefix}login.html" class="btn btn-secondary btn-sm" style="flex:1;">Sign In</a>
              <a href="${prefix}register.html" class="btn btn-primary btn-sm" style="flex:1;">Register</a>
            </div>
          `;
        }
      }

      // Hide admin links
      const isAdmin = isAuth && user && user.role === 'admin';
      document.querySelectorAll('a[href*="admin-overview.html"], a[href*="admin-content-form.html"]').forEach(function (link) {
        const parentLi = link.closest('li');
        if (parentLi) {
          parentLi.style.display = isAdmin ? '' : 'none';
        } else {
          link.style.display = isAdmin ? '' : 'none';
        }
      });
    },

    // Protected links interceptor (Section B)
    initProtectedLinksInterceptor: function () {
      const self = this;
      document.addEventListener('click', function (e) {
        const link = e.target.closest('a[href]');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href) return;

        // Check if destination is a protected route
        const isProtected = PROTECTED_ROUTES.some(function (route) {
          return href.endsWith(route) || href.includes(route + '?');
        });

        if (isProtected && !self.isAuthenticated()) {
          e.preventDefault();
          sessionStorage.setItem(REDIRECT_KEY, link.href);

          const promptModal = document.getElementById('authPromptModal');
          if (promptModal) {
            promptModal.classList.add('active');
          } else {
            const pageName = href.substring(href.lastIndexOf('/') + 1);
            const loginUrl = self.isSubpage()
              ? 'login.html?next=' + encodeURIComponent(pageName) + '&notice=login_required'
              : 'pages/login.html?next=' + encodeURIComponent(pageName) + '&notice=login_required';
            window.location.href = loginUrl;
          }
        }
      });
    },

    init: function () {
      this.checkRouteGuard();
      this.syncDOM();
      this.initProtectedLinksInterceptor();

      // Subscribe to auth changes
      const self = this;
      window.addEventListener('fanhub:auth-change', function () {
        self.syncDOM();
      });
    }
  };

  window.AuthContext = AuthContext;
  window.useAuth = function () {
    return AuthContext;
  };

  document.addEventListener('DOMContentLoaded', function () {
    AuthContext.init();
  });
})();
