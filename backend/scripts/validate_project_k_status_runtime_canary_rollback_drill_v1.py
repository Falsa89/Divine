#!/usr/bin/env python3
"""PROJECT_K Track F validator — in-process rollback drill."""
import importlib.util, json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_runtime_canary_rollback_drill_v1.json')
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_STATUS_RUNTIME_CANARY_ROLLBACK_DRILL_EXECUTED_IN_PROCESS': fail('verdict mismatch')
    spec = importlib.util.spec_from_file_location('_r', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    try:
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        if not mod.is_runtime_active(): fail('D2: flag=true should activate')
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'false'
        if mod.is_runtime_active(): fail('D3: flag=false should deactivate')
        os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        if mod.is_runtime_active(): fail('D4: flag unset should deactivate')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    print('[PASS] PROJECT_K Track F rollback drill EXECUTED: true→active, false→inactive, unset→inactive')
    sys.exit(0)
if __name__ == '__main__': main()
