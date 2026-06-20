#!/usr/bin/env python3
"""Pack 133 — No reward/EXP/progress mutation validator."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_pack_133_no_reward_exp_progress_mutation.py',
    'validate_pack_133_no_db_writes_no_seed.py',
    'validate_pack_133_device_qa_evidence_harness_contract.py',
}
FILES = [
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_manifest_builder.py',
] + sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_133_*.py'))
FORBIDDEN_CALL = [re.compile(r) for r in [
    r'\bgrant_reward\s*\(', r'\bgrant_exp\s*\(', r'\bgrant_progress\s*\(',
    r'\bmutate_progress\s*\(', r'\badd_exp\s*\(', r'\badd_progress\s*\(',
    r'\bclaim_reward\s*\(', r'\bincrement_progress\s*\(', r'\bapply_reward\s*\(',
]]


def main():
    errs, scanned = [], []
    for f in FILES:
        if not f.exists() or f.name == SELF or f.name in INTROSPECTIVE:
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for pat in FORBIDDEN_CALL:
            if pat.search(src):
                errs.append(f'{rel}: forbidden mutation call {pat.pattern}')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_133_NO_REWARD_EXP_PROGRESS_MUTATION',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_no_reward_exp_progress_mutation_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  no reward/EXP/progress mutation in {len(scanned)} files')
    return 0


if __name__ == '__main__': sys.exit(main())
