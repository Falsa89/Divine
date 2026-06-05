#!/usr/bin/env python3
"""v105 — Runtime consolidation roadmap validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_runtime_consolidation_roadmap_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
roadmap = d.get('roadmap') or []
if len(roadmap) < 7: print('FAIL \u2014 roadmap < 7 packs'); sys.exit(1)
for item in roadmap:
    for k in ('pack','title','priority','depends_on','deliverables','safety_constraints'):
        if k not in item: print(f'FAIL \u2014 roadmap item {item.get("pack")} missing {k}'); sys.exit(1)
required_packs = {'v106','v107','v108','v109','v110','v111','v112'}
present = {it.get('pack') for it in roadmap}
missing = required_packs - present
if missing: print(f'FAIL \u2014 missing roadmap packs {missing}'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('implementation_started_in_v105','db_writes','fake_PASS','validator_weakening','commercial_release_claim'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 runtime consolidation roadmap ({len(roadmap)} packs ordered)")
sys.exit(0)
