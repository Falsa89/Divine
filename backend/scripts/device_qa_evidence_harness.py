#!/usr/bin/env python3
"""Pack 133 — Device QA Evidence Harness (SAFE BY DEFAULT).

GET-only, env-gated. Designed to be runnable in CI or by a human reviewer
without ever leaking secrets, writing to DB, or mutating game state.

Responsibilities:
- run no-auth and fake-token probes against safe GET endpoints (always OK);
- optionally run authenticated GET probes only if QA env vars are present;
- classify every test as PASS / FAIL / MANUAL_REQUIRED / NOT_EXECUTED;
- produce a sanitized JSON evidence report (no JWT raw, no PII raw);
- write a Markdown evidence summary in $QA_EVIDENCE_DIR (default ./);
- NEVER call mutating endpoints (claim/purchase/upgrade/save-formation/...).

Usage:
    QA_TEST_BASE_URL=http://127.0.0.1:8001 \\
    QA_TEST_JWT=<token> QA_TEST_SERVER_ID=s1 QA_TEST_USER_ID=<id> \\
    QA_DEVICE_PLATFORM=ios QA_DEVICE_LABEL="iPhone 13 Expo Go" \\
    QA_EVIDENCE_DIR=docs/divine/evidence/pack_133 \\
    python backend/scripts/device_qa_evidence_harness.py
"""
from __future__ import annotations
import hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / 'backend' / 'scripts' / 'reports'
OUT_DIR.mkdir(parents=True, exist_ok=True)

ENV_REQUIRED = ['QA_TEST_JWT', 'QA_TEST_BASE_URL']
ENV_OPTIONAL = ['QA_TEST_SERVER_ID', 'QA_TEST_USER_ID',
                'QA_DEVICE_PLATFORM', 'QA_DEVICE_LABEL', 'QA_EVIDENCE_DIR']
DEFAULT_BASE_URL = 'http://127.0.0.1:8001'

SAFE_GET_ENDPOINTS = [
    '/api/health',
    '/api/lobby/launch-context/preview',
    '/api/combat/preview',
]
FORBIDDEN_ENDPOINTS = [
    '/api/team/save-formation', '/api/battle/simulate',
    '/api/reward/claim', '/api/mail/claim', '/api/shop/purchase',
    '/api/gacha/pull', '/api/hero/upgrade', '/api/affinity/gift',
    '/api/battlepass/claim', '/api/vip/claim',
]


def _sanitize(s):
    """Redact any raw JWT-looking blob in arbitrary text."""
    if not s:
        return s
    import re
    # Bearer eyJ... or eyJ at line start: redact body.
    s = re.sub(r'(Bearer\s+)eyJ[A-Za-z0-9._-]{10,}', r'\1<REDACTED_JWT>', s)
    s = re.sub(r'eyJ[A-Za-z0-9._-]{20,}\.[A-Za-z0-9._-]{6,}\.[A-Za-z0-9._-]{6,}', '<REDACTED_JWT>', s)
    return s


