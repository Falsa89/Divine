#!/usr/bin/env python3
"""Pack 132 — No reward/EXP/progress mutation validator.

Greps Pack 132 source files for forbidden mutation tokens. Markdown report
is excluded since it documents these as DISABLED in negation context.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = [
    REPO_ROOT / 'backend' / 'scripts' / 'pre_device_qa_authenticated_smoke_harness.py',
] + sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_132_*.py'))
# Patterns that would indicate actual mutation logic (not mere mention).
FORBIDDEN_CALL = [
    re.compile(r'grant_reward\s*\('),
    re.compile(r'grant_exp\s*\('),
    re.compile(r'grant_progress\s*\('),
    re.compile(r'mutate_progress\s*\('),
    re.compile(r'add_exp\s*\('),
    re.compile(r'add_progress\s*\('),
    re.compile(r'claim_reward\s*\('),
    re.compile(r'increment_progress\s*\('),
    re.compile(r'apply_reward\s*\('),
]


def main():
    errs = []
    scanned = []
    for f in FILES:
        if not f.exists():
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for pat in FORBIDDEN_CALL:
            if pat.search(src):
                errs.append(f'{rel}: forbidden mutation call {pat.pattern}')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_132_NO_REWARD_EXP_PROGRESS_MUTATION',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'scanned_files': scanned,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_no_reward_exp_progress_mutation_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print(f'PASS  no reward/EXP/progress mutation in Pack 132 ({len(scanned)} files)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
