#!/usr/bin/env python3
"""PROJECT_K Track D validator — canary fixture execution against pure resolver."""
import importlib.util, json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_canary_fixture_execution_v1.json')
FIX = Path('/app/data/design/status_effects/project_j_status_fixture_matrix_and_golden_tests_v1.json')
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_STATUS_CANARY_FIXTURE_EXECUTION_READY_NO_DRY_RUN_PATH_AVAILABLE': fail('verdict mismatch')
    spec = importlib.util.spec_from_file_location('_r', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    fixtures = json.loads(FIX.read_text()).get('fixture_matrix', [])
    for f in fixtures:
        out = mod.resolve_buff_envelope(f.get('input', []))
        exp = f.get('expected_envelope', {})
        for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct'):
            if abs(out.get(k, 0.0) - exp.get(k, 0.0)) > 1e-9:
                fail(f'fixture {f.get("id")} mismatch on {k}')
    print(f'[PASS] PROJECT_K Track D fixture execution {len(fixtures)}/{len(fixtures)} PASS against pure resolver')
    sys.exit(0)
if __name__ == '__main__': main()
