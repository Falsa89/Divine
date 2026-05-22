#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402

NAME = 'slc_f_route_patch_risk_matrix_v1'
ALLOWED_LEVELS = {'P0', 'P1', 'P2'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_route_patch_risk_matrix_v1.json')
    require_design_only(j, errs, NAME)
    risks = j.get('risks', [])
    require(len(risks) >= 8, f'must have >=8 risks (got {len(risks)})', errs)
    levels = {r.get('level') for r in risks}
    require(levels.issubset(ALLOWED_LEVELS), f'invalid risk levels: {levels - ALLOWED_LEVELS}', errs)
    require('P0' in levels and 'P1' in levels and 'P2' in levels, f'must contain at least one of each P0/P1/P2 (got {levels})', errs)
    for r in risks:
        require(r.get('mitigation'), f'risk {r.get("id")}: mitigation required', errs)
    inv = j.get('global_invariants_enforced', {})
    require(inv.get('af2n_cap') == 50000, 'global_invariants_enforced.af2n_cap must be 50000', errs)
    require(inv.get('af2n_allowlist') == 2500, 'global_invariants_enforced.af2n_allowlist must be 2500', errs)
    require(inv.get('api_heroes_count') == 100, 'global_invariants_enforced.api_heroes_count must be 100', errs)
    require(inv.get('primordial_gaia_status') == 404, 'global_invariants_enforced.primordial_gaia_status must be 404', errs)
    require(inv.get('server_profiles_runtime_enabled') is False, 'server_profiles_runtime_enabled must be False', errs)
    require(inv.get('second_server_opening_enabled') is False, 'second_server_opening_enabled must be False', errs)
    return finish(NAME, errs, extra={'risk_count': len(risks)})


if __name__ == '__main__':
    sys.exit(main())
