#!/usr/bin/env python3
"""V25 PART A — Validator for preflight result."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_v25_preflight_result_v1.json')


def main():
    if not P.exists():
        print('FAIL: preflight_result_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS':
        print('FAIL: preflight_verdict_not_pass'); return 2
    c = d.get('checks', {})
    fails = []
    if c.get('heroes_count') != 100: fails.append('heroes_count')
    if c.get('borea_leak_in_list'): fails.append('borea_leak')
    if not all([c.get('gift_spend_borea_404'), c.get('gift_spend_greek_borea_404'),
                c.get('gift_spend_primordial_gaia_404')]):
        fails.append('borea_404')
    if c.get('canary_rate_limit_backend') != 'redis': fails.append('rl_backend')
    if c.get('battle_runtime_attached') is not False: fails.append('battle_attached')
    if not all((c.get('guardrail_diffs_clean') or {}).values()): fails.append('guardrails')
    if fails:
        for f in fails: print('FAIL:', f)
        return 2
    print('PASS: AF2-N-V25-PREFLIGHT'); return 0


if __name__ == '__main__':
    sys.exit(main())
