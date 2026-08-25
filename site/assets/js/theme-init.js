/* Applied before first paint to avoid a light flash on dark-themed reloads. */
(function () {
  try {
    var t = window.localStorage.getItem('dlp.theme');
    if (t === 'dark' || t === 'light') document.documentElement.setAttribute('data-theme', t);
  } catch (e) { /* ignore */ }
})();
