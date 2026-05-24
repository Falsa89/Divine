#!/usr/bin/env python3
"""PROJECT_J Track F validator — rollback + kill-switch plan."""
import importlib.util, json, os, sys
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_rollback_kill_switch_plan_v1.json')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_F_STATUS_ROLLBACK_KILL_SWITCH_PLAN_READY': fail('verdict mismatch')
    if m.get('kill_switch_flag') != 'STATUS_RUNTIME_BUFF_SLICE_ENABLED': fail('kill_switch_flag mismatch')
    if len(m.get('rollback_steps', [])) < 5: fail('at least 5 rollback steps required')
    # In-process kill-switch test
    spec = importlib.util.spec_from_file_location('_kr', RESOLVER); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    try:
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        if not mod.is_runtime_active(): fail('kill-switch test: flag ON should activate')
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'false'
        if mod.is_runtime_active(): fail('kill-switch test: flag OFF should deactivate')
        os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        if mod.is_runtime_active(): fail('kill-switch test: flag unset should deactivate')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    print('[PASS] PROJECT_J Track F rollback + kill-switch plan READY; in-process kill-switch toggle verified')
    sys.exit(0)
if __name__ == '__main__': main()
