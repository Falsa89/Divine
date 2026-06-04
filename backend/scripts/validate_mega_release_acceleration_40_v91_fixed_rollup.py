#!/usr/bin/env python3
"""
v91_FIXED — Rollup marker validator.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROLLUP = os.path.join(ROOT, 'data', 'design', 'release_acceleration',
                     'mega_release_acceleration_40_v91_fixed_rollup_marker_v1.json')

REQUIRED_SUB_TRACKS = {
    'v91_pre_battle_lobby_flow',
    'v91_universal_no_random_enemy_source_policy',
    'v91_canonical_encounter_stub_catalogs',
    'v91_battle_engine_status_dot_audit',
}


def fail(msg: str) -> None:
    print(f"FAIL mega_release_acceleration_40_v91_fixed_rollup: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(ROLLUP):
        fail(f"missing rollup marker: {ROLLUP}")
    with open(ROLLUP, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get('pack') != 'MEGA_RELEASE_ACCELERATION_40_PRE_BATTLE_LOBBY_ENGINE_STATUS_DOT_AND_CANONICAL_ENCOUNTER_SOURCE_PACK_v91_FIXED':
        fail("pack mismatch")
    if data.get('sentinel') != 'PUBLIC_SYNC_SENTINEL_v91_FIXED_PRESENT=YES':
        fail("sentinel mismatch")
    if 'PUBLIC_SYNC_TAG_v91_FIXED' not in (data.get('tag') or ''):
        fail("tag must reference PUBLIC_SYNC_TAG_v91_FIXED")

    sub = set(data.get('sub_tracks') or [])
    if not REQUIRED_SUB_TRACKS.issubset(sub):
        fail(f"sub_tracks missing required: have {sorted(sub)}")

    expected_verdict = 'MEGA_RELEASE_ACCELERATION_40_PRE_BATTLE_LOBBY_ENGINE_STATUS_DOT_AND_CANONICAL_ENCOUNTER_SOURCE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if data.get('verdict') != expected_verdict:
        fail("verdict mismatch")

    safety = data.get('safety') or {}
    required_safety = {
        'db_writes': 0,
        'reward_live': False,
        'endpoint_live': False,
        'battle_engine_authoritative': False,
        'random_opponents_allowed': False,
        'runtime_random_enemy_generation_allowed': False,
        'fallback_random_allowed': False,
        'validator_weakening': False,
        'fake_pass': False,
    }
    for k, expected in required_safety.items():
        if safety.get(k) != expected:
            fail(f"safety.{k} expected {expected} got {safety.get(k)}")

    print("PASS mega_release_acceleration_40_v91_fixed_rollup")


if __name__ == '__main__':
    main()
