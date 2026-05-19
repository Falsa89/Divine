#!/usr/bin/env python3
"""V25 PART D — Validator for fail-open alerting contract."""
import json, sys
from pathlib import Path
CONTRACT = Path('/app/data/design/affinity/af2n_fail_open_alerting_contract_v1.json')


def main():
    if not CONTRACT.exists(): print('FAIL: contract_missing'); return 2
    d = json.loads(CONTRACT.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: contract_verdict'); return 2
    rules = d.get('rules', [])
    required_ids = {'redis_fail_open', 'redis_unavailable', 'rate_limit_backend_not_redis',
                    'rate_limit_429_drop_under_burst', 'unauthorized_success', 'borea_success',
                    'negative_inventory', 'delta_mismatch', '5xx_threshold'}
    present = {r['id'] for r in rules}
    missing = required_ids - present
    if missing:
        print('FAIL: missing_rules', sorted(missing)); return 2
    if not d.get('safety', {}).get('no_pii'):
        print('FAIL: safety_no_pii'); return 2
    print(f'PASS: AF2-N-V25-FAIL-OPEN-ALERTING-CONTRACT (rules={len(rules)})'); return 0


if __name__ == '__main__':
    sys.exit(main())
