#!/usr/bin/env python3
"""SLC-C — validate slc_c_multishard_rollback_plan_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_c_multishard_rollback_plan_v1'


def main() -> int:
    errs = []
    j = load_json('slc_c_multishard_rollback_plan_v1.json')
    require(j.get('design_only') is True, 'design_only must be true', errs)
    require(j.get('no_live_rollback_executed') is True, 'no_live_rollback_executed must be true', errs)
    br = j.get('backup_requirements', {})
    rc = set(br.get('required_collections', []))
    for k in ('users', 'user_heroes', 'teams', 'inventory', 'gift_transaction_ledger', 'user_gift_inventory'):
        require(k in rc, f'backup_requirements.required_collections missing {k}', errs)
    require(br.get('checksum_required') is True, 'checksum_required must be true', errs)
    # phase 11 must NOT be reversible
    require(11 not in j.get('reversible_phases', []), 'phase 11 must NOT be in reversible_phases', errs)
    require(11 in j.get('irreversible_phases_forbidden_without_approval', []), 'phase 11 must be forbidden without approval', errs)
    rv = j.get('restore_validation', {})
    checks = ' '.join(rv.get('checks', []))
    require('AF2-N' in checks, 'restore_validation must reference AF2-N preservation', errs)
    require('Borea' in checks or 'borea' in checks, 'restore_validation must reference Borea guard', errs)
    require('cap=50000' in checks, 'restore_validation must reference cap=50000 (Cap S2)', errs)
    require('heroes count 100' in checks, 'restore_validation must reference heroes count 100', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
