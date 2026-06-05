#!/usr/bin/env python3
"""v106 — Bot/server actor migration policy validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_bot_server_actor_migration_policy_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if len(d.get('approved_archetypes') or []) < 5: print('FAIL \u2014 archetypes < 5'); sys.exit(1)
inv = d.get('per_bot_invariants') or {}
if inv.get('start_level') != 1: print('FAIL \u2014 start_level must be 1'); sys.exit(1)
for k in ('credible_progression','roster_non_empty','team_valid','event_access_same_requirements_as_players'):
    if not inv.get(k, False): print(f'FAIL \u2014 invariant.{k} must be true'); sys.exit(1)
for k in ('no_day_one_level_100','no_ranking_top_domination','no_premium_reward_theft'):
    if not inv.get(k, False): print(f'FAIL \u2014 invariant.{k} must be true'); sys.exit(1)
for k in ('premium_currency_granted_to_bot','random_starter_heroes','legacy_heroes_in_starter'):
    if inv.get(k, True): print(f'FAIL \u2014 invariant.{k} must be false'); sys.exit(1)
if (inv.get('roster_min_size') or 0) < 3: print('FAIL \u2014 roster_min_size < 3'); sys.exit(1)
forb = set(d.get('forbidden_during_migration') or [])
for k in ('empty_bot_roster','legacy_hero_id_in_bot_roster','premium_currency_grant','random_hero_assignment'):
    if k not in forb: print(f'FAIL \u2014 forbidden_during_migration missing {k}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('premium_currency_grant','random_starter_heroes','legacy_heroes','empty_roster','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v106 bot/server actor migration policy (5 archetypes, invariants enforced)')
sys.exit(0)
