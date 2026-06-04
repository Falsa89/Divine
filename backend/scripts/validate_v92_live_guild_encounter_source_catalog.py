#!/usr/bin/env python3
"""v92 — Live/Guild encounter source catalog validator (no-random extension)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAT = os.path.join(ROOT, 'data', 'design', 'live_mode_testability',
                   'live_guild_special_mode_encounter_source_catalog_v1.json')

REQUIRED_MODES = {
    'crepuscolo_dei_titani', 'assalto_del_ragnarok',
    'guild_war', 'guild_raid', 'server_boss', 'faction_boss',
    'territory', 'war_avatar_mode', 'event_avatar_mode',
}


def fail(msg): print(f"FAIL v92_live_guild_encounter_source_catalog: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(CAT): fail(f"missing catalog: {CAT}")
    with open(CAT, 'r', encoding='utf-8') as f: data = json.load(f)
    if data.get('random_opponents_allowed') is not False:
        fail("random_opponents_allowed must be false")
    if data.get('runtime_random_enemy_generation_allowed') is not False:
        fail("runtime_random_enemy_generation_allowed must be false")
    if data.get('fallback_random_allowed') is not False:
        fail("fallback_random_allowed must be false")
    sources = data.get('sources') or []
    found = {s.get('mode_id') for s in sources}
    missing = REQUIRED_MODES - found
    if missing: fail(f"missing required modes: {sorted(missing)}")
    for s in sources:
        for must_false in ('is_random', 'runtime_generated', 'fallback_random_allowed'):
            if s.get(must_false) is not False:
                fail(f"{s.get('mode_id')}.{must_false} must be false")
        if not s.get('source_type') or not s.get('source_id'):
            fail(f"{s.get('mode_id')} missing source_type/source_id")
    print("PASS v92_live_guild_encounter_source_catalog")


if __name__ == '__main__': main()
