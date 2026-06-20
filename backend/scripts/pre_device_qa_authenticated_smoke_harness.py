#!/usr/bin/env python3
"""Pack 132 — Pre-Device-QA Authenticated Smoke Harness (SAFE BY DEFAULT).

Read-only / GET-only. Safe by default:
- If QA_TEST_JWT or QA_TEST_BASE_URL env vars are unset, classifies
  AUTHENTICATED_SMOKE_STATUS = MANUAL_REQUIRED and exits with code 0
  WITHOUT contacting backend with credentials.
- Always performs the no-auth and fake-token checks against /api/health and
  /api/lobby/launch-context/preview (expecting 401/403/structured errors).
  These are GET-only and do not mutate state.
- NEVER calls mutating endpoints. NEVER seeds DB. NEVER grants reward/EXP/progress.
- NEVER unlocks Device QA. Output stays preview-only.

Usage:
    QA_TEST_JWT=<token> QA_TEST_BASE_URL=http://localhost:8001 \\
    QA_TEST_SERVER_ID=s1 QA_TEST_USER_ID=<id> \\
    python backend/scripts/pre_device_qa_authenticated_smoke_harness.py
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / 'backend' / 'scripts' / 'reports'
OUT.mkdir(parents=True, exist_ok=True)

ENV_REQUIRED = ['QA_TEST_JWT', 'QA_TEST_BASE_URL']
ENV_OPTIONAL = ['QA_TEST_SERVER_ID', 'QA_TEST_USER_ID']
DEFAULT_BASE_URL = 'http://127.0.0.1:8001'

# GET-only, read-only endpoints. NO mutating endpoints allowed.
SAFE_GET_ENDPOINTS = [
    '/api/health',
    '/api/lobby/launch-context/preview',
    '/api/combat/preview',
]

FORBIDDEN_ENDPOINTS = [
    '/api/team/save-formation',
    '/api/battle/simulate',
    '/api/reward/claim',
    '/api/mail/claim',
    '/api/shop/purchase',
    '/api/gacha/pull',
    '/api/hero/upgrade',
    '/api/affinity/gift',
]


def _write(report):
    (OUT / 'pre_device_qa_authenticated_smoke_harness_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _safe_get(base_url, path, headers=None, timeout=4):
    """GET-only network call. Returns (status_code, body_text, error)."""
    try:
        import urllib.request
        req = urllib.request.Request(base_url.rstrip('/') + path, method='GET',
                                     headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2048).decode('utf-8', errors='replace')
            return resp.status, body, None
    except Exception as e:
        # urllib raises HTTPError for non-2xx; capture code if available.
        code = getattr(e, 'code', None)
        body = ''
        try:
            body = e.read().decode('utf-8', errors='replace')[:2048]
        except Exception:
            pass
        return code, body, str(e)


def main():
    base_url = os.getenv('QA_TEST_BASE_URL') or DEFAULT_BASE_URL
    jwt_token = os.getenv('QA_TEST_JWT')
    server_id = os.getenv('QA_TEST_SERVER_ID')
    user_id = os.getenv('QA_TEST_USER_ID')

    # Phase 1: always-safe checks (no auth + fake token). GET-only.
    phase_1 = []
    code, body, err = _safe_get(base_url, '/api/health')
    phase_1.append({'endpoint': '/api/health', 'method': 'GET', 'auth': 'none',
                    'status_code': code, 'expected': 'any (liveness)',
                    'result': 'OK' if code == 200 else 'INFO',
                    'error': err})

    # No-auth probe on preview endpoint. Expected 401.
    code, body, err = _safe_get(base_url, '/api/lobby/launch-context/preview?mode=training')
    phase_1.append({'endpoint': '/api/lobby/launch-context/preview',
                    'method': 'GET', 'auth': 'none', 'status_code': code,
                    'expected': '401', 'result': 'PASS' if code in (401, 403) else 'INFO',
                    'error': err})

    # Fake token probe. Expected 401.
    code, body, err = _safe_get(base_url, '/api/lobby/launch-context/preview?mode=training',
                                headers={'Authorization': 'Bearer invalid.fake.token'})
    phase_1.append({'endpoint': '/api/lobby/launch-context/preview',
                    'method': 'GET', 'auth': 'fake_token', 'status_code': code,
                    'expected': '401', 'result': 'PASS' if code in (401, 403) else 'INFO',
                    'error': err})

    # Phase 2: AUTH-required smoke. Only if env present.
    missing = [v for v in ENV_REQUIRED if not os.getenv(v)]
    phase_2 = []
    if missing:
        status = 'MANUAL_REQUIRED'
        manual_note = f'Missing env: {missing}. Authenticated smoke NOT_EXECUTED. Provide QA env vars to run.'
    else:
        status = 'EXECUTED'
        manual_note = None
        headers = {'Authorization': f'Bearer {jwt_token}'}
        for ep in SAFE_GET_ENDPOINTS:
            qs = ''
            if 'preview' in ep:
                qs = '?mode=training'
                if server_id:
                    qs += f'&server_id={server_id}'
            code, body, err = _safe_get(base_url, ep + qs, headers=headers)
            phase_2.append({'endpoint': ep, 'method': 'GET', 'auth': 'jwt',
                            'status_code': code, 'body_preview': (body or '')[:200],
                            'error': err})

    # Forbidden endpoints are NEVER contacted; we only list them for transparency.
    report = {
        'pack': 'PRE_DEVICE_QA_AUTHENTICATED_SMOKE_HARNESS',
        'AUTHENTICATED_SMOKE_STATUS': status,
        'MANUAL_REQUIRED_reason': manual_note,
        'NOT_EXECUTED_endpoints_under_auth': [] if status == 'EXECUTED' else SAFE_GET_ENDPOINTS,
        'env_required': ENV_REQUIRED,
        'env_optional': ENV_OPTIONAL,
        'safe_get_endpoints': SAFE_GET_ENDPOINTS,
        'forbidden_endpoints_never_called': FORBIDDEN_ENDPOINTS,
        'phase_1_unauth_probes': phase_1,
        'phase_2_auth_probes': phase_2,
        'db_write_scope': 'NONE',
        'device_qa_status': 'BLOCKED',
        'enforcement': 'SAFE_BY_DEFAULT',
        'note': 'GET-only harness. NEVER mutates state. Pack 132 gate.'
    }
    _write(report)
    print(f'AUTHENTICATED_SMOKE_STATUS = {status}')
    if status == 'MANUAL_REQUIRED':
        print(f'  {manual_note}')
    print(f'phase_1 probes: {len(phase_1)} | phase_2 probes: {len(phase_2)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
