#!/usr/bin/env python3
"""Pack 132 — No DB writes / no seed validator.

Greps Pack 132 source files (harness, suite runner) for any DB mutation
or seeding patterns. Excludes Markdown documentation and excludes the
introspective validators themselves (which legitimately list the forbidden
tokens as data).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
# Introspective validators that legitimately contain forbidden token strings
# as data inside their own forbidden-pattern lists are excluded from scan.
INTROSPECTIVE_VALIDATORS = {
    'validate_pack_132_no_db_writes_no_seed.py',
    'validate_pack_132_no_reward_exp_progress_mutation.py',
    'validate_pack_132_authenticated_smoke_harness_contract.py',
    'validate_pack_132_no_device_qa_ready_claim.py',
}
CANDIDATES = [
    REPO_ROOT / 'backend' / 'scripts' / 'pre_device_qa_authenticated_smoke_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'run_pack_127_128_129_130_131_132_safety_suite.py',
] + sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_132_*.py'))
# Regex per chiamate effettive (function-call), non semplici menzioni.
FORBIDDEN_DB = [re.compile(r) for r in [
    r'\bupdate_one\s*\(', r'\bupdate_many\s*\(', r'\binsert_one\s*\(',
    r'\binsert_many\s*\(', r'\bdelete_one\s*\(', r'\bdelete_many\s*\(',
    r'\breplace_one\s*\(', r'\bbulk_write\s*\(',
    r'\bfind_one_and_update\s*\(', r'\bfind_one_and_delete\s*\(',
    r'\bfind_one_and_replace\s*\(', r'\bcreate_index\s*\(',
    r'\bsession\.commit\s*\(',
]]
FORBIDDEN_SEED = [re.compile(r) for r in [
    r'\bseed_user\s*\(', r'\bseed_server\s*\(', r'\bseed_team\s*\(',
    r'\bseed_inventory\s*\(', r'\bseed_hero\s*\(',
    r'\bcreate_test_user\s*\(', r'\bcreate_qa_user\s*\(',
    r'\bbootstrap_player\s*\(', r'\bgrant_reward\s*\(',
    r'\bgrant_exp\s*\(', r'\bgrant_progress\s*\(',
    r'\bmutate_progress\s*\(',
]]


def main():
    errs = []
    scanned = []
    for f in CANDIDATES:
        if not f.exists():
            continue
        if f.name == SELF or f.name in INTROSPECTIVE_VALIDATORS:
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for pat in FORBIDDEN_DB:
            if pat.search(src):
                errs.append(f'{rel}: DB write call {pat.pattern}')
        for pat in FORBIDDEN_SEED:
            if pat.search(src):
                errs.append(f'{rel}: seed call {pat.pattern}')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_132_NO_DB_WRITES_NO_SEED',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'scanned_files': scanned,
              'excluded_introspective': sorted(INTROSPECTIVE_VALIDATORS),
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_NO_DB_WRITE_NO_SEED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_no_db_writes_no_seed_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print(f'PASS  zero DB write/seed calls across {len(scanned)} Pack 132 files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
