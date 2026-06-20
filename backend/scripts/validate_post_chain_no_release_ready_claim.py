#!/usr/bin/env python3
"""POST_CHAIN — No release-ready claim validator (post-chain artefacts).

Forbidden tokens must NOT appear in post-chain artefacts as positive claims.
They can appear only in explicit negation/policy contexts.
Introspective validators are excluded.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).name
INTROSPECTIVE = {
    'validate_post_chain_no_release_ready_claim.py',
    'validate_post_chain_marker_truth.py',
    'validate_post_chain_no_secret_leak_in_reports.py',
    'validate_post_chain_artifact_policy_doc.py',
    'validate_post_chain_future_pack_leak_guard.py',
    'validate_post_chain_no_runtime_scope_drift.py',
}
FORBIDDEN = ['RELEASE_READY', 'PUBLIC_RELEASE_READY',
             'COMMERCIAL_RELEASE_READY', 'PRODUCTION_READY',
             'DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY']
NEG_CTX = ['non ', 'no ', 'not ', 'never', 'forbidden', 'vietat', 'mai ',
           'fals', 'classifi', 'must not', 'cannot', 'non deve',
           '"forbidden', 'forbidden:', "don't", 'do not',
           ': false', '= false', 'release_ready: false',
           'release_ready": false', 'public_release_ready": false',
           'commercial_release_ready": false', 'production_ready": false',
           'forbidden_tokens', 'forbidden_verdicts']
TARGETS = [
    REPO_ROOT / 'data' / 'design' / 'system_safety' / 'post_chain_repo_hygiene_pass_1_marker.json',
    REPO_ROOT / 'backend' / 'scripts' / 'run_post_chain_repo_hygiene_pass_1_suite.py',
] + [p for p in sorted((REPO_ROOT / 'backend' / 'scripts').glob('validate_post_chain_*.py'))
     if p.name not in INTROSPECTIVE and p.name != SELF] + [
    REPO_ROOT / 'docs' / 'divine' / '536_POST_CHAIN_REPO_HYGIENE_PASS_1_ARTIFACT_POLICY.md',
    REPO_ROOT / 'docs' / 'divine' / '536_POST_CHAIN_REPO_HYGIENE_PASS_1_FINAL_REPORT.md',
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
                ctx = src[max(0, pos - 160):pos + len(tk) + 60].lower()
                if not any(neg in ctx for neg in NEG_CTX):
                    errs.append(f'{rel}: "{tk}" without negation @ pos {pos}')
                    break
                idx = pos + len(tk)
    return _emit(errs, scanned)


def _emit(errs, scanned):
    report = {'pack': 'POST_CHAIN_NO_RELEASE_READY_CLAIM',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'scanned_files': scanned,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_no_release_ready_claim_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  no release-ready claim ({len(scanned)} files)')
    return 0


if __name__ == '__main__': sys.exit(main())
