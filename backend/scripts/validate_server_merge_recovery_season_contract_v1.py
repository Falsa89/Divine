#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_recovery_season_contract_v1'
REQUIRED_CLASSES = {'must_catch_up', 'optional_catch_up', 'compress', 'skip'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_recovery_season_contract_v1.json')
    require_design_only(j, errs, NAME)
    require(j.get('default_duration_days') == 14, 'default_duration_days must be 14', errs)
    rng = j.get('configurable_range_days', [])
    require(rng == [14, 21], 'configurable_range_days must be [14, 21]', errs)
    seen = {c.get('class') for c in j.get('recovery_classes', [])}
    missing = REQUIRED_CLASSES - seen
    require(not missing, f'recovery_classes missing: {sorted(missing)}', errs)
    bp = j.get('banner_policy', {})
    require(bp.get('max_parallel_banners_during_recovery', 0) >= 1, 'max_parallel_banners_during_recovery must be >=1', errs)
    require(bp.get('shared_purchase_limits') is True, 'shared_purchase_limits must be True', errs)
    require(bp.get('pity_policy_inheritance') == 'best_per_account_server_safe', 'pity_policy_inheritance must be best_per_account_server_safe', errs)
    require(bp.get('never_clone_pity_across_servers') is True, 'never_clone_pity_across_servers must be True', errs)
    require(bp.get('never_clone_purchase_limits_across_servers') is True, 'never_clone_purchase_limits_across_servers must be True', errs)
    es = j.get('economy_safeguards', {})
    require(es.get('paid_currency_account_wide_invariant') is True, 'paid_currency_account_wide_invariant must be True', errs)
    require(es.get('free_currency_server_bound_invariant') is True, 'free_currency_server_bound_invariant must be True', errs)
    require(es.get('recovery_pool_capped_per_account') is True, 'recovery_pool_capped_per_account must be True', errs)
    af = j.get('af2n_safety', {})
    require(af.get('cap_50000_preserved') is True and af.get('allowlist_2500_preserved') is True, 'af2n cap/allowlist preservation flags must be True', errs)
    require(j.get('borea_safety', {}).get('borea_never_exposed_in_recovery_rewards') is True, 'borea_never_exposed_in_recovery_rewards must be True', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
