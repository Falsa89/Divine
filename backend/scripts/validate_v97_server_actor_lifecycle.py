#!/usr/bin/env python3
"""v97 — Validator: Server actor lifecycle policy."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_server_actor_lifecycle_policy_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
cr = d.get('core_rules') or {}
for k in ('is_bot_internal_flag','synthetic_server_actor_flag','created_by_system','admin_distinguishable'):
    if not cr.get(k): print(f'FAIL — core_rules.{k}'); sys.exit(1)
for k in ('no_real_iap','no_real_pii'):
    if not cr.get(k): print(f'FAIL — core_rules.{k}'); sys.exit(1)
start = d.get('start_state') or {}
if start.get('account_level') != 1: print('FAIL — start account_level != 1'); sys.exit(1)
if not start.get('day_one_high_level_forbidden'): print('FAIL — day_one_high_level_forbidden'); sys.exit(1)
prog = d.get('progression_rules') or {}
if not prog.get('server_age_based'): print('FAIL — server_age_based missing'); sys.exit(1)
if not prog.get('player_average_adaptation', {}).get('enabled'): print('FAIL — player_average_adaptation disabled'); sys.exit(1)
ea = d.get('event_access') or {}
for k in ('respect_level_unlock','respect_event_unlock','respect_guild_membership','respect_guild_requirements','no_bypass'):
    if not ea.get(k): print(f'FAIL — event_access.{k}'); sys.exit(1)
for f in ('day_one_level_100_bots','random_runtime_generation','ranking_domination','premium_reward_theft','economy_exploit','real_iap','real_pii','event_access_bypass'):
    if f not in (d.get('forbidden') or []): print(f'FAIL — forbidden missing: {f}'); sys.exit(1)
print('PASS — v97 server actor lifecycle policy')
sys.exit(0)
