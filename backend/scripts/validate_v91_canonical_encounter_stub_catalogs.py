#!/usr/bin/env python3
"""
v91_FIXED — Canonical encounter stub catalogs validator.

Verifica esistenza dei 7 stub catalog (story/tower/arena/training/raid/event/guild_live).
Per ogni record di ogni catalogo deve essere garantito:
- source_type presente
- source_id presente
- mode presente
- is_random == false
- runtime_generated == false
- fallback_random_allowed == false
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG_DIR = os.path.join(ROOT, 'data', 'design', 'battle_mode_enemy_sources')

EXPECTED_FILES = {
    'story_encounter_stub_catalog_v1.json': 'encounters',
    'tower_encounter_stub_catalog_v1.json': 'encounters',
    'arena_opponent_source_stub_catalog_v1.json': 'opponent_sources',
    'training_encounter_stub_catalog_v1.json': 'presets',
    'raid_boss_encounter_stub_catalog_v1.json': 'bosses',
    'event_encounter_stub_catalog_v1.json': 'events',
    'guild_live_encounter_source_stub_catalog_v1.json': 'sources',
}

REQUIRED_RECORD_KEYS = ('source_type', 'source_id', 'mode')
REQUIRED_FALSE_FLAGS = ('is_random', 'runtime_generated', 'fallback_random_allowed')


def fail(msg: str) -> None:
    print(f"FAIL v91_canonical_encounter_stub_catalogs: {msg}")
    sys.exit(1)


def main() -> None:
    for filename, list_key in EXPECTED_FILES.items():
        path = os.path.join(CATALOG_DIR, filename)
        if not os.path.isfile(path):
            fail(f"missing catalog: {filename}")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get('random_opponents_allowed') is not False:
            fail(f"{filename}: random_opponents_allowed must be false")
        if data.get('runtime_random_enemy_generation_allowed') is not False:
            fail(f"{filename}: runtime_random_enemy_generation_allowed must be false")
        if data.get('fallback_random_allowed') is not False:
            fail(f"{filename}: fallback_random_allowed must be false")

        records = data.get(list_key)
        if not records or not isinstance(records, list):
            fail(f"{filename}: missing or empty list '{list_key}'")

        for i, rec in enumerate(records):
            for k in REQUIRED_RECORD_KEYS:
                if not rec.get(k):
                    fail(f"{filename}[{i}] missing key {k}")
            for flag in REQUIRED_FALSE_FLAGS:
                if rec.get(flag) is not False:
                    fail(f"{filename}[{i}].{flag} must be false")

    print("PASS v91_canonical_encounter_stub_catalogs")


if __name__ == '__main__':
    main()
