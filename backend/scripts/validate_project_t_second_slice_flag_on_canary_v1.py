#!/usr/bin/env python3
"""PROJECT_T Track D validator — flag ON in-process canary.

In un subprocess isolato (tempfile script) setta STATUS_RUNTIME_SECOND_SLICE_ENABLED=true,
chiama il seam con dry_run=True e verifica che le 4 famiglie producano deltas
corretti. Pulisce la env var alla fine. NESSUNA scrittura sul .env reale.
"""
import json, os, subprocess, sys, tempfile, textwrap
from pathlib import Path

M = Path('/app/data/design/status_effects/project_t_second_slice_flag_on_canary_v1.json')
ENV = Path('/app/backend/.env')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


SCRIPT = textwrap.dedent('''
    import os, sys
    os.environ['STATUS_RUNTIME_SECOND_SLICE_ENABLED'] = 'true'
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview, is_seam_active

    assert is_seam_active() is True, 'seam should be active with flag=true'

    cases = [
        ('debuff_offensive', [{'family': 'debuff_offensive', 'value_pct': 15}], 'campaign', {'atk_pct': -15.0, 'def_pct': 0.0, 'speed_pct': 0.0}),
        ('debuff_defensive', [{'family': 'debuff_defensive', 'value_pct': 15}], 'campaign', {'atk_pct': 0.0, 'def_pct': -15.0, 'speed_pct': 0.0}),
        ('speed_up',         [{'family': 'speed_up',         'value_pct': 15}], 'campaign', {'atk_pct': 0.0, 'def_pct': 0.0, 'speed_pct': 15.0}),
        ('speed_down',       [{'family': 'speed_down',       'value_pct': 15}], 'campaign', {'atk_pct': 0.0, 'def_pct': 0.0, 'speed_pct': -15.0}),
    ]
    results = {}
    for name, statuses, mode, expected in cases:
        out = apply_prefight_second_slice_preview({'team': 'a'}, statuses, mode, dry_run=True)
        d = out.get('status_second_slice_preview')
        assert d is not None, f'{name}: preview missing'
        for k, v in expected.items():
            assert abs(d[k] - v) < 1e-9, f'{name}: {k} got {d[k]} expected {v}'
        results[name] = 'OK'

    # Out-of-scope ignored
    out = apply_prefight_second_slice_preview({'team': 'a'}, [{'family': 'dot', 'value_pct': 100}], 'campaign', dry_run=True)
    d = out['status_second_slice_preview']
    assert d == {'atk_pct': 0.0, 'def_pct': 0.0, 'speed_pct': 0.0}, f'out-of-scope leaked: {d}'
    results['out_of_scope_ignored'] = 'OK'

    # Caps clamps hold
    out = apply_prefight_second_slice_preview({'team': 'a'}, [{'family': 'debuff_offensive', 'value_pct': 9999}], 'campaign', dry_run=True)
    d = out['status_second_slice_preview']
    assert abs(d['atk_pct'] + 30.0) < 1e-9, f'cap not enforced: {d}'
    results['caps_clamp'] = 'OK'

    # Flag ON but dry_run=False -> identity (no live activation)
    sample = {'team': 'a'}
    out_live = apply_prefight_second_slice_preview(sample, [{'family': 'debuff_offensive', 'value_pct': 15}], 'campaign', dry_run=False)
    assert out_live is sample, f'flag ON + dry_run=False must remain identity (no live), got copy: {out_live}'
    results['no_live_without_dry_run'] = 'OK'

    print('CANARY_RESULTS:', results)
''')


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_SECOND_SLICE_FLAG_ON_IN_PROCESS_CANARY_READY': fail('verdict mismatch')
    if ENV.exists():
        env_txt = ENV.read_text()
        if any(ln.strip().startswith('STATUS_RUNTIME_SECOND_SLICE_ENABLED=') for ln in env_txt.splitlines()):
            fail('STATUS_RUNTIME_SECOND_SLICE_ENABLED present in /app/backend/.env (forbidden)')

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT)
        tmp_path = tf.name
    try:
        proc = subprocess.run(['python3', tmp_path], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if proc.returncode != 0 or 'CANARY_RESULTS' not in proc.stdout:
        fail(f'canary subprocess failed: rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}')

    # Re-verify env var did NOT leak into validator process
    if 'STATUS_RUNTIME_SECOND_SLICE_ENABLED' in os.environ:
        fail('CRITICAL: env var leaked into validator process')

    if m.get('flag_in_live_env') is not False or m.get('env_var_persisted_after_validator') is not False:
        fail('flag/env_var_persisted must be False')
    fams = m.get('families_verified_in_process') or {}
    for f in ('debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down'):
        if fams.get(f) is not True: fail(f'family {f} not verified')
    if m.get('caps_clamps_hold_in_process') is not True: fail('caps_clamps_hold_in_process must be True')
    if m.get('out_of_scope_ignored_in_process') is not True: fail('out_of_scope_ignored_in_process must be True')
    if m.get('no_dot_or_hard_cc_logic_in_process') is not True or m.get('no_borea_marchio_logic_in_process') is not True:
        fail('no_dot/no_borea_marchio must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_T Track D flag-ON in-process canary READY — 4 families OK, out-of-scope ignored, caps clamp, no live without dry_run, env var did NOT persist')
    sys.exit(0)


if __name__ == '__main__': main()
