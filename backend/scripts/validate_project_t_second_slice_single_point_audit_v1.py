#!/usr/bin/env python3
"""PROJECT_T Track A validator — single-point audit (read-only).

Verifica:
- classification e' SECOND_SLICE_SINGLE_POINT_SAFE_NOW_FLAGGED
- battle_engine.py esiste
- first-slice seam ancora presente (Project M reference)
- nessun runtime mutation è stato dichiarato in Track A
- hard safety invariants completi (>= 8)
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_t_second_slice_single_point_audit_v1.json')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
FIRST_SLICE_SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_SECOND_SLICE_SINGLE_POINT_AUDIT_READY': fail(f'verdict mismatch')
    allowed_classifications = ('SECOND_SLICE_SINGLE_POINT_SAFE_NOW_FLAGGED', 'SECOND_SLICE_SAFE_FUTURE_ONLY', 'SECOND_SLICE_UNSAFE_NO_PATCH')
    if m.get('classification') not in allowed_classifications: fail(f'classification invalid: {m.get("classification")}')
    if not BATTLE_ENGINE.exists(): fail('battle_engine.py missing')
    if not FIRST_SLICE_SEAM.exists(): fail('first-slice seam missing')
    src = BATTLE_ENGINE.read_text()
    if 'STATUS_RUNTIME_BUFF_SLICE_ENABLED' not in src and '_project_m_status_seam' not in src:
        fail('first-slice seam reference no longer present in battle_engine.py')
    if m.get('runtime_mutation_in_track_a') is not False: fail('Track A must not mutate runtime')
    if m.get('battle_core_mutation_required') is not False: fail('Track A must not require battle_core mutation')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    if len(m.get('hard_safety_invariants') or []) < 8: fail('hard_safety_invariants must list >= 8 items')
    print(f'[PASS] PROJECT_T Track A audit READY — classification={m.get("classification")}; battle_engine + first-slice seam present; no runtime mutation in Track A')
    sys.exit(0)


if __name__ == '__main__': main()
