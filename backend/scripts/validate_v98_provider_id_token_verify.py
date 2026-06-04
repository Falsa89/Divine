#!/usr/bin/env python3
"""v98 — Provider id_token verification."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','auth','v98_provider_id_token_verify_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
for prov in ('google','apple'):
    e=d.get(prov) or {}
    if e.get('verdict') not in ('READY','STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD'): print(f'FAIL — {prov} verdict'); sys.exit(1)
    if e.get('raw_id_token_logged',True): print(f'FAIL — {prov} raw_id_token_logged'); sys.exit(1)
    if not e.get('subject_hash_storage'): print(f'FAIL — {prov} subject_hash_storage'); sys.exit(1)
    if not e.get('env_required'): print(f'FAIL — {prov} env_required'); sys.exit(1)
safety=d.get('safety') or {}
for k in ('no_fake_production_readiness','sandbox_mode_clearly_labeled'):
    if not safety.get(k): print(f'FAIL — safety.{k}'); sys.exit(1)
for k in ('raw_oauth_token_logged','provider_secrets_in_repo'):
    if safety.get(k,True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
print('PASS — v98 provider id_token verify gate')
sys.exit(0)
