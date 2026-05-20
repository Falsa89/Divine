#!/usr/bin/env python3
"""V27 PART D — Validator for cap raise S1."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_cap_raise_s1_v27_result.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') not in ('APPLIED', 'READY_NOT_APPLIED'):
        print('FAIL: status'); return 2
    if d.get('status') == 'APPLIED' and d.get('post_cap_observed') != d.get('new_cap_target'):
        print('FAIL: cap_mismatch'); return 2
    if d.get('safety', {}).get('broad_rollout_authorized') is True:
        print('FAIL: broad_must_false'); return 2
    print(f"PASS: AF2-N-V27-CAP-RAISE-S1 ({d.get('status')})"); return 0


if __name__ == '__main__':
    sys.exit(main())
