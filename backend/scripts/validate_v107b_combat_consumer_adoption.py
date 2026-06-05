#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_combat_consumer_adoption_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='PARSER_HELPER_INTRODUCED_COMBAT_TSX_UNCHANGED': print('FAIL \u2014 status wrong'); sys.exit(1)
if d.get('combat_tsx_modified',True): print('FAIL \u2014 combat_tsx_modified must be false'); sys.exit(1)
if d.get('combat_tsx_behavior_rewritten',True): print('FAIL \u2014 combat_tsx_behavior_rewritten must be false'); sys.exit(1)
mod=os.path.join(R,d.get('parser_module',''))
if not os.path.isfile(mod): print(f'FAIL \u2014 parser missing: {mod}'); sys.exit(1)
c=open(mod,encoding='utf-8').read()
for t in ('readLaunchContextFromRouterParams','readLaunchContextFromPostResponse','parseLaunchContextFromParams','validateLaunchContext'):
    if t not in c: print(f'FAIL \u2014 parser missing {t}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('combat_tsx_changes','battle_engine_runtime_changes','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B combat consumer adoption (parser helper, combat.tsx unchanged)'); sys.exit(0)
