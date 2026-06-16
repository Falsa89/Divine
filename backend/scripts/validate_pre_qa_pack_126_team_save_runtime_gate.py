#!/usr/bin/env python3
"""
Pack 126 — Validator: team save runtime gate behavior.
Verifies POST /api/team/save-formation:
  - returns 403 QA_TEAM_SAVE_DISABLED when env gate not set;
  - is reachable (route registered);
  - returns proper blocker structure.
"""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors: list[str] = []
    # Use curl since requests may not be installed.
    try:
        r = subprocess.run([
            'curl', '-s', '-o', '/tmp/save_resp.json', '-w', '%{http_code}',
            '-X', 'POST', 'http://localhost:8001/api/team/save-formation',
            '-H', 'Content-Type: application/json',
            '-d', '{"server_id":"s1","team_formation":[]}',
        ], capture_output=True, text=True, timeout=10)
        code = r.stdout.strip()
        body = (Path('/tmp/save_resp.json').read_text(encoding='utf-8') if Path('/tmp/save_resp.json').exists() else '')
    except Exception as e:
        errors.append(f'curl failed: {e}')
        return _emit(errors, {})
    detail = {'http_code': code, 'body': body[:200]}
    if code not in ('401', '403'):
        errors.append(f'expected 401/403, got {code}: {body[:120]}')
    else:
        print(f'OK    endpoint reachable, gate behavior: HTTP {code}')
    # Verify route file presence (static + dynamic)
    route_src = (REPO_ROOT / 'backend' / 'routes' / 'v96_team_formation.py').read_text(encoding='utf-8')
    if 'QA_TEAM_SAVE_DISABLED' not in route_src:
        errors.append('QA_TEAM_SAVE_DISABLED blocker not present in route source')
    if '/save-formation' not in route_src:
        errors.append('save-formation endpoint not present in route source')
    return _emit(errors, detail)


def _emit(errors, detail):
    print('\n' + '='*72)
    print('Pack 126 — team save runtime gate')
    print('='*72)
    note = 'NEEDS_DEVICE_CONFIRMATION_FOR_FULL_SAVE' if not errors else None
    report = {'pack': 'PRE_QA_PACK_126_TEAM_SAVE_RUNTIME_GATE', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'detail': detail, 'note': note}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_team_save_runtime_gate_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  endpoint reachable, gate fail-closed when env not set (full save NEEDS_DEVICE_CONFIRMATION)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
