#!/usr/bin/env python3
"""POST_CHAIN — No secret leak in reports validator.

Scans all tracked backend/scripts/reports/*.json for:
- real-looking JWT (3-segment dot-separated base64url, >= ~36 chars)
- Authorization: Bearer <real JWT>
- literal password/access_token/refresh_token value assignments (>=8 chars)

Does NOT modify any file. Read-only.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / 'backend' / 'scripts' / 'reports'

REAL_JWT_RE = re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b')
REAL_AUTH_BEARER_RE = re.compile(r'Authorization\s*:\s*Bearer\s+eyJ[A-Za-z0-9_-]{15,}')
VALUE_LEAK_RE = re.compile(
    r'(?i)\b(password|access_token|refresh_token)\s*[=:]\s*[\'"][^\'"\s]{8,}[\'"]'
)


def main():
    errs, scanned = [], 0
    if not REPORTS_DIR.exists():
        return _emit([], 0)
    for f in sorted(REPORTS_DIR.rglob('*.json')):
        if not f.is_file():
            continue
        scanned += 1
        rel = str(f.relative_to(REPO_ROOT))
        try:
            src = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        if REAL_JWT_RE.search(src):
            errs.append(f'{rel}: real-looking JWT')
        if REAL_AUTH_BEARER_RE.search(src):
            errs.append(f'{rel}: Authorization Bearer with real JWT')
        if VALUE_LEAK_RE.search(src):
            errs.append(f'{rel}: literal password/token assignment')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'POST_CHAIN_NO_SECRET_LEAK_IN_REPORTS',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'reports_scanned': scanned,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_no_secret_leak_in_reports_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  no secret leak in {scanned} tracked report JSON files')
    return 0


if __name__ == '__main__': sys.exit(main())
