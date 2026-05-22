#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'benchmark_system_library_v1'
REQUIRED_SYSTEMS = {
    'tower_castle_roguelike', 'equipment_relic_forge', 'battle_stats_reporting',
    'monetized_events_guardrails', 'cosmetics_skins_titles_furniture',
}


def main() -> int:
    errs = []
    j = load('benchmark_system_library_v1.json')
    check_mandatory_flags(j, errs, NAME)
    lib = j.get('library', [])
    seen = {e.get('system') for e in lib}
    missing = REQUIRED_SYSTEMS - seen
    require(not missing, f'library missing systems: {sorted(missing)}', errs)
    for e in lib:
        check_canonical_fields(e, f'library system “{e.get("system")}”', errs, optional_inspiration=False)
    return finish(NAME, errs, {'library_systems': len(lib)})


if __name__ == '__main__':
    sys.exit(main())
