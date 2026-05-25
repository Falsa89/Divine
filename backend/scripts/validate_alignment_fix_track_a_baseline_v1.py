#!/usr/bin/env python3
# ALIGNMENT_FIX Track A validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/baseline_locks_mobile_qa_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_BASELINE_LOCKS_AND_MOBILE_QA_CONFIRMATION_READY'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['baseline']['last_suite_counts']['pass'] >= 600
    locks = d['locks_confirmed_by_mobile_qa']
    assert len(locks) >= 7
    issue = d['issue_to_fix_now']
    assert issue['area'] == 'soul_forge'
    print(f"[PASS] ALIGN-FIX Track A baseline\u2014locks_ok={len(locks)}")
    return 0
if __name__ == '__main__': sys.exit(main())
