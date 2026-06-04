#!/usr/bin/env python3
"""v94 — Reward safety contracts validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = os.path.join(ROOT, 'data', 'design', 'reward_runtime', 'v94_reward_claim_safety_contract_v1.json')
I = os.path.join(ROOT, 'data', 'design', 'reward_runtime', 'v94_reward_idempotency_and_rollback_contract_v1.json')
D = os.path.join(ROOT, 'docs', 'divine', '94_REWARD_RUNTIME_SAFETY_DRY_RUN.md')
REQ_REWARD_TYPES = {'story_reward', 'tower_reward', 'arena_reward_and_mmr', 'raid_boss_reward',
                    'guild_reward_and_score', 'event_currency', 'live_announcement_triggered'}

def fail(m): print(f"FAIL v94_reward_safety_contracts: {m}"); sys.exit(1)

def main():
    for p in (C, I, D):
        if not os.path.isfile(p): fail(f"missing: {p}")
    with open(C) as f: c = json.load(f)
    if c.get('dry_run_only') is not True: fail("dry_run_only must be true")
    if c.get('canary_design_no_apply') is not True: fail("canary_design_no_apply must be true")
    if c.get('live_grant') is not False: fail("live_grant must be false")
    rtypes = {x.get('type') for x in c.get('reward_types') or []}
    miss = REQ_REWARD_TYPES - rtypes
    if miss: fail(f"missing reward_types: {sorted(miss)}")
    for r in c.get('reward_types') or []:
        if r.get('grant_live') is not False: fail(f"{r.get('type')}.grant_live must be false")
        if r.get('idempotency_required') is not True: fail(f"{r.get('type')}.idempotency_required must be true")
        if r.get('replay_protection') is not True: fail(f"{r.get('type')}.replay_protection must be true")
    g = c.get('global_guards') or {}
    for must_true in ('idempotency_key_required', 'negative_inventory_guard', 'no_duplicate_grant', 'canary_allowlist_only', 'dry_run_only'):
        if g.get(must_true) is not True: fail(f"global_guards.{must_true} must be true")
    with open(I) as f: i = json.load(f)
    guards = i.get('guards') or {}
    for k in ('duplicate_claim', 'malformed_claim', 'over_cap_claim', 'unauthorized_claim'):
        if not guards.get(k): fail(f"idempotency contract missing guard: {k}")
    print("PASS v94_reward_safety_contracts")

if __name__ == '__main__': main()
