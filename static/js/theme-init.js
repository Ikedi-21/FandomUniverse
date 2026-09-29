/* Set display attributes before stylesheets paint. */
(function () {
  'use strict';
  var root = document.documentElement;
  var authenticated = root.getAttribute('data-authenticated') === 'true';
  var serverTheme = root.getAttribute('data-theme') || 'light';
  var serverFont = root.getAttribute('data-font-size') || 'medium';
  var theme = serverTheme;
  var font = serverFont;
  try {
    if (!authenticated) {
      theme = localStorage.getItem('fanhub_theme') || serverTheme;
      font = localStorage.getItem('fanhub_font_size') || serverFont;
    }
  } catch (error) { /* Keep the server defaults when browser storage is unavailable. */ }
  if (!['light', 'dark'].includes(theme)) theme = 'light';
  if (!['small', 'medium', 'large'].includes(font)) font = 'medium';
  root.setAttribute('data-theme', theme);
  root.setAttribute('data-font-size', font);
  if (authenticated) {
    try {
      localStorage.setItem('fanhub_theme', theme);
      localStorage.setItem('fanhub_font_size', font);
    } catch (error) { /* The server rendered values remain authoritative. */ }
  }
})();
