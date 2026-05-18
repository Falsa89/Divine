#!/usr/bin/env python3
"""Validator: suite supersedence cleanup V17 metadata."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPORT = Path('/app/data/design/system_safety/validator_suite_supersedence_cleanup_report_v1.json')
RUNNER = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')


def main():
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('SUITE SUPERSEDENCE CLEANUP V17 — Validator'); print('='*70)
    rec('report_present', REPORT.exists())
    if not REPORT.exists(): print('Overall: FAIL'); return 1
    data = json.loads(REPORT.read_text())
    rec('baseline_anchor_v6', data.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6')
    buckets = data.get('buckets', {})
    for b in ('ACTIVE_REQUIRED','ACTIVE_OPTIONAL','SUPERSEDED_PRE_AF2N','SUPERSEDED_PRE_INV_WRITES','HISTORICAL_MANUAL'):
        rec(f'bucket_present:{b}', b in buckets)
    rec('runner_present', RUNNER.exists())
    body = RUNNER.read_text()
    rec('runner_has_supersedence_logic_AF2N', 'SUPERSEDED_AFTER_AF2N' in body)
    rec('runner_has_supersedence_logic_INV', 'SUPERSEDED_AFTER_INV_WRITES' in body)
    rec('runner_no_active_required_removed', "'RM1.28-A'" in body and "'RM1.32-A'" in body and "'RM1.32-C2'" in body)
    pre_aft_inv = set(buckets.get('SUPERSEDED_PRE_INV_WRITES', {}).get('included_tasks', []))
    rec('superseded_pre_inv_writes_non_empty', len(pre_aft_inv) >= 20)
    rec('historical_manual_examples_listed', len(buckets.get('HISTORICAL_MANUAL', {}).get('examples', [])) >= 5)
    inv = data.get('safety_invariants', [])
    rec('battle_files_invariant_listed', any('battle_engine.py' in s for s in inv))
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
