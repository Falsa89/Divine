#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v107d_failed_binding_forensic_audit.py','validate_v107d_tsx_md5_supersede_review.py','validate_v107d_pre_battle_lobby_real_binding.py','validate_v107d_combat_parser_binding.py','validate_v107d_story_launch_path.py','validate_v107d_backend_loader_server_id_real_acceptance.py','validate_v107d_e2e_smoke.py','validate_v107d_route_menu_exposure_safety.py','validate_v107d_optional_fail_baseline_guard.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print(f'v107D rollup: {len(results)}/{len(V)} PASS')
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_59_v107d_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_59_v107D','type':'v107d_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':'MEGA_RELEASE_ACCELERATION_59_TSX_MD5_SUPERSEDE_AND_REAL_BATTLE_LAUNCH_CONSUMER_BINDING_READY_WITH_PARTIAL_BINDING_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}'); sys.exit(0)
