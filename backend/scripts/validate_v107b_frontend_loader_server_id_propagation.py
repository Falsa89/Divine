#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v107b_frontend_loader_server_id_propagation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('adoption_status')!='ADAPTERS_AVAILABLE_TSX_LOADERS_NOT_YET_PROPAGATING': print('FAIL \u2014 adoption_status wrong'); sys.exit(1)
for f in (d.get('hook'),d.get('helper')):
    if not os.path.isfile(os.path.join(R,f or '')): print(f'FAIL \u2014 file missing: {f}'); sys.exit(1)
for a in (d.get('adapters') or []):
    if not os.path.isfile(os.path.join(R,a)): print(f'FAIL \u2014 adapter missing: {a}'); sys.exit(1)
if len(d.get('loaders_should_propagate_server_id') or [])<10: print('FAIL \u2014 loaders < 10'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token wrong'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B frontend loader server_id propagation (helper+adapters present)'); sys.exit(0)
