#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v108_pre_backend_loader_server_id_acceptance_status_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('feature_flag_default',True): print('FAIL flag'); sys.exit(1)
if d.get('adoption_status')!='V107C_PROBE_ROUTER_LIVE_NO_NEW_LOADER_MODIFIED_v108_PRE': print('FAIL adoption'); sys.exit(1)
if d.get('probe_endpoints_live',0)!=5: print('FAIL probes'); sys.exit(1)
if d.get('filter_applied',True): print('FAIL filter_applied'); sys.exit(1)
if d.get('backend_isolation_live',True): print('FAIL isolation_live'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL banner'); sys.exit(1)
if not d.get('blocker_for_v108_runtime'): print('FAIL blocker'); sys.exit(1)
saf=d.get('safety') or {}
if saf.get('db_writes_performed',-1)!=0: print('FAIL db_writes'); sys.exit(1)
for k in ('fake_isolation_live','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre backend loader server_id acceptance status (probe-only, honest)'); sys.exit(0)
