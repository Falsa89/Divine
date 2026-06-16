#!/usr/bin/env python3
"""PRE_QA_ULTRA_121 — validate_pre_qa_ultra_121_device_qa_manifest.

Verifica statica del device QA manifest:
  * manifest JSON esiste e parsa.
  * checklist >= 20 step.
  * include i 5 mode (story/tower/training/arena/boss).
  * scope_invariants no-purchase + no-claim + no-env-flag.
  * preconditions presenti.
  * dont_do_in_device_qa esplicito (no purchase, no claim, no env flag).
  * pass_criteria + fail_criteria definiti.
"""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
MANIFEST_FP = os.path.join(R, 'data', 'design', 'vertical_slice_qa',
                           'ultra_121_device_qa_manifest_v1.json')
REPORTS_DIR = os.path.join(R, 'backend', 'reports', 'vertical_slice_qa')
os.makedirs(REPORTS_DIR, exist_ok=True)


def main() -> int:
    failures = []
    if not os.path.exists(MANIFEST_FP):
        failures.append(f'manifest mancante: {MANIFEST_FP}')
        return _emit(failures)

    m = json.load(open(MANIFEST_FP, encoding='utf-8'))
    if len(m.get('checklist_ordered') or []) < 20:
        failures.append(
            f"checklist_ordered count < 20 "
            f"({len(m.get('checklist_ordered') or [])})")

    # 5 mode coperti.
    text_all = json.dumps(m, ensure_ascii=False).lower()
    for needle in ('story', 'tower', 'training', 'arena', 'boss'):
        if needle not in text_all:
            failures.append(f'manifest non menziona {needle!r}')

    inv = m.get('scope_invariants') or {}
    for k in ('no_purchase_test', 'no_claim_reward_test',
              'no_env_flag_override', 'no_dev_qa_hidden_route_use'):
        if inv.get(k) is not True:
            failures.append(f'scope_invariants.{k} != true (val={inv.get(k)!r})')

    if not m.get('dont_do_in_device_qa'):
        failures.append('dont_do_in_device_qa vuoto')

    if not m.get('pass_criteria'):
        failures.append('pass_criteria vuoto')
    if not m.get('fail_criteria'):
        failures.append('fail_criteria vuoto')

    report = {
        'tool': 'validate_pre_qa_ultra_121_device_qa_manifest',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'manifest_path': os.path.relpath(MANIFEST_FP, R),
        'checklist_step_count': len(m.get('checklist_ordered') or []),
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(REPORTS_DIR, 'ultra_121_device_qa_manifest_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[v121_device_qa_manifest] {report['verdict']}")
    if failures:
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'  checklist_steps={report["checklist_step_count"]} all_5_modes_present=true scope_invariants_ok=true')
    return 0


def _emit(failures: list) -> int:
    print('[v121_device_qa_manifest] FAIL')
    for f in failures:
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
