#!/usr/bin/env python3
"""SLC-C — validate single_to_multishard_migration_phase_plan_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_single_to_multishard_migration_phase_plan_v1'


def main() -> int:
    errs = []
    j = load_json('single_to_multishard_migration_phase_plan_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('safety', {}).get('no_migration_executed') is True, 'no_migration_executed must be true', errs)
    require(j.get('safety', {}).get('no_db_write') is True, 'no_db_write must be true', errs)
    phases = j.get('phases', [])
    require(len(phases) >= 12, f'expected >=12 phases, got {len(phases)}', errs)
    nums = [p.get('phase') for p in phases]
    require(nums == sorted(nums), 'phases must be in ascending order', errs)
    require(len(set(nums)) == len(nums), 'duplicate phase numbers', errs)
    # irreversible phase 11 must require explicit approval
    p11 = next((p for p in phases if p.get('phase') == 11), None)
    require(p11 is not None, 'phase 11 missing', errs)
    if p11 is not None:
        require(p11.get('reversible') is False, 'phase 11 must be reversible=false', errs)
        require(p11.get('requires_explicit_user_approval') is True, 'phase 11 must require explicit user approval', errs)
    # phase 0 must include snapshot
    p0 = next((p for p in phases if p.get('phase') == 0), None)
    require(p0 is not None and any('snapshot' in a for a in p0.get('actions', [])), 'phase 0 must include snapshot', errs)
    return finish(NAME, errs, {'phase_count': len(phases)})


if __name__ == '__main__':
    sys.exit(main())
