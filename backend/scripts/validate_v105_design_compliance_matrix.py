#!/usr/bin/env python3
"""v105 — Design compliance matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_design_compliance_matrix_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
allowed_sev = set(d.get('severity_levels') or [])
if allowed_sev != {'P0','P1','P2','P3'}: print('FAIL \u2014 severity_levels must be P0/P1/P2/P3'); sys.exit(1)
matrix = d.get('matrix') or []
if len(matrix) < 25: print('FAIL \u2014 matrix < 25 systems'); sys.exit(1)
required_cols = {'system','approved','current','gap','severity','source_ref','required_pack'}
for row in matrix:
    missing = required_cols - set(row.keys())
    if missing: print(f'FAIL \u2014 row {row.get("system")} missing {missing}'); sys.exit(1)
    if row.get('severity') not in allowed_sev: print(f'FAIL \u2014 row {row.get("system")} invalid severity {row.get("severity")}'); sys.exit(1)
required_systems = {'Server lifecycle','Auth','Server selection','Player data isolation','Chat','Story','Tower','Arena','Battle renderer','Battle engine/status/DoT','Inventory','Roster','Bot actors','Summon/Gacha'}
present = {r.get('system') for r in matrix}
missing = required_systems - present
if missing: print(f'FAIL \u2014 missing systems {missing}'); sys.exit(1)
counts = d.get('counts') or {}
if counts.get('P0', 0) < 5: print('FAIL \u2014 P0 count < 5'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('design_changes','db_writes','fake_PASS','validator_weakening','commercial_release_claim'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 design compliance matrix ({len(matrix)} systems, {counts.get('P0')} P0)")
sys.exit(0)
