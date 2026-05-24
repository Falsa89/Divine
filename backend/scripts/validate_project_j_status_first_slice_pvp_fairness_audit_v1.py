#!/usr/bin/env python3
"""PROJECT_J REQUIRED-candidate 4 — PvP fairness audit (symmetric input → symmetric output)."""
import importlib.util, sys
from pathlib import Path
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    spec = importlib.util.spec_from_file_location('_pa', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    team_a = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.1}]
    team_b = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.1}]
    if mod.resolve_buff_envelope(team_a) != mod.resolve_buff_envelope(team_b):
        fail('symmetric input → asymmetric output (PvP unfairness)')
    print('[PASS] PvP fairness symmetric'); sys.exit(0)
if __name__ == '__main__': main()
