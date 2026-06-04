#!/usr/bin/env python3
"""
v91_FIXED — Universal no-random enemy source policy validator.

Verifica che il file canonical_encounter_source_policy_v1.json esista e dichiari:
- random_opponents_allowed = false
- runtime_random_enemy_generation_allowed = false
- fallback_random_allowed = false
- applies_to_all_modes = true

E che la matrice modalita' copra: story, tower, arena, training, raid, event, guild_live_future.
E che ogni modalita' dichiari is_random=false / runtime_generated=false / fallback_random_allowed=false.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POLICY = os.path.join(ROOT, 'data', 'design', 'battle_mode_enemy_sources',
                     'canonical_encounter_source_policy_v1.json')

REQUIRED_MODES = {'story', 'tower', 'arena', 'training', 'raid', 'event', 'guild_live_future'}


def fail(msg: str) -> None:
    print(f"FAIL v91_universal_no_random_enemy_source_policy: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(POLICY):
        fail(f"missing policy: {POLICY}")
    with open(POLICY, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get('random_opponents_allowed') is not False:
        fail("random_opponents_allowed must be false")
    if data.get('runtime_random_enemy_generation_allowed') is not False:
        fail("runtime_random_enemy_generation_allowed must be false")
    if data.get('fallback_random_allowed') is not False:
        fail("fallback_random_allowed must be false")
    if data.get('applies_to_all_modes') is not True:
        fail("applies_to_all_modes must be true")

    matrix = data.get('mode_matrix') or {}
    missing = REQUIRED_MODES - set(matrix.keys())
    if missing:
        fail(f"mode_matrix missing modes: {sorted(missing)}")

    for mode, conf in matrix.items():
        if conf.get('is_random') is not False:
            fail(f"mode_matrix[{mode}].is_random must be false")
        if conf.get('runtime_generated') is not False:
            fail(f"mode_matrix[{mode}].runtime_generated must be false")
        if conf.get('fallback_random_allowed') is not False:
            fail(f"mode_matrix[{mode}].fallback_random_allowed must be false")
        if not conf.get('required_source_type'):
            fail(f"mode_matrix[{mode}] missing required_source_type")

    print("PASS v91_universal_no_random_enemy_source_policy")


if __name__ == '__main__':
    main()
