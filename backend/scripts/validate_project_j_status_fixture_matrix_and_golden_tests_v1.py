#!/usr/bin/env python3
"""PROJECT_J Track D validator — fixture matrix + 10 golden tests against resolver."""
import importlib.util, json, sys
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_fixture_matrix_and_golden_tests_v1.json')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_D_STATUS_FIXTURE_MATRIX_AND_GOLDEN_TESTS_READY': fail('verdict mismatch')
    spec = importlib.util.spec_from_file_location('_r', RESOLVER); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    fixtures = m.get('fixture_matrix', [])
    if len(fixtures) < 10: fail('at least 10 fixtures required')
    for f in fixtures:
        out = mod.resolve_buff_envelope(f.get('input', []))
        exp = f.get('expected_envelope', {})
        for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct'):
            if abs(out.get(k, 0.0) - exp.get(k, 0.0)) > 1e-9:
                fail(f'fixture {f.get("id")} mismatch on {k}: got {out.get(k)} expected {exp.get(k)}')
    # Determinism: call twice with same input → same output
    sample = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.15}]
    if mod.resolve_buff_envelope(sample) != mod.resolve_buff_envelope(sample): fail('determinism violated')
    # Side-effect free: input not mutated
    orig = [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.05}]
    snapshot = json.dumps(orig)
    mod.resolve_buff_envelope(orig)
    if json.dumps(orig) != snapshot: fail('side-effect: input mutated')
    print(f'[PASS] PROJECT_J Track D fixture matrix + {len(fixtures)} golden tests PASS; determinism + side-effect-free verified')
    sys.exit(0)
if __name__ == '__main__': main()
