#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_combat_launch_context_binding_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='COMBAT_LAUNCH_CONTEXT_BINDING_APPLIED_PREVIEW_NON_AUTHORITATIVE': print('FAIL status'); sys.exit(1)
tsx=os.path.join(R,d.get('tsx_file',''))
c=open(tsx,encoding='utf-8').read()
for t in ('readLaunchContextFromRouterParams','combatLaunchParser','PREVIEW_NON_AUTHORITATIVE','LEGACY_COMBAT_ENTRY','v108_pre'):
    if t not in c: print(f'FAIL token {t}'); sys.exit(1)
if not d.get('legacy_fallback_preserved',False): print('FAIL fallback'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','reward_grant','progress_live_write','battle_engine_formula_rewrite','broad_combat_rewrite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre combat launch context binding (preview, non-authoritative)'); sys.exit(0)
