#!/usr/bin/env python3
"""V21 — Audit affinity gift-spend rate-limit runtime.

Verifies that the route module exposes the V21 rate-limit guard and the
canary-status endpoint advertises the rate-limit config, and that no
battle/combat files were mutated.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from urllib.request import urlopen

ROUTE = Path('/app/backend/routes/affinity_gift_spend.py')
CONTRACT = Path('/app/data/design/affinity/affinity_gift_spend_rate_limit_runtime_contract_v1.json')


def main():
    fails = []
    if not ROUTE.exists():
        fails.append('route_missing')
        print('FAIL: route_missing'); return 2
    t = ROUTE.read_text()
    required_tokens = [
        '_RATE_LIMIT_ENV', '_RATE_LIMIT_ON_VALUE', '_rate_limit_enabled',
        '_rate_limit_check', '_RL_BURST_MAX', '_RL_PER_USER_PER_MIN',
        'AF2-N-V21-RATE-LIMIT', 'status_code=429',
    ]
    for tok in required_tokens:
        if tok not in t:
            fails.append(f'missing_token:{tok}')
    # ensure Borea check still runs first
    rb_pos = t.find('forbidden hero alias')
    rl_pos = t.find('AF2-N-V21-RATE-LIMIT')
    if rb_pos < 0 or rl_pos < 0 or rb_pos > rl_pos:
        fails.append('borea_check_must_precede_rate_limit')
    # ensure no battle/combat file changed
    out = subprocess.run([
        'git', '-C', '/app', 'diff', '--stat', '--',
        'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
        'backend/synergy_system.py', 'backend/game_systems.py'
    ], capture_output=True, text=True, timeout=10)
    if out.stdout.strip() != '':
        fails.append('battle_files_changed')
    # canary-status advertises rate-limit
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
        if 'rate_limit_enabled' not in st:
            fails.append('canary_status_missing_rate_limit_field')
        if st.get('rate_limit_per_user_per_minute') != 30:
            fails.append('canary_status_rl_per_user_min_mismatch')
        if st.get('rate_limit_burst_max') != 6:
            fails.append('canary_status_rl_burst_max_mismatch')
    except Exception as e:
        fails.append(f'canary_status_unreachable:{e}')
    if not CONTRACT.exists():
        fails.append('contract_doc_missing')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V21-RATE-LIMIT-AUDIT')
    return 0


if __name__ == '__main__':
    sys.exit(main())
