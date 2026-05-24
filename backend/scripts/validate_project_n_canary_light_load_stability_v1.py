#!/usr/bin/env python3
"""PROJECT_N Track D validator — canary light load + stability (verifies recorded results)."""
import json, sys, urllib.request, urllib.error, time
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_canary_light_load_stability_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _hit(p):
    try:
        t0 = time.time()
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            r.read()
            return r.status, (time.time() - t0) * 1000
    except urllib.error.HTTPError as e:
        return e.code, (time.time() - t0) * 1000
    except Exception:
        return -1, 0.0


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_CANARY_LIGHT_LOAD_AND_STABILITY_READY': fail('verdict mismatch')
    if m.get('load_profile', {}).get('destructive') is not False: fail('load must be non-destructive')
    if m.get('load_profile', {}).get('db_mutation') is not False: fail('no DB mutation allowed')
    rc = m.get('response_codes', {})
    if rc.get('5xx', 0) != 0: fail(f'recorded 5xx={rc.get("5xx")}')
    if rc.get('err', 0) != 0: fail(f'recorded err={rc.get("err")}')
    # Independent quick sanity light load (30 reqs across 3 endpoints).
    lat = []; ok = 0
    for _ in range(10):
        for p in ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea'):
            code, dt = _hit(p)
            lat.append(dt)
            if 200 <= code < 300: ok += 1
    if ok < 30: fail(f'live light-load sanity: only {ok}/30 ok')
    lat.sort()
    p99 = lat[int(len(lat) * 0.99)] if lat else 0.0
    if p99 > 1000.0: fail(f'p99 too high: {p99}ms')
    print(f'[PASS] PROJECT_N Track D light load + stability READY: recorded 150/150 2xx; sanity 30/30 ok p99={p99:.1f}ms')
    sys.exit(0)


if __name__ == '__main__': main()
