#!/usr/bin/env python3
"""PROJECT_S Track F validator — rollback + deletion plan.

Verifica che lo script rollback esista, default sia dry-run, --execute richieda il gate env,
che la lista deletion_targets non contenga forbidden files (first-slice, battle_engine, battle_core).
Esegue lo script in modalita' dry-run per verificare exit=0 e nessuna cancellazione.
"""
import json, os, subprocess, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_s_second_slice_rollback_deletion_plan_v1.json')
SCRIPT = Path('/app/backend/scripts/rollback_project_s_status_second_slice_pure_resolver.py')
FORBIDDEN = {
    '/app/backend/game_logic/status_first_slice_resolver_pure.py',
    '/app/backend/game_logic/status_prefight_runtime_seam.py',
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_SECOND_SLICE_ROLLBACK_AND_DELETION_PLAN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if not SCRIPT.exists():
        fail(f'rollback script missing: {SCRIPT}')
    src = SCRIPT.read_text()
    if '--execute' not in src or 'PROJECT_S_ROLLBACK_PURE_RESOLVER_OK' not in src:
        fail('rollback script missing --execute flag or env gate marker')
    if m.get('rollback_executed_in_pack_s') is not False:
        fail('rollback_executed_in_pack_s must be False')
    if m.get('rollback_default_mode') != 'dry-run':
        fail('rollback_default_mode must be dry-run')
    if m.get('rollback_execute_requires_explicit_env_marker') is not True:
        fail('rollback_execute_requires_explicit_env_marker must be True')
    # Check forbidden_to_delete contains all critical files
    declared_forbidden = set(m.get('forbidden_to_delete') or [])
    missing = FORBIDDEN - declared_forbidden
    if missing:
        fail(f'forbidden_to_delete missing entries: {sorted(missing)}')
    targets = set(m.get('deletion_targets') or [])
    overlap = targets & FORBIDDEN
    if overlap:
        fail(f'deletion_targets contains forbidden files: {sorted(overlap)}')
    # Run dry-run; must exit 0 and not delete anything
    proc = subprocess.run(['python3', str(SCRIPT)], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        fail(f'dry-run rollback returned {proc.returncode}: {proc.stderr.strip()}')
    if '[DRY-RUN]' not in proc.stdout:
        fail('dry-run rollback did not emit [DRY-RUN] marker')
    # Verify forbidden files still present (untouched)
    for fp in FORBIDDEN:
        if not Path(fp).exists():
            fail(f'CRITICAL: forbidden file no longer present after dry-run (must be untouched): {fp}')
    # Verify --execute without env gate aborts
    env = dict(os.environ); env.pop('PROJECT_S_ROLLBACK_PURE_RESOLVER_OK', None)
    proc2 = subprocess.run(['python3', str(SCRIPT), '--execute'], capture_output=True, text=True, timeout=30, env=env)
    if proc2.returncode == 0:
        fail('--execute without env gate must abort (exit != 0)')
    if '[ABORT]' not in proc2.stdout:
        fail('--execute without env gate must emit [ABORT]')
    if m.get('db_writes') is not False:
        fail('db_writes must be False')
    print('[PASS] PROJECT_S Track F rollback + deletion plan READY — dry-run OK, --execute gated, forbidden files untouched')
    sys.exit(0)


if __name__ == '__main__': main()
