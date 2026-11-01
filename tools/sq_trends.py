#!/usr/bin/env python3
"""Weekly SQ5 trends for /sq/trends.html, from sq-dash's /api/drives (LAN) or a saved copy of it.
Writes data/sq_trends.json. Week granularity only: the site is public under his name, so no trip
dates or times leave the LAN, just per-week peaks and rates (same rule as sq_health_card.py).

  python3 tools/sq_trends.py                       # fetch http://sq.netwatch:8766/api/drives
  python3 tools/sq_trends.py --file drives.json    # offline
"""
import argparse, json, os, datetime, urllib.request
MIN_RATE_H = 1 / 60          # a week needs a minute of misfire-logged running before it gets a rate (sq-dash MIN_TREND_MS)

ap = argparse.ArgumentParser()
ap.add_argument('--url', default='http://sq.netwatch:8766/api/drives')
ap.add_argument('--file')
a = ap.parse_args()
raw = json.load(open(a.file)) if a.file else json.load(urllib.request.urlopen(a.url, timeout=15))
caps = [c for c in raw['drives'] if c.get('when')]

def monday(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return d - datetime.timedelta(days=d.weekday())

weeks = {}
for c in caps:
    w = weeks.setdefault(monday(c['when']), {'captures': 0, 'ms': 0, 'mis': 0.0, 'mis_ms': 0,
                                            'knock_ev': 0, 'knock_n': 0, 'oil': None, 'boost': None, 'rpm': None})
    w['captures'] += 1
    w['ms'] += c.get('duration_ms') or 0
    if c.get('has_misfire'):
        w['mis'] += c.get('misfires') or 0
        w['mis_ms'] += c.get('duration_ms') or 0
    if c.get('has_knock'):
        w['knock_ev'] += c.get('knock_events') or 0
        w['knock_n'] += c.get('samples') or 0
    for k, src in (('oil', 'oil_max'), ('boost', 'boost_psi'), ('rpm', 'rpm_max')):
        v = c.get(src)
        if v is not None: w[k] = v if w[k] is None else max(w[k], v)

def r(x, nd=1): return None if x is None else round(x, nd)
out, d = [], min(weeks)
while d <= max(weeks):     # empty weeks stay in as nulls so time off the road reads as a gap
    w = weeks.get(d)
    if w is None:
        out.append({'week': d.isoformat(), 'hours': 0, 'captures': 0})
    else:
        mh = w['mis_ms'] / 3.6e6
        out.append({'week': d.isoformat(), 'hours': r(w['ms'] / 3.6e6, 2), 'captures': w['captures'],
                    'misfire_hr': r(w['mis'] / mh) if mh >= MIN_RATE_H else None,
                    'knock_pct': r(100 * w['knock_ev'] / w['knock_n'], 2) if w['knock_n'] else None,
                    'oil_max': r(w['oil']), 'boost_psi': r(w['boost']), 'rpm_max': r(w['rpm'], 0)})
    d += datetime.timedelta(days=7)

peak = lambda k: max((x[k] for x in out if x.get(k) is not None), default=None)
doc = {'through_week': out[-1]['week'],
       'totals': {'hours': r(sum(x['hours'] for x in out)), 'captures': sum(x['captures'] for x in out),
                  'boost_psi': peak('boost_psi'), 'rpm_max': peak('rpm_max'), 'oil_max': peak('oil_max')},
       'weeks': out}
dest = os.path.join(os.path.dirname(__file__), '..', 'data', 'sq_trends.json')
json.dump(doc, open(dest, 'w'), separators=(',', ':'))
print(f"wrote {len(out)} weeks through {doc['through_week']}: {doc['totals']}")
