#!/usr/bin/env python3
"""v98 — GDPR data export + hard delete cron."""
import os, sys, json, urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for rel in ('data/design/auth/v98_gdpr_data_export_result_v1.json','data/design/auth/v98_hard_delete_cron_result_v1.json'):
    if not os.path.isfile(os.path.join(ROOT,rel)): print(f'FAIL — missing: {rel}'); sys.exit(1)
with open(os.path.join(ROOT,'data/design/auth/v98_gdpr_data_export_result_v1.json'),'r',encoding='utf-8') as f: d1=json.load(f)
with open(os.path.join(ROOT,'data/design/auth/v98_hard_delete_cron_result_v1.json'),'r',encoding='utf-8') as f: d2=json.load(f)
if d1.get('endpoint')!='GET /api/auth/data-export': print('FAIL — data-export endpoint'); sys.exit(1)
if not d1.get('runtime_verified'): print('FAIL — data-export runtime_verified'); sys.exit(1)
excl=d1.get('fields_excluded_for_security') or []
for f in ('provider_user_id_hash','password_hash','refresh_token_hash'):
    if f not in excl: print(f'FAIL — data-export missing exclusion: {f}'); sys.exit(1)
if d2.get('runtime_apply_status')!='GATED_DEFAULT_OFF': print('FAIL — hard_delete runtime_apply_status'); sys.exit(1)
if d2.get('cron_runtime_mode')!='DRY_RUN_ONLY_SCAN_PENDING_DELETION': print('FAIL — cron mode'); sys.exit(1)
# live smoke
BASE=os.environ.get('V98_BASE_URL','http://localhost:8001')
import urllib.request as _u
req=_u.Request(BASE+'/api/auth/guest',data=json.dumps({'alias_hint':'gdpr_v98'}).encode('utf-8'),headers={'Content-Type':'application/json'},method='POST')
with _u.urlopen(req,timeout=5) as r: token=json.loads(r.read().decode('utf-8'))['token']
req2=_u.Request(BASE+'/api/auth/data-export',headers={'Authorization':f'Bearer {token}'})
with _u.urlopen(req2,timeout=5) as r:
    if r.status!=200: print(f'FAIL — data-export status {r.status}'); sys.exit(1)
req3=_u.Request(BASE+'/api/auth/hard-delete-confirm',data=b'',headers={'Authorization':f'Bearer {token}','Content-Type':'application/json'},method='POST')
with _u.urlopen(req3,timeout=5) as r:
    dd=json.loads(r.read().decode('utf-8'))
    if dd.get('hard_delete_runtime')!='DISABLED_PENDING_COMMERCIAL_REVIEW': print(f'FAIL — hard_delete unexpected: {dd}'); sys.exit(1)
print('PASS — v98 GDPR data export + hard delete cron')
sys.exit(0)
