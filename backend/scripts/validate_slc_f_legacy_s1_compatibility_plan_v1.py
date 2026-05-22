#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402

NAME = 'slc_f_legacy_s1_compatibility_plan_v1'


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_legacy_s1_compatibility_plan_v1.json')
    require_design_only(j, errs, NAME)
    require(j.get('backfill_executed') is False, 'backfill_executed must be False', errs)
    require(j.get('default_legacy_server_id') == 's1', f'default_legacy_server_id must be s1 (got {j.get("default_legacy_server_id")})', errs)
    cw = j.get('compatibility_window', {})
    require(cw.get('single_shard_runtime') is True, 'compatibility_window.single_shard_runtime must be True', errs)
    require(cw.get('second_server_opening_allowed') is False, 'compatibility_window.second_server_opening_allowed must be False', errs)
    require(cw.get('after_migration_default_s1_for_all_legacy_accounts') is True, 'after_migration default s1 for all legacy accounts must be True', errs)
    phases = j.get('phases', [])
    nums = [p.get('phase') for p in phases]
    require(0 in nums and 11 in nums, 'phases must include phase 0 and phase 11', errs)
    p11 = next((p for p in phases if p.get('phase') == 11), None)
    require(p11 is not None, 'phase 11 missing', errs)
    if p11:
        require(p11.get('reversible') is False, 'phase 11 must be reversible=False', errs)
        require(p11.get('requires_explicit_user_approval') is True, 'phase 11 must require explicit user approval', errs)
    af2n = j.get('af2n_preservation_during_compatibility', {})
    require(af2n.get('cap') == 50000, f'af2n cap must be 50000 (got {af2n.get("cap")})', errs)
    require(af2n.get('allowlist') == 2500, f'af2n allowlist must be 2500 (got {af2n.get("allowlist")})', errs)
    return finish(NAME, errs, extra={'phase_count': len(phases)})


if __name__ == '__main__':
    sys.exit(main())
