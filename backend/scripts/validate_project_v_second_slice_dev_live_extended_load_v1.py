#!/usr/bin/env python3
"""PROJECT_V Track D validator — extended load (1000 calls)."""
import json, re, subprocess, sys, tempfile, textwrap
from pathlib import Path
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_extended_load_v1.json')
SCRIPT = textwrap.dedent('''
    import os, sys, time, statistics
    os.environ['STATUS_RUNTIME_SECOND_SLICE_ENABLED'] = 'true'
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview
    statuses = [{'family':'debuff_offensive','value_pct':15},{'family':'speed_up','value_pct':10},{'family':'debuff_defensive','value_pct':8}]
    latencies = []
    errors = 0
    for i in range(1000):
        t0 = time.perf_counter_ns()
        try:
            mode = 'campaign' if i%3 else ('pvp' if i%2 else 'boss')
            out = apply_prefight_second_slice_preview({'t':'a','heroes':[{'hp':100},{'hp':80}]}, statuses, mode, dry_run=True)
            if 'status_second_slice_preview' not in out: errors += 1
        except Exception:
            errors += 1
        latencies.append((time.perf_counter_ns()-t0)/1000.0)
    ls = sorted(latencies)
    print(f'EXTLOAD count=1000 errors={errors} p50={statistics.median(latencies):.1f}us p95={ls[950]:.1f}us p99={ls[990]:.1f}us')
''')
def fail(msg): print(f'[FAIL] {msg}'); sys.exit(1)
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_SECOND_SLICE_DEV_LIVE_EXTENDED_LOAD_READY': fail('verdict mismatch')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=30)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'EXTLOAD' not in proc.stdout: fail(f'load failed: {proc.stdout!r} {proc.stderr!r}')
    em = re.search(r'errors=(\d+)', proc.stdout); p95m = re.search(r'p95=([\d.]+)us', proc.stdout)
    if not em or int(em.group(1)) != 0: fail(f'errors > 0: {proc.stdout}')
    if not p95m: fail('cannot extract p95')
    if float(p95m.group(1))/1000 > 100: fail(f'p95 > 100ms')
    if int(m.get('call_count', 0)) < 500: fail('call_count must be >= 500')
    for k in ('spend','gacha','db_mutation','destructive_load','db_writes'):
        if m.get(k) is not False: fail(f'{k} must be False')
    print(f'[PASS] PROJECT_V Track D extended load READY — 1000 calls, 0 errors, p95 within target')
    sys.exit(0)
if __name__ == '__main__': main()
