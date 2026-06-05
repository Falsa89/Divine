#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v107b_backend_loader_server_id_acceptance_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('feature_flag_default',True): print('FAIL \u2014 flag default must be false'); sys.exit(1)
if d.get('adoption_status')!='REAL_ACCEPTANCE_ON_BATTLE_LAUNCH_ENDPOINT_OTHERS_CONTRACT_ONLY': print('FAIL \u2014 adoption_status wrong'); sys.exit(1)
live=d.get('endpoints_accepting_server_id_today') or []
if len(live)<1: print('FAIL \u2014 no real endpoint accepting server_id'); sys.exit(1)
for e in live:
    if not e.get('accepts_server_id',False): print(f'FAIL \u2014 {e.get("endpoint")} must accept_server_id'); sys.exit(1)
    if e.get('enforces_filtering',True): print(f'FAIL \u2014 {e.get("endpoint")} enforces_filtering must be false'); sys.exit(1)
if d.get('backend_isolation_live',True): print('FAIL \u2014 backend_isolation_live must be false'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token wrong'); sys.exit(1)
saf=d.get('safety') or {}
if saf.get('db_writes_performed',-1)!=0: print('FAIL \u2014 db_writes must be 0'); sys.exit(1)
if saf.get('loader_endpoints_modified_v107b',-1)!=0: print('FAIL \u2014 loader_endpoints_modified_v107b must be 0'); sys.exit(1)
for k in ('fake_isolation_live','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print(f"PASS \u2014 v107B backend loader server_id acceptance ({len(live)} live, others contract-only)"); sys.exit(0)
