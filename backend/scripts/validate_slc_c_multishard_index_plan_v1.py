#!/usr/bin/env python3
"""SLC-C — validate multishard_index_plan_v1.json (no DB execution)."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_multishard_index_plan_v1'
MUST_HAVE_UNIQUE = {
    'servers': ('server_id',),
    'server_profiles': ('account_id', 'server_id'),
    'user_heroes': ('account_id', 'server_id', 'hero_id'),
    'gift_transaction_ledger': ('account_id', 'server_id', 'idempotency_key'),
    'user_gift_inventory': ('account_id', 'server_id', 'gift_id'),
    'accounts_wallet_paid': ('account_id',),
    'accounts_wallet_paid_ledger': ('account_id', 'tx_id'),
}


def main() -> int:
    errs = []
    j = load_json('multishard_index_plan_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('safety', {}).get('no_db_write') is True, 'safety.no_db_write must be true', errs)
    idx = j.get('indexes', [])
    for col, keys in MUST_HAVE_UNIQUE.items():
        match = [i for i in idx if i.get('collection') == col and i.get('unique') is True and tuple(i.get('keys', {}).keys()) == tuple(keys)]
        require(bool(match), f'missing required UNIQUE index on {col}: keys={keys}', errs)
    # no duplicate (collection, name)
    seen = set()
    for i in idx:
        key = (i.get('collection'), i.get('name'))
        if key in seen:
            errs.append(f'duplicate index: {key}')
        seen.add(key)
    return finish(NAME, errs, {'index_count': len(idx)})


if __name__ == '__main__':
    sys.exit(main())
