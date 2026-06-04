#!/usr/bin/env python3
"""v92 — Mode Test Matrix validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MATRIX = os.path.join(ROOT, 'data', 'design', 'live_mode_testability',
                     'v92_mode_test_matrix_v1.json')

REQUIRED_MODES = {
    'story', 'tower', 'arena', 'training', 'raid', 'event',
    'crepuscolo_dei_titani', 'assalto_del_ragnarok', 'guild_war', 'guild_raid',
    'server_boss', 'faction_boss', 'territory', 'war_avatar_mode', 'event_avatar_mode',
}
REQUIRED_FIELDS = {
    'mode_id', 'menu_path', 'pre_entry_path', 'qa_override',
    'avatar_placeholder_needed', 'encounter_source', 'expected_test_action',
    'safety_flags', 'current_status',
}


def fail(msg): print(f"FAIL v92_mode_test_matrix: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(MATRIX): fail(f"missing matrix: {MATRIX}")
    with open(MATRIX, 'r', encoding='utf-8') as f: data = json.load(f)
    if data.get('random_opponents_allowed') is not False:
        fail("random_opponents_allowed must be false")
    modes = data.get('modes') or []
    found = {m.get('mode_id') for m in modes}
    missing = REQUIRED_MODES - found
    if missing: fail(f"missing modes in matrix: {sorted(missing)}")
    for m in modes:
        for k in REQUIRED_FIELDS:
            if k not in m: fail(f"mode {m.get('mode_id')} missing field: {k}")
        sf = m.get('safety_flags') or {}
        if sf.get('reward_live', False) is not False:
            fail(f"{m.get('mode_id')}.safety_flags.reward_live must be false")
    print("PASS v92_mode_test_matrix")


if __name__ == '__main__': main()
