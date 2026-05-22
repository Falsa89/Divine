#!/usr/bin/env python3
"""SLC-B — Validate server_profile_creation_contract_v1.json (extended for SLC-BE)."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_b_server_profile_creation_contract_v1'


def main() -> int:
    errs = []
    j = load_json('server_profile_creation_contract_v1.json')
    # Core flags
    for flag in ('design_only', 'runtime_attached', 'battle_runtime_attached', 'db_write',
                 'migration_required_before_runtime', 'second_server_opening_allowed'):
        require(flag in j, f'missing flag {flag}', errs)
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('runtime_attached') is False, 'runtime_attached must be False', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    require(j.get('migration_required_before_runtime') is True, 'migration_required_before_runtime must be True', errs)
    require(j.get('second_server_opening_allowed') is False, 'second_server_opening_allowed must be False', errs)
    require(j.get('future_feature_flag') == 'SERVER_PROFILES_RUNTIME_ENABLED', 'future_feature_flag must be SERVER_PROFILES_RUNTIME_ENABLED', errs)
    require(j.get('default_server_id_for_legacy') == 's1', 'default_server_id_for_legacy must be s1', errs)
    require(j.get('implementation_status') == 'NOT_IMPLEMENTED_IN_RUNTIME', 'implementation_status must be NOT_IMPLEMENTED_IN_RUNTIME', errs)
    # future_flow has the 5 expected steps in correct order
    ff = j.get('future_flow', [])
    require(len(ff) >= 5, f'future_flow must have >=5 steps (got {len(ff)})', errs)
    require(any('login_global_account' in s for s in ff), 'future_flow missing login_global_account', errs)
    require(any('zero_server_bound_progression' in s for s in ff), 'future_flow missing zero_server_bound_progression', errs)
    # scope_rules
    sr = j.get('scope_rules', {})
    require(sr.get('starter_heroes_and_rewards_scope') == 'server_bound', 'starter_heroes scope must be server_bound', errs)
    require(sr.get('free_currency_scope') == 'server_bound', 'free_currency_scope must be server_bound', errs)
    require(sr.get('paid_currency_scope') == 'account_wide', 'paid_currency_scope must be account_wide', errs)
    require(sr.get('vip_level_scope') == 'account_wide', 'vip_level_scope must be account_wide', errs)
    require(sr.get('vip_claims_and_rewards_scope') == 'server_bound', 'vip_claims_and_rewards_scope must be server_bound', errs)
    require(sr.get('paid_cosmetics_ownership_scope') == 'account_wide', 'paid_cosmetics_ownership_scope must be account_wide', errs)
    require(sr.get('paid_cosmetics_equip_and_use_scope') == 'server_bound', 'paid_cosmetics_equip_and_use_scope must be server_bound', errs)
    require(sr.get('active_title_scope') == 'server_bound', 'active_title_scope must be server_bound', errs)
    # invariants
    inv = j.get('invariants', {})
    require(inv.get('borea_never_exposed') is True, 'invariants.borea_never_exposed must be True', errs)
    require(inv.get('no_cross_server_data_transfer') is True, 'invariants.no_cross_server_data_transfer must be True', errs)
    require(inv.get('paid_currency_balance_not_cloned_to_server_profile') is True, 'paid balance not cloned to server profile', errs)
    require(inv.get('no_inherited_roster_from_other_servers') is True, 'no_inherited_roster invariant', errs)
    require(inv.get('no_inherited_free_currency_from_other_servers') is True, 'no_inherited_free_currency invariant', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
