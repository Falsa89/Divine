#!/usr/bin/env python3
"""v94 — Rollup marker validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(ROOT, 'data', 'design', 'release_acceleration', 'mega_release_acceleration_43_v94_rollup_marker_v1.json')
REQ_SUB = {'v94_battle_engine_status_dot_patch', 'v94_engine_regression_fixtures',
           'v94_battle_report_extensions', 'v94_reward_safety_contracts',
           'v94_reward_score_dry_run', 'v94_live_guild_score_gating',
           'v94_readonly_catalog_endpoints', 'v94_real_formation_integration',
           'v94_live_announcement_safety_bridge'}
REQ_SAF = {'db_writes': 0, 'reward_live': False, 'ranking_live': False,
           'event_currency_live': False, 'guild_score_mutation': 0,
           'arena_mmr_live': False, 'production_announcement_broadcast': False,
           'production_push_notifications': False, 'random_opponents': False,
           'character_bible_mutation': False, 'hero_roster_mutation': False,
           'final_asset_import': False, 'final_numbers_balance_lock': False,
           'validator_weakening': False, 'fake_pass': False}

def fail(m): print(f"FAIL mega_release_acceleration_43_v94_rollup: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(R): fail(f"missing: {R}")
    with open(R) as f: d = json.load(f)
    if d.get('pack') != 'MEGA_RELEASE_ACCELERATION_43_ENGINE_REWARDS_LIVE_GUILD_SUPERPACK_v94': fail("pack mismatch")
    if d.get('sentinel') != 'PUBLIC_SYNC_SENTINEL_v94_PRESENT=YES': fail("sentinel mismatch")
    if 'PUBLIC_SYNC_TAG_v94' not in (d.get('tag') or ''): fail("tag missing v94")
    sub = set(d.get('sub_tracks') or [])
    if not REQ_SUB.issubset(sub): fail(f"sub_tracks missing: {sorted(REQ_SUB - sub)}")
    if d.get('verdict') != 'MEGA_RELEASE_ACCELERATION_43_ENGINE_REWARDS_LIVE_GUILD_SUPERPACK_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail("verdict mismatch")
    saf = d.get('safety') or {}
    for k, v in REQ_SAF.items():
        if saf.get(k) != v: fail(f"safety.{k} expected {v} got {saf.get(k)}")
    md5s = d.get('md5_unlock_summary') or {}
    for k in ('battle_engine_py', 'server_py'):
        if k not in md5s: fail(f"md5_unlock_summary missing {k}")
        if not md5s[k].get('old_md5') or not md5s[k].get('new_md5'): fail(f"{k} missing old/new MD5")
    print("PASS mega_release_acceleration_43_v94_rollup")

if __name__ == '__main__': main()
