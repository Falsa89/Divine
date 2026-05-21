#!/usr/bin/env python3
"""SLC-C — validate account_wide_document_contract_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require, no_borea_anywhere  # noqa: E402

NAME = 'slc_c_account_wide_document_contract_v1'


def main() -> int:
    errs = []
    j = load_json('account_wide_document_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('runtime_attached') is False, 'runtime_attached must be false', errs)
    c = j.get('contract', {})
    require('account_id' in c.get('required_fields_every_doc', []), 'contract requires account_id in every doc', errs)
    cols = set(c.get('applies_to_collections', []))
    for k in ('users', 'accounts_wallet_paid', 'accounts_wallet_paid_ledger', 'account_cosmetics'):
        require(k in cols, f'applies_to_collections missing: {k}', errs)
    inv = j.get('borea_invariant', {})
    require(set(inv.get('borea_must_never_appear', [])) >= {'borea', 'greek_borea', 'primordial_gaia'}, 'borea_must_never_appear incomplete', errs)
    leaks = no_borea_anywhere(j.get('contract', {}))
    require(not leaks, f'borea leak in contract: {leaks}', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
