#!/usr/bin/env python3
"""v92 — Rollup marker validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROLLUP = os.path.join(ROOT, 'data', 'design', 'release_acceleration',
                     'mega_release_acceleration_41_v92_rollup_marker_v1.json')

REQUIRED_SUB_TRACKS = {
    'v92_live_guild_special_mode_inventory',
    'v92_qa_time_gate_override_contract',
    'v92_avatar_placeholder_dev_registry',
    'v92_live_guild_mode_qa_hub',
    'v92_live_guild_encounter_source_catalog',
    'v92_mode_test_matrix',
}
REQUIRED_SAFETY = {
    'db_writes': 0,
    'reward_live': False,
    'ranking_live': False,
    'event_currency_live': False,
    'guild_score_mutation': 0,
    'arena_mmr': False,
    'story_progress': False,
    'tower_completion': False,
    'boss_fragments': False,
    'inventory_grant': False,
    'cosmetic_unlock': False,
    'monetization': False,
    'random_opponents': False,
    'final_asset_import': False,
    'production_time_gate_override': False,
    'production_ui_exposure': False,
    'validator_weakening': False,
    'fake_pass': False,
}


def fail(msg): print(f"FAIL mega_release_acceleration_41_v92_rollup: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(ROLLUP): fail(f"missing rollup: {ROLLUP}")
    with open(ROLLUP, 'r', encoding='utf-8') as f: data = json.load(f)
    if data.get('pack') != 'MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY_AND_AVATAR_PLACEHOLDER_PACK_v92':
        fail("pack name mismatch")
    if data.get('sentinel') != 'PUBLIC_SYNC_SENTINEL_v92_PRESENT=YES':
        fail("sentinel mismatch")
    if 'PUBLIC_SYNC_TAG_v92' not in (data.get('tag') or ''):
        fail("tag must reference PUBLIC_SYNC_TAG_v92")
    sub = set(data.get('sub_tracks') or [])
    if not REQUIRED_SUB_TRACKS.issubset(sub):
        fail(f"sub_tracks missing required: have {sorted(sub)}")
    expected = 'MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY_AND_AVATAR_PLACEHOLDER_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if data.get('verdict') != expected:
        fail("verdict mismatch")
    safety = data.get('safety') or {}
    for k, v in REQUIRED_SAFETY.items():
        if safety.get(k) != v:
            fail(f"safety.{k} expected {v} got {safety.get(k)}")
    print("PASS mega_release_acceleration_41_v92_rollup")


if __name__ == '__main__': main()
