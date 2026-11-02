"""The only project identifiers allowed in the public token export."""
import re
PUBLIC_PROJECTS = frozenset({
    'sq-garage', 'Sq', 'iot', 'flowtrace', 'phosphor', 'alertboard',
    'macwatch', 'netdash', 'partswatch', 'fleet-patch', 'lanwatch', 'inbox',
    'jackal-protocol-re', 'workout', 'ahk02x-site',
})

def public_tokens(data):
    """Preserve totals, allowlist project names; dates go no finer than a day, never a time."""
    if not data:
        return {}
    keys = ('total_tokens', 'by_kind', 'assistant_messages', 'sessions', 'files')
    result = {k: data[k] for k in keys if k in data}
    for key in ('first', 'last'):
        result[key] = str(data[key])[:7] if data.get(key) else None
    result['top_projects'] = [
        {'project': p['project'], 'tokens': p['tokens']}
        for p in data.get('top_projects', []) if p.get('project') in PUBLIC_PROJECTS
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
