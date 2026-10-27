"""The only project identifiers allowed in the public token export."""
PUBLIC_PROJECTS = frozenset({
    'sq-garage', 'Sq', 'iot', 'flowtrace', 'phosphor', 'Crucix', 'alertboard',
    'macwatch', 'netdash', 'partswatch', 'fleet-patch', 'lanwatch', 'inbox',
    'jackal-protocol-re',
})

def public_tokens(data):
    """Preserve totals, allowlist project names, and reduce dates to months."""
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
    return result
