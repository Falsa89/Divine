#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING-SHADOW — Audit + result validator.

Verifies:
  - adapter file exists and is inert (no motor/pymongo/insert_one/etc.)
  - adapter not imported by any live route / battle / UI file
  - shadow probe result is PASS, ledger unchanged, all invariants True
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ADAPTER = Path('/app/backend/data/affinity_gift_inventory_shadow_adapter.py')
RESULT = Path('/app/data/design/affinity/affinity_gift_inventory_shadow_wiring_result_v1.json')
ROUTE = Path('/app/backend/routes/affinity_gift_spend.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BATTLE_CORE = Path('/app/backend/battle_core.py')
COMBAT_TSX = Path('/app/frontend/app/combat.tsx')

failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('adapter_present', ADAPTER.exists(), str(ADAPTER))
asrc = ADAPTER.read_text()
rec('adapter_entry', 'def shadow_inventory_apply' in asrc, '')
rec('adapter_no_motor', not re.search(r'(?m)^\s*(from\s+motor\b|import\s+motor\b)', asrc), '')
rec('adapter_no_pymongo', not re.search(r'(?m)^\s*(from\s+pymongo\b|import\s+pymongo\b)', asrc), '')
rec('adapter_no_insert_one', not re.search(r'\.\s*insert_one\s*\(', asrc), '')
rec('adapter_no_update_one', not re.search(r'\.\s*update_one\s*\(', asrc), '')
rec('adapter_no_delete_one', not re.search(r'\.\s*delete_one\s*\(', asrc), '')
rec('adapter_no_battle_engine_import', 'from backend.battle_engine' not in asrc and 'import battle_engine' not in asrc, '')
rec('adapter_no_battle_core_import', 'from backend.battle_core' not in asrc and 'import battle_core' not in asrc, '')
rec('adapter_no_frontend_import', not re.search(r'(?m)^\s*(from\s+\S*frontend\S*|import\s+\S*frontend\S*)', asrc), '')
rec('adapter_runtime_attached_false',
    re.search(r'["\']runtime_attached["\']\s*:\s*False', asrc) is not None, '')
rec('adapter_db_write_false',
    re.search(r'["\']db_write["\']\s*:\s*False', asrc) is not None, '')
rec('adapter_borea_block', 'borea' in asrc and 'greek_borea' in asrc and 'primordial_gaia' in asrc, '')
rec('adapter_feature_flag_name', 'AFFINITY_GIFT_INVENTORY_WIRING_ENABLED' in asrc, '')

for name, path in [('route_gift_spend', ROUTE), ('battle_engine', BATTLE_ENGINE),
                   ('battle_core', BATTLE_CORE), ('combat_tsx', COMBAT_TSX)]:
    if path.exists():
        body = path.read_text()
        rec(f'{name}_no_shadow_import', 'affinity_gift_inventory_shadow_adapter' not in body, '')

rec('result_present', RESULT.exists(), str(RESULT))
r = json.loads(RESULT.read_text())
rec('result_id', r.get('result_id') == 'affinity_gift_inventory_shadow_wiring_result_v1', '')
rec('result_task', r.get('task_origin') == 'AF2-N-INVENTORY-WIRING-SHADOW', '')
rec('result_runtime_off', r.get('runtime_attached') is False, '')
rec('result_db_write_off', r.get('db_write') is False, '')
rec('result_baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('result_overall_pass', r.get('overall_status') == 'PASS', '')
for inv_name in ('ledger_unchanged','all_runtime_attached_false','all_shadow_only_true',
                 'all_db_write_false','borea_filtered_correctly','rollback_contract_present_all',
                 'insufficient_inv_rejected','normal_ok_applied_shadow'):
    rec(f'invariant:{inv_name}', (r.get('invariants') or {}).get(inv_name) is True, '')

print('='*70); print('AF2-N-INVENTORY-WIRING-SHADOW — Audit + Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
