#!/usr/bin/env python3
"""SLC-C — validate server_profile_creation_contract_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_server_profile_creation_contract_v1'


def main() -> int:
    errs = []
    j = load_json('server_profile_creation_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('implementation_status') == 'NOT_IMPLEMENTED_IN_RUNTIME', 'implementation_status must be NOT_IMPLEMENTED_IN_RUNTIME', errs)
    c = j.get('contract', {})
    require(set(c.get('inputs_required', [])) >= {'account_id', 'target_server_id'}, 'inputs_required must include account_id+target_server_id', errs)
    require(c.get('creates', {}).get('unique_key') == ['account_id', 'server_id'], 'unique_key must be [account_id,server_id]', errs)
    inv = j.get('invariants', {})
    require(inv.get('no_cross_server_data_transfer') is True, 'no_cross_server_data_transfer must be true', errs)
    require(inv.get('borea_never_exposed') is True, 'borea_never_exposed must be true', errs)
    require(inv.get('paid_currency_balance_not_cloned_to_server_profile') is True, 'paid_currency not cloned to server_profile', errs)
    require(c.get('idempotency', {}).get('replay_returns_existing_profile') is True, 'idempotent replay must return existing profile', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
