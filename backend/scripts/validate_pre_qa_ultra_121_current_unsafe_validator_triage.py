#!/usr/bin/env python3
"""PRE_QA_ULTRA_121 — validate_pre_qa_ultra_121_current_unsafe_validator_triage.

Verifica che il triage JSON dei validator current-unsafe sia coerente con
il P0 (validator_truth_status_matrix_v1) e dichiari onestamente le
decisioni adottate.

Verifica:
  * triage JSON esiste e parsa.
  * Per ogni validator nella validator_truth_status_matrix_v1.json marcato
    come current_unsafe / environment_dependent, esiste un entry nel
    triage con decision_121 valida.
  * decisions enum rispetta i 4 valori dichiarati.
  * summary onesto: no fake PASS, no REQUIRED weakened, no historical
    doc deleted.
"""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
TRIAGE_FP = os.path.join(R, 'data', 'design', 'current_truth',
                         'ultra_121_current_unsafe_validator_triage_v1.json')
MATRIX_FP = os.path.join(R, 'data', 'design', 'current_truth',
                         'validator_truth_status_matrix_v1.json')
REPORTS_DIR = os.path.join(R, 'backend', 'reports', 'vertical_slice_qa')
os.makedirs(REPORTS_DIR, exist_ok=True)

VALID_DECISIONS = {
    'UPDATE_BASELINE_NOW', 'MARK_SUPERSEDED_HISTORICAL',
    'SPLIT_ENVIRONMENTAL_CHECK', 'DEFER_TO_DEDICATED_PACK',
}


def main() -> int:
    failures = []

    if not os.path.exists(TRIAGE_FP):
        failures.append(f'triage mancante: {TRIAGE_FP}')
        return _emit(failures)
    if not os.path.exists(MATRIX_FP):
        failures.append(f'matrix P0 mancante: {MATRIX_FP}')
        return _emit(failures)

    triage = json.load(open(TRIAGE_FP, encoding='utf-8'))
    matrix = json.load(open(MATRIX_FP, encoding='utf-8'))

    triage_paths = {e['validator_path']
                    for e in (triage.get('entries') or [])}

    # Per ogni unsafe/environment in matrix, deve esistere triage entry.
    unsafe_in_matrix = []
    for e in matrix.get('entries', []):
        if e.get('status_current_zip') in (
            'current_unsafe', 'environment_dependent_unreliable',
        ):
            unsafe_in_matrix.append(e['validator_path'])
            if e['validator_path'] not in triage_paths:
                failures.append(
                    f"triage 121 manca entry per validator unsafe in P0 matrix: "
                    f"{e['validator_path']}")

    # Decision enum.
    for e in triage.get('entries') or []:
        d = e.get('decision_121')
        if d not in VALID_DECISIONS:
            failures.append(
                f"triage entry {e.get('validator_path')!r}: "
                f"decision_121 non valida ({d!r})")

    # Honesty
    hs = triage.get('honesty_statement') or {}
    for k in ('no_runtime_change', 'no_fake_pass',
              'no_required_validator_weakening',
              'no_historical_doc_deletion'):
        if hs.get(k) is not True:
            failures.append(f'honesty_statement.{k} != true (val={hs.get(k)!r})')

    summary = triage.get('summary') or {}
    if summary.get('runtime_changes_introduced_by_triage', None) != 0:
        failures.append('summary.runtime_changes_introduced_by_triage != 0')
    if summary.get('fake_pass_introduced', None) != 0:
        failures.append('summary.fake_pass_introduced != 0')
    if summary.get('required_validator_weakened', None) != 0:
        failures.append('summary.required_validator_weakened != 0')
    if summary.get('historical_doc_deleted', None) != 0:
        failures.append('summary.historical_doc_deleted != 0')

    report = {
        'tool': 'validate_pre_qa_ultra_121_current_unsafe_validator_triage',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'triage_path': os.path.relpath(TRIAGE_FP, R),
        'unsafe_in_matrix_count': len(unsafe_in_matrix),
        'triage_entries_count': len(triage_paths),
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(
        REPORTS_DIR, 'ultra_121_current_unsafe_validator_triage_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[v121_unsafe_validator_triage] {report['verdict']}")
    if failures:
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'  unsafe_covered={len(unsafe_in_matrix)}/{len(unsafe_in_matrix)} '
          f'decision_enum_ok=true honesty_ok=true')
    return 0


def _emit(failures: list) -> int:
    print('[v121_unsafe_validator_triage] FAIL')
    for f in failures:
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
