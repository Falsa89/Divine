#!/usr/bin/env python3
"""PROJECT_M Track A validator — battle_engine single-point wiring audit."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_m_battle_engine_single_point_audit_v1.json')
BE = Path('/app/backend/battle_engine.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_BATTLE_ENGINE_SINGLE_POINT_WIRING_AUDIT_READY': fail('verdict mismatch')
    if m.get('insertion_point_classification') != 'SINGLE_POINT_SAFE_NOW_FLAGGED': fail('classification must be SINGLE_POINT_SAFE_NOW_FLAGGED')
    if not BE.exists(): fail('battle_engine.py missing')
    txt = BE.read_text(encoding='utf-8', errors='ignore')
    if 'def simulate_battle' not in txt: fail('simulate_battle not found in battle_engine.py')
    forb = m.get('forbidden_in_track_a_respected', {})
    for k in ('runtime_mutation_in_track_a', 'battle_behavior_change_in_track_a', 'broad_refactor'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_a.{k} must be False')
    print('[PASS] PROJECT_M Track A single-point audit READY: SINGLE_POINT_SAFE_NOW_FLAGGED')
    sys.exit(0)


if __name__ == '__main__': main()
