"""Refresh data/local_tokens.json: the "others" figure, tokens from open models on my own GPUs.

Two sources, kept separately under "sources" and summed into the top-level totals:
  lab   the Crucix lab and other jobs on the home server's GPU, read once from the model server's
        log (2026-11-02). Fixed: nothing updates it automatically.
  chat  my private chat app on the 3080. Its own usage ledger records the model server's reported
        counters per request (no estimates). A backup job on the Mac checks each export snapshot
        against its manifest and stages the counts at CHAT_TOTALS. This script only reads that file.

Counts only: no text, model names, request times or hosts reach this repo, and dates stay at day level.
A missing or unreadable staged file keeps the committed numbers. Counters only ever grow, so a staged
total lower than the committed one is refused as a sign the wrong ledger was read.
"""
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'local_tokens.json'
CHAT_TOTALS = Path(os.environ.get('LOCAL_CHAT_TOTALS', Path.home() / '.local/share/3080-chat/usage-totals.json'))
KEYS = ('input_tokens', 'output_tokens', 'total_tokens', 'requests')


def load(path=None):
    data = json.loads((path or OUT).read_text())
    if 'sources' not in data:   # the original hand-written file: all of it is the lab figure
        data = {'sources': {'lab': {**{k: data[k] for k in KEYS},
                                    'note': data.get('source', ''), 'updated': data.get('updated', '')}}}
    return data


def read_chat(path=None):
    """The staged counts as a source entry, or None with a reason."""
    path = path or CHAT_TOTALS
    try:
        s = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return None, f'no staged chat totals at {path} ({type(e).__name__})'
    try:
        i, o, r = int(s['input_tokens']), int(s['output_tokens']), int(s['requests'])
        day = datetime.date.fromisoformat(str(s['date'])[:10]).isoformat()  # a real calendar day, never '2026-99-99'
    except (KeyError, TypeError, ValueError) as e:
        return None, f'staged chat totals malformed ({type(e).__name__})'
    if min(i, o, r) < 0 or len(day) != 10:
        return None, 'staged chat totals out of range'
    return {'input_tokens': i, 'output_tokens': o, 'total_tokens': i + o, 'requests': r,
            'note': "private chat app on the 3080; the model server's reported counters, from the app's own usage ledger",
            'updated': day}, None


def merge(data, chat):
    """New data dict with `chat` applied, or (data, reason) unchanged when it would move a counter backwards."""
    old = data['sources'].get('chat')
    if old and any(chat[k] < old[k] for k in ('input_tokens', 'output_tokens', 'requests')):
        return data, f"staged chat totals ({chat['total_tokens']:,}) are below the committed ones ({old['total_tokens']:,}); keeping the committed numbers"
    sources = dict(data['sources'], chat=chat)
    out = {k: sum(s[k] for s in sources.values()) for k in KEYS}
    out['source'] = "Open models on my own GPUs, by source below; tokens are the model server's reported input + output."
    out['updated'] = max(s['updated'] for s in sources.values())
    out['sources'] = sources
    return out, None


def main():
    data = load()
    chat, why = read_chat()
    if chat is None:
        print(f'local_tokens: {why}; keeping the committed numbers', file=sys.stderr)
        return 0
    new, why = merge(data, chat)
    if why:
        print(f'local_tokens: {why}', file=sys.stderr)
        return 0
    if new != json.loads(OUT.read_text()):
        OUT.write_text(json.dumps(new, indent=1) + '\n')
    print(json.dumps({k: new[k] for k in ('total_tokens', 'requests', 'updated')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
