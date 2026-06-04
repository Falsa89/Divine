#!/usr/bin/env python3
"""v95 — Validator: Live/Guild Runtime Gating."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'live_guild_runtime', 'v95_live_guild_runtime_gating_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
gates = d.get('gates') or {}
for k in ('guild_score', 'live_boss_score', 'faction_boss_score', 'territory_score',
         'live_event_kill_score', 'live_event_streak_score'):
    if gates.get(k) != 'gated':
        print(f'FAIL — gate {k} != gated:', gates.get(k)); sys.exit(1)
for k in ('global_ranking_update', 'arena_mmr'):
    if gates.get(k) != 'blocked':
        print(f'FAIL — gate {k} != blocked:', gates.get(k)); sys.exit(1)
if d.get('qa_time_override_in_production', True):
    print('FAIL — qa_time_override_in_production'); sys.exit(1)
safety = d.get('safety') or {}
if safety.get('db_writes') != 0:
    print('FAIL — safety.db_writes != 0'); sys.exit(1)
print('PASS — v95 live/guild runtime gating')
sys.exit(0)
