#!/usr/bin/env python3
"""V25 PART F — Validate economy stress 10x simulation result."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_economy_stress_10x_simulation_v25_result.json')


def main():
    if not P.exists(): print('FAIL: sim_result_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: sim_verdict'); return 2
    if d.get('mode') != 'READ_ONLY_SIMULATION': print('FAIL: mode_not_sim'); return 2
    if d.get('live_mutations', -1) != 0: print('FAIL: live_mutations_nonzero'); return 2
    sc = d.get('scenarios', {})
    for s in ('1x', '2x', '5x', '10x'):
        if s not in sc: print(f'FAIL: missing_scenario:{s}'); return 2
    s10 = sc['10x']
    for k in ('users_modeled', 'ledger_cap', 'expected_total_spend_events',
              'cap_pressure_ratio', 'expected_429_events',
              'redis_ops_per_sec_peak_estimate'):
        if k not in s10: print(f'FAIL: 10x_missing_key:{k}'); return 2
    safety = d.get('safety', {})
    for k in ('no_db_mutation', 'no_http_calls', 'no_broad_rollout', 'no_borea_data', 'no_pii'):
        if safety.get(k) is not True: print(f'FAIL: safety:{k}'); return 2
    print('PASS: AF2-N-V25-ECONOMY-STRESS-10X-SIMULATION'); return 0


if __name__ == '__main__':
    sys.exit(main())
