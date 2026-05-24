#!/usr/bin/env python3
"""PROJECT_J Track A validator — scope lock + flag contract."""
import importlib.util, json, os, sys
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_first_slice_scope_lock_v1.json')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_A_STATUS_FIRST_SLICE_SCOPE_LOCKED': fail('verdict mismatch')
    if set(m.get('slice_categories_locked', [])) != {'buff_offensive', 'buff_defensive'}: fail('slice categories mismatch')
    out_of = set(m.get('out_of_slice_excluded', []))
    must_exclude = {'buff_support', 'debuff_offensive', 'debuff_defensive', 'control', 'dot', 'hot', 'shield', 'meta'}
    if out_of != must_exclude: fail(f'out_of_slice_excluded mismatch: missing={sorted(must_exclude-out_of)}')
    if m.get('flag_name') != 'STATUS_RUNTIME_BUFF_SLICE_ENABLED': fail('flag_name mismatch')
    if m.get('flag_default_state') != 'OFF': fail('flag_default_state must be OFF')
    if os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED', '').strip().lower() == 'true':
        fail('flag must NOT be true in local backend env')
    spec = importlib.util.spec_from_file_location('_r', RESOLVER); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_runtime_active(): fail('resolver.is_runtime_active() must be False with flag OFF')
    print('[PASS] PROJECT_J Track A scope locked: {buff_offensive, buff_defensive}; flag OFF; resolver inactive')
    sys.exit(0)
if __name__ == '__main__': main()
