#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107d_combat_parser_binding_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='COMBAT_BINDING_DEFERRED_TO_v108_PRE_LEGACY_VALIDATORS_PROTECTED': print('FAIL status'); sys.exit(1)
if d.get('combat_tsx_modified_v107d',True): print('FAIL combat_modified'); sys.exit(1)
h=d.get('helper_available','')
if 'combatLaunchParser.ts' not in h: print('FAIL helper ref'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('combat_tsx_changes','battle_engine_runtime_changes','fake_PASS','validator_weakening','silent_validator_deletion'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D combat parser binding (deferred to v108_pre)'); sys.exit(0)
