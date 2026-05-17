#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING-PRE — Audit.

Verifies:
  - adapter present, returns runtime_attached=False, borea_filtered semantics
  - no top-level battle_engine/battle_core/frontend imports
  - no motor/pymongo/insert_one in source
  - NO live route imports it
  - battle_engine.py / battle_core.py / combat.tsx do NOT import it
"""
from __future__ import annotations
import importlib.util, json, re, sys
from pathlib import Path

ADAPTER = Path('/app/backend/data/inventory_wiring_preview_adapter.py')
ROUTE_GIFT = Path('/app/backend/routes/affinity_gift_spend.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BATTLE_CORE = Path('/app/backend/battle_core.py')
COMBAT_TSX = Path('/app/frontend/app/combat.tsx')

failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('adapter_present', ADAPTER.exists(), str(ADAPTER))
asrc = ADAPTER.read_text()
rec('adapter_has_entry_point', 'def preview_inventory_apply' in asrc, '')
rec('adapter_no_motor_import', not re.search(r'(?m)^\s*(from\s+motor\b|import\s+motor\b)', asrc), '')
rec('adapter_no_pymongo_import', not re.search(r'(?m)^\s*(from\s+pymongo\b|import\s+pymongo\b)', asrc), '')
rec('adapter_no_insert_one', 'insert_one' not in asrc, '')
rec('adapter_no_update_one', 'update_one' not in asrc, '')
rec('adapter_no_delete_one', 'delete_one' not in asrc, '')
rec('adapter_no_battle_engine_import',
    'from backend.battle_engine' not in asrc and 'import battle_engine' not in asrc, '')
rec('adapter_no_battle_core_import',
    'from backend.battle_core' not in asrc and 'import battle_core' not in asrc, '')
rec('adapter_no_frontend_import',
    not re.search(r'(?m)^\s*(from\s+\S*frontend\S*|import\s+\S*frontend\S*)', asrc), '')
rec('adapter_runtime_attached_false', "'runtime_attached': False" in asrc, '')
rec('adapter_borea_block', 'borea' in asrc and 'greek_borea' in asrc and 'primordial_gaia' in asrc, '')
rec('adapter_feature_flag_name', 'AFFINITY_GIFT_INVENTORY_WIRING_ENABLED' in asrc, '')

# Live route MUST NOT import the adapter
for name, path in [('route_gift_spend', ROUTE_GIFT), ('battle_engine', BATTLE_ENGINE),
                   ('battle_core', BATTLE_CORE), ('combat_tsx', COMBAT_TSX)]:
    if path.exists():
        body = path.read_text()
        rec(f'{name}_no_adapter_import', 'inventory_wiring_preview_adapter' not in body, '')

# Dynamic call test
try:
    spec = importlib.util.spec_from_file_location('inv_preview', ADAPTER)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    out_normal = mod.preview_inventory_apply('user_canary_001','gift_x','greek_zeus',1,0)
    rec('call_normal_runtime_off', out_normal.get('runtime_attached') is False, '')
    rec('call_normal_status', out_normal.get('would_have_status') == 'applied_preview_only', '')
    rec('call_normal_no_borea', out_normal.get('borea_filtered') is False, '')
    out_borea = mod.preview_inventory_apply('user_canary_001','gift_x','borea',1,0)
    rec('call_borea_runtime_off', out_borea.get('runtime_attached') is False, '')
    rec('call_borea_filtered', out_borea.get('borea_filtered') is True, '')
    rec('call_borea_status', out_borea.get('would_have_status') == 'borea_filtered', '')
    rec('call_borea_no_inventory', out_borea.get('would_have_consumed_inventory') is False, '')
    env = out_normal.get('safety_envelope') or {}
    rec('envelope_flag_off', env.get('feature_flag_currently_enabled') is False, '')
    rec('envelope_db_write_false', env.get('db_write') is False, '')
except Exception as e:
    rec('call_normal_runtime_off', False, f'{e!r}')

print('='*70); print('AF2-N-INVENTORY-WIRING-PRE — Audit'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
