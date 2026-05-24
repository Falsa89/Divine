#!/usr/bin/env python3
"""PROJECT_G Track C validator — status effect runtime readiness matrix.

Verifies:
  * marker present with verdict TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_READY
  * 10 categories covered, matching canonical adapter set
  * each row contains required fields: runtime_handler_needed, boss_behavior,
    stacking, cleanse_immunity, display_vfx_needed, test_coverage_status, blockers
  * adapter stub still NOT imported by battle_engine/battle_core/combat.tsx
  * runtime_changes_applied == False
"""
import importlib.util, json, sys
from pathlib import Path

MARKER = Path('/app/data/design/status_effects/project_g_status_effect_runtime_readiness_matrix_v1.json')
ADAPTER = Path('/app/backend/game_logic/status_effect_runtime_adapter_stub.py')
FORBIDDEN_IMPORT_TARGETS = (
    Path('/app/backend/game_logic/battle_engine.py'),
    Path('/app/backend/game_logic/battle_core.py'),
    Path('/app/frontend/components/combat.tsx'),
)
NEEDLE = 'status_effect_runtime_adapter_stub'
REQUIRED_FIELDS = ('runtime_handler_needed', 'boss_behavior', 'stacking', 'cleanse_immunity', 'display_vfx_needed', 'test_coverage_status', 'blockers')
EXPECTED_CATEGORIES = {
    'buff_offensive', 'buff_defensive', 'buff_support',
    'debuff_offensive', 'debuff_defensive',
    'control', 'dot', 'hot', 'shield', 'meta',
}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_READY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('runtime_active') is not False: fail('runtime_active must be False')
    matrix = m.get('matrix', [])
    if len(matrix) != 10: fail(f'matrix must have 10 rows, got {len(matrix)}')
    cats = {r.get('category') for r in matrix}
    if cats != EXPECTED_CATEGORIES: fail(f'matrix categories mismatch: missing={sorted(EXPECTED_CATEGORIES - cats)} extra={sorted(cats - EXPECTED_CATEGORIES)}')
    for row in matrix:
        for fld in REQUIRED_FIELDS:
            if fld not in row: fail(f'matrix row {row.get("category")} missing field {fld}')
        if not isinstance(row['blockers'], list): fail(f'matrix row {row.get("category")} blockers must be list')
    # Cross-check with adapter canonical categories
    spec = importlib.util.spec_from_file_location('_proj_g_status', ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if set(mod.CANONICAL_CATEGORIES) != EXPECTED_CATEGORIES:
        fail('adapter CANONICAL_CATEGORIES drift vs matrix expected')
    # Adapter still NOT imported by battle/runtime
    for p in FORBIDDEN_IMPORT_TARGETS:
        if p.exists() and NEEDLE in p.read_text():
            fail(f'adapter must NOT be imported by {p}')
    forb = m.get('forbidden_in_track_c_respected', {})
    for k in ('battle_mutation', 'runtime_status_activation', 'battle_engine_change', 'battle_core_change', 'combat_tsx_change'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_c.{k} must be False')
    print('[PASS] PROJECT_G Track C status effect runtime readiness matrix READY: 10/10 categories with 7 fields each; adapter NOT imported by runtime')
    sys.exit(0)

if __name__ == '__main__': main()
