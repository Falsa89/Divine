#!/usr/bin/env python3
"""PROJECT_V Track F validator — rollback/kill-switch drill."""
import hashlib, json, subprocess, sys, tempfile, textwrap
from pathlib import Path
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_rollback_kill_switch_v1.json')
ENV = Path('/app/backend/.env'); BACKUP = Path('/app/backend/.env.project_v_pre_flip_backup'); BE = Path('/app/backend/battle_engine.py')
FLAG = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'
SCRIPT_IDENTITY = textwrap.dedent('''
    import os, sys
    os.environ.pop('STATUS_RUNTIME_SECOND_SLICE_ENABLED', None)
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview, is_seam_active
    assert is_seam_active() is False
    for s in [{'a':1}, [], None, 's', 42, {'n':{'x':9}}]:
        assert apply_prefight_second_slice_preview(s) is s
    print('IDENTITY_OK')
''')
def fail(msg): print(f'[FAIL] {msg}'); sys.exit(1)
def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_SECOND_SLICE_DEV_LIVE_ROLLBACK_KILL_SWITCH_READY': fail('verdict mismatch')
    if not BACKUP.exists(): fail('backup missing')
    if _md5(ENV) != _md5(BACKUP): fail('env md5 != backup md5 (rollback incomplete)')
    if any(ln.strip().startswith(FLAG + '=') for ln in ENV.read_text().splitlines()): fail(f'{FLAG} still in .env')
    if _md5(BE) != m.get('battle_engine_md5_post_rollback'): fail('battle_engine md5 != declared')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT_IDENTITY); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'IDENTITY_OK' not in proc.stdout: fail(f'identity check failed: {proc.stdout!r}')
    api = m.get('api_smoke_post_rollback') or {}
    if api.get('/api/heroes') != 200: fail('api smoke post-rollback mismatch')
    if m.get('rollback_within_target') is not True: fail('rollback_within_target must be True')
    if m.get('battle_engine_unchanged_during_rollback') is not True: fail('battle_engine_unchanged must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_V Track F rollback kill-switch drill READY — .env byte-identical, flag absent, battle_engine intact, identity OK')
    sys.exit(0)
if __name__ == '__main__': main()
