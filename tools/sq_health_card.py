#!/usr/bin/env python3
"""Render the SQ5's weekly health card as a site page source from sq_weekly.py --json (stdin).
Writes src/pages/sq-health.html (built by tools/build.py) and sq/health.json. Week granularity only."""
import json, sys, os, html
d = json.load(sys.stdin)
site = os.path.join(os.path.dirname(__file__), '..')
w, p, mf, mfp = d.get('week', {}), d.get('prior', {}), d.get('misfire', {}), d.get('misfire_prior', {})
status = d.get('status', 'OK')
WORD = {'OK': 'Healthy', 'WATCH': 'Keep an eye on it', 'FLAG': 'Needs attention'}; CLS = {'OK': 'ok', 'WATCH': 'warn', 'FLAG': 'crit'}
def n(x, nd=0):
    try: return f"{float(x):,.{nd}f}"
    except Exception: return '—'
def tile(k, v, unit, t): return f'<div class="tile"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}<small>{html.escape(unit)}</small></div><div class="t">{html.escape(t)}</div></div>'
tiles = []; rows = []
om = w.get('oil_max'); tiles.append(tile('Oil, hottest', n(om), '°C', 'fine, worry starts at 130' if om is not None and om < 130 else 'too hot'))
am = w.get('atf_max'); tiles.append(tile('Transmission fluid, hottest', n(am), '°C', 'fine, worry starts at 110' if am is not None and am < 110 else 'too hot'))
a6, a6p = mf.get('all6'), mfp.get('all6')
if a6 is not None:
    r = (a6 / a6p) if a6p else None
    verdict = 'about the same as last week' if r and 0.8 <= r <= 1.25 else ('up on last week' if r and r > 1.25 else 'down on last week')
    tiles.append(tile('Misfires per 10,000 firings', n(a6, 1), f'last week {n(a6p,1)}', verdict))
cb, b = w.get('cold_boost_s'), w.get('boost_s')
if cb is not None and b:
    pct = 100 * cb / b; tiles.append(tile('Boost on cold oil', f'{pct:.0f}', '%', 'fine, under 25%' if pct <= 25 else 'go easier until the oil is warm'))
