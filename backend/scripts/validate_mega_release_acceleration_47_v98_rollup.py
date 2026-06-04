#!/usr/bin/env python3
"""v98 — Rollup (all 13 v98 sub-validators)."""
import os, sys, subprocess, json, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALIDATORS=['validate_v98_optional_fail_cleanup.py','validate_v98_server_actor_runtime_persistence.py','validate_v98_bot_progression_runtime.py','validate_v98_bot_live_event_runtime.py','validate_v98_bot_chat_runtime_classifier.py','validate_v98_server_actor_admin_controls.py','validate_v98_gdpr_data_export_hard_delete.py','validate_v98_provider_id_token_verify.py','validate_v98_multi_provider_linking.py','validate_v98_live_privacy_terms_urls.py','validate_v98_full_load_locust.py','validate_v98_physical_mobile_qa.py','validate_v98_closed_alpha_gate.py']
failed=[]; passed=[]
for v in VALIDATORS:
    r=subprocess.run([sys.executable,os.path.join(ROOT,'backend','scripts',v)],capture_output=True,text=True)
    if r.returncode!=0: failed.append((v,r.stdout+r.stderr))
    else: passed.append(v); print(r.stdout.strip())
print('---'); print(f'v98 rollup: {len(passed)}/{len(VALIDATORS)} PASS')
if failed:
    print('FAIL —')
    for v,msg in failed: print(f' [{v}] {msg.strip()}')
    sys.exit(1)
marker=os.path.join(ROOT,'data','design','release_acceleration','mega_release_acceleration_47_v98_rollup_marker_v1.json')
os.makedirs(os.path.dirname(marker),exist_ok=True)
with open(marker,'w',encoding='utf-8') as f:
    json.dump({'pack':'MEGA_RELEASE_ACCELERATION_47_v98','public_sync_tag':'PUBLIC_SYNC_TAG_v98_MEGA_RELEASE_ACCELERATION_47_CLOSED_ALPHA_RAMPUP_AND_BOT_RUNTIME_SUPERPACK','rollup_validators_total':len(VALIDATORS),'rollup_validators_passed':len(passed),'verdict':'MEGA_RELEASE_ACCELERATION_47_CLOSED_ALPHA_RAMPUP_AND_BOT_RUNTIME_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING','safety':{'db_writes_scope':'users_and_refresh_tokens_only','reward_live':False,'production_broadcast':False,'fake_users_presented_as_real':False,'day_one_high_level_bots':False,'validator_weakening':False,'fake_PASS':False,'no_fake_urls':True},'timestamp_utc':datetime.datetime.utcnow().isoformat()+'Z'},f,ensure_ascii=False,indent=2)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
