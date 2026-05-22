#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_risk_matrix_v1'


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_risk_matrix_v1.json')
    require_design_only(j, errs, NAME)
    risks = j.get('risks', [])
    require(len(risks) >= 8, f'must have >=8 risks (got {len(risks)})', errs)
    levels = {r.get('level') for r in risks}
    require(levels == {'P0', 'P1', 'P2'}, f'levels must be exactly P0/P1/P2 (got {levels})', errs)
    for r in risks:
        require(r.get('mitigation'), f'risk {r.get("id")}: mitigation required', errs)
    inv = j.get('global_invariants_enforced', {})
    require(inv.get('af2n_cap') == 50000 and inv.get('af2n_allowlist') == 2500, 'global_invariants.af2n cap/allowlist mismatch', errs)
    require(inv.get('api_heroes_count') == 100, 'global_invariants.api_heroes_count must be 100', errs)
    require(inv.get('primordial_gaia_status') == 404, 'global_invariants.primordial_gaia_status must be 404', errs)
    require(inv.get('merge_execution_allowed') is False, 'merge_execution_allowed must be False', errs)
    return finish(NAME, errs, extra={'risk_count': len(risks)})


if __name__ == '__main__':
    sys.exit(main())
