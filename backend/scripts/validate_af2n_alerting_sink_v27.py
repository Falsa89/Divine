#!/usr/bin/env python3
"""V27 PART C — Validator for alerting sink."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_alerting_sink_v27_result.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('safety', {}).get('no_secrets_logged') is not True: print('FAIL: secrets'); return 2
    if d.get('safety', {}).get('no_pii_in_payload') is not True: print('FAIL: pii'); return 2
    if len(d.get('rules_required', [])) < 6: print('FAIL: rules'); return 2
    if d.get('mock_log_size_bytes', 0) <= 0 and d.get('sink_mode') == 'LOCAL_MOCK':
        print('FAIL: mock_log_empty'); return 2
    print(f"PASS: AF2-N-V27-ALERTING-SINK ({d.get('sink_mode')})"); return 0


if __name__ == '__main__':
    sys.exit(main())
