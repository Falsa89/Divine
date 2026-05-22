#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, SAFETY_DIR, load, finish, require, require_design_only  # noqa: E402

NAME = 'slc_f_readiness_rollup_v1'


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_readiness_rollup_v1.json')
    require_design_only(j, errs, NAME)
    s = j.get('state', {})
    for k, exp in (
        ('route_scope_inventory_ready', True), ('collection_scope_matrix_ready', True),
        ('endpoint_patch_contract_ready', True), ('legacy_s1_compatibility_plan_ready', True),
        ('dry_run_simulation_plan_ready', True), ('route_patch_risk_matrix_ready', True),
        ('runtime_guardrail_policy_ready', True),
        ('runtime_patch_applied', False), ('db_write', False), ('migration_applied', False),
        ('second_server_opening_allowed', False), ('server_profiles_runtime_enabled', False),
        ('borea_safe', True), ('af2n_invariant_intact', True),
    ):
        require(s.get(k) is exp, f'state.{k} must be {exp} (got {s.get(k)})', errs)
    require(len(j.get('blockers_to_runtime_patch', [])) >= 5, 'must list >=5 blockers', errs)
    ff = {f.get('name'): f for f in j.get('future_feature_flags', [])}
    for k in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SERVER_AWARE_READS_ENABLED', 'SERVER_AWARE_WRITES_ENABLED', 'SECOND_SERVER_OPENING_ENABLED'):
        require(k in ff and ff[k].get('value') is False, f'feature flag {k} must be False', errs)
    # Cross-check system_safety rollup also present and consistent
    safety = SAFETY_DIR / 'server_lifecycle_slc_f_route_patch_dryrun_readiness_rollup_v1.json'
    require(safety.exists(), f'system_safety rollup missing: {safety}', errs)
    if safety.exists():
        sj = load(safety)
        require(sj.get('slc_f_route_patch_applied') is False, 'safety rollup route_patch_applied must be False', errs)
        require(sj.get('slc_f_db_write') is False, 'safety rollup db_write must be False', errs)
        require(sj.get('slc_f_second_server_opening_allowed') is False, 'safety rollup second_server_opening_allowed must be False', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
