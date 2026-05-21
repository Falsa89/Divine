#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/observability/af2n_observability_dashboard_spec_v1.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('panel_count', 0) < 10: print('FAIL: panels<10'); return 2
    if d.get('alert_count', 0) < 5: print('FAIL: alerts<5'); return 2
    if not d.get('safety', {}).get('plan_only'): print('FAIL: not_plan_only'); return 2
    print('PASS: AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC'); return 0
if __name__ == '__main__': sys.exit(main())
