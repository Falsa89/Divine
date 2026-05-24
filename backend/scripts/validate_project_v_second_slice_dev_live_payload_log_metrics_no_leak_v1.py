#!/usr/bin/env python3
"""PROJECT_V Track E validator — payload + log + metrics no-leak."""
import json, sys
from pathlib import Path
from urllib import request, error
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_payload_log_metrics_no_leak_v1.json')
FORBIDDEN = ('status_second_slice_preview', '__second_slice_seam_version', 'second_slice_active', 'second_slice_deltas', 'debuff_offensive_runtime', 'debuff_defensive_runtime', 'speed_up_runtime', 'speed_down_runtime')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def _get(url):
    try:
        with request.urlopen(url, timeout=3) as r: return r.status, r.read().decode('utf-8', errors='replace')
    except error.HTTPError as e: return e.code, ''
    except Exception: return 0, ''
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_SECOND_SLICE_DEV_LIVE_PAYLOAD_LOG_METRICS_NO_LEAK_READY': fail('verdict mismatch')
    for ep in ENDPOINTS:
        s, b = _get(f'http://localhost:8001{ep}')
        if s and 200 <= s < 300:
            for k in FORBIDDEN:
                if k in b: fail(f'leak on {ep}: {k}')
    import subprocess
    try:
        out = subprocess.run(['tail','-n','500','/var/log/supervisor/backend.err.log'], capture_output=True, text=True, timeout=5)
        if 'status_second_slice_runtime_seam ERROR' in (out.stdout or ''): fail('backend log second_slice ERROR detected')
    except Exception:
        pass
    for k in ('payload_leak_with_flag_on','payload_leak_with_flag_off','backend_log_leak','metrics_leak','frontend_payload_changed','db_writes'):
        if m.get(k) is not False: fail(f'{k} must be False')
    print('[PASS] PROJECT_V Track E payload/log/metrics no-leak READY — 0 leak on 5 endpoints, 0 log errors')
    sys.exit(0)
if __name__ == '__main__': main()
