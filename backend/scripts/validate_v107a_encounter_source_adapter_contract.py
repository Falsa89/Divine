#!/usr/bin/env python3
"""v107A — Encounter source adapter contract validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_encounter_source_adapter_contract_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
ada = d.get('adapters') or []
if len(ada) < 6: print(f'FAIL \u2014 adapters < 6 (got {len(ada)})'); sys.exit(1)
required_types = {'authored','player_team','bot_team','boss','training_preset','event_preset'}
for t in required_types:
    if not any(a.get('enemy_source_type') == t for a in ada): print(f'FAIL \u2014 adapter for {t} missing'); sys.exit(1)
for a in ada:
    for k in ('enemy_source_type','applies_to_modes','id_format','source','legacy_hero_id_risk'):
        if k not in a: print(f'FAIL \u2014 adapter {a.get("enemy_source_type")} missing {k}'); sys.exit(1)
proto = d.get('adapter_protocol') or {}
for k in ('input','output','side_effects','runtime_implementation_pack'):
    if k not in proto: print(f'FAIL \u2014 protocol.{k} missing'); sys.exit(1)
if proto.get('side_effects') != 'none': print('FAIL \u2014 protocol.side_effects must be none'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('legacy_hero_id_propagated','random_starter_heroes_in_encounter','db_writes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v107A encounter source adapter contract ({len(ada)} adapters, side_effects=none)")
sys.exit(0)
