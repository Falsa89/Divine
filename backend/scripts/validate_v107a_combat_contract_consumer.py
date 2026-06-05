#!/usr/bin/env python3
"""v107A — Combat renderer contract consumer validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_combat_contract_consumer_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('status') != 'ADAPTER_DOCUMENTED_BEHAVIOR_UNCHANGED': print('FAIL \u2014 status wrong'); sys.exit(1)
if d.get('combat_tsx_behavior_rewritten', True): print('FAIL \u2014 combat_tsx_behavior_rewritten must be false'); sys.exit(1)
ac = d.get('adapter_contract') or {}
for k in ('input_source','required_fields_for_render','fallback_when_missing','future_authoritative_path'):
    if k not in ac: print(f'FAIL \u2014 adapter_contract.{k} missing'); sys.exit(1)
if len(ac.get('required_fields_for_render') or []) < 3: print('FAIL \u2014 required_fields_for_render < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('combat_tsx_changes','battle_engine_runtime_changes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A combat contract consumer (adapter documented, behavior unchanged)')
sys.exit(0)