kn = w.get('knock_min'); tiles.append(tile('Deepest knock correction', n(kn, 1), '°', 'fine, worry at −6 and beyond' if kn is not None and kn > -6 else 'a lot of timing pulled'))
tiles.append(tile('Driving', str(w.get('trips', '—')), 'trips', f"{n(w.get('km'))} km · {n(w.get('engine_h'),1)} engine hours · {w.get('cold_starts','—')} cold starts"))
# per-cylinder chart: ratio to sibling median, 1.0 reference, one direct label on the max bar
ratio = mf.get('ratio') or []; chart = ''
if ratio:
    W, H, L, R, T, B = 640, 220, 44, 16, 18, 36; pw, ph = W - L - R, H - T - B
    top = max(2.5, max(ratio) * 1.15); gap = 14; bw = (pw - gap * (len(ratio) - 1)) / len(ratio)
    y = lambda v: T + ph - ph * v / top
    worst = max(range(len(ratio)), key=lambda i: ratio[i]); bars = []
    for i, v in enumerate(ratio):
        x = L + i * (bw + gap); h = ph * v / top
        col = 'var(--crit)' if v >= 1.5 else ('var(--warn)' if v >= 1.25 else 'var(--fg-2)')
        bars.append(f'<path d="M{x:.1f},{T+ph:.1f} V{y(v)+4:.1f} a4,4 0 0 1 4,-4 H{x+bw-4:.1f} a4,4 0 0 1 4,4 V{T+ph:.1f} Z" fill="{col}"><title>cylinder {i+1}: {v:.2f}× the median of its five siblings</title></path>')
        bars.append(f'<text x="{x+bw/2:.1f}" y="{T+ph+18}" text-anchor="middle">cyl {i+1}</text>')
        if i == worst: bars.append(f'<text x="{x+bw/2:.1f}" y="{y(v)-7:.1f}" text-anchor="middle" class="lbl">{v:.1f}×</text>')
    ticks = ''.join(f'<line x1="{L}" x2="{L+pw}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="var(--line)"/><text x="{L-8}" y="{y(t)+4:.1f}" text-anchor="end">{t:g}×</text>' for t in (0.5, 1, 1.5, 2) if t < top)
    chart = f'''<figure><svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="Misfire rate per cylinder this week, as a multiple of the median of the other five cylinders">
{ticks}<line x1="{L}" x2="{L+pw}" y1="{y(1):.1f}" y2="{y(1):.1f}" stroke="var(--accent)" stroke-dasharray="4 4"/><text x="{L+6}" y="{y(1)-7:.1f}" text-anchor="start" fill="var(--accent)">siblings' median = 1×</text>
{''.join(bars)}<line x1="{L}" x2="{L+pw}" y1="{T+ph}" y2="{T+ph}" stroke="var(--line-2)"/></svg>
<figcaption>Each cylinder's warm misfire rate this week as a multiple of the median of the other five. Amber from 1.25×, red from 1.5×. Hover a bar for the exact figure.</figcaption></figure>'''
findings = d.get('findings', [])
f_html = ''.join(f'<li><span class="chip {CLS.get(f.get("sev",""),"")}">{html.escape(f.get("sev",""))}</span><div>{html.escape(f.get("text",""))}' + (f'<em><b>do</b>{html.escape(f["action"])}</em>' if f.get('action') else '') + '</div></li>' for f in findings) or '<li><span class="chip ok">OK</span><div>Nothing unusual this week.</div></li>'
win = d.get('window', ['', '']); gen = (d.get('generated') or '')[:10]
body = f'''title: SQ5 weekly health
description: A one-page, plain-language weekly health card for Amir Khademi's Audi SQ5, generated from the car's own data logger.
path: /sq/health.html
nav: /sq/
---
<main class="wrap">
<section class="hero"><div class="eyebrow">SQ5 · week of {html.escape(win[0])} to {html.escape(win[1])} · generated {html.escape(gen)}</div><h1>Weekly health</h1>
<p class="lede">What the car's own logger says about the last seven days, in the words I'd want to read on a Sunday evening. Verdict first, then what to do, then the evidence with its threshold.</p></section>
<div class="verdict {CLS.get(status,'ok')}"><div class="word">{WORD.get(status, status)}</div><div class="muted" style="align-self:center">{len(findings)} finding{'s' if len(findings)!=1 else ''} this week</div><ul>{f_html}</ul></div>
<h2>The week in numbers, each with its line</h2>
<div class="tiles">{''.join(tiles)}</div>
<h2>Which cylinder</h2>
{chart}
<h2>How this is made</h2>
<p>A Raspberry Pi in the footwell logs 53 engine-computer channels five times a second on every drive and pushes the data home. A Sunday job compares the week to the week before and to a four-week baseline. The verdict rules are written down: oil over 130 °C or transmission fluid over 110 °C flags; a crank below 9.6 V flags; misfires at 1.5× the baseline flag and 1.25× is a watch; any Pi boot storm is a watch. Nothing here is a guess, and nothing here is live: this is a static snapshot by design. More in <a href="/sq/">the garage</a>.</p>
</main>
'''
os.makedirs(os.path.join(site, 'src', 'pages'), exist_ok=True); os.makedirs(os.path.join(site, 'sq'), exist_ok=True)
open(os.path.join(site, 'src', 'pages', 'sq-health.html'), 'w').write(body)
json.dump({'status': status, 'window': win, 'generated': gen, 'findings': findings}, open(os.path.join(site, 'sq', 'health.json'), 'w'), indent=1)
print('health card source:', status, win, len(findings), 'findings')
