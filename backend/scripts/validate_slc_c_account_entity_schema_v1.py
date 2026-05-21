#!/usr/bin/env python3
"""SLC-C — validate account_entity_schema_v1.json (design-only)."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require, no_borea_anywhere  # noqa: E402

NAME = 'slc_c_account_entity_schema_v1'


def main() -> int:
    errs = []
    j = load_json('account_entity_schema_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('runtime_attached') is False, 'runtime_attached must be false', errs)
    require(j.get('battle_runtime_attached') is False, 'battle_runtime_attached must be false', errs)
    req = j.get('required_fields', [])
    for f in ('account_id', 'email', 'auth_provider', 'created_at', 'design_only'):
        require(f in req, f'required_fields missing: {f}', errs)
    awf = set(j.get('account_wide_fields', []))
    for f in ('vip_level', 'paid_currency_balance'):
        require(f in awf, f'account_wide_fields missing: {f}', errs)
    forb = set(j.get('forbidden_account_wide_fields', []))
    for f in ('gold', 'diamonds_free', 'event_currency', 'team_active', 'equipped_skin', 'affinity_points', 'arena_rank'):
        require(f in forb, f'forbidden_account_wide_fields missing: {f}', errs)
    require(j.get('safety', {}).get('no_db_write') is True, 'safety.no_db_write must be true', errs)
    leaks = no_borea_anywhere(j)
    require(not leaks, f'borea leak in schema: {leaks}', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
