#!/usr/bin/env python3
"""PROJECT_Q Track D validator — bonus cap + economy dry-run.

Verifica:
- global master cap 5.0%
- per-artifact max 1.5%
- max simultaneous active artifacts per account == 4
- per_account_theoretical_max_total_bonus_pct <= 5.0
- cap_compliance: tutti compliant
- db_writes_in_dry_run == 0
- live_economy_touched == false
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_bonus_cap_economy_dry_run_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_ARTIFACT_BONUS_CAP_AND_ECONOMY_DRY_RUN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if float(m.get('global_roster_account_bonus_master_cap_pct', -1)) != 5.0:
        fail('master cap must be 5.0%')
    if float(m.get('per_artifact_max_value_pct', -1)) > 1.5:
        fail('per-artifact max must be <= 1.5%')
    if int(m.get('max_simultaneous_active_artifacts_per_account', 0)) > 4:
        fail('max simultaneous active artifacts must be <= 4')
    theo = float(m.get('per_account_theoretical_max_total_bonus_pct', 0.0))
    if theo > 5.0:
        fail(f'per_account_theoretical_max_total_bonus_pct {theo} exceeds master cap 5.0%')
    eco = m.get('economy_dry_run') or {}
    if int(eco.get('db_writes_in_dry_run', -1)) != 0:
        fail('economy_dry_run.db_writes_in_dry_run must be 0')
    if eco.get('live_economy_touched') is not False:
        fail('economy_dry_run.live_economy_touched must be False')
    for entry in (m.get('cap_compliance_per_candidate') or []):
        if entry.get('compliant') is not True:
            fail(f'cap non-compliant candidate: {entry.get("artifact_id")}')
        if float(entry.get('value_pct', 99)) > 1.5:
            fail(f'{entry.get("artifact_id")} value_pct > 1.5')
    if m.get('all_candidates_compliant') is not True:
        fail('all_candidates_compliant must be True')
    print('[PASS] PROJECT_Q Track D bonus cap + economy dry-run READY — caps respected, 0 DB writes')
    sys.exit(0)


if __name__ == '__main__':
    main()
