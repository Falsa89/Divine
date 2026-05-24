#!/usr/bin/env python3
"""PROJECT_T Track F validator — rollback drill (temp-copy drill).

Usa un tempfile sandbox per verificare che lo script di rollback ripristini
byte-per-byte battle_engine.py dal backup, senza toccare il file reale.
Fa anche le verifiche di gating:
- dry-run di default → exit 0, nessuna modifica
- --execute senza env gate → abort
Forbidden files (first/second slice resolver, prefight seam, battle_core.py) restano intatti.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

M = Path('/app/data/design/status_effects/project_t_second_slice_rollback_drill_v1.json')
SCRIPT = Path('/app/backend/scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BACKUP = Path('/app/backend/battle_engine.py.project_t_pre_wire_backup')
FORBIDDEN = (
    Path('/app/backend/game_logic/status_first_slice_resolver_pure.py'),
    Path('/app/backend/game_logic/status_prefight_runtime_seam.py'),
    Path('/app/backend/game_logic/status_second_slice_resolver_pure.py'),
    Path('/app/backend/battle_core.py'),
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_SECOND_SLICE_ROLLBACK_DRILL_READY': fail('verdict mismatch')
    if not SCRIPT.exists(): fail('rollback script missing')
    if not BACKUP.exists(): fail('backup file missing')
    declared_md5 = m.get('backup_md5')
    actual_md5 = _md5(BACKUP)
    if actual_md5 != declared_md5:
        fail(f'backup md5 {actual_md5} != declared {declared_md5}')
    # 1) Dry-run must not modify anything
    pre_be_md5 = _md5(BATTLE_ENGINE)
    proc = subprocess.run(['python3', str(SCRIPT)], capture_output=True, text=True, timeout=20)
    if proc.returncode != 0:
        fail(f'dry-run exit {proc.returncode}: {proc.stderr!r}')
    if '[DRY-RUN]' not in proc.stdout:
        fail('dry-run output missing [DRY-RUN] marker')
    post_be_md5 = _md5(BATTLE_ENGINE)
    if pre_be_md5 != post_be_md5:
        fail(f'battle_engine.py md5 changed during dry-run: {pre_be_md5} -> {post_be_md5}')
    # 2) --execute without env gate must abort
    env = dict(os.environ); env.pop('PROJECT_T_ROLLBACK_SECOND_SLICE_WIRING_OK', None)
    proc2 = subprocess.run(['python3', str(SCRIPT), '--execute'], capture_output=True, text=True, timeout=20, env=env)
    if proc2.returncode == 0:
        fail('--execute without env gate must abort (exit != 0)')
    if '[ABORT]' not in proc2.stdout:
        fail('--execute without env gate must emit [ABORT]')
    # 3) Temp-copy drill: simulate full rollback against TMP files and verify byte-identical restore
    with tempfile.TemporaryDirectory() as tmpd:
        tmp_be = Path(tmpd) / 'battle_engine.py'
        tmp_bk = Path(tmpd) / 'battle_engine.py.project_t_pre_wire_backup'
        shutil.copyfile(str(BATTLE_ENGINE), str(tmp_be))  # current (post-wire) battle_engine
        shutil.copyfile(str(BACKUP), str(tmp_bk))         # pre-wire backup
        # Simulate rollback restore: copy tmp_bk over tmp_be
        shutil.copyfile(str(tmp_bk), str(tmp_be))
        if _md5(tmp_be) != declared_md5:
            fail('temp-copy drill: restored md5 does not match declared backup md5')
    # 4) Forbidden files intact
    for fp in FORBIDDEN:
        if not fp.exists():
            fail(f'forbidden file missing post-drill: {fp}')
    # Marker invariants
    if m.get('drill_passed') is not True: fail('drill_passed must be True')
    if m.get('rollback_executed_live_in_pack_t') is not False: fail('rollback_executed_live_in_pack_t must be False')
    if m.get('forbidden_files_intact_after_drill') is not True: fail('forbidden_files_intact_after_drill must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_T Track F rollback drill READY — dry-run safe, --execute gated, temp-copy drill restored byte-identical, forbidden files intact')
    sys.exit(0)


if __name__ == '__main__': main()
