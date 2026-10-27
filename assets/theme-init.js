// Runs before CSS to avoid a flash of the wrong theme. Storage may be unavailable.
try {
  const saved = localStorage.getItem('ahk-theme');
  if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
} catch (_) { /* Follow the system preference. */ }
