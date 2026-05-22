#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags  # noqa: E402

NAME = 'benchmark_canonical_index_v1'
REQUIRED_COVERS = {
    '16_live_special_modes', 'server_lifecycle_calendar_merge', 'event_hub_daily_guide',
    'summon_pity_fragments_wishlist', 'cosmetics_skins_titles_furniture',
    'sanctuary_housing_dimora_divina', 'guild_social_coop', 'tower_castle_roguelike',
    'equipment_relic_forge', 'battle_stats_reporting', 'monetized_events_guardrails',
    'slc_f_next_checkpoint',
}


def main() -> int:
    errs = []
    j = load('benchmark_canonical_index_v1.json')
    check_mandatory_flags(j, errs, NAME)
    covers = set(j.get('covers', []))
    missing = REQUIRED_COVERS - covers
    require(not missing, f'index missing covers: {sorted(missing)}', errs)
    docs = j.get('canonical_documents', {})
    require(len(docs) >= 11, f'canonical_documents must reference >=11 files (got {len(docs)})', errs)
    hg = j.get('hard_guardrails', {})
    for k in ('db_writes', 'migrations', 'runtime_routes', 'frontend_runtime_ui',
              'battle_runtime_changes', 'gacha_roster_catalog_changes',
              'affinity_af2n_stage4_changes', 'second_server_opening'):
        require(hg.get(k) is False, f'hard_guardrails.{k} must be False', errs)
    return finish(NAME, errs, {'covers_count': len(covers)})


if __name__ == '__main__':
    sys.exit(main())
