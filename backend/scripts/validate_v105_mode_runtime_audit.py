#!/usr/bin/env python3
"""v105 — Mode runtime audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_mode_runtime_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
modes = d.get('modes') or []
if len(modes) < 20: print('FAIL \u2014 modes < 20'); sys.exit(1)
required = {'mode','design_expected','current_status','has_lobby','has_team_selection','has_combat_renderer','has_reward_flow','has_server_scope','blocker','required_fix'}
for m in modes:
    missing = required - set(m.keys())
    if missing: print(f'FAIL \u2014 mode {m.get("mode")} missing {missing}'); sys.exit(1)
summ = d.get('summary') or {}
if summ.get('modes_total', 0) < 20: print('FAIL \u2014 modes_total < 20'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','new_modes_added','reward_mutation','battle_engine_modified','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 mode runtime audit ({len(modes)} modes)")
sys.exit(0)
