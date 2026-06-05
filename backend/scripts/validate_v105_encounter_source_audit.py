#!/usr/bin/env python3
"""v105 — Encounter source audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_encounter_source_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
modes = d.get('modes') or []
if len(modes) < 8: print('FAIL \u2014 modes < 8'); sys.exit(1)
required = {'mode','current_source','random','authored','bot_or_player_team','boss','legacy_hero_id_risk','server_scoped','needs_replacement'}
for m in modes:
    missing = required - set(m.keys())
    if missing: print(f'FAIL \u2014 mode {m.get("mode")} missing {missing}'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('random_starter_heroes','legacy_heroes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 encounter source audit ({len(modes)} modes)")
sys.exit(0)
