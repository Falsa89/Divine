#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v107c_v107b_baseline_snapshot.py','validate_v107c_pre_battle_lobby_tsx_binding.py','validate_v107c_combat_tsx_parser_binding.py','validate_v107c_story_screen_launch_path.py','validate_v107c_backend_loader_server_id_acceptance.py','validate_v107c_frontend_loader_server_id_binding.py','validate_v107c_e2e_preview_smoke.py','validate_v107c_story_autoresolve_deprecation_guard.py','validate_v107c_route_menu_exposure_safety.py']
results=[]
for v in V:
    path=os.path.join(S,v)
    if not os.path.isfile(path): print(f'FAIL missing {v}'); sys.exit(1)
    r=subprocess.run([sys.executable,path],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print('---'); print(f'v107C rollup: {len(results)}/{len(V)} PASS')
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_58_v107c_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_58_v107C','type':'v107c_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':'MEGA_RELEASE_ACCELERATION_58_TSX_CONSUMER_BINDING_AND_BACKEND_LOADER_SERVER_ID_ACCEPTANCE_READY_WITH_PARTIAL_BINDING_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}'); sys.exit(0)
