#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_abort_rollback_policy_v1'
REQUIRED_TRIGGERS = {
    'af2n_canary_burst_detected','redis_rate_limit_unavailable','protected_event_window_starts',
    'banner_pity_critical_window_starts','target_server_status_changes_unexpectedly',
    'borea_exposure_drift_detected','primordial_gaia_404_drift_detected',
    'unresolved_leaderboard_settlement',
}
REQUIRED_CLASSES = {'pre_freeze_abort', 'during_freeze_abort', 'post_merge_audit_failure'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_abort_rollback_policy_v1.json')
    require_design_only(j, errs, NAME)
    trig = set(j.get('abort_triggers', []))
    missing = REQUIRED_TRIGGERS - trig
    require(not missing, f'abort_triggers missing: {sorted(missing)}', errs)
    actions = j.get('abort_actions', {})
    require(actions.get('never_proceed_to_merged_state') is True, 'never_proceed_to_merged_state must be True', errs)
    require(actions.get('db_write') is False, 'abort_actions.db_write must be False', errs)
    cls = {c.get('class') for c in j.get('rollback_classes', [])}
    missing_c = REQUIRED_CLASSES - cls
    require(not missing_c, f'rollback_classes missing: {sorted(missing_c)}', errs)
    gates = j.get('approval_gates', {})
    for k in ('merge_execution_requires_explicit_user_approval',
              'merged_state_transition_requires_explicit_user_approval',
              'archived_state_transition_requires_explicit_user_approval',
              'phase_11_unsafe_fallback_removal_requires_explicit_user_approval'):
        require(gates.get(k) is True, f'approval_gates.{k} must be True', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
