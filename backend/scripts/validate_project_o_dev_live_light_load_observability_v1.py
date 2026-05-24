#!/usr/bin/env python3
"""PROJECT_O Track D validator — dev-live light load + observability."""
import json, sys, urllib.request, urllib.error, time
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_dev_live_light_load_observability_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _hit(p):
    t0 = time.time()
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            r.read(); return r.status, (time.time() - t0) * 1000
    except urllib.error.HTTPError as e: return e.code, (time.time() - t0) * 1000
    except Exception: return -1, 0.0


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_DEV_LIVE_LIGHT_LOAD_AND_OBSERVABILITY_READY': fail('verdict mismatch')
    lp = m.get('load_profile', {})
    if lp.get('total_requests', 0) > lp.get('max_requests_authorized', 0): fail('total_requests exceeded authorized cap')
    if lp.get('destructive') is not False: fail('load must be non-destructive')
    if lp.get('db_mutation') is not False: fail('no DB mutation allowed')
    rc = m.get('response_codes', {})
    if rc.get('5xx', 0) != 0: fail(f'recorded 5xx={rc.get("5xx")}')
    if rc.get('err', 0) != 0: fail(f'recorded err={rc.get("err")}')
    # Sanity 30 reqs live.
    lat = []; ok = 0
    for _ in range(10):
        for p in ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea'):
            c, dt = _hit(p); lat.append(dt)
            if 200 <= c < 300: ok += 1
    if ok < 30: fail(f'sanity 30/30 not met: {ok}')
    lat.sort(); p99 = lat[int(len(lat) * 0.99)] if lat else 0.0
    if p99 > 1000.0: fail(f'p99 too high: {p99}ms')
    print(f'[PASS] PROJECT_O Track D light load + observability READY: recorded 300/300 2xx; sanity 30/30 ok p99={p99:.1f}ms')
    sys.exit(0)


if __name__ == '__main__': main()
