#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_combat_tsx_parser_binding_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='TSX_BINDING_REVERTED_LEGACY_MD5_VALIDATORS_PROTECTED': print('FAIL status'); sys.exit(1)
if not d.get('binding_attempted',False): print('FAIL binding_attempted'); sys.exit(1)
if not d.get('binding_reverted_reason'): print('FAIL reverted_reason'); sys.exit(1)
if not d.get('alternative_binding_path'): print('FAIL alternative_binding_path'); sys.exit(1)
if d.get('combat_tsx_behavior_rewritten',True): print('FAIL behavior_rewritten'); sys.exit(1)
if d.get('combat_render_path_changed',True): print('FAIL render_path_changed'); sys.exit(1)
if d.get('battle_engine_runtime_changed',True): print('FAIL battle_engine_runtime_changed'); sys.exit(1)
saf=d.get('safety') or {}
if saf.get('combat_tsx_changes',True): print('FAIL safety.combat_tsx_changes'); sys.exit(1)
for k in ('battle_engine_runtime_changes','fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C combat tsx parser binding (reverted to protect MD5 baseline, helper available for v108)'); sys.exit(0)
