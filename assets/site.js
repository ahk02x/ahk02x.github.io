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
    // Weekly cadence: the next card is due seven days after this one; past a day over, say it is late.
    const line = element.querySelector('[data-health-updated]');
    if (line && Number.isFinite(date)) {
      const day = ms => new Date(ms).toLocaleDateString('en', { month: 'short', day: 'numeric', timeZone: 'UTC' });
      const next = date + 7 * 86400000, late = Date.now() > next + 86400000;
      line.innerHTML = `<span>Last updated ${day(date)}</span><span class="hc-next">${late ? `Next update was due ${day(next)} · late` : `Next update ${day(next)}`}</span>`;
      line.classList.toggle('late', late);
    }
  });
})();
