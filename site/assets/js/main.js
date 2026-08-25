/* DevOps Learning Path — shared behaviour: theme toggle + per-page progress. */
(function () {
  'use strict';

  var THEME_KEY = 'dlp.theme';

  function store(key, value) {
    try { window.localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }
  function load(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }

  /* ---- theme ---------------------------------------------------------- */

  function applyTheme(theme) {
    if (theme === 'dark' || theme === 'light') {
      document.documentElement.setAttribute('data-theme', theme);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }

  function currentTheme() {
    var explicit = document.documentElement.getAttribute('data-theme');
    if (explicit) return explicit;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function initTheme() {
    applyTheme(load(THEME_KEY));
    var btn = document.querySelector('[data-theme-toggle]');
    if (!btn) return;
    var sync = function () {
      var dark = currentTheme() === 'dark';
      btn.textContent = dark ? '☀' : '☾';
      btn.setAttribute('aria-label', dark ? '밝은 테마로 전환' : '어두운 테마로 전환');
    };
    sync();
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      store(THEME_KEY, next);
      sync();
    });
  }

  /* ---- progress checkboxes -------------------------------------------- */

  function initProgress() {
    var lists = document.querySelectorAll('[data-progress]');
    if (!lists.length) return;

    Array.prototype.forEach.call(lists, function (list) {
      var key = 'dlp.progress.' + list.getAttribute('data-progress');
      var saved = {};
      try { saved = JSON.parse(load(key) || '{}'); } catch (e) { saved = {}; }

      var boxes = list.querySelectorAll('input[type="checkbox"]');
      var meter = document.querySelector('[data-progress-for="' + list.getAttribute('data-progress') + '"]');

      var render = function () {
        if (!meter) return;
        var done = list.querySelectorAll('input[type="checkbox"]:checked').length;
        var pct = boxes.length ? Math.round((done / boxes.length) * 100) : 0;
        var fill = meter.querySelector('i');
        if (fill) fill.style.width = pct + '%';
        var label = meter.parentNode.querySelector('[data-progress-label]');
        if (label) label.textContent = done + ' / ' + boxes.length + ' (' + pct + '%)';
      };

      Array.prototype.forEach.call(boxes, function (box) {
        if (saved[box.id]) box.checked = true;
        box.addEventListener('change', function () {
          saved[box.id] = box.checked;
          store(key, JSON.stringify(saved));
          render();
        });
      });

      render();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { initTheme(); initProgress(); });
  } else {
    initTheme();
    initProgress();
  }
})();
