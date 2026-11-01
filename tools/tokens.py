#!/usr/bin/env python3
"""Count Claude Code tokens across every transcript on this Mac (the hourly archive + the live store) -> data/tokens.json.
Dedupes by assistant message id (streaming writes one line per content block with the same usage).
Attributes a session's tokens to the ~/Projects/<name> dirs it touched, split evenly."""
import json, glob, os, re, collections, sys, datetime
from zoneinfo import ZoneInfo
from public_data import PUBLIC_PROJECTS, public_tokens
roots = [os.path.expanduser('~/claude-archive/raw'), os.path.expanduser('~/.claude/projects')]  # archive first (July 2026 on), then live
files = [f for r in roots for f in glob.glob(r + '/**/*.jsonl', recursive=True) if '/tool-results/' not in f]
tot = collections.Counter(); seen = set(); msgs = 0; first = last = None
per_proj = collections.Counter(); sess_count = 0; per_month = collections.Counter(); per_day = collections.Counter()
TZ = ZoneInfo('America/Toronto'); GAP = 30 * 60; longest = 0  # a 'task' = a stretch of one session with no gap over 30 min
def local(ts): return datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(TZ)
KEYS = ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')
PROJ = re.compile(rb'Projects/([A-Za-z0-9_.-]{2,40})')
for f in files:
    sess_tok = 0; projs = set(); any_usage = False; stamps = []
    try:
        with open(f, 'rb') as fh:
            for line in fh:
                for p in PROJ.findall(line): projs.add(p.decode())
                if b'"usage"' not in line: continue
                try: o = json.loads(line)
                except Exception: continue
                m = o.get('message') or {}
                u = m.get('usage') if isinstance(m, dict) else None
                if not u: continue
                ts = o.get('timestamp')
                if ts: first = ts if first is None or ts < first else first; last = ts if last is None or ts > last else last
                mid = m.get('id') or o.get('uuid')
                if mid in seen: continue
                seen.add(mid); msgs += 1; any_usage = True
                lt = local(ts) if ts else None
                if lt: stamps.append(lt.timestamp())
                for k in KEYS:
                    v = u.get(k) or 0; tot[k] += v; sess_tok += v
                    if lt: per_month[lt.strftime('%Y-%m')] += v; per_day[lt.strftime('%Y-%m-%d')] += v
    except Exception as e:
        print('skip', f, e, file=sys.stderr); continue
    if any_usage: sess_count += 1
    stamps.sort(); start = prev = stamps[0] if stamps else 0
    for t in stamps:
        if t - prev > GAP: start = t
        longest = max(longest, t - start); prev = t
    projs.discard('ahk02x-site')
    for p in projs: per_proj[p] += sess_tok / len(projs)
total = sum(tot.values())
out = {'total_tokens': total, 'by_kind': dict(tot), 'assistant_messages': msgs, 'sessions': sess_count,
       'first': first[:7] if first else None, 'last': last[:7] if last else None, 'files': len(files),
       'top_projects': [{'project': p, 'tokens': int(t)} for p, t in per_proj.most_common() if p in PUBLIC_PROJECTS],
       'by_month': [{'month': m, 'tokens': int(v)} for m, v in sorted(per_month.items())],
       'by_day': [{'day': d, 'tokens': int(v)} for d, v in sorted(per_day.items())], 'longest_task_min': int(longest // 60)}
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
out = public_tokens(out)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'data', 'tokens.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('total_tokens', 'sessions', 'assistant_messages', 'first', 'last')}))
print('top:', [(d['project'], round(d['tokens'] / 1e9, 2)) for d in out['top_projects'][:12]])

