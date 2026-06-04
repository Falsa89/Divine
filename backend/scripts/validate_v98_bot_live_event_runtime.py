#!/usr/bin/env python3
"""v98 — Bot live event runtime participation."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','server_actors','v98_bot_live_event_runtime_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('runtime_mode')!='GATED_DRY_RUN': print('FAIL — runtime_mode'); sys.exit(1)
if d.get('core_rule')!='bot_fill_only_when_real_player_count_below_min_threshold': print('FAIL — core_rule'); sys.exit(1)
events=d.get('events_covered') or {}
for e in ('live_event','guild_war','guild_raid','server_world_boss','faction_boss','territory_front','event_avatar_mode'):
    if e not in events: print(f'FAIL — event missing: {e}'); sys.exit(1)
elig=d.get('eligibility_checks_runtime') or {}
for k in ('level_unlock','event_unlock','guild_membership_required_for_guild_events','guild_join_level_requirement'):
    if not elig.get(k): print(f'FAIL — elig.{k}'); sys.exit(1)
caps=d.get('contribution_caps') or {}
if not caps.get('top_3_leaderboard_domination_forbidden'): print('FAIL — top3 domination'); sys.exit(1)
if caps.get('premium_reward_eligibility',True): print('FAIL — premium_reward_eligibility must be false'); sys.exit(1)
print(f'PASS — v98 bot live event runtime ({len(events)} events)')
sys.exit(0)
