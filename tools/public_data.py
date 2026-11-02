"""The only project identifiers allowed in the public token export."""
import collections
import re
PUBLIC_PROJECTS = frozenset({
    'sq-garage', 'Sq', 'iot', 'flowtrace', 'phosphor', 'alertboard',
    'macwatch', 'netdash', 'partswatch', 'fleet-patch', 'lanwatch', 'inbox',
    'obd-cable-protocol-re', 'workout', 'ahk02x-site',
})

# Dirs renamed on disk: old transcripts still name the old dir, so fold its
# tokens into the current name rather than dropping them from the public total.
RENAMED = {'jackal-protocol-re': 'obd-cable-protocol-re'}

def public_tokens(data):
    """Preserve totals, allowlist project names; dates go no finer than a day, never a time."""
    if not data:
        return {}
    keys = ('total_tokens', 'by_kind', 'assistant_messages', 'sessions', 'files')
    result = {k: data[k] for k in keys if k in data}
    for key in ('first', 'last'):
        result[key] = str(data[key])[:7] if data.get(key) else None
    merged = collections.Counter()
    for p in data.get('top_projects', []):
        name = RENAMED.get(p.get('project'), p.get('project'))
        if name in PUBLIC_PROJECTS:
            merged[name] += p['tokens']
    result['top_projects'] = [
        {'project': n, 'tokens': t} for n, t in merged.most_common()
    ]
    result['by_month'] = [
        {'month': str(m['month'])[:7], 'tokens': int(m['tokens'])}
        for m in data.get('by_month', []) if m.get('month') and re.match(r'^\d{4}-\d{2}', str(m['month']))
    ]
    result['by_day'] = [
        {'day': str(d['day'])[:10], 'tokens': int(d['tokens'])}
        for d in data.get('by_day', []) if d.get('day') and re.match(r'^\d{4}-\d{2}-\d{2}', str(d['day']))
    ]
    if isinstance(data.get('longest_task_min'), int):
        result['longest_task_min'] = data['longest_task_min']
    return result
