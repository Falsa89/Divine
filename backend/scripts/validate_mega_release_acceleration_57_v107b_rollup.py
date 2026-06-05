#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v107b_v107a_baseline_snapshot.py','validate_v107b_pre_battle_lobby_adoption.py','validate_v107b_combat_consumer_adoption.py','validate_v107b_story_to_lobby_routing.py','validate_v107b_backend_loader_server_id_acceptance.py','validate_v107b_frontend_loader_server_id_propagation.py','validate_v107b_battle_launch_smoke.py','validate_v107b_story_autoresolve_guard.py','validate_v107b_route_exposure_safety.py']
results=[]
for v in V:
    path=os.path.join(S,v)
    if not os.path.isfile(path): print(f'FAIL \u2014 missing {v}'); sys.exit(1)
    r=subprocess.run([sys.executable,path],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line)
    results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL \u2014 sub-validator {v} returned {r.returncode}'); sys.exit(1)
print('---')
print(f'v107B rollup: {len(results)}/{len(V)} PASS')
md=os.path.join(R,'data','design','release_acceleration')
os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_57_v107b_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_57_v107B','type':'v107b_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':'MEGA_RELEASE_ACCELERATION_57_BATTLE_LAUNCH_CONTRACT_ADOPTION_FRONTEND_CONSUMERS_AND_LOADER_SERVER_ID_ACCEPTANCE_READY_WITH_PARTIAL_ADOPTION_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}')
sys.exit(0)
