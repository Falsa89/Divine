#!/usr/bin/env python3
"""Pack 133 — Device QA Evidence Harness Contract validator (ENFORCED)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS = REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py'
FORBIDDEN_DB = [re.compile(r) for r in [
    r'\binsert_one\s*\(', r'\binsert_many\s*\(',
    r'\bupdate_one\s*\(', r'\bupdate_many\s*\(',
    r'\bdelete_one\s*\(', r'\bdelete_many\s*\(',
    r'\breplace_one\s*\(', r'\bbulk_write\s*\(',
    r'\bfind_one_and_update\s*\(', r'\bsession\.commit\s*\(',
]]
FORBIDDEN_NON_GET = [re.compile(r) for r in [
    r'requests\.post\(', r'requests\.put\(', r'requests\.delete\(', r'requests\.patch\(',
    r'urllib\.request\.urlopen\(.*method\s*=\s*[\'"]POST', 
]]
REQUIRED_TOKENS = [
    'MANUAL_REQUIRED', 'NOT_EXECUTED', 'QA_TEST_JWT', 'QA_TEST_BASE_URL',
    'AUTHENTICATED_SMOKE_STATUS', 'DEVICE_EVIDENCE_STATUS',
    'SCREENSHOT_EVIDENCE_STATUS', 'MANUAL_SIGNOFF_STATUS',
    'forbidden_endpoints_never_called', 'safe_get_endpoints',
    'secret_redaction_policy', 'jwt_fingerprint',
]
FORBIDDEN_CALLED_ENDPOINTS = [
    '/api/team/save-formation', '/api/reward/claim',
    '/api/shop/purchase', '/api/gacha/pull', '/api/hero/upgrade',
    '/api/affinity/gift', '/api/battlepass/claim', '/api/vip/claim',
]


def main():
    errs = []
    if not HARNESS.exists():
        return _emit(['harness missing'])
    src = HARNESS.read_text(encoding='utf-8')
    for pat in FORBIDDEN_DB:
        if pat.search(src):
            errs.append(f'harness DB call: {pat.pattern}')
    for pat in FORBIDDEN_NON_GET:
        if pat.search(src):
            errs.append(f'harness non-GET HTTP: {pat.pattern}')
    for tok in REQUIRED_TOKENS:
        if tok not in src:
            errs.append(f'harness missing token: {tok}')
    # Endpoint forbidden non devono apparire come chiamata effettiva.
    for ep in FORBIDDEN_CALLED_ENDPOINTS:
        call_pat = re.compile(r"_safe_get\([^)]*['\"]" + re.escape(ep) + r"['\"]")
        if call_pat.search(src):
            errs.append(f'harness CALLS forbidden endpoint: {ep}')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_133_DEVICE_QA_EVIDENCE_HARNESS_CONTRACT',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_SAFE_BY_DEFAULT'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_device_qa_evidence_harness_contract_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  device QA evidence harness contract safe-by-default')
    return 0


if __name__ == '__main__': sys.exit(main())
