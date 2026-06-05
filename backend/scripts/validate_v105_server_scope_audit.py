#!/usr/bin/env python3
"""v105 — Server scope audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_server_scope_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
surfaces = d.get('surfaces') or []
if len(surfaces) < 12: print('FAIL \u2014 surfaces < 12'); sys.exit(1)
required = {'surface','should_be_server_bound','current_filter','reads_selected_server_id','sends_server_id_to_backend','backend_enforces_server_id','data_leak_risk','fix_required'}
for s in surfaces:
    missing = required - set(s.keys())
    if missing: print(f'FAIL \u2014 surface {s.get("surface")} missing {missing}'); sys.exit(1)
if d.get('verdict') != 'SERVER_SCOPE_BACKEND_NOT_IMPLEMENTED': print('FAIL \u2014 verdict wrong'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','destructive_migration','fake_isolation','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 server scope audit ({len(surfaces)} surfaces)")
sys.exit(0)
