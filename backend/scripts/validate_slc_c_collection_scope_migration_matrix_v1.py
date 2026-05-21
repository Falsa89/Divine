#!/usr/bin/env python3
"""SLC-C — validate collection_scope_migration_matrix_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_collection_scope_migration_matrix_v1'
MUST_HAVE_COLLECTIONS = {
    'users', 'servers', 'server_profiles', 'user_heroes', 'teams', 'inventory',
    'server_wallets_free', 'accounts_wallet_paid', 'accounts_wallet_paid_ledger',
    'gacha_history', 'story_progress', 'guilds', 'arena_rankings',
    'user_affinity_state', 'gift_transaction_ledger', 'user_gift_inventory',
    'event_progress',
}
ALLOWED_SCOPES = {'account_wide', 'server_bound', 'mixed'}
ALLOWED_PRIORITIES = {'P0', 'P1', 'P2', 'P3'}


def main() -> int:
    errs = []
    j = load_json('collection_scope_migration_matrix_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    entries = j.get('entries', [])
    require(len(entries) >= 15, f'expected >=15 entries, got {len(entries)}', errs)
    seen = set()
    for e in entries:
        cn = e.get('collection_name')
        require(bool(cn), 'entry missing collection_name', errs)
        if cn in seen:
            errs.append(f'duplicate collection_name: {cn}')
        seen.add(cn)
        for k in ('current_key_model', 'target_key_model', 'scope', 'migration_priority', 'rollback_strategy'):
            require(k in e, f'{cn}: missing field {k}', errs)
        require(e.get('scope') in ALLOWED_SCOPES, f'{cn}: invalid scope {e.get("scope")}', errs)
        require(e.get('migration_priority') in ALLOWED_PRIORITIES, f'{cn}: invalid priority {e.get("migration_priority")}', errs)
        # server_bound implies requires_server_id
        if e.get('scope') == 'server_bound':
            require(e.get('requires_server_id') is True, f'{cn}: server_bound must require server_id', errs)
        if e.get('scope') == 'account_wide':
            require(e.get('requires_server_id') is False, f'{cn}: account_wide must NOT require server_id', errs)
    missing = MUST_HAVE_COLLECTIONS - seen
    require(not missing, f'matrix missing required collections: {sorted(missing)}', errs)
    # AF2-N rows preservation note
    af2n = next((e for e in entries if e.get('collection_name') == 'gift_transaction_ledger'), None)
    require(af2n is not None and 'AF2-N' in (af2n.get('backfill_source', '') + af2n.get('rollback_strategy', '')), 'gift_transaction_ledger entry must reference AF2-N preservation', errs)
    return finish(NAME, errs, {'entry_count': len(entries)})


if __name__ == '__main__':
    sys.exit(main())
