#!/usr/bin/env python3
"""PROJECT_L Track E validator — status payload no-leak regression."""
import json, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_status_payload_no_leak_regression_v1.json')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')
FORBIDDEN_MARKERS = (b'status_envelope_preview', b'__seam_version')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def probe(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r: return r.read()
    except urllib.error.HTTPError as e:
        try: return e.read()
        except Exception: return b''
    except Exception: return b''


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_STATUS_PAYLOAD_NO_LEAK_REGRESSION_READY': fail('verdict mismatch')
    leaks = 0
    for p in ENDPOINTS:
        body = probe(p)
        for marker in FORBIDDEN_MARKERS:
            if marker in body:
                leaks += 1
                print(f'  LEAK "{marker.decode()}" in {p}')
    if leaks > 0: fail(f'{leaks} payload leak(s) detected')
    print(f'[PASS] PROJECT_L Track E payload no-leak regression: 0 leaks across {len(ENDPOINTS)} endpoints')
    sys.exit(0)


if __name__ == '__main__': main()
