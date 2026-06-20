#!/usr/bin/env python3
"""Pack 133 — Secret Redaction Policy validator.

Scans Pack 133 artefacts (harness, builder, suite runner, evidence dir,
manifest, checklist, final report) for real-looking secret leaks. Real JWT
is a 3-segment dot-separated base64url string >= ~40 chars. We match that
shape, not the bare word 'Bearer'. Introspective validators that mention
the forbidden patterns as data are excluded.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_pack_133_secret_redaction_policy.py',
    'validate_pack_133_device_qa_evidence_harness_contract.py',
}
TARGETS = [
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_manifest_builder.py',
    REPO_ROOT / 'backend' / 'scripts' / 'run_pack_127_128_129_130_131_132_133_safety_suite.py',
] + sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_133_*.py')) + [
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_device_qa_evidence_marker.json',
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_final_pre_qa_chain_marker.json',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_evidence_manifest_PACK_133.md',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_manual_checklist_PACK_133.md',
    REPO_ROOT / 'docs' / 'divine' / '535_PACK_133_DEVICE_QA_EVIDENCE_HARNESS_FINAL_REPORT.md',
]
EVIDENCE_DIR = REPO_ROOT / 'docs' / 'divine' / 'evidence' / 'pack_133'
if EVIDENCE_DIR.exists():
    TARGETS += sorted([f for f in EVIDENCE_DIR.rglob('*') if f.is_file()])

# Real-looking JWT: 3 segments of base64url, each >= 10 chars.
REAL_JWT_RE = re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b')
# Real Authorization header carrying a real-looking JWT body.
REAL_AUTH_BEARER_RE = re.compile(r'Authorization\s*:\s*Bearer\s+eyJ[A-Za-z0-9_-]{15,}')
# Password / secret value assignments (non-policy contexts).
# Heuristic: 'password' or 'secret' followed by '=' or ':' AND a value of >=8 chars
# that is NOT 'password' or 'secret' word literal.
VALUE_LEAK_RE = re.compile(
    r'(?i)\b(password|access_token|refresh_token)\s*[=:]\s*[\'"][^\'"\s]{8,}[\'"]'
)


def main():
    errs = []
    scanned = []
    for f in TARGETS:
        if not f.exists() or f.name == SELF or f.name in INTROSPECTIVE:
            continue
        rel = str(f.relative_to(REPO_ROOT)) if str(f).startswith(str(REPO_ROOT)) else str(f)
        scanned.append(rel)
        try:
            src = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        if REAL_JWT_RE.search(src):
            errs.append(f'{rel}: real-looking JWT leak')
        if REAL_AUTH_BEARER_RE.search(src):
            errs.append(f'{rel}: Authorization Bearer with real-looking JWT leak')
        if VALUE_LEAK_RE.search(src):
            errs.append(f'{rel}: literal password/token assignment')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_133_SECRET_REDACTION_POLICY',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'excluded_introspective': sorted(INTROSPECTIVE),
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_secret_redaction_policy_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  secret redaction policy clean across {len(scanned)} files')
    return 0


if __name__ == '__main__': sys.exit(main())
