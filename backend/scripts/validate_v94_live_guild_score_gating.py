#!/usr/bin/env python3
"""v94 — Live/guild score gating validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = os.path.join(ROOT, 'data', 'design', 'live_guild_runtime', 'v94_live_guild_score_gating_contract_v1.json')
D = os.path.join(ROOT, 'docs', 'divine', '94_LIVE_GUILD_SCORE_GATING_AND_DRY_RUN.md')
REQ_SYS = {'guild_war_score', 'guild_raid_contribution', 'server_boss_contribution',
           'faction_boss_contribution', 'territory_front_score',
           'live_event_kill_score', 'live_event_kill_streak_score', 'global_ranking_update'}

def fail(m): print(f"FAIL v94_live_guild_score_gating: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(C): fail(f"missing: {C}")
    if not os.path.isfile(D): fail(f"missing doc: {D}")
    with open(C) as f: c = json.load(f)
    if c.get('dry_run_only') is not True: fail("dry_run_only must be true")
    if c.get('score_live') is not False: fail("score_live must be false")
    if c.get('ranking_live') is not False: fail("ranking_live must be false")
    if c.get('guild_score_mutation') != 0: fail("guild_score_mutation must be 0")
    if c.get('event_currency_live') is not False: fail("event_currency_live must be false")
    if c.get('canary_flag_state_in_v94') != 'DISABLED': fail("canary_flag_state_in_v94 must be DISABLED")
    systems = {x.get('system') for x in c.get('gated_systems') or []}
    miss = REQ_SYS - systems
    if miss: fail(f"missing gated systems: {sorted(miss)}")
    for s in c.get('gated_systems') or []:
        if s.get('dry_run_only') is not True: fail(f"{s.get('system')}.dry_run_only must be true")
        if s.get('canary_enabled') is not False: fail(f"{s.get('system')}.canary_enabled must be false")
        if s.get('db_writes') != 0: fail(f"{s.get('system')}.db_writes must be 0")
    print("PASS v94_live_guild_score_gating")

if __name__ == '__main__': main()
