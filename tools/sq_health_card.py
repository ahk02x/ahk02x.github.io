#!/usr/bin/env python3
"""Render the SQ5's weekly health card for the public site from sq_weekly.py --json (stdin).
Writes sq/health.html and sq/health.json. Week granularity only: no dates, no places, no hostnames."""
import json, sys, os, html, datetime
d = json.load(sys.stdin)
site = os.path.join(os.path.dirname(__file__), '..')
w, p, mf, mfp = d.get('week', {}), d.get('prior', {}), d.get('misfire', {}), d.get('misfire_prior', {})
status = d.get('status', 'OK')
WORD = {'OK': 'Healthy', 'WATCH': 'Keep an eye on it', 'FLAG': 'Needs attention'}
COLOR = {'OK': '#2e7d32', 'WATCH': '#b26a00', 'FLAG': '#c62828'}
def n(x, nd=0):
    try: return f"{float(x):,.{nd}f}"
    except Exception: return '—'
def line(label, value, verdict):
    return f'<tr><td>{html.escape(label)}</td><td>{html.escape(value)}</td><td class="v">{html.escape(verdict)}</td></tr>'
rows = []
om = w.get('oil_max');  rows.append(line('Hottest the oil got', f"{n(om)} °C", 'fine (worry starts at 130)' if om is not None and om < 130 else 'too hot'))
am = w.get('atf_max');  rows.append(line('Hottest the transmission fluid got', f"{n(am)} °C", 'fine (worry starts at 110)' if am is not None and am < 110 else 'too hot'))
a6, a6p = mf.get('all6'), mfp.get('all6')
if a6 is not None:
    ratio = (a6 / a6p) if a6p else None
    verdict = 'about the same as last week' if ratio and 0.8 <= ratio <= 1.25 else ('up on last week' if ratio and ratio > 1.25 else ('down on last week' if ratio else ''))
    rows.append(line('Misfires per 10,000 firings (all six cylinders)', f"{n(a6,1)} (last week {n(a6p,1)})", verdict))
    r = mf.get('ratio') or []
    if r:
        worst = max(range(len(r)), key=lambda i: r[i])
        rows.append(line('Cylinder standing out', f"cylinder {worst+1} at {n(r[worst],1)}× its siblings", 'the long-running one; plugs helped, cause still open' if r[worst] >= 1.5 else 'nothing stands out'))
cb, b = w.get('cold_boost_s'), w.get('boost_s')
if cb is not None and b:
    pct = 100 * cb / b
    rows.append(line('Boost used before the oil was warm', f"{pct:.0f}% of boost time", 'fine (under 25%)' if pct <= 25 else 'go easier until the oil is warm'))
kn = w.get('knock_min');  rows.append(line('Deepest knock correction', f"{n(kn,1)}°", 'fine (worry at −6 and beyond)' if kn is not None and kn > -6 else 'the ECU is pulling a lot of timing'))
rows.append(line('Driving this week', f"{w.get('trips','—')} trips, {n(w.get('km'))} km, {n(w.get('engine_h'),1)} engine hours", f"{w.get('cold_starts','—')} cold starts, {w.get('short_trips','—')} short trips"))
findings = d.get('findings', [])
f_html = ''.join(f'<li><span class="sev {html.escape(f.get("sev","").lower())}">{html.escape(f.get("sev",""))}</span> {html.escape(f.get("text",""))}' + (f' <em>Do: {html.escape(f["action"])}</em>' if f.get('action') else '') + '</li>' for f in findings) or '<li>Nothing unusual this week.</li>'
win = d.get('window', ['', ''])
gen = (d.get('generated') or '')[:10]
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SQ5 weekly health — Amir Khademi</title>
<meta name="description" content="A one-page, plain-language weekly health card for Amir Khademi's Audi SQ5, generated from the car's own data logger.">
<link rel="canonical" href="https://ahk02x.dev/sq/health.html"><link rel="stylesheet" href="/style.css">
<style>.card{{border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:18px 0}}.status{{font-size:1.6rem;font-weight:700;color:{COLOR.get(status,'#444')}}}
table{{width:100%;border-collapse:collapse;font-size:.95em}}td{{padding:8px 6px;border-top:1px solid var(--line);vertical-align:top}}td.v{{color:var(--muted)}}
.sev{{font-size:.75em;font-weight:700;padding:1px 6px;border-radius:4px;color:#fff;background:#777;margin-right:6px}}.sev.flag{{background:#c62828}}.sev.watch{{background:#b26a00}}li em{{color:var(--muted)}}</style></head>
<body><header><nav><a href="/">Home</a><a href="/projects/">Projects</a><a href="/sq/">SQ5 garage</a><a href="/writing/">Writing</a><a href="/about.html">About</a></nav>
<h1>SQ5 weekly health</h1><p class="muted">Week of {html.escape(win[0])} to {html.escape(win[1])} · generated {html.escape(gen)} by the car's own logger</p></header>
<main>
<div class="card"><div class="status">{WORD.get(status, status)}</div>
<ul>{f_html}</ul></div>
<h2>The week in plain words</h2>
<table>{''.join(rows)}</table>
<p class="muted">How this is made: a Raspberry Pi in the footwell logs 53 engine-computer channels five times a second on every drive, pushes the data home, and a Sunday job compares the week to the week before and to a four-week baseline. The verdict rules are written down; nothing here is a guess. This page is a static snapshot, not a live feed, on purpose. More in <a href="/sq/">the garage</a>.</p>
</main><footer>Amir Khademi · Toronto, Canada</footer></body></html>'''
open(os.path.join(site, 'sq', 'health.html'), 'w').write(page)
json.dump({'status': status, 'window': win, 'generated': gen, 'findings': findings, 'rows': len(rows)}, open(os.path.join(site, 'sq', 'health.json'), 'w'), indent=1)
print('health card:', status, win, len(findings), 'findings', len(rows), 'rows')
