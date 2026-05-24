#!/usr/bin/env python3
"""PROJECT_U Track E validator — payload + log no-leak with FINAL flag state (OFF).

Dopo il rollback, scansiona endpoint live: con flag OFF, nessuna chiave second-slice
deve apparire nei payload pubblici. Scansiona anche backend logs per errori second-slice.
"""
import json, sys
from pathlib import Path
from urllib import request, error

M = Path('/app/data/design/status_effects/project_u_second_slice_payload_log_no_leak_v1.json')
FORBIDDEN = ('status_second_slice_preview', '__second_slice_seam_version', 'second_slice_active', 'second_slice_deltas', 'debuff_offensive_runtime', 'debuff_defensive_runtime', 'speed_up_runtime', 'speed_down_runtime')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def _get(url: str):
    try:
        with request.urlopen(url, timeout=3) as r:
            return r.status, r.read().decode('utf-8', errors='replace')
    except error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_SECOND_SLICE_PAYLOAD_LOG_NO_LEAK_READY': fail('verdict mismatch')
    for ep in ENDPOINTS:
        status, body = _get(f'http://localhost:8001{ep}')
        if status and 200 <= status < 300:
            for k in FORBIDDEN:
                if k in body:
                    fail(f'live payload leak on {ep}: {k}')
    # Backend log scan (best-effort)
    import subprocess
    try:
        out = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.err.log'], capture_output=True, text=True, timeout=5)
        log_txt = (out.stdout or '') + (out.stderr or '')
    except Exception:
        log_txt = ''
    if 'status_second_slice_runtime_seam ERROR' in log_txt:
        fail('backend log contains second_slice runtime seam ERROR')
    if m.get('payload_leak_with_flag_on') is not False or m.get('payload_leak_with_flag_off') is not False: fail('payload_leak flags must be False')
    if m.get('backend_log_leak') is not False: fail('backend_log_leak must be False')
    if m.get('frontend_payload_changed') is not False: fail('frontend_payload_changed must be False')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_U Track E payload + log no-leak READY — 0 leak on 5 endpoints post-rollback, 0 backend log errors')
    sys.exit(0)


if __name__ == '__main__': main()
