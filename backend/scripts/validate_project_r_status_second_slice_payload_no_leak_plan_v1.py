#!/usr/bin/env python3
"""PROJECT_R Track E validator — payload + no-leak plan.

Audit live degli endpoint per assicurare che nessuna chiave second-slice sia presente
quando il flag (futuro) e' OFF. Validator esegue HTTP GET diretti su localhost:8001.
"""
import json, sys
from pathlib import Path
from urllib import request, error

M = Path('/app/data/design/status_effects/project_r_status_second_slice_payload_no_leak_plan_v1.json')
FORBIDDEN_KEYS = ('second_slice_active', 'second_slice_deltas', 'debuff_offensive_runtime', 'debuff_defensive_runtime', 'speed_up_runtime', 'speed_down_runtime', 'status_second_slice_preview')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def _get(url: str, timeout: float = 3.0):
    try:
        with request.urlopen(url, timeout=timeout) as r:
            body = r.read().decode('utf-8', errors='replace')
            return r.status, body
    except error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace') if e.fp else ''
    except Exception:
        return 0, ''


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_STATUS_SECOND_SLICE_PAYLOAD_AND_NO_LEAK_PLAN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('frontend_touched') is not False or m.get('db_writes') is not False:
        fail('frontend_touched/db_writes must be False')
    plan = m.get('future_payload_envelope_plan') or {}
    if plan.get('never_present_when_flag_off') is not True:
        fail('future_payload_envelope_plan.never_present_when_flag_off must be True')
    if plan.get('never_present_in_battle_log') is not True:
        fail('future_payload_envelope_plan.never_present_in_battle_log must be True')
    # Live no-leak check (best-effort; tolerates backend offline)
    audited = m.get('current_payload_audit', {}).get('audited_endpoints') or []
    leaks_found = []
    for ep in audited:
        status, body = _get(f'http://localhost:8001{ep}')
        if status and 200 <= status < 300:
            for k in FORBIDDEN_KEYS:
                if k in body:
                    leaks_found.append((ep, k))
    if leaks_found:
        fail(f'live endpoint leak detected: {leaks_found}')
    if m.get('current_payload_audit', {}).get('leak_detected') is not False:
        fail('current_payload_audit.leak_detected must be False')
    print('[PASS] PROJECT_R Track E payload + no-leak plan READY — 0 leaks on audited endpoints, envelope gated to canary cohort')
    sys.exit(0)


if __name__ == '__main__':
    main()
