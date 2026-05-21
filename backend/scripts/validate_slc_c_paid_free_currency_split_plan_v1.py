#!/usr/bin/env python3
"""SLC-C — validate paid_free_currency_split_plan_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require, no_borea_anywhere  # noqa: E402

NAME = 'slc_c_paid_free_currency_split_plan_v1'


def main() -> int:
    errs = []
    j = load_json('paid_free_currency_split_plan_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    r = j.get('rules', {})
    for k in ('paid_divine_crystals_account_wide', 'paid_currency_ledger_account_wide',
              'free_crystals_server_bound', 'gold_server_bound', 'event_currencies_server_bound',
              'no_free_currency_cross_server_transfer', 'vip_level_account_wide'):
        require(r.get(k) is True, f'rules.{k} must be true', errs)
    require(r.get('paid_spend_visibility_per_server_is_view_not_balance_clone') is True, 'paid balance must not be cloned per server (view-only)', errs)
    inv = j.get('runtime_invariants', {})
    require(inv.get('no_live_economy_change_in_this_task') is True, 'no live economy change in this task', errs)
    require(inv.get('paid_balance_never_cloned_per_server') is True, 'paid_balance never cloned per server', errs)
    require(inv.get('free_balance_never_global') is True, 'free balance never global', errs)
    require(j.get('borea_safety', {}).get('borea_never_referenced_in_currency_documents') is True, 'borea_safety required', errs)
    leaks = no_borea_anywhere(j)
    require(not leaks, f'borea leak: {leaks}', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
