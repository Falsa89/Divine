#!/usr/bin/env python3
"""Pack 132 — No false Device QA ready claim validator.

Scans Pack 132 markers, harness and final report for forbidden 'ready' tokens.
Forbidden tokens must NOT appear OR must appear only inside an explicit negation
context (so we can SAY 'do not declare DEVICE_QA_READY' without failing).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
# Validatori introspettivi che legittimamente contengono i token forbidden
# come dato nelle loro stesse liste di scan (auto-referenza). Escludi dal target.
INTROSPECTIVE = {
    'validate_pack_132_no_device_qa_ready_claim.py',
    'validate_pack_132_master_device_qa_gate_matrix.py',
    'validate_pack_132_docs_truth_cleanup_pack127_131.py',
}
FORBIDDEN = ['DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY', 'RELEASE_READY']
TARGETS = [
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_132_master_device_qa_gate_marker.json',
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_132_docs_truth_cleanup_marker.json',
    REPO_ROOT / 'backend' / 'scripts' / 'pre_device_qa_authenticated_smoke_harness.py',
] + [p for p in sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_pack_132_*.py'))
     if p.name not in INTROSPECTIVE and p.name != SELF] + [
    REPO_ROOT / 'docs' / 'divine' / '534_PACK_132_MASTER_DEVICE_QA_GATE_SUITE_DOCS_TRUTH_CLEANUP_FINAL_REPORT.md',
]
NEGATION_TOKENS = ['non ', 'no ', 'not ', 'never', 'forbidden', 'vietat', 'mai ',
                   'fals', 'classifi', 'non usare', 'must not', 'forbidden_verdicts',
                   'forbidden_keywords_audit', 'cannot', 'non deve', '"forbidden', 'forbidden:']


def main():
    errs = []
    scanned = []
    for f in TARGETS:
        if not f.exists():
            continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for tk in FORBIDDEN:
            idx = 0
            while True:
                pos = src.find(tk, idx)
                if pos < 0:
                    break
                ctx = src[max(0, pos - 120):pos].lower()
                if not any(neg in ctx for neg in NEGATION_TOKENS):
                    errs.append(f'{rel}: forbidden ready token "{tk}" without negation context @ pos {pos}')
                    break
                idx = pos + len(tk)
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_132_NO_DEVICE_QA_READY_CLAIM',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'scanned_files': scanned,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_NO_FALSE_READY_CLAIM'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_no_device_qa_ready_claim_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print(f'PASS  no false Device QA ready claim ({len(scanned)} files)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
