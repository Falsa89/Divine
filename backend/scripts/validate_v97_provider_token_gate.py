#!/usr/bin/env python3
"""v97 — Validator: Provider token verification gate."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v97_provider_token_verification_gate_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
for prov in ('google','apple'):
    e = d.get(prov) or {}
    if e.get('verdict') not in ('READY','STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD'): print(f'FAIL — {prov} verdict'); sys.exit(1)
    if not e.get('env_required'): print(f'FAIL — {prov} env_required missing'); sys.exit(1)
if d.get('apple', {}).get('client_constraint') != 'iOS-only client side per policy Apple': print('FAIL — apple ios-only constraint'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('no_fake_production_readiness','sandbox_mode_clearly_labeled','credentials_required_for_store_build_marker'):
    if not safety.get(k): print(f'FAIL — safety.{k}'); sys.exit(1)
for k in ('raw_id_token_logged','provider_secret_in_repo'):
    if safety.get(k, True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
print('PASS — v97 provider token verification gate')
sys.exit(0)
