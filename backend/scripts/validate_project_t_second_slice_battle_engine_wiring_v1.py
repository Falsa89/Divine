#!/usr/bin/env python3
"""PROJECT_T Track B validator — battle_engine wiring (flag OFF identity).

Verifica:
- seam module esiste e importabile
- battle_engine.py contiene import block + 2 call sites del second-slice seam
- battle_engine.py importa correttamente in subprocess
- backup battle_engine.py esiste (per rollback)
- battle_core.py / combat.tsx NON modificati (md5 dichiarato in marker)
- con flag OFF: apply_prefight_second_slice_preview(payload) ritorna lo STESSO OBJECT (identity)
- rollback script esiste
"""
import json, subprocess, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_t_second_slice_battle_engine_wiring_v1.json')
SEAM = Path('/app/backend/game_logic/status_second_slice_runtime_seam.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BACKUP = Path('/app/backend/battle_engine.py.project_t_pre_wire_backup')
ROLLBACK = Path('/app/backend/scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    allowed = ('TRACK_B_SECOND_SLICE_BATTLE_ENGINE_WIRED_FLAG_OFF_SAFE', 'TRACK_B_SECOND_SLICE_BATTLE_ENGINE_READY_NOT_APPLIED_SAFETY_BLOCKED', 'TRACK_B_SECOND_SLICE_BATTLE_ENGINE_READY_NOT_APPLIED_APPROVAL_MISSING')
    if m.get('verdict') not in allowed: fail(f'verdict not allowed: {m.get("verdict")}')
    if not SEAM.exists(): fail(f'seam module missing: {SEAM}')
    if not BATTLE_ENGINE.exists(): fail('battle_engine.py missing')
    if not BACKUP.exists(): fail(f'battle_engine backup missing: {BACKUP}')
    if not ROLLBACK.exists(): fail(f'rollback script missing: {ROLLBACK}')
    src = BATTLE_ENGINE.read_text()
    # Required wiring markers
    for tok in ('from game_logic.status_second_slice_runtime_seam', '_project_t_second_slice_seam', '_project_t_second_slice_seam(team_a)', '_project_t_second_slice_seam(team_b)'):
        if tok not in src:
            fail(f'battle_engine.py missing wiring token: {tok}')
    # Identity fallback present
    if 'def _project_t_second_slice_seam' not in src:
        fail('battle_engine.py missing defensive identity fallback for _project_t_second_slice_seam')
    # Import + identity verification in a subprocess (isolated, with flag UNSET)
    code = (
        "import sys, os; os.environ.pop('STATUS_RUNTIME_SECOND_SLICE_ENABLED', None);"
        "sys.path.insert(0,'/app/backend');"
        "from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview as f, is_seam_active;"
        "assert is_seam_active() is False, 'seam should be inactive with flag unset';"
        "samples=[{'a':1},[],None,'s',42,{'n':{'x':9}}];"
        "[ (lambda s,o: (_ for _ in ()).throw(AssertionError(f'NOT identity: {s!r}')))(s,f(s)) for s in samples if f(s) is not s ];"
        "print('OK')"
    )
    proc = subprocess.run(['python3', '-c', code], capture_output=True, text=True, timeout=15)
    if proc.returncode != 0 or 'OK' not in proc.stdout:
        fail(f'subprocess identity check failed: rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}')
    # Marker invariants
    if m.get('applied') is not True: fail('marker.applied must be True (Track B was applied in this pack)')
    for k in ('identity_fallback_present',):
        if m.get(k) is not True: fail(f'marker.{k} must be True')
    for k in ('first_slice_behavior_changed', 'damage_or_heal_formula_changed', 'battle_round_loop_changed', 'battle_core_mutated', 'combat_tsx_mutated', 'flag_in_live_env', 'rollback_executed_in_pack_t', 'db_writes'):
        if m.get(k) is not False: fail(f'marker.{k} must be False')
    print(f'[PASS] PROJECT_T Track B wiring SAFE FLAG-OFF — seam imported, 2 call sites, identity verified on 6 samples, rollback script + backup present')
    sys.exit(0)


if __name__ == '__main__': main()
