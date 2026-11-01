// Home is static; both activity grids are rendered at build time.

(() => {  // theme toggle, same contract as site.js
  const root = document.documentElement, toggle = document.querySelector('.theme-toggle');
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const current = () => root.dataset.theme || (system.matches ? 'dark' : 'light');
  const sync = () => { if (toggle) toggle.querySelector('[data-theme-label]').textContent = current() === 'dark' ? 'Light' : 'Dark'; };
  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      root.dataset.theme = current() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('ahk-theme', root.dataset.theme); } catch (_) { /* Session only. */ }
      sync();
    });
  }
  system.addEventListener('change', sync); sync();
})();
