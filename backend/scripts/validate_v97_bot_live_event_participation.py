#!/usr/bin/env python3
"""v97 — Validator: Bot live event participation + low population thresholds."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p1 = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_bot_live_event_participation_policy_v1.json')
p2 = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_low_population_thresholds_v1.json')
for p in (p1,p2):
    if not os.path.isfile(p): print(f'FAIL — file missing: {p}'); sys.exit(1)
with open(p1,'r',encoding='utf-8') as f: d1 = json.load(f)
with open(p2,'r',encoding='utf-8') as f: d2 = json.load(f)
if d1.get('core_rule') != 'bot_fill_only_when_real_player_population_low': print('FAIL — core_rule'); sys.exit(1)
thr = d1.get('thresholds_by_event') or {}
for evt in ('live_events','guild_war','guild_raid','world_boss','faction_boss','territory','event_avatar_modes'):
    if evt not in thr: print(f'FAIL — threshold missing: {evt}'); sys.exit(1)
elig = d1.get('eligibility_requirements') or {}
for k in ('same_as_real_players','level_unlock','event_unlock','guild_membership_required_for_guild_events','guild_join_level_requirement'):
    if not elig.get(k): print(f'FAIL — eligibility.{k}'); sys.exit(1)
caps = d1.get('caps') or {}
for k in ('no_top_3_leaderboard_domination','bot_score_dry_run_unless_authorized'):
    if not caps.get(k): print(f'FAIL — caps.{k}'); sys.exit(1)
if caps.get('bot_premium_reward_eligibility', True): print('FAIL — caps.bot_premium_reward_eligibility must be false'); sys.exit(1)
gt = d2.get('global_thresholds') or {}
if gt.get('healthy_concurrent_threshold',0) <= gt.get('under_population_threshold',999): print('FAIL — thresholds inverted'); sys.exit(1)
ks = d2.get('admin_override_kill_switches') or []
if 'disable_all_bots' not in ks: print('FAIL — disable_all_bots kill switch'); sys.exit(1)
print(f'PASS — v97 bot live event participation ({len(thr)} events)')
sys.exit(0)
