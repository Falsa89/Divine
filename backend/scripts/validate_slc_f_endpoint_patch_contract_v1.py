#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402

NAME = 'slc_f_endpoint_patch_contract_v1'
REQUIRED_ENDPOINTS = {
    'GET /api/user/heroes', 'POST /api/team', 'GET /api/inventory',
    'POST /api/gacha/pull', 'GET /api/account/profile', 'GET /api/account/wallet/paid',
    'GET /api/server/wallet/free', 'POST /api/affinity/gift-spend',
    'GET /api/heroes (list)', 'GET /api/heroes/{id}', 'GET /api/cosmetics/owned',
    'POST /api/cosmetics/equip', 'GET /api/rankings', 'GET /api/guild',
}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_endpoint_patch_contract_v1.json')
    require_design_only(j, errs, NAME)
    require(j.get('do_not_implement_routes_now') is True, 'do_not_implement_routes_now must be True', errs)
    rp = j.get('required_patterns', {})
    for k in ('server_bound_endpoints_require_resolved_profile',
              'account_wide_endpoints_explicitly_opt_out_of_server_id',
              'mixed_endpoints_split_into_account_wide_and_server_bound_reads',
              'global_catalog_endpoints_remain_unchanged'):
        require(rp.get(k) is True, f'required_patterns.{k} must be True', errs)
    eps = {e.get('endpoint') for e in j.get('endpoint_pseudo_diffs', [])}
    missing = REQUIRED_ENDPOINTS - eps
    require(not missing, f'endpoint_pseudo_diffs missing: {sorted(missing)}', errs)
    # AF2-N protected endpoint must declare cap preservation
    af2n_ep = next((e for e in j['endpoint_pseudo_diffs'] if e.get('endpoint') == 'POST /api/affinity/gift-spend'), None)
    require(af2n_ep is not None, 'AF2-N endpoint missing', errs)
    if af2n_ep is not None:
        require(af2n_ep.get('protected') is True, 'AF2-N endpoint must be protected=True', errs)
        require('50000' in af2n_ep.get('af2n_invariant', ''), 'AF2-N endpoint must declare cap=50000 invariant', errs)
        require('2500' in af2n_ep.get('af2n_invariant', ''), 'AF2-N endpoint must declare allowlist=2500 invariant', errs)
    # Heroes list+detail must be protected and global_catalog_readonly
    for tag in ('GET /api/heroes (list)', 'GET /api/heroes/{id}'):
        e = next((x for x in j['endpoint_pseudo_diffs'] if x.get('endpoint') == tag), None)
        require(e and e.get('scope') == 'global_catalog_readonly', f'{tag} must be global_catalog_readonly', errs)
        require(e and e.get('protected') is True, f'{tag} must be protected=True', errs)
    # New dependencies declared
    deps = {d.get('name') for d in j.get('new_dependencies_future', [])}
    require({'get_current_user', 'get_current_server_profile'}.issubset(deps), 'new_dependencies_future must include both get_current_user and get_current_server_profile', errs)
    return finish(NAME, errs, extra={'endpoint_count': len(eps)})


if __name__ == '__main__':
    sys.exit(main())
