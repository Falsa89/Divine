#!/usr/bin/env python3
"""PROJECT_U Track D validator — canary light load.

Replay del load test per ottenere evidenza fresca p50/p95/p99.
"""
import json, subprocess, sys, tempfile, textwrap
from pathlib import Path

M = Path('/app/data/design/status_effects/project_u_second_slice_canary_light_load_v1.json')

SCRIPT = textwrap.dedent('''
    import os, sys, time, statistics
    os.environ['STATUS_RUNTIME_SECOND_SLICE_ENABLED'] = 'true'
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview
    statuses = [{'family':'debuff_offensive','value_pct':15},{'family':'speed_up','value_pct':10}]
    latencies = []
    errors = 0
    for i in range(300):
        t0 = time.perf_counter_ns()
        try:
            out = apply_prefight_second_slice_preview({'t':'a','heroes':[{'hp':100}]}, statuses, 'campaign', dry_run=True)
            if 'status_second_slice_preview' not in out:
                errors += 1
        except Exception:
            errors += 1
        latencies.append((time.perf_counter_ns()-t0)/1000.0)
    lat_sorted = sorted(latencies)
    p50 = statistics.median(latencies)
    p95 = lat_sorted[int(0.95 * len(latencies))]
    p99 = lat_sorted[int(0.99 * len(latencies))]
    print(f'CANARY_LOAD count=300 errors={errors} p50={p50:.1f}us p95={p95:.1f}us p99={p99:.1f}us')
''')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_SECOND_SLICE_CANARY_LIGHT_LOAD_READY': fail('verdict mismatch')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(SCRIPT); tmp = tf.name
    try:
        proc = subprocess.run(['python3', tmp], capture_output=True, text=True, timeout=30)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0 or 'CANARY_LOAD' not in proc.stdout:
        fail(f'load failed: rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}')
    out = proc.stdout.strip()
    # Extract errors
    import re
    em = re.search(r'errors=(\d+)', out)
    if not em or int(em.group(1)) != 0:
        fail(f'errors > 0 in load test: {out}')
    p95m = re.search(r'p95=([\d.]+)us', out)
    if not p95m:
        fail('cannot extract p95')
    p95_ms = float(p95m.group(1)) / 1000.0
    if p95_ms > 100:
        fail(f'p95 {p95_ms} ms exceeds 100ms target')
    if int(m.get('call_count', 0)) < 150:
        fail('call_count must be >= 150')
    if m.get('errors_count', -1) != 0: fail('marker errors_count must be 0')
    if m.get('latency_p95_within_target') is not True: fail('latency_p95_within_target must be True')
    if m.get('spend') is not False or m.get('gacha') is not False or m.get('db_mutation') is not False or m.get('destructive_load') is not False:
        fail('spend/gacha/db_mutation/destructive_load must be False')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print(f'[PASS] PROJECT_U Track D canary light load READY — 300 calls, 0 errors, p95 within 100ms target')
    sys.exit(0)


if __name__ == '__main__': main()
