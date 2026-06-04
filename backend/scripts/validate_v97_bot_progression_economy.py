#!/usr/bin/env python3
"""v97 — Validator: Bot progression/economy simulation."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_bot_progression_economy_simulation_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
sim = d.get('simulated_activities') or {}
for k in ('daily_login','exp_account_progress','roster_growth','pull_banner_history','reward_accumulation_controlled','team_upgrades','guild_faction_participation_if_unlocked','event_progress_if_eligible'):
    if not sim.get(k): print(f'FAIL — simulated_activities.{k}'); sys.exit(1)
forb = d.get('forbidden') or []
for f in ('real_iap','economy_exploit','tradeable_inventory','reward_claims_impacting_real_economy','premium_currency_inflation','hidden_advantage_over_players'):
    if f not in forb: print(f'FAIL — forbidden missing: {f}'); sys.exit(1)
econ = d.get('economy_isolation') or {}
if not econ.get('bot_iap_simulated_no_real_charge'): print('FAIL — bot_iap_simulated_no_real_charge'); sys.exit(1)
team = d.get('team_upgrade_policy') or {}
if not team.get('no_max_gear_at_day_one'): print('FAIL — no_max_gear_at_day_one'); sys.exit(1)
print('PASS — v97 bot progression/economy simulation')
sys.exit(0)
