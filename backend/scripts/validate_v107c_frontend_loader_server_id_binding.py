#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v107c_frontend_loader_server_id_binding_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
for f in (d.get('hook'),d.get('helper')):
    if not os.path.isfile(os.path.join(R,f or '')): print(f'FAIL missing {f}'); sys.exit(1)
for a in (d.get('adapters') or []):
    if not os.path.isfile(os.path.join(R,a)): print(f'FAIL adapter {a}'); sys.exit(1)
if d.get('binding_kind')!='helper_adapter_ready_tsx_binding_reverted_protecting_md5_baseline': print('FAIL binding_kind'); sys.exit(1)
if len(d.get('loaders_target_v108_real_filter') or [])<10: print('FAIL loaders<10'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL banner_token'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C frontend loader server_id binding (helper+adapters ready, tsx binding reverted)'); sys.exit(0)
