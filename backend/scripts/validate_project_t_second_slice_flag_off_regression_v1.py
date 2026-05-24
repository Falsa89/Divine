#!/usr/bin/env python3
"""PROJECT_T Track C validator — flag OFF byte-identical (runtime-equivalent) guard.

Verifica che con flag OFF il seam ritorni STRETTAMENTE l'oggetto in input (identity
per id()). Esegue la verifica in un subprocess isolato (tempfile) dove la env var
è stata rimossa esplicitamente. Verifica anche che il backup di battle_engine.py
sia uguale byte-per-byte al pre-pack md5.
"""
import hashlib, json, subprocess, sys, tempfile, textwrap
from pathlib import Path

M = Path('/app/data/design/status_effects/project_t_second_slice_flag_off_regression_v1.json')
BACKUP = Path('/app/backend/battle_engine.py.project_t_pre_wire_backup')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


SCRIPT = textwrap.dedent('''
    import os, sys
    os.environ.pop('STATUS_RUNTIME_SECOND_SLICE_ENABLED', None)
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview as f
    from game_logic.status_prefight_runtime_seam import apply_prefight_status_slice_preview as g

    # Mimic simulate_battle 2-call pattern with both first-slice and second-slice seams.
    team_a = {'team': 'a', 'heroes': [{'hp': 100}]}
    team_b = {'team': 'b', 'heroes': [{'hp': 100}]}
    orig_a, orig_b = team_a, team_b

    team_a = g(team_a)
    team_b = g(team_b)
    team_a = f(team_a)
    team_b = f(team_b)

    assert team_a is orig_a, 'team_a identity broken'
    assert team_b is orig_b, 'team_b identity broken'
    print('IDENTITY_OK')
''')


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_SECOND_SLICE_FLAG_OFF_BYTE_IDENTICAL_GUARD_READY': fail('verdict mismatch')
    if m.get('normalization_used') is not False: fail('normalization_used must be False (we use strict identity)')
    if m.get('gameplay_relevant_field_changed_with_flag_off') is not False: fail('gameplay_relevant_field_changed_with_flag_off must be False')
    if m.get('runtime_byte_identical_when_flag_off') is not True: fail('runtime_byte_identical_when_flag_off must be True')
    if not BACKUP.exists(): fail(f'backup missing: {BACKUP}')
    backup_md5 = hashlib.md5(BACKUP.read_bytes()).hexdigest()
    declared = m.get('battle_engine_md5_pre_pack')
    if backup_md5 != declared:
        fail(f'backup md5 {backup_md5} != declared pre-pack md5 {declared}')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT)
        tmp_path = tf.name
    try:
        proc = subprocess.run(['python3', tmp_path], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if proc.returncode != 0 or 'IDENTITY_OK' not in proc.stdout:
        fail(f'identity check failed: rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_T Track C flag-OFF runtime-byte-identical guard READY — backup md5 matches declared, double-seam call preserves identity')
    sys.exit(0)


if __name__ == '__main__': main()
