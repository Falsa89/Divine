#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_conflict_resolution_contract_v1'
REQUIRED_IDS = {
    'duplicate_player_name','duplicate_guild_name','duplicate_guild_tag',
    'active_title_collision','equipped_cosmetics_collision',
    'paid_currency_account_wide_preservation','free_currency_server_bound',
    'materials_server_bound','guild_membership_collision','guild_leadership_collision',
    'offline_leadership_handover','leaderboards_reset_settlement',
    'active_events_banners_shops','af2n_ledgers_inventory_preservation',
    'borea_visibility_unchanged',
}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_conflict_resolution_contract_v1.json')
    require_design_only(j, errs, NAME)
    seen = {c.get('id') for c in j.get('conflicts', [])}
    missing = REQUIRED_IDS - seen
    require(not missing, f'conflicts missing: {sorted(missing)}', errs)
    for c in j.get('conflicts', []):
        require(c.get('db_write') is False, f'conflict {c.get("id")}: db_write must be False', errs)
        require(c.get('strategy'), f'conflict {c.get("id")}: strategy required', errs)
    paid = next((c for c in j['conflicts'] if c.get('id') == 'paid_currency_account_wide_preservation'), None)
    require(paid and paid.get('af2n_safe') is True, 'paid_currency conflict must be af2n_safe', errs)
    require(paid and paid.get('reversible') is False, 'paid_currency conflict must be reversible=False (invariant)', errs)
    af2n = next((c for c in j['conflicts'] if c.get('id') == 'af2n_ledgers_inventory_preservation'), None)
    require(af2n and af2n.get('af2n_safe') is True, 'af2n conflict must be af2n_safe', errs)
    borea = next((c for c in j['conflicts'] if c.get('id') == 'borea_visibility_unchanged'), None)
    require(borea and borea.get('borea_safe') is True, 'borea conflict must be borea_safe', errs)
    inv = j.get('global_invariants', {})
    require(inv.get('paid_balance_never_cloned') is True, 'global_invariants.paid_balance_never_cloned must be True', errs)
    require(inv.get('af2n_cap') == 50000 and inv.get('af2n_allowlist') == 2500, 'global_invariants.af2n cap/allowlist mismatch', errs)
    return finish(NAME, errs, extra={'conflict_count': len(j.get('conflicts', []))})


if __name__ == '__main__':
    sys.exit(main())
