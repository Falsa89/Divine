#!/usr/bin/env python3
"""PROJECT_U Track F validator — rollback / kill-switch drill (post-rollback state).

Verifica che il rollback sia stato eseguito: .env e' byte-identico al backup pre-flip,
flag NON presente in .env, battle_engine.py md5 invariato (mai toccato dal flip),
seam ritorna identita' con flag OFF.
"""
import hashlib, json, subprocess, sys, tempfile, textwrap
from pathlib import Path

M = Path('/app/data/design/status_effects/project_u_second_slice_rollback_kill_switch_v1.json')
ENV = Path('/app/backend/.env')
BACKUP = Path('/app/backend/.env.project_u_pre_flip_backup')
BE = Path('/app/backend/battle_engine.py')
FLAG = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'

SCRIPT_IDENTITY = textwrap.dedent('''
    import os, sys
    os.environ.pop('STATUS_RUNTIME_SECOND_SLICE_ENABLED', None)
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview, is_seam_active
    assert is_seam_active() is False, 'flag should be OFF post-rollback'
    samples = [{'a':1}, [], None, 's', 42, {'n':{'x':9}}]
    for s in samples:
        out = apply_prefight_second_slice_preview(s)
        assert out is s, f'NOT identity for {s!r}'
    print('POST_ROLLBACK_IDENTITY_OK')
''')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_SECOND_SLICE_ROLLBACK_KILL_SWITCH_DRILL_READY': fail('verdict mismatch')
    if not BACKUP.exists(): fail('backup missing')
    env_md5 = _md5(ENV); backup_md5 = _md5(BACKUP)
    if env_md5 != backup_md5: fail(f'env md5 {env_md5} != backup md5 {backup_md5} (rollback incomplete)')
    env_txt = ENV.read_text()
    if any(ln.strip().startswith(FLAG + '=') for ln in env_txt.splitlines()):
        fail(f'{FLAG} still present in .env after rollback')
    declared_be = m.get('battle_engine_md5_post_rollback')
    actual_be = _md5(BE)
    if actual_be != declared_be: fail(f'battle_engine.py md5 {actual_be} != declared {declared_be}')
    # Run identity test
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT_IDENTITY); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'POST_ROLLBACK_IDENTITY_OK' not in proc.stdout:
        fail(f'post-rollback identity check failed: {proc.stdout!r} {proc.stderr!r}')
    api = m.get('api_smoke_post_rollback') or {}
    if api.get('/api/heroes') != 200 or api.get('/api/heroes/primordial_gaia') != 404: fail('api smoke post-rollback baseline mismatch')
    if m.get('rollback_within_target') is not True: fail('rollback_within_target must be True')
    if m.get('battle_engine_unchanged_during_rollback') is not True: fail('battle_engine_unchanged_during_rollback must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_U Track F rollback drill READY — .env byte-identical to backup, flag absent, battle_engine intact, identity verified')
    sys.exit(0)


if __name__ == '__main__': main()
