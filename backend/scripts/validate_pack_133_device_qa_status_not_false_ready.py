#!/usr/bin/env python3
"""Pack 133 — Device QA status must not be false-ready."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_pack_133_device_qa_status_not_false_ready.py',
    'validate_pack_133_evidence_manifest_truth.py',
    'validate_pack_133_no_release_ready_claim.py',
    'validate_pack_133_secret_redaction_policy.py',
    'validate_pack_133_device_qa_evidence_harness_contract.py',
    'validate_pack_133_final_chain_marker.py',
}
FORBIDDEN_TOKENS = ['DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY',
                   'RELEASE_READY', 'PRODUCTION_READY', 'COMMERCIAL_READY']
NEG_CTX = ['non ', 'no ', 'not ', 'never', 'forbidden', 'vietat', 'mai ',
           'fals', 'classifi', 'non usare', 'must not', 'cannot',
           'non deve', 'forbidden:', '"forbidden', 'forbidden_verdicts',
           'forbidden_tokens', 'forbidden_keywords', 'a meno che', "don't",
           'do not', 'release_ready: false', 'release_ready=false',
           'release_ready": false', '"release_ready": false',
           'public_release_ready": false', 'commercial_release_ready": false',
           'production_ready": false']
TARGETS = [
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_device_qa_evidence_marker.json',
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_final_pre_qa_chain_marker.json',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_manifest_builder.py',
] + [p for p in sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_133_*.py'))
     if p.name not in INTROSPECTIVE and p.name != SELF] + [
    REPO_ROOT / 'docs' / 'divine' / '535_PACK_133_DEVICE_QA_EVIDENCE_HARNESS_FINAL_REPORT.md',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_evidence_manifest_PACK_133.md',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_manual_checklist_PACK_133.md',
]


def main():
    errs = []
    scanned = []
    for f in TARGETS:
        if not f.exists():
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for tk in FORBIDDEN_TOKENS:
            idx = 0
            while True:
                pos = src.find(tk, idx)
                if pos < 0: break
                ctx = src[max(0, pos - 160):pos].lower()
                if not any(neg in ctx for neg in NEG_CTX):
                    errs.append(f'{rel}: forbidden ready token "{tk}" without negation @ pos {pos}')
                    break
                idx = pos + len(tk)
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_133_DEVICE_QA_STATUS_NOT_FALSE_READY',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_device_qa_status_not_false_ready_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  Device QA status not false-ready ({len(scanned)} files)')
    return 0


if __name__ == '__main__': sys.exit(main())
