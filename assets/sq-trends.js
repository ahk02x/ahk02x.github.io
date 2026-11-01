// /sq/trends.html: baseline tiles + weekly trend charts from /data/sq_trends.json (built by tools/sq_trends.py).
(() => {
  const $ = id => document.getElementById(id);
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = iso => { const [, m, d] = iso.split('-'); return `${MON[+m - 1]} ${+d}`; };
  const fmt = (v, nd = 0) => v == null ? '—' : v.toLocaleString('en', { maximumFractionDigits: nd, minimumFractionDigits: nd });
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  // lower = better only where a rise means something is wrong; oil and boost are readings, not verdicts
  const CHARTS = [
    { key: 'misfire_hr', title: 'Misfire rate', unit: 'per engine hour', color: 'var(--mis)', nd: 1, better: 'down' },
    { key: 'knock_pct', title: 'Knock', unit: '% of time', color: 'var(--knk)', nd: 2, better: 'down' },
    { key: 'oil_max', title: 'Oil peak', unit: '°C', color: 'var(--oil)', nd: 0 },
    { key: 'boost_psi', title: 'Peak boost', unit: 'psi', color: 'var(--bst)', nd: 0 },
  ];

  function spark(vals, color, bars) {
    const W = 200, H = 34, n = vals.length, max = Math.max(...vals.filter(v => v != null), 1);
    const min = bars ? 0 : Math.min(...vals.filter(v => v != null));
    const x = i => n < 2 ? W / 2 : 2 + i * (W - 4) / (n - 1), y = v => H - 3 - (v - min) / ((max - min) || 1) * (H - 6);
    if (bars) {
      const bw = (W - 4) / n * 0.6;
      return `<svg class="tr-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${vals.map((v, i) => v ? `<rect x="${x(i) - bw / 2}" y="${y(v)}" width="${bw}" height="${H - 3 - y(v)}" fill="${color}" opacity=".55"/>` : '').join('')}</svg>`;
    }
    const pts = vals.map((v, i) => v == null ? null : `${x(i).toFixed(1)},${y(v).toFixed(1)}`).filter(Boolean);
    const last = pts[pts.length - 1].split(',');
    return `<svg class="tr-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><polyline points="${pts.join(' ')}" fill="none" stroke="${color}" stroke-width="1.6" vector-effect="non-scaling-stroke"/><circle cx="${last[0]}" cy="${last[1]}" r="2.5" fill="${color}"/></svg>`;
  }

  function baseline(d) {
    const w = d.weeks, t = d.totals, col = k => w.map(x => x[k] ?? null);
    const card = (k, v, unit, sub, svg) => `<div class="tr-card"><div class="tr-k">${k}</div><div class="tr-v">${v}<small>${unit}</small></div><div class="tr-t">${sub}</div>${svg}</div>`;
    $('base').innerHTML =
      card('Peak boost', fmt(t.boost_psi), 'psi', 'manifold, across all drives', spark(col('boost_psi'), 'var(--bst)')) +
      card('Redline seen', fmt(t.rpm_max), 'rpm', 'highest logged', spark(col('rpm_max'), 'var(--rpm)')) +
      card('Oil peak', fmt(t.oil_max), '°C', t.oil_max < 140 ? 'never near 140 °C danger' : 'reached the 140 °C line', spark(col('oil_max'), 'var(--oil)')) +
      card('Data logged', fmt(t.hours, 1), 'h', `${fmt(w.filter(x => x.hours).length)} weeks · ${fmt(t.captures)} captures`, spark(col('hours'), 'var(--muted)', true));
  }

  const mean = a => { const v = a.filter(x => x != null); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };

  function chart(c, cur, prev) {
    const W = 520, H = 220, L = 38, R = 30, T = 22, B = 26, n = cur.length;
    const vc = cur.map(x => x[c.key] ?? null), vp = prev ? prev.map(x => x[c.key] ?? null) : [];
    const all = vc.concat(vp).filter(v => v != null);
    if (!all.length) return `<div class="tr-card"><div class="tr-head"><b>${c.title}</b></div><p class="tr-note">No readings in this window.</p></div>`;
    let lo = Math.min(0, ...all), hi = Math.max(...all) * 1.08 || 1;
    const x = i => n < 2 ? L + (W - L - R) / 2 : L + i * (W - L - R) / (n - 1), y = v => T + (hi - v) / (hi - lo) * (H - T - B);
    const path = vals => { let s = '', pen = false; vals.forEach((v, i) => { if (v == null) { pen = false; return; } s += `${pen ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`; pen = true; }); return s; };
    const area = vals => vals.map((v, i) => v == null ? null : i).filter(i => i != null).length < 2 ? '' :
      path(vals).split('M').filter(Boolean).map(seg => { const p = seg.split('L'); if (p.length < 2) return ''; const x0 = p[0].split(',')[0], x1 = p[p.length - 1].split(',')[0]; return `<path d="M${seg}L${x1},${y(lo)}L${x0},${y(lo)}Z" fill="${c.color}" opacity=".12"/>`; }).join('');
    const ticks = Array.from({ length: 5 }, (_, i) => lo + (hi - lo) * i / 4);
    const grid = ticks.map(t => `<line x1="${L}" x2="${W - R}" y1="${y(t)}" y2="${y(t)}" stroke="var(--soft-line)" stroke-width=".6"/><text x="${L - 6}" y="${y(t) + 3}" text-anchor="end">${fmt(t, hi < 5 ? 1 : 0)}</text>`).join('');
    const labels = [0, Math.floor((n - 1) / 2), n - 1].filter((v, i, a) => a.indexOf(v) === i).map(i => `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${day(cur[i].week)}</text>`).join('');
    const pk = vc.reduce((b, v, i) => v != null && (b < 0 || v > vc[b]) ? i : b, -1);
    const li = vc.map((v, i) => v == null ? -1 : i).filter(i => i >= 0).pop();
    const dots = vc.map((v, i) => v == null ? '' : `<circle cx="${x(i)}" cy="${y(v)}" r="2.6" fill="${c.color}"><title>week of ${day(cur[i].week)}: ${fmt(v, c.nd)} ${c.unit}</title></circle>`).join('');
    const tag = (i, dy) => `<text x="${x(i)}" y="${y(vc[i]) + dy}" text-anchor="${i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'}" style="fill:var(--fg-2)">${fmt(vc[i], c.nd)}</text>`;
    let badge = '';
    const mc = mean(vc), mp = prev ? mean(vp) : null;
    if (mc != null && mp != null) {
      const dlt = mc - mp, flat = Math.abs(dlt) < Math.max(Math.abs(mp) * 0.03, 10 ** -c.nd);
      const cls = flat || !c.better ? 'flat' : (dlt < 0) === (c.better === 'down') ? 'good' : 'bad';
      badge = `<span class="tr-delta tr-${cls}">${dlt < 0 ? '▼' : '▲'} ${fmt(Math.abs(dlt), c.nd)}</span><span class="tr-t" style="margin:0">vs before</span>`;
    }
    const svg = `<svg class="tr-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(c.title)} by week">${grid}${area(vc)}` +
      (prev ? `<path d="${path(vp)}" fill="none" stroke="var(--prev)" stroke-width="1.2" stroke-dasharray="4 3"/>` : '') +
      `<path d="${path(vc)}" fill="none" stroke="${c.color}" stroke-width="2"/>${dots}${pk >= 0 ? tag(pk, -8) : ''}${li !== pk && li >= 0 ? tag(li, -8) : ''}${labels}</svg>`;
    const legend = `<div class="tr-legend"><span><i style="background:${c.color}"></i>${day(cur[0].week)} – ${day(cur[n - 1].week)}</span>` +
      (prev ? `<span><i style="background:var(--prev)"></i>${day(prev[0].week)} – ${day(prev[prev.length - 1].week)} (before)</span>` : '') + '</div>';
    return `<div class="tr-card"><div class="tr-head"><b>${c.title}</b>${badge}<span class="tr-u">${c.unit}</span></div>${svg}${legend}</div>`;
  }

  function render(d, w, cmp) {
    const all = d.weeks, n = w && w < all.length ? w : all.length, cur = all.slice(-n);
    const prev = cmp && w && all.length >= 2 * n ? all.slice(-2 * n, -n) : null;
    $('span').textContent = `${cur.filter(x => x.hours).length} driving weeks · ${day(cur[0].week)} – ${day(cur[n - 1].week)}`;
    $('cmp').disabled = !w || all.length < 2 * n;
    $('charts').innerHTML = CHARTS.map(c => chart(c, cur, prev)).join('');
  }

  fetch('/data/sq_trends.json').then(r => r.json()).then(d => {
    let w = 8;
    baseline(d);
    $('asof').textContent = `Through the week of ${day(d.through_week)}. Weeks only, never trip dates or times. The current week fills in as it is driven.`;
    $('win').addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      w = +b.dataset.w;
      $('win').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
      render(d, w, $('cmp').checked);
    });
    $('cmp').addEventListener('change', () => render(d, w, $('cmp').checked));
    render(d, w, true);
  }).catch(() => { $('charts').innerHTML = '<p class="tr-note">Trend data did not load.</p>'; });
})();
