#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/alerting_live_v28_probe_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    s = d.get('safety', {})
    if not s.get('no_secrets_logged'): print('FAIL: secrets'); return 2
    if not s.get('no_pii_in_payload'): print('FAIL: pii'); return 2
    print(f"PASS: AF2-N-V28-ALERTING-LIVE-PROBE ({d.get('sink_mode')})"); return 0
if __name__ == '__main__': sys.exit(main())
