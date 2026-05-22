#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402

NAME = 'slc_f_collection_scope_matrix_v1'
REQUIRED_COLS = {'users','accounts_wallet_paid','accounts_wallet_paid_ledger','server_profiles',
                 'servers','server_wallets_free','user_heroes','teams','inventory','gacha_history',
                 'story_progress','guilds','arena_rankings','user_affinity_state',
                 'gift_transaction_ledger','user_gift_inventory','event_progress',
                 'account_cosmetics','heroes_catalog'}
ALLOWED_STRATEGIES = {'account_id_only','account_id_plus_server_id',
                      'account_id_plus_server_id_plus_entity_id','global_static_catalog'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_collection_scope_matrix_v1.json')
    require_design_only(j, errs, NAME)
    matrix = j.get('matrix', [])
    seen = {e.get('collection') for e in matrix}
    missing = REQUIRED_COLS - seen
    require(not missing, f'matrix missing collections: {sorted(missing)}', errs)
    for e in matrix:
        require(e.get('future_key_strategy') in ALLOWED_STRATEGIES, f'{e.get("collection")}: invalid future_key_strategy {e.get("future_key_strategy")}', errs)
        require(isinstance(e.get('unique_index_future'), list) and e.get('unique_index_future'), f'{e.get("collection")}: unique_index_future must be a non-empty list', errs)
    # AF2-N preservation flags
    for col in ('gift_transaction_ledger', 'user_gift_inventory'):
        e = next((x for x in matrix if x.get('collection') == col), None)
        require(e and e.get('af2n_preservation_required') is True, f'{col}: af2n_preservation_required must be True', errs)
    # paid wallet must remain account-wide
    pw = next((x for x in matrix if x.get('collection') == 'accounts_wallet_paid'), None)
    require(pw and pw.get('future_key_strategy') == 'account_id_only', 'accounts_wallet_paid must remain account_id_only', errs)
    return finish(NAME, errs, extra={'collection_count': len(matrix)})


if __name__ == '__main__':
    sys.exit(main())
