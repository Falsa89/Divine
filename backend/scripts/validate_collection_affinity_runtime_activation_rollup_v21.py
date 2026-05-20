#!/usr/bin/env python3
"""V26 PART L — Validator for Safety Rollup U."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v21.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('broad_rollout_authorized') is not False: print('FAIL: broad'); return 2
    if d.get('public_spend_ui') is not False: print('FAIL: public_ui'); return 2
    if d.get('battle_wiring_live') is not False: print('FAIL: battle'); return 2
    if d.get('borea_hidden') is not True: print('FAIL: borea'); return 2
    if d.get('api_heroes_count_100') is not True: print('FAIL: heroes'); return 2
    if not all((d.get('guardrails_clean') or {}).values()): print('FAIL: guardrails'); return 2
    print('PASS: AF2-N-V26-SAFETY-ROLLUP-U'); return 0


if __name__ == '__main__':
    sys.exit(main())
