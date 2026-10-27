(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('.theme-toggle');
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const current = () => root.dataset.theme || (system.matches ? 'dark' : 'light');
  const sync = () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    if (toggle) {
      toggle.querySelector('[data-theme-label]').textContent = next === 'dark' ? 'Dark' : 'Light';
      toggle.setAttribute('aria-label', `Switch to ${next} theme`);
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = current() === 'dark' ? '#171c19' : '#f2f0e9';
  };
  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      root.dataset.theme = current() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('ahk-theme', root.dataset.theme); } catch (_) { /* Session only. */ }
      sync();
    });
  }
  system.addEventListener('change', sync);
  sync();
  // A static snapshot can outlive the build. Keep the original verdict as history.
  document.querySelectorAll('[data-health-date]').forEach(element => {
    const value = element.dataset.healthDate;
    const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? Date.parse(`${value}T00:00:00Z`) : NaN;
    if (!Number.isFinite(date) || Date.now() - date > 14 * 86400000) {
      const label = element.querySelector('[data-health-label]');
      if (label) {
        label.textContent = Number.isFinite(date) ? 'Older snapshot — open report' : 'No dated snapshot';
        element.classList.remove('ok', 'warn', 'crit');
        element.classList.add('unknown');
      }
      const notice = element.querySelector('[data-stale-notice]');
      if (notice) notice.hidden = false;
    }
  });
})();
