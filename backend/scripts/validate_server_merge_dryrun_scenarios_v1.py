#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_dryrun_scenarios_v1'
REQUIRED_SCENARIOS = {
    'three_similar_age_servers','three_staggered_age_servers',
    'ten_plus_low_population_servers','blocked_protected_event_state',
    'duplicate_names_and_guild_tags',
}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_dryrun_scenarios_v1.json')
    require_design_only(j, errs, NAME)
    scs = j.get('scenarios', [])
    require(len(scs) >= 5, f'must have >=5 scenarios (got {len(scs)})', errs)
    names = {s.get('name') for s in scs}
    missing = REQUIRED_SCENARIOS - names
    require(not missing, f'scenarios missing: {sorted(missing)}', errs)
    for s in scs:
        exp = s.get('expected', {})
        require(exp.get('db_write') is False, f'scenario {s.get("name")}: expected.db_write must be False', errs)
    blocked = next((s for s in scs if s.get('name') == 'blocked_protected_event_state'), None)
    require(blocked and blocked.get('expected', {}).get('merge_allowed') is False, 'blocked scenario must have merge_allowed=False', errs)
    return finish(NAME, errs, extra={'scenario_count': len(scs)})


if __name__ == '__main__':
    sys.exit(main())
