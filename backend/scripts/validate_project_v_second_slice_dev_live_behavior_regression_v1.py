#!/usr/bin/env python3
"""PROJECT_V Track C validator — behavior regression replay (14 cases)."""
import json, subprocess, sys, tempfile, textwrap
from pathlib import Path
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_behavior_regression_v1.json')
SCRIPT = textwrap.dedent('''
    import os, sys
    os.environ['STATUS_RUNTIME_SECOND_SLICE_ENABLED'] = 'true'
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview
    cases = [
        ('debuff_off_minor', [{'family':'debuff_offensive','value_pct':10}], 'campaign', {'atk_pct':-10,'def_pct':0,'speed_pct':0}),
        ('debuff_off_max', [{'family':'debuff_offensive','value_pct':30}], 'campaign', {'atk_pct':-30,'def_pct':0,'speed_pct':0}),
        ('debuff_off_clamp', [{'family':'debuff_offensive','value_pct':9999}], 'campaign', {'atk_pct':-30,'def_pct':0,'speed_pct':0}),
        ('agg_off_cap', [{'family':'debuff_offensive','value_pct':30}]*2, 'campaign', {'atk_pct':-40,'def_pct':0,'speed_pct':0}),
        ('debuff_def_max', [{'family':'debuff_defensive','value_pct':30}], 'campaign', {'atk_pct':0,'def_pct':-30,'speed_pct':0}),
        ('agg_def_cap', [{'family':'debuff_defensive','value_pct':30}]*2, 'campaign', {'atk_pct':0,'def_pct':-40,'speed_pct':0}),
        ('speed_up', [{'family':'speed_up','value_pct':20}], 'campaign', {'atk_pct':0,'def_pct':0,'speed_pct':20}),
        ('speed_down', [{'family':'speed_down','value_pct':20}], 'campaign', {'atk_pct':0,'def_pct':0,'speed_pct':-20}),
        ('agg_speed_cap', [{'family':'speed_up','value_pct':25}]*2, 'campaign', {'atk_pct':0,'def_pct':0,'speed_pct':30}),
        ('opposing_zero', [{'family':'speed_up','value_pct':25},{'family':'speed_down','value_pct':25}], 'campaign', {'atk_pct':0,'def_pct':0,'speed_pct':0}),
        ('pvp_cap', [{'family':'debuff_offensive','value_pct':30}]*2, 'pvp', {'atk_pct':-30,'def_pct':0,'speed_pct':0}),
        ('boss_cap', [{'family':'debuff_defensive','value_pct':30}]*2, 'boss', {'atk_pct':0,'def_pct':-20,'speed_pct':0}),
        ('oos_ignored', [{'family':'dot','value_pct':100},{'family':'freeze','value_pct':100},{'family':'stun','value_pct':100}], 'campaign', {'atk_pct':0,'def_pct':0,'speed_pct':0}),
        ('mixed', [{'family':'debuff_offensive','value_pct':15},{'family':'dot','value_pct':99},{'family':'speed_up','value_pct':10}], 'campaign', {'atk_pct':-15,'def_pct':0,'speed_pct':10}),
    ]
    fails = 0
    for name, st, mode, exp in cases:
        d = apply_prefight_second_slice_preview({'t':'a'}, st, mode, dry_run=True)['status_second_slice_preview']
        if not all(abs(d[k]-v) < 1e-9 for k,v in exp.items()):
            fails += 1
            print(f'FAIL {name}: got {d} expected {exp}')
    print(f'REGRESSION_RESULT: {len(cases)-fails}/{len(cases)} pass')
''')
def fail(msg): print(f'[FAIL] {msg}'); sys.exit(1)
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_SECOND_SLICE_DEV_LIVE_BEHAVIOR_REGRESSION_READY': fail('verdict mismatch')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=15)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'REGRESSION_RESULT' not in proc.stdout: fail(f'regression subprocess failed: {proc.stdout!r} {proc.stderr!r}')
    import re
    rm = re.search(r'REGRESSION_RESULT: (\d+)/(\d+) pass', proc.stdout)
    if not rm or int(rm.group(1)) != int(rm.group(2)): fail(f'not all regression cases passed: {proc.stdout}')
    if int(rm.group(2)) < 12: fail(f'regression cases count {rm.group(2)} < 12')
    if int(m.get('regression_cases_pass', 0)) != int(m.get('regression_cases_total', -1)): fail('marker regression mismatch')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print(f'[PASS] PROJECT_V Track C dev-live behavior regression READY — {rm.group(1)}/{rm.group(2)} cases pass')
    sys.exit(0)
if __name__ == '__main__': main()
