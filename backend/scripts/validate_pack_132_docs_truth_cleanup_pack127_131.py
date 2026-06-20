#!/usr/bin/env python3
"""Pack 132 — Docs Truth Cleanup validator for Pack 127→131 final reports.

Verifies presence, expected verdict tokens, no forbidden 'ready' claims,
no unresolved placeholders. Read-only, static.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / 'docs' / 'divine'
FORBIDDEN_TOKENS = ['DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY', 'RELEASE_READY']
PLACEHOLDER_RE = re.compile(r'(?<!`)\{\{[A-Z_]+\}\}(?!`)')
EXPECTED = [
    ('529_PACK_127', 'PACK_127_PRE_QA_ENV_PREFLIGHT_AND_MUTATION_ALLOWLIST_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED'),
    ('530_PACK_128', 'PACK_128_ROUTE_DEEPLINK_LOCKDOWN_AND_BACKEND_MUTATION_MIDDLEWARE_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED'),
    ('531_PACK_129', 'PACK_129_TEAMFORMATION_SERVER_READY_STRUCTURED_ERRORS_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED'),
    ('532_PACK_130', 'PACK_130_LOBBY_LAUNCH_CONTEXT_REAL_PLAYER_SNAPSHOT_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED'),
    ('533_PACK_131', 'PACK_131_COMBAT_CONSUMES_REAL_SNAPSHOT_POST_BATTLE_PREVIEW_SAFE_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED'),
]


def main():
    errs = []
    audited = []
    for prefix, verdict_token in EXPECTED:
        matches = list(DOCS.glob(f'{prefix}*FINAL_REPORT.md'))
        if not matches:
            errs.append(f'missing final report: {prefix}*')
            continue
        for f in matches:
            rel = str(f.relative_to(REPO_ROOT))
            src = f.read_text(encoding='utf-8')
            audited.append(rel)
            if verdict_token not in src:
                errs.append(f'{rel}: expected verdict token missing ({verdict_token})')
            if 'BLOCKED' not in src:
                errs.append(f'{rel}: missing Device QA BLOCKED marker')
            for ft in FORBIDDEN_TOKENS:
                # Allow occurrences only in negation contexts (e.g. "NON", "never", "non usato", "NOT").
                # Conservative check: any raw FORBIDDEN token must be wrapped in NEGATION nearby.
                idx = 0
                while True:
                    pos = src.find(ft, idx)
                    if pos < 0:
                        break
                    ctx = src[max(0, pos - 80):pos].lower()
                    if not any(neg in ctx for neg in ['non ', 'no ', 'not ', 'never', 'forbidden', 'vietat', 'mai ', 'fals', 'classifi', 'non usare']):
                        errs.append(f'{rel}: forbidden token "{ft}" without negation context')
                        break
                    idx = pos + len(ft)
            for m in PLACEHOLDER_RE.findall(src):
                errs.append(f'{rel}: unresolved placeholder {m}')
    return _emit(errs, audited)


def _emit(errs, audited):
    report = {'pack': 'PACK_132_DOCS_TRUTH_CLEANUP_PACK127_131',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'audited_reports': audited,
              'validation_kind': 'STATIC',
              'enforcement': 'VALIDATED_ONLY'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_docs_truth_cleanup_pack127_131_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print(f'PASS  docs truth cleanup OK ({len(audited)} reports)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
