#!/usr/bin/env python3
"""SLC-C — validate server_bound_document_contract_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_server_bound_document_contract_v1'


def main() -> int:
    errs = []
    j = load_json('server_bound_document_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    c = j.get('contract', {})
    req = set(c.get('required_fields_every_doc', []))
    require({'account_id', 'server_id'}.issubset(req), 'server-bound docs must require account_id+server_id', errs)
    cols = set(c.get('applies_to_collections', []))
    for k in ('user_heroes', 'teams', 'inventory', 'server_wallets_free', 'gift_transaction_ledger', 'user_gift_inventory'):
        require(k in cols, f'applies_to_collections missing: {k}', errs)
    tr = j.get('transition_rules', {})
    require(tr.get('during_dual_read_window', {}).get('writes_must_already_include_server_id') is True, 'dual-read writes must include server_id', errs)
    require(tr.get('after_dual_read_window', {}).get('legacy_fallback_removed') is True, 'after dual-read window, legacy fallback removed', errs)
    require(set(j.get('borea_invariant', {}).get('borea_hero_ids_must_never_appear', [])) >= {'borea', 'greek_borea', 'primordial_gaia'}, 'borea invariant incomplete', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
