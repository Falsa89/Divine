#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_group_planning_contract_v1'


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_group_planning_contract_v1.json')
    require_design_only(j, errs, NAME)
    gc = j.get('group_composition_rules', {})
    require(gc.get('min_servers_per_merge_group', 0) >= 2, 'min_servers_per_merge_group must be >=2', errs)
    require(gc.get('max_servers_per_merge_group', 0) >= 10, 'max_servers_per_merge_group must be >=10', errs)
    ts = j.get('target_server_selection', {})
    require(ts.get('prefer') == 'oldest_eligible_server_in_group', 'target preference must be oldest_eligible_server_in_group', errs)
    require(ts.get('target_must_inherit_status_open_or_crowded_after_merge') is True, 'target must inherit open/crowded after merge', errs)
    bpi = j.get('baseline_progress_index', {})
    require(bpi.get('computed_offline') is True, 'baseline_progress_index must be computed_offline=True', errs)
    require(bpi.get('db_write') is False, 'baseline_progress_index.db_write must be False', errs)
    rp = j.get('recovery_pool', {})
    require(rp.get('af2n_unaffected') is True, 'recovery_pool.af2n_unaffected must be True', errs)
    sah = j.get('server_age_harmonization', {})
    require(sah.get('prevent_unfair_event_acceleration') is True, 'server_age_harmonization.prevent_unfair_event_acceleration must be True', errs)
    pmc = j.get('post_merge_calendar', {})
    require(pmc.get('reuse_target_server_calendar') is True, 'post_merge_calendar.reuse_target_server_calendar must be True', errs)
    require(pmc.get('do_not_double_run_live_modes') is True, 'post_merge_calendar.do_not_double_run_live_modes must be True', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
