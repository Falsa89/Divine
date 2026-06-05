#!/usr/bin/env python3
# v108_POSTQA_A — Rollup di tutti i validator runtime-invariant + result JSONs + sentinel.
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v108_postqa_invariant_suite_relocatable.py','validate_v108_postqa_invariant_preview_no_simulate.py','validate_v108_postqa_invariant_preview_no_rewards_affinity.py','validate_v108_postqa_invariant_story_no_qa_autoresolve_player_facing.py','validate_v108_postqa_invariant_lobby_no_fake_team_launch.py','validate_v108_postqa_invariant_lobby_launch_context_to_combat.py','validate_v108_postqa_invariant_no_generate_enemy_player_facing.py','validate_v108_postqa_invariant_no_bot_default_startup.py','validate_v108_postqa_invariant_mutation_endpoint_watchlist.py','validate_v108_postqa_invariant_server_scope_false_positive.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0:
        print(f'FAIL sub {v}'); sys.exit(1)
print(f'v108_POSTQA_A rollup: {len(results)}/{len(V)} PASS')
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_61_v108_postqa_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_61_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A','type':'v108_postqa_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'public_sync_tag':'PUBLIC_SYNC_TAG_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A','validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':'MEGA_RELEASE_ACCELERATION_61_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}'); sys.exit(0)
