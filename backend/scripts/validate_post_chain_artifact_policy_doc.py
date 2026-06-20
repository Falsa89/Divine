#!/usr/bin/env python3
"""POST_CHAIN_REPO_HYGIENE_PASS_1 — Artifact Policy Doc validator.

Verifies that the artifact policy markdown exists and contains the required
sections classifying tracked audit artifacts vs runtime/build artifacts.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / 'docs' / 'divine' / '536_POST_CHAIN_REPO_HYGIENE_PASS_1_ARTIFACT_POLICY.md'
REQUIRED_SECTIONS = [
    'Artifact policy',
    'Tracked audit artifacts',
    'Runtime / build artifacts',
    '.emergent',
    'Conteggi audit',
    'No secret leak',
    'Pack 134',
    'Future chain',
    'Recommendation',
]


def main():
    errs = []
    if not DOC.exists():
        return _emit(['artifact policy doc missing: ' + str(DOC.relative_to(REPO_ROOT))])
    src = DOC.read_text(encoding='utf-8')
    src_lower = src.lower()
    for s in REQUIRED_SECTIONS:
        if s.lower() not in src_lower:
            errs.append(f'missing section: {s}')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'POST_CHAIN_ARTIFACT_POLICY_DOC',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'VALIDATED_ONLY'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_artifact_policy_doc_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  artifact policy doc present and complete')
    return 0


if __name__ == '__main__': sys.exit(main())
