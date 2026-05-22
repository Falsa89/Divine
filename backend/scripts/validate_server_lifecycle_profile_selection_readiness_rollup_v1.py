#!/usr/bin/env python3
"""SLC-BE — Validate readiness rollup JSON."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import finish, require  # noqa: E402

NAME = 'slc_be_readiness_rollup_v1'
P = Path('/app/data/design/system_safety/server_lifecycle_profile_selection_readiness_rollup_v1.json')


def main() -> int:
    errs = []
    require(P.exists(), f'rollup file missing: {P}', errs)
    if not P.exists():
        return finish(NAME, errs)
    j = json.loads(P.read_text())
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    s = j.get('state', {})
    for k, exp in (
        ('server_profile_contract_ready', True),
        ('server_selection_contract_ready', True),
        ('active_server_resolution_contract_ready', True),
        ('new_player_routing_policy_ready', True),
        ('server_status_transition_policy_ready', True),
        ('dry_run_scenarios_ready', True),
        ('runtime_safety_audit_ready', True),
        ('runtime_enabled', False),
        ('db_write', False),
        ('migration_applied', False),
        ('second_server_opening_allowed', False),
        ('route_patch_required', True),
        ('default_s1_migration_required', True),
        ('borea_safe', True),
        ('af2n_invariant_intact', True),
    ):
        require(s.get(k) is exp, f'state.{k} must be {exp} (got {s.get(k)})', errs)
    blockers = j.get('blockers_to_runtime_enable', [])
    require(len(blockers) >= 5, f'expected >=5 blockers (got {len(blockers)})', errs)
    ff = {f.get('name'): f for f in j.get('future_feature_flags', [])}
    for k in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SERVER_AWARE_READS_ENABLED', 'SERVER_AWARE_WRITES_ENABLED', 'SECOND_SERVER_OPENING_ENABLED'):
        require(k in ff, f'future_feature_flags missing {k}', errs)
        require(ff.get(k, {}).get('current_value') is False, f'{k} current_value must be False', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
