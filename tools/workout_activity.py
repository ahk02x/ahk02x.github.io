#!/usr/bin/env python3
"""Gym days from ~/Projects/workout/sets.csv -> data/workout.json. Day set-counts only: no exercises, weights or reps."""
import collections, csv, json, os
days = collections.Counter(r['date'] for r in csv.DictReader(open(os.path.expanduser('~/Projects/workout/sets.csv'))) if r.get('date'))
json.dump({'sessions': len(days), 'sets': sum(days.values()), 'by_day': dict(sorted(days.items()))}, open('data/workout.json', 'w'), indent=1)
print(f"workout: {len(days)} sessions, {sum(days.values())} sets")
