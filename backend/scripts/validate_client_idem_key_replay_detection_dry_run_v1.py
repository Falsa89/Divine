#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib, json, os, subprocess, sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UTIL_REL = 'backend/utils/economy_client_idem_key_replay_detection_dry_run.py'
MARKER_REL = 'data/design/economy_safety/client_idem_key_replay_detection_dry_run_marker_v1.json'
DOC_REL = 'docs/divine/266_CLIENT_IDEM_KEY_REPLAY_DETECTION_DRY_RUN.md'
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
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN validator'); sys.exit(1)
proc = subprocess.run([sys.executable,'-m','py_compile',repo(UTIL_REL)], capture_output=True, text=True)
if proc.returncode != 0: fail(f'[2] py_compile fail: {proc.stderr[:200]}')
sys.path.insert(0, repo('backend'))
mod = importlib.import_module('utils.economy_client_idem_key_replay_detection_dry_run')
for name in ('build_client_key_replay_detection_dry_run_envelope','build_config_block','_test_reset','_test_snapshot_size'):
    if not callable(getattr(mod, name, None)): fail(f'[3] missing callable {name}')
if mod.MAX_ENTRIES_DEFAULT != 256: fail('[3] MAX_ENTRIES_DEFAULT must be 256')
if mod.TTL_SECONDS_DEFAULT != 60: fail('[3] TTL_SECONDS_DEFAULT must be 60')
if mod.KEY_STRATEGY != 'client_key_user_server_family': fail('[3] KEY_STRATEGY mismatch')
mod._test_reset()
e = mod.build_client_key_replay_detection_dry_run_envelope
e1 = e('material_raid_claim', client_idempotency_key='CK1', request_hash='H1', user_id='u1', server_id='s1')
e2 = e('material_raid_claim', client_idempotency_key='CK1', request_hash='H1', user_id='u1', server_id='s1')
e3 = e('material_raid_claim', client_idempotency_key='CK1', request_hash='H2', user_id='u1', server_id='s1')
e4 = e('material_raid_claim', client_idempotency_key=None, request_hash=None)
if e1.get('detection_status') != 'new_client_key_preview': fail(f'[3] new state wrong: {e1.get("detection_status")}')
if e2.get('detection_status') != 'same_client_key_same_hash_replay_preview': fail(f'[3] replay state wrong: {e2.get("detection_status")}')
if e3.get('detection_status') != 'same_client_key_diff_hash_conflict_preview': fail(f'[3] conflict state wrong: {e3.get("detection_status")}')
if e4.get('detection_status') != 'missing_client_key_preview': fail(f'[3] missing state wrong: {e4.get("detection_status")}')
mod._test_reset()
mod.build_client_key_replay_detection_dry_run_envelope('material_raid_claim', client_idempotency_key='CK_X', request_hash='H1', user_id='u1', server_id='s1')
e5 = mod.build_client_key_replay_detection_dry_run_envelope('gem_socket_commit', client_idempotency_key='CK_X', request_hash='H1', user_id='u1', server_id='s1')
if e5.get('detection_status') != 'new_client_key_preview': fail('[3] cross-family must be new')
e6 = mod.build_client_key_replay_detection_dry_run_envelope('material_raid_claim', client_idempotency_key='CK_X', request_hash='H1', user_id='u2', server_id='s1')
if e6.get('detection_status') != 'new_client_key_preview': fail('[3] cross-user must be new')
for tag, env in (('e1',e1),('e2',e2),('e3',e3),('e4',e4)):
    for key, exp in [('db_writes',0),('persistent_ledger_enabled',False),('redis_enabled',False),('live_enforcement_enabled',False),('preview_request_blocked',False),('not_shared_across_workers',True),('not_durable_across_restart',True),('dry_run_only',True),('enabled',True),('max_entries',256),('ttl_seconds',60),('key_strategy','client_key_user_server_family')]:
        if env.get(key) != exp: fail(f'[3] {tag}.{key} != {exp!r}')
cfg = mod.build_config_block()
for k, exp in [('enabled',True),('db_writes',0),('max_entries',256),('ttl_seconds',60),('key_strategy','client_key_user_server_family'),('live_enforcement_enabled',False),('persistent_ledger_enabled',False),('redis_enabled',False),('not_shared_across_workers',True),('not_durable_across_restart',True)]:
    if cfg.get(k) != exp: fail(f'[3] cfg.{k} != {exp!r}')
for rel in ROUTES:
    src = open(repo(rel),'r',encoding='utf-8').read()
    if 'from utils.economy_client_idem_key_replay_detection_dry_run import' not in src: fail(f'[4] {rel} no import')
    if src.count('_v44_ck_env = _v44_client_key_replay_envelope(') != 3: fail(f'[4] {rel} ck_assign != 3')
    if src.count('"client_key_replay_detection_dry_run": _v44_ck_env') != 3: fail(f'[4] {rel} ck_resp != 3')
    if '"client_key_replay_detection_dry_run": _v44_client_key_replay_config_block()' not in src: fail(f'[4] {rel} cfg block missing')
    if 'raise HTTPException(status_code=503' not in src: fail(f'[4] {rel} 503 removed')
m = json.load(open(repo(MARKER_REL)))
for k, exp in [('runtime_activation',False),('db_writes',0),('live_enforcement_enabled',False),('persistent_ledger_enabled',False),('redis_enabled',False),('filesystem_writes_enabled',False),('preview_request_blocked',False),('key_strategy','client_key_user_server_family'),('max_entries',256),('ttl_seconds',60),('all_8_operation_families_instrumented',True),('endpoint_paths_unchanged',True),('feature_flags_unchanged',True),('default_503_behavior_unchanged',True),('safety_flags_unchanged',True)]:
    if m.get(k) != exp: fail(f'[5] marker.{k} != {exp!r}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN validator'); sys.exit(1)
print('[PASS] PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN validator'); sys.exit(0)
