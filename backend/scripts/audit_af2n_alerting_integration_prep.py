#!/usr/bin/env python3
"""V26 PART F — Validator for alerting integration prep."""
import json, sys
from pathlib import Path
PLAN = Path('/app/data/design/affinity/af2n_alerting_integration_plan_v1.json')
AUDIT = Path('/app/data/design/affinity/af2n_alerting_integration_prep_result_v1.json')


def main():
    if not PLAN.exists(): print('FAIL: plan_missing'); return 2
    if not AUDIT.exists(): print('FAIL: audit_missing'); return 2
    p = json.loads(PLAN.read_text())
    a = json.loads(AUDIT.read_text())
    if p.get('verdict') != 'PASS': print('FAIL: plan_verdict'); return 2
    if a.get('verdict') != 'PASS': print('FAIL: audit_verdict'); return 2
    if p.get('live_integration_in_v26') is True: print('FAIL: live_forbidden'); return 2
    if p.get('secrets_in_repo') is True: print('FAIL: secrets_in_repo'); return 2
    if len(p.get('sinks_evaluated', [])) < 3: print('FAIL: insufficient_sinks'); return 2
    if not p.get('safety', {}).get('no_secrets_committed'): print('FAIL: safety_secrets'); return 2
    print('PASS: AF2-N-V26-ALERTING-INTEGRATION-PREP'); return 0


if __name__ == '__main__':
    sys.exit(main())
