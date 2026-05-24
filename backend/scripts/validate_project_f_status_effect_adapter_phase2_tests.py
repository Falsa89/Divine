#!/usr/bin/env python3
"""PROJECT_F Track C validator — status effect adapter phase 2 contract tests.

8 non-runtime UT against the existing adapter stub. No runtime activation.
"""
import importlib.util, json, sys
from pathlib import Path

MARKER = Path('/app/data/design/status_effects/project_f_status_effect_adapter_phase2_tests_v1.json')
ADAPTER = Path('/app/backend/game_logic/status_effect_runtime_adapter_stub.py')
FORBIDDEN_IMPORT_TARGETS = (
    Path('/app/backend/game_logic/battle_engine.py'),
    Path('/app/backend/game_logic/battle_core.py'),
    Path('/app/frontend/components/combat.tsx'),
)
NEEDLE = 'status_effect_runtime_adapter_stub'


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_EFFECT_ADAPTER_PHASE2_TESTS_READY': fail('verdict mismatch')
    if m.get('unit_test_count') != 8: fail('unit_test_count must be 8')
    if not ADAPTER.exists(): fail(f'adapter missing {ADAPTER}')
    spec = importlib.util.spec_from_file_location('_proj_f_status_adapter', ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # UT1: rejects empty status_id
    try:
        mod.build_status_mapping('', 'buff_offensive', 'positive', 'none', 'normal', False, 'buff_icon')
        fail('UT_PHASE2_1: empty status_id must raise')
    except ValueError: pass
    # UT2: rejects unknown category
    try:
        mod.build_status_mapping('s1', 'bogus_category', 'positive', 'none', 'normal', False, 'buff_icon')
        fail('UT_PHASE2_2: unknown category must raise')
    except ValueError: pass
    # UT3: rejects unknown polarity/stacking/boss_behavior
    for kwargs, label in (
        ({'polarity': 'extra'}, 'polarity'),
        ({'stacking': 'extra'}, 'stacking'),
        ({'boss_behavior': 'extra'}, 'boss_behavior'),
    ):
        params = dict(status_id='s1', category='buff_offensive', polarity='positive', stacking='none', boss_behavior='normal', source_lock=False, display_hint='buff_icon')
        params.update(kwargs)
        try:
            mod.build_status_mapping(**params)
            fail(f'UT_PHASE2_3: unknown {label} must raise')
        except ValueError: pass
    # UT4: rejects non-bool source_lock
    try:
        mod.build_status_mapping('s1', 'buff_offensive', 'positive', 'none', 'normal', 'yes', 'buff_icon')
        fail('UT_PHASE2_4: non-bool source_lock must raise')
    except ValueError: pass
    # UT5: rejects unknown display_hint
    try:
        mod.build_status_mapping('s1', 'buff_offensive', 'positive', 'none', 'normal', False, 'glow_icon')
        fail('UT_PHASE2_5: unknown display_hint must raise')
    except ValueError: pass
    # UT6: build returns runtime_active=False
    out = mod.build_status_mapping('atk_up_5', 'buff_offensive', 'positive', 'refresh', 'normal', False, 'buff_icon')
    if out.get('runtime_active') is not False: fail('UT_PHASE2_6: runtime_active must be False')
    # UT7: validate_canonical_sets True
    if mod.validate_canonical_sets() is not True: fail('UT_PHASE2_7: validate_canonical_sets must return True')
    # UT8: adapter NOT imported by battle_engine/battle_core/combat.tsx
    for p in FORBIDDEN_IMPORT_TARGETS:
        if p.exists() and NEEDLE in p.read_text():
            fail(f'UT_PHASE2_8: adapter must NOT be imported by {p}')
    print('[PASS] PROJECT_F Track C status effect adapter PHASE2 OK: 8/8 UT pass; adapter NOT imported by battle/runtime')
    sys.exit(0)

if __name__ == '__main__': main()
