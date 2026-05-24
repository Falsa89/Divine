#!/usr/bin/env python3
"""PROJECT_J REQUIRED-candidate 3 — caps respect."""
import importlib.util, sys
from pathlib import Path
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    spec = importlib.util.spec_from_file_location('_cr', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    # Try huge values; envelope must be <= master cap
    s = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 100.0}, {'category': 'buff_defensive', 'stat': 'hp_pct', 'value': 100.0}]
    env = mod.resolve_buff_envelope(s)
    for stat, cap in mod.MASTER_CAP_PCT.items():
        if env[stat] > cap: fail(f'envelope {stat}={env[stat]} exceeds master cap {cap}')
    print('[PASS] envelope respects master cap'); sys.exit(0)
if __name__ == '__main__': main()
