#!/usr/bin/env python3
"""v105 — Frontend route inventory validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_frontend_route_inventory_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('total_route_files', 0) < 50: print('FAIL \u2014 too few routes inventoried'); sys.exit(1)
allowed = set(d.get('classifications_allowed') or [])
required_classes = {'PLAYER_FACING_READY','PLAYER_FACING_BROKEN','PREVIEW_ONLY','QA_ONLY','SANDBOX','DEPRECATED','HIDDEN_INTENTIONAL','NEEDS_ROUTING_DECISION','DANGEROUS_IF_EXPOSED'}
if not required_classes.issubset(allowed): print(f'FAIL \u2014 missing classifications {required_classes - allowed}'); sys.exit(1)
routes = d.get('routes') or []
if len(routes) < 30: print('FAIL \u2014 routes audited < 30'); sys.exit(1)
for r in routes:
    if r.get('classification') not in allowed: print(f'FAIL \u2014 invalid classification {r.get("classification")} for {r.get("path")}'); sys.exit(1)
if len(d.get('preview_only_routes') or []) < 20: print('FAIL \u2014 preview routes < 20 (drift documented)'); sys.exit(1)
if len(d.get('qa_only_routes') or []) < 5: print('FAIL \u2014 qa routes < 5'); sys.exit(1)
if len(d.get('key_findings') or []) < 3: print('FAIL \u2014 key_findings < 3'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','new_routes_added','reward_mutation','battle_engine_modified','combat_tsx_rewritten','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 frontend route inventory ({len(routes)} routes detailed, {d.get('total_route_files')} total)")
sys.exit(0)
