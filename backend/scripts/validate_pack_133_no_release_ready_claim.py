#!/usr/bin/env python3
"""Pack 133 — No release-ready claim validator.

Forbidden tokens MUST NOT appear in Pack 133 artefacts as positive claims.
They can appear only in explicit negation contexts (policy, list of
forbidden tokens, statement of false). Introspective validators excluded.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_pack_133_no_release_ready_claim.py',
    'validate_pack_133_device_qa_status_not_false_ready.py',
    'validate_pack_133_evidence_manifest_truth.py',
    'validate_pack_133_secret_redaction_policy.py',
    'validate_pack_133_final_chain_marker.py',
}
FORBIDDEN = ['RELEASE_READY', 'PUBLIC_RELEASE_READY',
             'COMMERCIAL_RELEASE_READY', 'PRODUCTION_READY']
NEG_CTX = ['non ', 'no ', 'not ', 'never', 'forbidden', 'vietat',
           'mai ', 'fals', 'classifi', 'must not', 'cannot',
           'non deve', '"forbidden', 'forbidden:', "don't", 'do not',
           ': false', '= false', 'release_ready: false',
           'release_ready=false', 'release_ready": false',
           'public_release_ready": false', 'commercial_release_ready": false',
           'production_ready": false', 'forbidden_verdicts', 'forbidden_tokens']
TARGETS = [
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_device_qa_evidence_marker.json',
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_final_pre_qa_chain_marker.json',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_harness.py',
    REPO_ROOT / 'backend' / 'scripts' / 'device_qa_evidence_manifest_builder.py',
    REPO_ROOT / 'docs' / 'divine' / '535_PACK_133_DEVICE_QA_EVIDENCE_HARNESS_FINAL_REPORT.md',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_evidence_manifest_PACK_133.md',
    REPO_ROOT / 'docs' / 'divine' / 'device_qa_manual_checklist_PACK_133.md',
]


def main():
    errs, scanned = [], []
    for f in TARGETS:
        if not f.exists(): continue
        rel = str(f.relative_to(REPO_ROOT))
        scanned.append(rel)
        src = f.read_text(encoding='utf-8')
        for tk in FORBIDDEN:
            idx = 0
            while True:
                pos = src.find(tk, idx)
                if pos < 0: break
                ctx_lower = src[max(0, pos - 160):pos + len(tk) + 60].lower()
                if not any(neg in ctx_lower for neg in NEG_CTX):
                    errs.append(f'{rel}: "{tk}" without negation @ pos {pos}')
                    break
                idx = pos + len(tk)
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'PACK_133_NO_RELEASE_READY_CLAIM',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_no_release_ready_claim_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  no release-ready claim ({len(scanned)} files)')
    return 0


if __name__ == '__main__': sys.exit(main())
