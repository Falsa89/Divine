#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_eligibility_policy_v1'


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_eligibility_policy_v1.json')
    require_design_only(j, errs, NAME)
    ec = j.get('eligibility_criteria', {})
    require(ec.get('min_server_age_days', 0) >= 30, 'min_server_age_days must be >=30', errs)
    require(set(ec.get('eligible_states', [])) >= {'closed_to_new', 'merge_pending'}, 'eligible_states must include closed_to_new and merge_pending', errs)
    require('open' in ec.get('protected_states', []), 'protected_states must include "open"', errs)
    require('merged' in ec.get('forbidden_states_for_merge_source', []), 'merged must be forbidden as source', errs)
    require('archived' in ec.get('forbidden_states_for_merge_target', []), 'archived must be forbidden as target', errs)
    lock = j.get('live_mode_lock_rules', {})
    require(lock.get('forbid_merge_during_any_live_window') is True, 'forbid_merge_during_any_live_window must be True', errs)
    require(lock.get('forbid_merge_within_minutes_before_window') == 120, 'before window lock must be 120 minutes', errs)
    require(lock.get('forbid_merge_within_minutes_after_window') == 120, 'after window lock must be 120 minutes', errs)
    eco = j.get('economy_risk_blockers', {})
    for k in ('forbid_merge_during_paid_event','forbid_merge_during_pity_critical_banner_end_window',
              'forbid_merge_if_af2n_canary_active','forbid_merge_if_redis_rate_limit_unavailable'):
        require(eco.get(k) is True, f'economy_risk_blockers.{k} must be True', errs)
    af = j.get('af2n_safety', {})
    require(af.get('cap_must_stay_50000') is True, 'af2n cap_must_stay_50000', errs)
    require(af.get('allowlist_must_stay_2500') is True, 'af2n allowlist_must_stay_2500', errs)
    require(j.get('borea_safety', {}).get('primordial_gaia_must_remain_404') is True, 'primordial_gaia_must_remain_404', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
