#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v108_pre_v107d_baseline_snapshot.py','validate_v108_pre_combat_story_md5_forensic_audit.py','validate_v108_pre_combat_story_md5_supersede_review.py','validate_v108_pre_combat_launch_context_binding.py','validate_v108_pre_story_launch_path_binding.py','validate_v108_pre_pre_battle_lobby_compatibility.py','validate_v108_pre_e2e_story_lobby_launch_combat_smoke.py','validate_v108_pre_backend_loader_server_id_acceptance_status.py','validate_v108_pre_route_menu_exposure_safety.py','validate_v108_pre_optional_fail_validator_integrity_guard.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print(f'v108_pre rollup: {len(results)}/{len(V)} PASS')
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_60_v108_pre_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_60_v108_pre','type':'v108_pre_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'public_sync_tag':'PUBLIC_SYNC_TAG_v108_PRE_MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME','validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':'MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}'); sys.exit(0)
