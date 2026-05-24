#!/usr/bin/env python3
"""PROJECT_J REQUIRED-candidate 1 — resolver pure deterministic."""
import importlib.util, json, sys
from pathlib import Path
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    spec = importlib.util.spec_from_file_location('_rd', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not mod.validate_invariants_static(): fail('static invariants False')
    s = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.1}, {'category': 'buff_defensive', 'stat': 'def_pct', 'value': 0.05}]
    a = mod.resolve_buff_envelope(s); b = mod.resolve_buff_envelope(s)
    if a != b: fail('not deterministic')
    snap = json.dumps(s)
    mod.resolve_buff_envelope(s)
    if json.dumps(s) != snap: fail('input mutated')
    print('[PASS] resolver pure deterministic'); sys.exit(0)
if __name__ == '__main__': main()
