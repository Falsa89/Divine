#!/usr/bin/env python3
"""v105 — Battle launch contract audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_battle_launch_contract_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
contract = d.get('contract_target') or {}
required = {'server_id','mode','encounter_id','player_team_id','player_team_snapshot','enemy_source_type','reward_policy','progress_policy','battle_engine_mode','idempotency_key'}
missing = required - set(contract.keys())
if missing: print(f'FAIL \u2014 contract_target missing {missing}'); sys.exit(1)
cur = d.get('current_state') or {}
if 'combat.tsx' not in cur: print('FAIL \u2014 combat.tsx audit missing'); sys.exit(1)
if cur.get('combat.tsx', {}).get('accepts_launch_context', True): print('FAIL \u2014 combat.tsx accepts_launch_context must be false (honest)'); sys.exit(1)
if len(d.get('surfaces_currently_launching_battle') or []) < 5: print('FAIL \u2014 surfaces_currently_launching_battle < 5'); sys.exit(1)
if len(d.get('gaps') or []) < 3: print('FAIL \u2014 gaps < 3'); sys.exit(1)
if not d.get('required_fix_pack'): print('FAIL \u2014 required_fix_pack missing'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('battle_engine_modified','combat_tsx_rewritten','new_battle_endpoints_added','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print('PASS \u2014 v105 battle launch contract audit (contract defined, gaps documented)')
sys.exit(0)
