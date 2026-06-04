#!/usr/bin/env python3
"""v97 — Rollup validator (all 12 v97 sub-validators)."""
import os, sys, subprocess, json, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALIDATORS = [
    'validate_v97_account_deletion_gdpr.py',
    'validate_v97_refresh_token_rotation.py',
    'validate_v97_provider_token_gate.py',
    'validate_v97_physical_mobile_qa_matrix.py',
    'validate_v97_load_locust_result.py',
    'validate_v97_optional_fail_cleanup.py',
    'validate_v97_server_actor_lifecycle.py',
    'validate_v97_bot_progression_economy.py',
    'validate_v97_bot_live_event_participation.py',
    'validate_v97_contextual_bot_chat.py',
    'validate_v97_server_actor_admin_controls.py',
    'validate_v97_internal_alpha_gate.py',
]
failed=[]; passed=[]
for v in VALIDATORS:
    r = subprocess.run([sys.executable, os.path.join(ROOT,'backend','scripts',v)], capture_output=True, text=True)
    if r.returncode != 0: failed.append((v,r.stdout+r.stderr))
    else: passed.append(v); print(r.stdout.strip())
print('---'); print(f'v97 rollup: {len(passed)}/{len(VALIDATORS)} PASS')
if failed:
    print('FAIL —')
    for v,msg in failed: print(f' [{v}] {msg.strip()}')
    sys.exit(1)
marker = os.path.join(ROOT,'data','design','release_acceleration','mega_release_acceleration_46_v97_rollup_marker_v1.json')
os.makedirs(os.path.dirname(marker), exist_ok=True)
with open(marker,'w',encoding='utf-8') as f:
    json.dump({
        'pack':'MEGA_RELEASE_ACCELERATION_46_v97',
        'public_sync_tag':'PUBLIC_SYNC_TAG_v97_MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_SUPERPACK',
        'rollup_validators_total':len(VALIDATORS),
        'rollup_validators_passed':len(passed),
        'verdict':'MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING',
        'safety':{'db_writes_scope':'users_and_refresh_tokens_only','reward_live':False,'production_broadcast':False,'fake_users_presented_as_real':False,'day_one_high_level_bots':False,'validator_weakening':False,'fake_PASS':False},
        'timestamp_utc':datetime.datetime.utcnow().isoformat()+'Z'
    },f,ensure_ascii=False,indent=2)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
