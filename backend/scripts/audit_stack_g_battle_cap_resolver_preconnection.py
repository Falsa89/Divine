#!/usr/bin/env python3
"""STACK-G-PRE — Audit pre-connection plan + preview adapter.

Ensures:
  - plan JSON + adapter module + audit doc/plan all present
  - battle_engine.py, battle_core.py, combat.tsx do NOT import the adapter
    or the resolver
  - adapter has no top-level mongo/pymongo/motor or `from battle_*` import
  - adapter.resolve_battle_cap_preview() returns runtime_attached=False
  - adapter detects borea / greek_borea / primordial_gaia and sets
    borea_filtered=True without exposing/activating them
"""
from __future__ import annotations
import importlib.util, json, sys, re
from pathlib import Path

PLAN = Path('/app/data/design/system_safety/stack_g_battle_cap_resolver_connection_plan_v1.json')
ADAPTER = Path('/app/backend/data/global_modifier_cap_battle_preview_adapter.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BATTLE_CORE = Path('/app/backend/battle_core.py')
COMBAT_TSX = Path('/app/frontend/app/combat.tsx')

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('plan_present', PLAN.exists(), str(PLAN))
p = json.loads(PLAN.read_text())
rec('plan_id', p.get('plan_id') == 'stack_g_battle_cap_resolver_connection_plan_v1', '')
rec('task_origin', p.get('task_origin') == 'STACK-G-PRE', '')
rec('design_only', p.get('design_only') is True, '')
rec('runtime_off', p.get('runtime_attached') is False, '')
rec('db_write_off', p.get('db_write') is False, '')
rec('baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('contract_present', isinstance(p.get('connection_contract'), dict), '')
rec('contract_inputs_min_3', len((p.get('connection_contract') or {}).get('inputs') or []) >= 3, '')
rec('contract_outputs_min_3', len((p.get('connection_contract') or {}).get('outputs') or []) >= 3, '')
rec('contract_side_effects_none', (p.get('connection_contract') or {}).get('side_effects') == 'none', '')
rec('safety_constraints_min_4', len(p.get('safety_constraints') or []) >= 4, '')

sf = p.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')
rec('sf_stack_g_off', sf.get('stack_g_battle_runtime_enabled') is False, '')

rec('adapter_present', ADAPTER.exists(), str(ADAPTER))
asrc = ADAPTER.read_text()
rec('adapter_no_motor_import',
    not re.search(r'(?m)^\s*(from\s+motor\b|import\s+motor\b)', asrc), '')
rec('adapter_no_pymongo_import',
    not re.search(r'(?m)^\s*(from\s+pymongo\b|import\s+pymongo\b)', asrc), '')
rec('adapter_no_battle_engine_import',
    'from backend.battle_engine' not in asrc and 'import battle_engine' not in asrc, '')
rec('adapter_no_battle_core_import',
    'from backend.battle_core' not in asrc and 'import battle_core' not in asrc, '')
rec('adapter_no_frontend_import',
    not re.search(r'(?m)^\s*(from\s+\S*frontend\S*|import\s+\S*frontend\S*)', asrc), '')
rec('adapter_no_db_write', 'insert_one' not in asrc and 'update_one' not in asrc
    and 'delete_one' not in asrc and 'create_collection' not in asrc, '')
rec('adapter_returns_runtime_false',
    "'runtime_attached': False" in asrc, '')
rec('adapter_borea_check',
    "'borea'" in asrc and 'greek_borea' in asrc and 'primordial_gaia' in asrc, '')
rec('adapter_entry_point_named',
    'def resolve_battle_cap_preview' in asrc, '')
rec('adapter_feature_flag_name',
    'STACK_G_BATTLE_RUNTIME_ENABLED' in asrc, '')

# Verify forbidden imports in battle/combat
for name, path in [('battle_engine', BATTLE_ENGINE),
                   ('battle_core', BATTLE_CORE),
                   ('combat_tsx', COMBAT_TSX)]:
    if path.exists():
        body = path.read_text()
        rec(f'{name}_no_adapter_import',
            'global_modifier_cap_battle_preview_adapter' not in body, '')
        rec(f'{name}_no_resolver_import',
            'global_modifier_cap_resolver' not in body, '')
    else:
        rec(f'{name}_present', False, f'missing: {path}')

# Dynamic load + call test (no DB, no DB write)
try:
    spec = importlib.util.spec_from_file_location('stack_g_adapter', ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out_normal = mod.resolve_battle_cap_preview('greek_zeus', 'fire', 'greek')
    rec('runtime_call_normal_ok', isinstance(out_normal, dict)
        and out_normal.get('runtime_attached') is False, f'got {out_normal!r}')
    rec('runtime_call_normal_borea_false', out_normal.get('borea_filtered') is False, '')
    out_borea = mod.resolve_battle_cap_preview('borea', 'wind', 'greek')
    rec('runtime_call_borea_filtered', out_borea.get('borea_filtered') is True, '')
    rec('runtime_call_borea_runtime_off', out_borea.get('runtime_attached') is False, '')
    env = out_normal.get('safety_envelope') or {}
    rec('envelope_flag_off', env.get('feature_flag_currently_enabled') is False, '')
except Exception as e:
    rec('runtime_call_normal_ok', False, f'{e!r}')

print('='*70); print('STACK-G-PRE — Pre-connection audit'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
