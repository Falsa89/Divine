#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SAFETY_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'slc_d_merge_tooling_offline_readiness_rollup_v1'


def main() -> int:
    errs = []
    j = load(SAFETY_DIR / 'slc_d_merge_tooling_offline_readiness_rollup_v1.json')
    require_design_only(j, errs, NAME)
    s = j.get('state', {})
    for k, exp in (
        ('merge_tooling_offline_plan_ready', True),
        ('eligibility_policy_ready', True),
        ('group_planning_contract_ready', True),
        ('conflict_resolution_contract_ready', True),
        ('recovery_season_contract_ready', True),
        ('calendar_harmonization_policy_ready', True),
        ('dryrun_scenarios_ready', True),
        ('risk_matrix_ready', True),
        ('abort_rollback_policy_ready', True),
        ('merge_execution_allowed', False),
        ('db_write', False),
        ('migration_applied', False),
        ('second_server_opening_allowed', False),
        ('server_profiles_runtime_enabled', False),
        ('borea_safe', True),
        ('af2n_invariant_intact', True),
        ('route_patch_applied', False),
    ):
        require(s.get(k) is exp, f'state.{k} must be {exp} (got {s.get(k)})', errs)
    require(len(j.get('blockers_to_runtime_merge', [])) >= 5, 'must list >=5 blockers', errs)
    base = j.get('baseline', {})
    require(base.get('af2n_cap') == 50000 and base.get('af2n_allowlist') == 2500, 'baseline af2n mismatch', errs)
    return finish(NAME, errs, target_dir=SAFETY_DIR)


if __name__ == '__main__':
    sys.exit(main())
