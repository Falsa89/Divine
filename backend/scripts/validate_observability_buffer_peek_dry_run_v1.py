#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib, json, os, subprocess, sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UTIL_REL = 'backend/utils/economy_observability_buffer_peek_dry_run.py'
MARKER_REL = 'data/design/economy_safety/observability_buffer_peek_dry_run_marker_v1.json'
DOC_REL = 'docs/divine/267_OBSERVABILITY_BUFFER_PEEK_DRY_RUN.md'
ROUTES = [
    'backend/routes/gem_socket_commit_safety_preview.py',
    'backend/routes/material_raid_claim_safety_preview.py',
    'backend/routes/gear_forge_fusion_safety_preview.py',
    'backend/routes/rune_scroll_talisman_safety_preview.py',
    'backend/routes/artifact_upgrade_safety_preview.py',
    'backend/routes/divine_weapon_upgrade_safety_preview.py',
    'backend/routes/battle_pass_claim_safety_preview.py',
    'backend/routes/mail_claim_safety_preview.py',
]
FAILURES = []
def fail(m): FAILURES.append(m)
def repo(p): return os.path.join(REPO_ROOT, p)
for rel in (UTIL_REL, MARKER_REL, DOC_REL):
    if not os.path.isfile(repo(rel)): fail(f'[1] missing: {rel}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN validator'); sys.exit(1)
proc = subprocess.run([sys.executable,'-m','py_compile',repo(UTIL_REL)], capture_output=True, text=True)
if proc.returncode != 0: fail(f'[2] py_compile fail: {proc.stderr[:200]}')
sys.path.insert(0, repo('backend'))
mod = importlib.import_module('utils.economy_observability_buffer_peek_dry_run')
for name in ('record_observability_preview','peek_buffer','build_buffer_status_block','_test_reset'):
    if not callable(getattr(mod, name, None)): fail(f'[3] missing callable {name}')
if mod.MAX_ENTRIES_PER_FAMILY_DEFAULT != 100: fail('[3] MAX_ENTRIES_PER_FAMILY_DEFAULT must be 100')
if mod.TTL_SECONDS_DEFAULT != 300: fail('[3] TTL_SECONDS_DEFAULT must be 300')
mod._test_reset()
# PII scrub: record entry with PII; peek must NOT leak
aep = {'audit_event_kind':'preview_invocation','operation_family':'material_raid_claim','operation':'x','server_request_hash':'h1','server_idempotency_key':'sik','user_id_hashed':'h','client_idempotency_key_present':True,'outcome':'success_preview_503','db_writes':0,'live_commit_executed':False,'live_claim_executed':False,'reward_granted':False,'safety_feature_flag_state':'enabled_preview_only','email':'leak@x.y','ip':'1.1.1.1','device_id':'D','push_token':'T','raw_payload':{'x':1}}
msp = {'metric_namespace':'economy_safety','operation_family':'material_raid_claim','route':'validate-claim-request','counters':{'economy_safety_db_writes_total':0,'economy_safety_live_commit_executions_total':0,'economy_safety_live_claim_executions_total':0,'economy_safety_reward_grants_total':0}}
for _ in range(5):
    mod.record_observability_preview('material_raid_claim', audit_event_preview=aep, metric_sample_preview=msp, route_name='validate-claim-request', detection_summaries={'decision':'preview_ok','blocked_reason_codes':[]})
pk = mod.peek_buffer('material_raid_claim', limit=10)
if pk.get('sizes_by_family',{}).get('material_raid_claim') != 5: fail(f'[3] buffer size != 5: {pk.get("sizes_by_family")}')
entries = pk.get('entries_by_family',{}).get('material_raid_claim') or []
for e in entries:
    audit = e.get('audit_summary',{})
    for fkey in ('email','ip','device_id','push_token','raw_payload','client_ip','phone','hwid'):
        if fkey in audit: fail(f'[3] PII leaked in audit_summary: {fkey}')
    if e.get('pii_safe') is not True: fail('[3] entry.pii_safe must be true')
    if e.get('db_writes') != 0: fail('[3] entry.db_writes must be 0')
    if e.get('persisted') is not False: fail('[3] entry.persisted must be false')
# Cap test: max_entries_per_family bounded
mod._test_reset(max_entries_per_family=3, ttl_seconds=300)
for i in range(10):
    mod.record_observability_preview('material_raid_claim', audit_event_preview={'operation_family':'material_raid_claim','operation':'x'}, metric_sample_preview=None, route_name='validate-claim-request')
pk2 = mod.peek_buffer('material_raid_claim', limit=50)
if pk2.get('sizes_by_family',{}).get('material_raid_claim',0) > 3: fail(f'[3] cap exceeded: {pk2["sizes_by_family"]}')
mod._test_reset()
status = mod.build_buffer_status_block()
for k, exp in [('enabled',True),('db_writes',0),('max_entries_per_family',100),('ttl_seconds',300),('pii_safe',True),('persistent_ledger_enabled',False),('redis_enabled',False),('not_shared_across_workers',True),('not_durable_across_restart',True)]:
    if status.get(k) != exp: fail(f'[3] status.{k} != {exp!r}')
for rel in ROUTES:
    src = open(repo(rel),'r',encoding='utf-8').read()
    if 'from utils.economy_observability_buffer_peek_dry_run import' not in src: fail(f'[4] {rel} no import')
    if src.count('_v44_buffer_record(') < 3: fail(f'[4] {rel} buffer_record < 3')
    if '@router.get("/peek-buffer")' not in src: fail(f'[4] {rel} no /peek-buffer endpoint')
    if '"observability_buffer_peek_dry_run": _v44_buffer_status_block()' not in src: fail(f'[4] {rel} cfg block missing')
    if 'raise HTTPException(status_code=503' not in src: fail(f'[4] {rel} 503 missing')
m = json.load(open(repo(MARKER_REL)))
for k, exp in [('runtime_activation',False),('db_writes',0),('persistent_ledger_enabled',False),('redis_enabled',False),('filesystem_writes_enabled',False),('max_entries_per_family',100),('ttl_seconds',300),('pii_safe',True),('raw_payload_stored',False),('reset_endpoint_exposed',False),('all_8_operation_families_instrumented',True),('endpoint_paths_unchanged',True),('feature_flags_unchanged',True),('default_503_behavior_unchanged',True),('safety_flags_unchanged',True)]:
    if m.get(k) != exp: fail(f'[5] marker.{k} != {exp!r}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN validator'); sys.exit(1)
print('[PASS] PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN validator'); sys.exit(0)
