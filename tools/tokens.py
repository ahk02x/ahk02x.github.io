#!/usr/bin/env python3
"""Count Claude Code tokens across every transcript on this Mac (the hourly archive + the live store) -> data/tokens.json.
Dedupes by assistant message id (streaming writes one line per content block with the same usage).
Attributes a session's tokens to the ~/Projects/<name> dirs it touched, split evenly."""
import json, glob, os, re, collections, sys
roots = [os.path.expanduser('~/claude-archive/raw'), os.path.expanduser('~/.claude/projects')]  # archive first (July 2026 on), then live
files = [f for r in roots for f in glob.glob(r + '/**/*.jsonl', recursive=True) if '/tool-results/' not in f]
tot = collections.Counter(); seen = set(); msgs = 0; first = last = None
per_proj = collections.Counter(); sess_count = 0
KEYS = ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')
PROJ = re.compile(rb'Projects/([A-Za-z0-9_.-]{2,40})')
for f in files:
    sess_tok = 0; projs = set(); any_usage = False
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
                for k in KEYS:
                    v = u.get(k) or 0; tot[k] += v; sess_tok += v
    except Exception as e:
        print('skip', f, e, file=sys.stderr); continue
    if any_usage: sess_count += 1
    projs.discard('ahk02x-site')
    for p in projs: per_proj[p] += sess_tok / len(projs)
total = sum(tot.values())
out = {'total_tokens': total, 'by_kind': dict(tot), 'assistant_messages': msgs, 'sessions': sess_count,
       'first': first, 'last': last, 'files': len(files),
       'top_projects': [{'project': p, 'tokens': int(t)} for p, t in per_proj.most_common(25)]}
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'data', 'tokens.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('total_tokens', 'sessions', 'assistant_messages', 'first', 'last')}))
print('top:', [(d['project'], round(d['tokens'] / 1e9, 2)) for d in out['top_projects'][:12]])
