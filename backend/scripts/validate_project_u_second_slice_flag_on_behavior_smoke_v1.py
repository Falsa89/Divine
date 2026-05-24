#!/usr/bin/env python3
"""PROJECT_U Track C validator — flag ON behavior smoke (replayed in-process).

Replay del canary smoke per ottenere evidenza fresca, indipendente dal marker.
"""
import json, subprocess, sys, tempfile, textwrap
from pathlib import Path

M = Path('/app/data/design/status_effects/project_u_second_slice_flag_on_behavior_smoke_v1.json')

SCRIPT = textwrap.dedent('''
    import os, sys
    os.environ['STATUS_RUNTIME_SECOND_SLICE_ENABLED'] = 'true'
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview, is_seam_active
    assert is_seam_active() is True
    cases = [
        ('debuff_offensive', [{'family':'debuff_offensive','value_pct':15}], 'campaign', {'atk_pct':-15.0,'def_pct':0.0,'speed_pct':0.0}),
        ('debuff_defensive', [{'family':'debuff_defensive','value_pct':15}], 'campaign', {'atk_pct':0.0,'def_pct':-15.0,'speed_pct':0.0}),
        ('speed_up',         [{'family':'speed_up','value_pct':15}], 'campaign', {'atk_pct':0.0,'def_pct':0.0,'speed_pct':15.0}),
        ('speed_down',       [{'family':'speed_down','value_pct':15}], 'campaign', {'atk_pct':0.0,'def_pct':0.0,'speed_pct':-15.0}),
    ]
    for name, st, mode, exp in cases:
        d = apply_prefight_second_slice_preview({'t':'a'}, st, mode, dry_run=True)['status_second_slice_preview']
        for k,v in exp.items():
            assert abs(d[k]-v) < 1e-9, f'{name} {k}: {d[k]} != {v}'
    # PvP cap
    d = apply_prefight_second_slice_preview({'t':'a'}, [{'family':'debuff_offensive','value_pct':30}]*2, 'pvp', dry_run=True)['status_second_slice_preview']
    assert abs(d['atk_pct'] + 30.0) < 1e-9, f'pvp cap broken: {d}'
    # Boss cap
    d = apply_prefight_second_slice_preview({'t':'a'}, [{'family':'debuff_defensive','value_pct':30}]*2, 'boss', dry_run=True)['status_second_slice_preview']
    assert abs(d['def_pct'] + 20.0) < 1e-9, f'boss cap broken: {d}'
    # Out of scope ignored
    d = apply_prefight_second_slice_preview({'t':'a'}, [{'family':'dot','value_pct':100},{'family':'freeze','value_pct':100}], 'campaign', dry_run=True)['status_second_slice_preview']
    assert d == {'atk_pct':0.0,'def_pct':0.0,'speed_pct':0.0}, f'OOS leaked: {d}'
    print('SMOKE_OK')
''')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_SECOND_SLICE_FLAG_ON_BEHAVIOR_SMOKE_READY': fail('verdict mismatch')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'SMOKE_OK' not in proc.stdout:
        fail(f'smoke failed: rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}')
    for k in ('no_dot_or_tick_loop', 'no_hard_cc', 'no_borea_marchio_live'):
        if m.get(k) is not True: fail(f'marker.{k} must be True')
    if m.get('battle_engine_runtime_behavior_changed_for_unflagged_callers') is not False:
        fail('battle_engine_runtime_behavior_changed_for_unflagged_callers must be False')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    api = m.get('api_endpoints_status') or {}
    if api.get('/api/heroes') != 200 or api.get('/api/heroes/primordial_gaia') != 404: fail('api smoke baseline mismatch')
    print('[PASS] PROJECT_U Track C flag-ON smoke READY — 4 families, caps, OOS ignored, no DoT/CC/Borea, replayed in-process')
    sys.exit(0)


if __name__ == '__main__': main()
