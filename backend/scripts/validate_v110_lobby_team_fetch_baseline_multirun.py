#!/usr/bin/env python3
# Pack 80 — Track A: baseline 3-run suite snapshot (legge il summary, NON ri-esegue la suite).
import os, json, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
b = d.get('baseline_pre_pack', {})
assert b.get('required_fail') == 0, f'REQUIRED FAIL must be 0, got {b}'
assert b.get('miss') == 0, f'MISS must be 0, got {b}'
assert b.get('pass', 0) > 1000, f'baseline pass too low: {b}'
print(f"[v110 LOBBY_TEAM_FETCH_BASELINE_MULTIRUN] OK pass={b.get('pass')} fail={b.get('fail')} required_fail=0 miss=0")
