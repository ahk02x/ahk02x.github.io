#!/usr/bin/env python3
"""Public GitHub contribution calendar for ahk02x (via the gh CLI) -> data/github.json. Day counts only."""
import json, subprocess
q = '{viewer{contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
cal = json.loads(subprocess.run(['gh', 'api', 'graphql', '-f', f'query={q}'], capture_output=True, text=True, check=True).stdout)['data']['viewer']['contributionsCollection']['contributionCalendar']
days = {d['date']: d['contributionCount'] for w in cal['weeks'] for d in w['contributionDays'] if d['contributionCount']}
json.dump({'total': cal['totalContributions'], 'by_day': days}, open('data/github.json', 'w'), indent=1)
print(f"github: {cal['totalContributions']} contributions, {len(days)} active days")
