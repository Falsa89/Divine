#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_stage4_observation_v27_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('total_5xx_count', 1) != 0: print('FAIL: 5xx'); return 2
    if d.get('phases', {}).get('canary_status_final', {}).get('rate_limit_backend') != 'redis':
        print('FAIL: rl_backend'); return 2
    print('PASS: AF2-N-V27-STAGE4-OBSERVATION'); return 0
if __name__ == '__main__': sys.exit(main())
