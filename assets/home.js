// Activity panel: switch between the AI-token grid and the GitHub grid (both rendered at build time).
document.querySelectorAll('.act-tabs button').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('.act-tabs button').forEach(x => x.setAttribute('aria-selected', x === b));
  document.querySelectorAll('.act-p').forEach(p => { p.hidden = p.dataset.p !== b.dataset.p });
}));
