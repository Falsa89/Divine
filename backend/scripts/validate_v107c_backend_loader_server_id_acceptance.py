#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v107c_backend_loader_server_id_acceptance_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('feature_flag_default',True): print('FAIL flag default'); sys.exit(1)
if d.get('adoption_status')!='PROBE_ROUTER_LIVE_5_ENDPOINTS_ACCEPT_SERVER_ID_NO_FILTER': print('FAIL adoption_status'); sys.exit(1)
rf=os.path.join(R,d.get('probe_router_file',''))
if not os.path.isfile(rf): print('FAIL probe router missing'); sys.exit(1)
c=open(rf,encoding='utf-8').read()
for t in ('/api/v107c/loader-probe','user-heroes','team-get-formation','inventory','currencies','story-progress','ACCEPTANCE_PROBE_NO_FILTER_APPLIED','SERVER_SCOPED_RUNTIME_ENABLED'):
    if t not in c: print(f'FAIL token {t}'); sys.exit(1)
eps=d.get('probe_endpoints') or []
if len(eps)<5: print('FAIL probe_endpoints<5'); sys.exit(1)
for e in eps:
    if not e.get('accepts_server_id',False): print(f'FAIL {e.get("endpoint")} accepts'); sys.exit(1)
    if e.get('filter_applied',True): print(f'FAIL {e.get("endpoint")} filter_applied'); sys.exit(1)
if d.get('existing_loader_endpoints_modified_v107c',-1)!=0: print('FAIL existing_loader_modified'); sys.exit(1)
if d.get('backend_isolation_live',True): print('FAIL backend_isolation_live'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL banner_token'); sys.exit(1)
saf=d.get('safety') or {}
if saf.get('db_writes_performed',-1)!=0: print('FAIL db_writes'); sys.exit(1)
for k in ('fake_isolation_live','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
srv=open(os.path.join(R,'backend','server.py'),encoding='utf-8').read()
if 'v107c_loader_server_id_probe_router' not in srv: print('FAIL server.py include missing'); sys.exit(1)
print(f"PASS \u2014 v107C backend loader server_id acceptance ({len(eps)} probes live)"); sys.exit(0)
