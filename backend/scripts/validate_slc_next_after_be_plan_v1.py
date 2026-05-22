#!/usr/bin/env python3
"""SLC-NEXT-PREP-A — validate SLC-Next planning artifacts.

Validates 3 server_lifecycle JSON + 1 system_safety rollup. No DB writes.
"""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import SLC_DIR, SAFETY_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'slc_next_after_be_plan_v1'

EXPECTED_SLC_STEPS = {'SLC-F', 'SLC-G', 'SLC-D', 'SLC-H'}
EXPECTED_BLOCKERS = {
    'migration_required_before_runtime', 'route_patch_required',
    'default_s1_migration_required', 'second server opening locked',
    'runtime feature flags unset', 'user approval required for each runtime/DB phase',
}


def main() -> int:
    errs = []
    # 1) Route-patch dry-run plan
    j_rp = load_json_at(SLC_DIR / 'slc_next_after_be_route_patch_dryrun_plan_v1.json')
    require_design_only_flags(j_rp, errs, NAME + '.route_patch_dryrun_plan')
    require(j_rp.get('execute_now') is False, 'route_patch_dryrun_plan.execute_now must be False', errs)
    pf = j_rp.get('protected_files', [])
    for must in ('battle_engine.py', 'battle_core.py', 'affinity_gift_spend.py'):
        require(must in pf, f'protected_files missing {must}', errs)
    # 2) Blocker status
    j_bl = load_json_at(SLC_DIR / 'slc_next_after_be_blocker_status_v1.json')
    require_design_only_flags(j_bl, errs, NAME + '.blocker_status')
    require(j_bl.get('second_server_opening_allowed') is False, 'blocker_status.second_server_opening_allowed must be False', errs)
    bl_set = set(j_bl.get('blockers', []))
    missing = EXPECTED_BLOCKERS - bl_set
    require(not missing, f'blocker_status: missing blockers {sorted(missing)}', errs)
    # 3) Recommended sequence
    j_rs = load_json_at(SLC_DIR / 'slc_next_after_be_recommended_sequence_v1.json')
    require_design_only_flags(j_rs, errs, NAME + '.recommended_sequence')
    require(j_rs.get('latest_completed') == 'SLC-BE', f'latest_completed must be SLC-BE (got {j_rs.get("latest_completed")})', errs)
    seq_steps = {s.get('step') for s in j_rs.get('recommended_next_sequence', [])}
    missing_steps = EXPECTED_SLC_STEPS - seq_steps
    require(not missing_steps, f'recommended_sequence missing steps: {sorted(missing_steps)}', errs)
    for s in j_rs.get('recommended_next_sequence', []):
        require(s.get('execute_now') is False, f'recommended step {s.get("step")}: execute_now must be False', errs)
    # SLC-BE baseline summary checks
    be = j_rs.get('slc_be_summary', {})
    require(be.get('runtime_enabled') is False, 'slc_be_summary.runtime_enabled must be False', errs)
    require(be.get('db_write') is False, 'slc_be_summary.db_write must be False', errs)
    require(be.get('second_server_opening_allowed') is False, 'slc_be_summary.second_server_opening_allowed must be False', errs)
    require(be.get('api_baseline', {}).get('/api/heroes') == 100, 'slc_be_summary.api_baseline.heroes must be 100', errs)
    require(be.get('api_baseline', {}).get('/api/heroes/primordial_gaia') == 404, 'slc_be_summary.api_baseline.primordial_gaia must be 404', errs)
    require(be.get('af2n', {}).get('cap') == 50000, 'slc_be_summary.af2n.cap must be 50000', errs)
    require(be.get('af2n', {}).get('allowlist') == 2500, 'slc_be_summary.af2n.allowlist must be 2500', errs)
    ff = be.get('future_flags', {})
    require(ff.get('SERVER_PROFILES_RUNTIME_ENABLED') is False, 'SERVER_PROFILES_RUNTIME_ENABLED must be False', errs)
    require(ff.get('SECOND_SERVER_OPENING_ENABLED') is False, 'SECOND_SERVER_OPENING_ENABLED must be False', errs)
    # 4) System-safety readiness rollup
    j_ro = load_json_at(SAFETY_DIR / 'live_modes_slc_next_readiness_rollup_v1.json')
    require_design_only_flags(j_ro, errs, NAME + '.readiness_rollup')
    require(j_ro.get('live_modes_reconciliation_ready') is True, 'readiness_rollup.live_modes_reconciliation_ready must be True', errs)
    require(j_ro.get('slc_be_accepted_as_baseline') is True, 'readiness_rollup.slc_be_accepted_as_baseline must be True', errs)
    require(j_ro.get('slc_next_runtime_allowed') is False, 'readiness_rollup.slc_next_runtime_allowed must be False', errs)
    require(j_ro.get('db_write_allowed') is False, 'readiness_rollup.db_write_allowed must be False', errs)
    require(j_ro.get('second_server_opening_allowed') is False, 'readiness_rollup.second_server_opening_allowed must be False', errs)
    return finish_result(NAME, errs, SLC_DIR)


if __name__ == '__main__':
    sys.exit(main())
