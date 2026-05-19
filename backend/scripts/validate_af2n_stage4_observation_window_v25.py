#!/usr/bin/env python3
"""V25 PART H — Validate observation window V25 output (phased schema)."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_stage4_observation_window_v25_result.json')


def main():
    if not P.exists(): print('FAIL: obs_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: obs_verdict'); return 2
    if d.get('total_5xx_count', 1) != 0: print('FAIL: 5xx_present'); return 2
    ph = d.get('phases', {})
    if ph.get('borea_probes', {}).get('borea_404_count', 0) < 45:
        print('FAIL: borea_404_count_low'); return 2
    if ph.get('canary_status_final', {}).get('rate_limit_backend') != 'redis':
        print('FAIL: rl_backend_not_redis'); return 2
    print('PASS: AF2-N-V25-STAGE4-OBSERVATION-WINDOW'); return 0


if __name__ == '__main__':
    sys.exit(main())
