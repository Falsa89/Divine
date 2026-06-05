#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: server scope deve restare PENDING dichiarato, ensure_server_scope NON e' filtro reale.
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','server_scope','v108_pre_backend_loader_server_id_acceptance_status_v1.json')
if not os.path.isfile(p): print('FAIL acceptance status JSON missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('backend_isolation_live',True): print('FAIL backend_isolation_live=true (must be false)'); sys.exit(1)
if d.get('filter_applied',True): print('FAIL filter_applied=true (must be false)'); sys.exit(1)
if d.get('banner_token')!='SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL banner token wrong'); sys.exit(1)
saf=d.get('safety') or {}
if saf.get('fake_isolation_live',True): print('FAIL fake_isolation_live=true'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: server scope honestly PENDING, no false positive'); sys.exit(0)
