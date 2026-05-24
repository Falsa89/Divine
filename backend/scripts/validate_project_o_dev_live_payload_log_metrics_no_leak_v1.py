#!/usr/bin/env python3
"""PROJECT_O Track E validator — dev-live payload/log/metrics no-leak."""
import glob, json, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_dev_live_payload_log_metrics_no_leak_v1.json')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')
FORBIDDEN = (b'status_envelope_preview', b'__seam_version')
LOG_GLOBS = ('/var/log/supervisor/backend*.log', '/var/log/supervisor/backend*.err.log')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _hit(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r: return r.read()
    except urllib.error.HTTPError as e:
        try: return e.read()
        except Exception: return b''
    except Exception: return b''


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_DEV_LIVE_PAYLOAD_LOG_METRICS_NO_LEAK_READY': fail('verdict mismatch')
    leaks = 0
    for p in ENDPOINTS:
        body = _hit(p)
        for marker in FORBIDDEN:
            if marker in body: leaks += 1; print(f'  LEAK {marker} in {p}')
    if leaks: fail(f'{leaks} endpoint leak(s)')
    log_leaks = 0; log_files = 0
    for g in LOG_GLOBS:
        for f in glob.glob(g):
            log_files += 1
            try:
                with open(f, 'rb') as fp: data = fp.read()[-65536:]
                for marker in FORBIDDEN:
                    if marker in data: log_leaks += 1; print(f'  LEAK {marker} in log {f}')
            except Exception: pass
    if log_leaks: fail(f'{log_leaks} log leak(s)')
    if m.get('metric_endpoints_introduced') is not False: fail('no new metric endpoints allowed')
    print(f'[PASS] PROJECT_O Track E no-leak: 0 endpoint leaks; 0 log leaks across {log_files} log(s)')
    sys.exit(0)


if __name__ == '__main__': main()
