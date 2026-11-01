#!/usr/bin/env python3
"""Count GPT (OpenAI Codex) tokens across every Codex session on this Mac -> data/gpt_tokens.json.
Each rollout file's last token_count event carries the session's running total; sessions are deduped by file name
(the ~/bin/gpt cage keeps its own CODEX_HOME per run). Only totals and Toronto days are written, never content."""
import json, glob, os, collections, datetime, zoneinfo
TZ = zoneinfo.ZoneInfo('America/Toronto')
roots = [os.path.expanduser('~/.codex/sessions'), *glob.glob(os.path.expanduser('~/.gpt-cage/runs/*/home/sessions'))]
files = {}
for r in roots:
    for f in glob.glob(r + '/**/rollout-*.jsonl', recursive=True): files.setdefault(os.path.basename(f), f)
tot = collections.Counter(); by_day = collections.Counter(); sessions = 0; first = last = None
for f in files.values():
    usage = None; ts = None
    try:
        with open(f, 'rb') as fh:
            for line in fh:
                if b'"total_token_usage"' not in line: continue
                try: o = json.loads(line)
                except Exception: continue
                u = ((o.get('payload') or o).get('info') or {}).get('total_token_usage')
                if u: usage = u; ts = o.get('timestamp') or ts
    except OSError: continue
    if not usage: continue
    sessions += 1
    for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens'): tot[k] += usage.get(k, 0)
    day = (datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(TZ).date().isoformat() if ts
           else datetime.datetime.fromtimestamp(os.path.getmtime(f), TZ).date().isoformat())
    by_day[day] += usage.get('total_tokens', 0)
    first = min(first or day, day); last = max(last or day, day)
out = {'updated': datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M'), 'total_tokens': tot['total_tokens'], 'by_kind': dict(tot), 'sessions': sessions, 'first': first, 'last': last,
       'by_day': dict(sorted(by_day.items()))}
os.makedirs('data', exist_ok=True)
json.dump(out, open('data/gpt_tokens.json', 'w'), indent=1); open('data/gpt_tokens.json', 'a').write('\n')
print(f"gpt: {out['total_tokens']:,} tokens, {sessions} sessions, {first}..{last}")
