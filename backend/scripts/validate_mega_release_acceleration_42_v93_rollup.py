#!/usr/bin/env python3
"""v93 — Rollup marker validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(ROOT, 'data', 'design', 'release_acceleration', 'mega_release_acceleration_42_v93_rollup_marker_v1.json')
REQ_SUB = {'v93_real_formation_source', 'v93_team_editor_wiring',
           'v93_readonly_catalog_endpoints', 'v93_avatar_placeholder_visuals',
           'v93_war_event_avatar_preview_screens', 'v93_guild_war_sandbox_flow',
           'v93_full_mode_playability_matrix', 'v93_live_announcements_qa'}
REQ_SAF = {'db_writes': 0, 'reward_live': False, 'ranking_live': False,
           'event_currency_live': False, 'guild_score_mutation': 0,
           'arena_mmr': False, 'production_announcements_broadcast': False,
           'production_push_notifications': False, 'real_user_pii': False,
           'random_opponents': False, 'final_asset_import': False,
           'validator_weakening': False, 'fake_pass': False}

def fail(m): print(f"FAIL mega_release_acceleration_42_v93_rollup: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(R): fail(f"missing: {R}")
    with open(R) as f: d = json.load(f)
    if d.get('pack') != 'MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK_v93':
        fail("pack mismatch")
    if d.get('sentinel') != 'PUBLIC_SYNC_SENTINEL_v93_PRESENT=YES': fail("sentinel mismatch")
    if 'PUBLIC_SYNC_TAG_v93' not in (d.get('tag') or ''): fail("tag must reference v93")
    sub = set(d.get('sub_tracks') or [])
    if not REQ_SUB.issubset(sub): fail(f"sub_tracks missing: {sorted(REQ_SUB - sub)}")
    if d.get('verdict') != 'MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail("verdict mismatch")
    saf = d.get('safety') or {}
    for k, v in REQ_SAF.items():
        if saf.get(k) != v: fail(f"safety.{k} expected {v} got {saf.get(k)}")
    print("PASS mega_release_acceleration_42_v93_rollup")

if __name__ == '__main__': main()
