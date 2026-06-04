#!/usr/bin/env python3
"""v94 — Reward/score dry-run validator (verifies simulator output)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(ROOT, 'data', 'design', 'reward_runtime', 'v94_reward_score_dry_run_result_v1.json')
REQ_CASES = {'story_victory_reward', 'tower_floor_reward', 'arena_win_loss_mmr',
             'raid_boss_contribution', 'guild_war_score', 'event_currency',
             'duplicate_claim_replay', 'malformed_claim', 'over_cap_claim', 'unauthorized_claim'}

def fail(m): print(f"FAIL v94_reward_score_dry_run: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(R): fail(f"missing simulator result: {R} (run simulator first)")
    with open(R) as f: d = json.load(f)
    if d.get('live_grant_emitted') is True: fail("live_grant_emitted must be false")
    if d.get('db_writes_total', 0) != 0: fail("db_writes_total must be 0")
    if d.get('dry_run_only') is not True: fail("dry_run_only must be true")
    cases = {c.get('case') for c in d.get('cases') or []}
    miss = REQ_CASES - cases
    if miss: fail(f"missing cases: {sorted(miss)}")
    # at least the 4 protective rejects must reject
    rejects = {c.get('case') for c in d.get('cases') or [] if c.get('result', {}).get('status') == 'REJECT'}
    for must_reject in ('duplicate_claim_replay', 'malformed_claim', 'over_cap_claim', 'unauthorized_claim'):
        if must_reject not in rejects: fail(f"{must_reject} must REJECT")
    saf = d.get('safety') or {}
    if saf.get('reward_live') is not False: fail("safety.reward_live must be false")
    print("PASS v94_reward_score_dry_run")

if __name__ == '__main__': main()
