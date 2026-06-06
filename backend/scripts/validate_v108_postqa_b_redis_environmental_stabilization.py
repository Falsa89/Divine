#!/usr/bin/env python3
import os,sys,json,subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_redis_environmental_stabilization_v1.json')))
# Verify actual Redis is running before claiming stabilization
try:
    r=subprocess.run(['redis-cli','ping'],capture_output=True,text=True,timeout=3)
    if 'PONG' not in r.stdout.upper(): print('FAIL redis not responding PONG'); sys.exit(1)
except Exception as e:
    print(f'FAIL redis-cli error: {e}'); sys.exit(1)
if not d.get('redis_daemon_running',False): print('FAIL daemon_running flag'); sys.exit(1)
if d.get('redis_ping_response')!='PONG': print('FAIL ping_response'); sys.exit(1)
if d.get('runtime_gameplay_altered',True): print('FAIL gameplay_altered=true'); sys.exit(1)
if d.get('redis_production_ready_claim',True): print('FAIL production_ready_claim=true'); sys.exit(1)
if d.get('redis_local_container_only',False) is not True: print('FAIL local_container_only=false'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_passed_redis','validator_ignored_redis_absence_without_proof','production_ready_claim','gameplay_economy_touched'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_POSTQA_B redis environmental stabilization (PONG verified)'); sys.exit(0)
