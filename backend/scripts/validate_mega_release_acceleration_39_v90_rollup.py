#!/usr/bin/env python3
"""
v90 — Rollup marker MEGA_RELEASE_ACCELERATION_39.

Verifica:
- esiste rollup marker JSON
- sentinel/tag pubblici corretti
- sub_tracks coprono i 3 validator v90
- verdict v90 corretto
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROLLUP = os.path.join(ROOT, 'data', 'design', 'release_acceleration',
                     'mega_release_acceleration_39_v90_rollup_marker_v1.json')


def fail(msg: str) -> None:
    print(f"FAIL mega_release_acceleration_39_v90_rollup: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(ROLLUP):
        fail(f"missing rollup marker: {ROLLUP}")

    with open(ROLLUP, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get('pack') != 'MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_PACK_v90':
        fail("pack name mismatch")
    if data.get('sentinel') != 'PUBLIC_SYNC_SENTINEL_v90_PRESENT=YES':
        fail("sentinel mismatch")
    if 'PUBLIC_SYNC_TAG_v90' not in (data.get('tag') or ''):
        fail("tag must reference PUBLIC_SYNC_TAG_v90")

    sub = data.get('sub_tracks') or []
    required = {'v90_home_battle_renderer_forensic_audit',
                'v90_restored_battle_renderer_reuse',
                'v90_no_mock_preview_regression'}
    if not required.issubset(set(sub)):
        fail(f"sub_tracks missing required: have {sub}")

    expected_verdict = 'MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if data.get('verdict') != expected_verdict:
        fail("verdict mismatch")

    safety = data.get('safety') or {}
    if safety.get('db_writes') != 0:
        fail("safety db_writes must be 0")
    if safety.get('reward_live') is not False:
        fail("safety reward_live must be false")
    if safety.get('endpoint_live') is not False:
        fail("safety endpoint_live must be false")
    if safety.get('battle_engine_authoritative') is not False:
        fail("safety battle_engine_authoritative must be false")
    if safety.get('validator_weakening') is not False:
        fail("safety validator_weakening must be false")
    if safety.get('fake_pass') is not False:
        fail("safety fake_pass must be false")

    print("PASS mega_release_acceleration_39_v90_rollup")


if __name__ == '__main__':
    main()
