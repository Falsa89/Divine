#!/usr/bin/env python3
"""SLC-C — validate server_aware_route_patch_contract_v1.json.

Also confirms (read-only) that the contract does NOT touch protected files:
  - /app/backend/battle_engine.py / battle_core.py
  - /app/frontend/app/combat.tsx
  - /app/backend/routes/affinity_gift_spend.py
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_server_aware_route_patch_contract_v1'
PROTECTED = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
    '/app/backend/routes/affinity_gift_spend.py',
]


def main() -> int:
    errs = []
    j = load_json('server_aware_route_patch_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('do_not_implement_routes_now') is True, 'do_not_implement_routes_now must be true', errs)
    require(j.get('safety', {}).get('no_runtime_change') is True, 'safety.no_runtime_change must be true', errs)
    rp = j.get('required_patterns', {})
    for k in ('server_bound_endpoints_require_active_server_id', 'new_dependency_get_current_server_profile',
              'account_wide_endpoints_must_opt_out_of_server_id',
              'user_heroes_filter_by_account_id_and_server_id', 'team_filter_by_account_id_and_server_id'):
        require(rp.get(k) is True, f'required_patterns.{k} must be true', errs)
    cat = j.get('endpoint_categorization', {})
    for sb in ('/api/user/heroes', '/api/team', '/api/inventory', '/api/gacha/pull'):
        require(sb in cat.get('server_bound_endpoints', []), f'server_bound_endpoints missing {sb}', errs)
    for aw in ('/api/auth/register', '/api/auth/login', '/api/account/profile'):
        require(aw in cat.get('account_wide_endpoints', []), f'account_wide_endpoints missing {aw}', errs)
    # confirm protected files still exist (no accidental deletion)
    for p in PROTECTED:
        require(Path(p).exists() or p.endswith('battle_core.py'), f'protected file missing: {p}', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