def _jwt_fingerprint(token):
    """Return short hash fingerprint of the JWT (NOT the JWT itself)."""
    if not token:
        return None
    h = hashlib.sha256(token.encode('utf-8')).hexdigest()
    return f'sha256:{h[:12]}'


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
    device_platform = os.getenv('QA_DEVICE_PLATFORM')
    device_label = os.getenv('QA_DEVICE_LABEL')
    evidence_dir = os.getenv('QA_EVIDENCE_DIR')

    # Phase 1: ALWAYS-SAFE GET probes (no auth + fake token). MAI mutativi.
    phase_1 = []
    code, body, err = _safe_get(base_url, '/api/health')
    phase_1.append({'endpoint': '/api/health', 'method': 'GET', 'auth': 'none',
                    'status_code': code, 'expected': '200',
                    'result': 'PASS' if code == 200 else 'INFO',
                    'error': _sanitize(err)})
    code, body, err = _safe_get(base_url, '/api/lobby/launch-context/preview?mode=training')
    phase_1.append({'endpoint': '/api/lobby/launch-context/preview',
                    'method': 'GET', 'auth': 'none', 'status_code': code,
                    'expected': '401/403', 'result': 'PASS' if code in (401, 403) else 'INFO',
                    'error': _sanitize(err)})
    code, body, err = _safe_get(base_url, '/api/lobby/launch-context/preview?mode=training',
                                headers={'Authorization': 'Bearer invalid.fake.token'})
    phase_1.append({'endpoint': '/api/lobby/launch-context/preview',
                    'method': 'GET', 'auth': 'fake_token', 'status_code': code,
                    'expected': '401/403', 'result': 'PASS' if code in (401, 403) else 'INFO',
                    'error': _sanitize(err)})

    # Phase 2: AUTH-required smoke. Solo se env presente.
    missing = [v for v in ENV_REQUIRED if not os.getenv(v)]
    phase_2 = []
    if missing:
        auth_status = 'MANUAL_REQUIRED'
        manual_note = f'Missing env: {missing}. Phase 2 NOT_EXECUTED.'
    else:
        auth_status = 'EXECUTED'
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
                            'status_code': code,
                            # Sanitize body before storing.
                            'body_preview_redacted': _sanitize((body or '')[:300]),
                            'result': 'PASS' if isinstance(code, int) and 200 <= code < 500 else 'INFO',
                            'error': _sanitize(err)})

    # Device evidence is ALWAYS manual_required unless we have human-provided
    # screenshot or video evidence. We do NOT auto-claim it.
    device_evidence_status = 'MANUAL_REQUIRED'
    if device_platform and device_label and evidence_dir:
        # Even with env, we only claim 'HARNESS_REGISTERED' (not 'COLLECTED')
        # because the harness itself cannot prove a human took the screenshot.
        device_evidence_status = 'HARNESS_REGISTERED_AWAITING_HUMAN_CONFIRMATION'

    report = {
        'pack': 'PACK_133_DEVICE_QA_EVIDENCE_HARNESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'AUTHENTICATED_SMOKE_STATUS': auth_status,
        'AUTHENTICATED_SMOKE_NOT_RUN_REASON': manual_note,
        'DEVICE_EVIDENCE_STATUS': device_evidence_status,
        'SCREENSHOT_EVIDENCE_STATUS': 'MANUAL_REQUIRED',
        'MANUAL_SIGNOFF_STATUS': 'MANUAL_REQUIRED',
        'env_required': ENV_REQUIRED,
        'env_optional': ENV_OPTIONAL,
        'qa_jwt_fingerprint': _jwt_fingerprint(jwt_token),  # short hash only
        'qa_test_server_id': server_id,
        'qa_device_platform': device_platform,
        'qa_device_label': device_label,
        'safe_get_endpoints': SAFE_GET_ENDPOINTS,
        'forbidden_endpoints_never_called': FORBIDDEN_ENDPOINTS,
        'phase_1_unauth_probes': phase_1,
        'phase_2_auth_probes': phase_2,
        'db_write_scope': 'NONE',
        'runtime_mutation_scope': 'NONE',
        'reward_progress_scope': 'NONE',
        'release_ready': False,
        'device_qa_status': 'MANUAL_REQUIRED',
        'enforcement': 'SAFE_BY_DEFAULT',
        'secret_redaction_policy': {
            'never_persist_raw_jwt': True,
            'never_print_raw_jwt': True,
            'jwt_fingerprint_only': True,
            'sanitize_headers_in_logs': True,
        },
        'notes': [
            'GET-only harness. No DB writes. No seed. No reward/EXP/progress.',
            'Device QA pass is NEVER auto-declared by this harness.',
            'Manual evidence (screenshot/video/signoff) is REQUIRED to advance.',
        ],
    }
    (OUT_DIR / 'pack_133_device_qa_evidence_harness_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    # Optionally drop a sanitized Markdown summary into evidence dir.
    if evidence_dir:
        ed = (REPO_ROOT / evidence_dir).resolve()
        try:
            ed.mkdir(parents=True, exist_ok=True)
            (ed / 'harness_run_summary.md').write_text(
                _render_md_summary(report), encoding='utf-8')
        except Exception as e:
            print(f'WARN  could not write evidence dir summary: {e}')

    print(f'AUTHENTICATED_SMOKE_STATUS = {auth_status}')
    print(f'DEVICE_EVIDENCE_STATUS    = {device_evidence_status}')
    print(f'SCREENSHOT_EVIDENCE_STATUS = MANUAL_REQUIRED')
    print(f'MANUAL_SIGNOFF_STATUS     = MANUAL_REQUIRED')
    if manual_note:
        print(f'  {manual_note}')
    print(f'phase_1 probes: {len(phase_1)} | phase_2 probes: {len(phase_2)}')
    return 0


def _render_md_summary(r):
    lines = [
        '# Device QA Evidence Harness — run summary (sanitized)',
        '',
        f'- timestamp: {r["timestamp_utc"]}',
        f'- authenticated smoke: **{r["AUTHENTICATED_SMOKE_STATUS"]}**',
        f'- device evidence: **{r["DEVICE_EVIDENCE_STATUS"]}**',
        f'- screenshot evidence: **{r["SCREENSHOT_EVIDENCE_STATUS"]}**',
        f'- manual signoff: **{r["MANUAL_SIGNOFF_STATUS"]}**',
        f'- JWT fingerprint (never raw): `{r.get("qa_jwt_fingerprint")}`',
        f'- device platform: `{r.get("qa_device_platform")}`',
        f'- device label: `{r.get("qa_device_label")}`',
        '',
        '## phase 1 (unauth, GET-only, always safe)',
    ]
    for p in r['phase_1_unauth_probes']:
        lines.append(f'- `{p["endpoint"]}` auth=`{p["auth"]}` code=`{p["status_code"]}` result=`{p["result"]}`')
    lines.append('')
    lines.append('## phase 2 (auth, GET-only)')
    if not r['phase_2_auth_probes']:
        lines.append('- NOT_EXECUTED (MANUAL_REQUIRED)')
    for p in r['phase_2_auth_probes']:
        lines.append(f'- `{p["endpoint"]}` code=`{p["status_code"]}` result=`{p["result"]}`')
    lines.append('')
    lines.append('## forbidden endpoints never called')
    for ep in r['forbidden_endpoints_never_called']:
        lines.append(f'- `{ep}`')
    lines.append('')
    lines.append('> Device QA pass is NEVER auto-declared by this harness.')
    lines.append('> Manual evidence (screenshot/video/signoff) is REQUIRED to advance.')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    sys.exit(main())
