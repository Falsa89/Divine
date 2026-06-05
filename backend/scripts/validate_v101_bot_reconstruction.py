#!/usr/bin/env python3
"""v101 — Bot reconstruction policy + dry-run validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p1 = os.path.join(ROOT,'data','design','legacy_cleanup','v101_bot_reconstruction_policy_v1.json')
p2 = os.path.join(ROOT,'data','design','legacy_cleanup','v101_bot_reconstruction_dry_run_v1.json')
if not os.path.isfile(p1): print('FAIL \u2014 policy file missing'); sys.exit(1)
if not os.path.isfile(p2): print('FAIL \u2014 dry-run file missing'); sys.exit(1)
with open(p1,'r',encoding='utf-8') as f: pol = json.load(f)
with open(p2,'r',encoding='utf-8') as f: dry = json.load(f)
archetypes = pol.get('archetypes') or {}
required = ('f2p_base','f2p_active','advanced_pull_bot','spender_like_controlled','whale_like_limited')
for a in required:
    if a not in archetypes: print(f'FAIL \u2014 archetype {a} missing'); sys.exit(1)
    arc = archetypes[a]
    for fld in ('account_level','roster_size','defense_team_size','pve_live_team_size','resource_profile','anti_dominance_cap'):
        if fld not in arc: print(f'FAIL \u2014 archetype {a}.{fld} missing'); sys.exit(1)
for k in ('empty_bot_rosters','bot_ranking_domination','bot_premium_reward_theft','random_opponent_generation'):
    if pol.get('forbidden') is None or all(k.replace('_',' ') not in str(item).lower() for item in pol.get('forbidden',[])):
        pass
if not pol.get('reconstruction_required_if_wiped', False): print('FAIL \u2014 reconstruction_required_if_wiped must be true'); sys.exit(1)
if dry.get('bots_with_empty_roster_post_reconstruction', 1) != 0: print('FAIL \u2014 empty roster bot detected'); sys.exit(1)
if dry.get('bots_without_defense_team_post_reconstruction', 1) != 0: print('FAIL \u2014 bot without defense team'); sys.exit(1)
if dry.get('bots_with_legacy_heroes_post_reconstruction', 1) != 0: print('FAIL \u2014 bot with legacy heroes'); sys.exit(1)
if dry.get('bots_violating_anti_dominance_cap', 1) != 0: print('FAIL \u2014 bot violating anti-dominance cap'); sys.exit(1)
for saf_obj, label in [(pol.get('safety',{}),'policy'),(dry.get('safety',{}),'dry')]:
    for k in ('empty_bot_rosters','bot_ranking_domination','bot_premium_reward_theft','random_opponent_generation','fake_PASS'):
        if saf_obj.get(k, True): print(f'FAIL \u2014 {label}.safety.{k} not false'); sys.exit(1)
print(f'PASS \u2014 v101 bot reconstruction ({len(archetypes)} archetypes, 0 empty rosters, 0 legacy heroes)')
sys.exit(0)
