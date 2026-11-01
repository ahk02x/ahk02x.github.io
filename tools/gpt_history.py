#!/usr/bin/env python3
"""ChatGPT web history (2023 on) from the exports archived in ~/codex-archive/raw -> data/gpt_history.json.
Estimate: chars/4 + attachment tokens; every model step counts the conversation so far (as API context), on the reply's Toronto day.
Only totals and per-day counts are written, never text or titles."""
import collections, datetime, glob, json, os
from zoneinfo import ZoneInfo

TZ = ZoneInfo('America/Toronto')
convs = {}
for f in sorted(glob.glob(os.path.expanduser('~/codex-archive/raw/*/conversations*.json'))):
    for c in json.load(open(f)):
        if c.get('id') not in convs or (c.get('update_time') or 0) >= (convs[c['id']].get('update_time') or 0): convs[c['id']] = c


def branch(c):
    m, n, out = c.get('mapping') or {}, c.get('current_node'), []
    while n in m:
        msg = m[n].get('message')
        if msg: out.append(msg)
        n = m[n].get('parent')
    return out[::-1]


by_day = collections.Counter()
for c in convs.values():
    ctx = 0
    for msg in branch(c):
        co = msg.get('content') or {}
        ctx += sum(len(p) for p in co.get('parts') or [] if isinstance(p, str)) // 4
        ctx += sum(len(x.get('content', '')) for x in co.get('thoughts') or [] if isinstance(x, dict)) // 4
        ctx += sum(a.get('file_token_size') or a.get('fileTokenSize') or 0 for a in (msg.get('metadata') or {}).get('attachments') or [])
        t = msg.get('create_time') or c.get('create_time')
        if (msg.get('author') or {}).get('role') == 'assistant' and t:  # every model step re-reads the context, like Claude's count
            by_day[datetime.datetime.fromtimestamp(t, TZ).date().isoformat()] += ctx
days = sorted(d for d, v in by_day.items() if v)
out = {'tokens': sum(by_day.values()), 'since': days[0][:4], 'first': days[0], 'until': days[-1], 'conversations': len(convs),
       'method': 'ChatGPT data exports archived in ~/codex-archive: text, reasoning summaries and attachments (chars/4 + file_token_size); every model step (replies, tool calls) '
                 'counts the conversation so far, the way Claude Code transcripts count context re-reads. Estimate; refreshed by tools/gpt_history.py.',
       'by_day': dict(sorted(by_day.items()))}
json.dump(out, open('data/gpt_history.json', 'w'), indent=1)
print(f"gpt web: {out['tokens']:,} est tokens, {len(convs)} conversations, {out['first']}..{out['until']}")
