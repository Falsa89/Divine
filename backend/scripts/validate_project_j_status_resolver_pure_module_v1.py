#!/usr/bin/env python3
"""PROJECT_J Track B validator — pure resolver module exists and not imported by runtime."""
import importlib.util, json, sys
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_resolver_pure_module_v1.json')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
FORBIDDEN = (Path('/app/backend/game_logic/battle_engine.py'), Path('/app/backend/game_logic/battle_core.py'), Path('/app/frontend/components/combat.tsx'))
NEEDLE = 'status_first_slice_resolver_pure'
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_B_STATUS_RESOLVER_PURE_MODULE_CREATED_INERT': fail('verdict mismatch')
    if not RESOLVER.exists(): fail('resolver module missing')
    spec = importlib.util.spec_from_file_location('_p', RESOLVER); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not mod.validate_invariants_static(): fail('resolver.validate_invariants_static() False')
    for p in FORBIDDEN:
        if p.exists() and NEEDLE in p.read_text():
            fail(f'resolver must NOT be imported by {p}')
    print('[PASS] PROJECT_J Track B pure resolver module created INERT: invariants OK; not imported by battle/runtime')
    sys.exit(0)
if __name__ == '__main__': main()
