#!/usr/bin/env python3
"""PRE_QA_ULTRA_121 — validate_pre_qa_ultra_121_report_completeness.

Verifica che il report finale del Pack 121 in docs/divine contenga tutte
le sezioni richieste:

  1. Verdict
  2. Scope
  3. Truth sources usate
  4. Files created/modified
  5. Playable preview flow matrix
  6. Public route reachability/copy matrix
  7. No-write invariant evidence
  8. Route flow evidence
  9. Device QA manifest
  10. Current-unsafe validator triage
  11. Validator results
  12. Regression gate results
  13. Repo hygiene
  14. No-touch confirmation
  15. What remains blocked
  16. Next recommended macro-pack
"""
import glob
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
DOCS_DIR = os.path.join(R, 'docs', 'divine')

REQUIRED_SECTIONS = [
    r'Verdict',
    r'Scope',
    r'Truth sources',
    r'Files created',
    r'Playable preview flow matrix',
    r'Public route reachability',
    r'No-write invariant',
    r'Route flow',
    r'Device QA manifest',
    r'Current-unsafe validator triage',
    r'Validator results',
    r'Regression gate',
    r'Repo hygiene',
    r'No-touch confirmation',
    r'What remains blocked',
    r'Next recommended macro-pack',
]

REPORT_GLOB = os.path.join(
    DOCS_DIR,
    '*_PRE_QA_ULTRA_ACCELERATION_121_VERTICAL_SLICE_PLAYABLE_PREVIEW_AND_QA_REBASELINE_COMBO*.md',
)


def main() -> int:
    failures = []
    matches = glob.glob(REPORT_GLOB)
    if not matches:
        failures.append(f'report 121 mancante (glob={REPORT_GLOB})')
        return _emit(failures)
    if len(matches) > 1:
        # Non-fatale ma segnaliamo.
        print(f'  [info] piu\' di un report 121 trovato: {matches}')

    fp = max(matches)  # piu' alto numero progressivo
    src = open(fp, encoding='utf-8', errors='replace').read()
    for sec in REQUIRED_SECTIONS:
        if not re.search(sec, src, re.IGNORECASE):
            failures.append(f'sezione mancante nel report: {sec!r}')

    # Verdict line obbligatoria.
    if 'PRE_QA_VERTICAL_SLICE_PLAYABLE_PREVIEW_READY_FOR_DEVICE_QA' not in src \
       and 'PRE_QA_ULTRA_ACCELERATION_121_VERTICAL_SLICE_' not in src:
        failures.append('verdict line obbligatoria assente')

    if failures:
        return _emit(failures)

    print(f'[v121_report_completeness] PASS report={os.path.relpath(fp, R)} '
          f'sections_checked={len(REQUIRED_SECTIONS)}')
    return 0


def _emit(failures: list) -> int:
    print('[v121_report_completeness] FAIL')
    for f in failures:
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
