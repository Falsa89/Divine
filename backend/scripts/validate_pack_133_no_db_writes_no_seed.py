#!/usr/bin/env python3
"""Pack 133 — No DB writes / no seed validator (regex call patterns)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_pack_133_no_db_writes_no_seed.py',
    'validate_pack_133_no_reward_exp_progress_mutation.py',
    'validate_pack_133_device_qa_evidence_harness_contract.py',
    'validate_pack_133_secret_redaction_policy.py',
    'validate_pack_133_authenticated_smoke_truth.py',
    'validate_pack_133_device_qa_status_not_false_ready.py',
    'validate_pack_133_no_release_ready_claim.py',
}
CANDIDATES = [
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_manifest_builder.py',
    REPO_ROOT / 'backend' / 'scripts' / 'run_pack_127_128_129_130_131_132_133_safety_suite.py',
] + sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_133_*.py'))
FORBIDDEN_DB = [re.compile(r) for r in [
    r'\binsert_one\s*\(', r'\binsert_many\s*\(',
    r'\bupdate_one\s*\(', r'\bupdate_many\s*\(',
    r'\bdelete_one\s*\(', r'\bdelete_many\s*\(',
    r'\breplace_one\s*\(', r'\bbulk_write\s*\(',
    r'\bfind_one_and_update\s*\(', r'\bfind_one_and_delete\s*\(',
    r'\bfind_one_and_replace\s*\(', r'\bcreate_index\s*\(',
    r'\bsession\.commit\s*\(',
]]
FORBIDDEN_SEED = [re.compile(r) for r in [
    r'\bseed_user\s*\(', r'\bseed_server\s*\(', r'\bseed_team\s*\(',
    r'\bseed_inventory\s*\(', r'\bseed_hero\s*\(',
    r'\bcreate_test_user\s*\(', r'\bcreate_qa_user\s*\(',
    r'\bbootstrap_player\s*\(',
]]


def main():
    errs, scanned = [], []
    for f in CANDIDATES:
        if not f.exists() or f.name == SELF or f.name in INTROSPECTIVE:
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for pat in FORBIDDEN_DB:
            if pat.search(src): errs.append(f'{rel}: DB call {pat.pattern}')
        for pat in FORBIDDEN_SEED:
            if pat.search(src): errs.append(f'{rel}: seed call {pat.pattern}')
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_133_NO_DB_WRITES_NO_SEED',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'excluded_introspective': sorted(INTROSPECTIVE),
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_no_db_writes_no_seed_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  zero DB/seed calls in {len(scanned)} Pack 133 files')
    return 0


if __name__ == '__main__': sys.exit(main())
