#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track B: PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42

Asserisce che:
  - backend/utils/economy_observability_dry_run.py esista e py_compile pulito
  - esponga le 3 funzioni richieste + build_config_block
  - audit_event preview matchi lo schema v41 (no PII, user_id hashed o None)
  - metric_sample preview includa invariant counters = 0
  - tutte le 8 safety preview route importino l'utility e usino l'envelope
  - endpoint path/feature flag/default 503 invariati
"""
from __future__ import annotations
import importlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UTIL_REL = 'backend/utils/economy_observability_dry_run.py'
MARKER_REL = 'data/design/economy_safety/economy_observability_runtime_dry_run_marker_v1.json'
DOC_REL = 'docs/divine/260_ECONOMY_OBSERVABILITY_RUNTIME_DRY_RUN.md'

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

FORBIDDEN_PII = {
    'email', 'display_name', 'raw_user_id', 'ip', 'client_ip',
    'device_id', 'device_serial', 'hwid', 'push_token',
    'phone', 'phone_number', 'raw_payload',
}

INVARIANT_ZERO = {
    'economy_safety_db_writes_total',
    'economy_safety_live_commit_executions_total',
    'economy_safety_live_claim_executions_total',
    'economy_safety_reward_grants_total',
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def read_text(rel: str) -> str:
    return open(repo(rel), 'r', encoding='utf-8').read()


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


# [1] file esistenti
for rel in (UTIL_REL, MARKER_REL, DOC_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN validator')
    sys.exit(1)

# [2] py_compile
proc = subprocess.run([sys.executable, '-m', 'py_compile', repo(UTIL_REL)],
                     capture_output=True, text=True)
if proc.returncode != 0:
    fail(f'[2] py_compile failed for {UTIL_REL}: {proc.stderr.strip()[:200]}')

# [3] import + behavior
sys.path.insert(0, repo('backend'))
try:
    mod = importlib.import_module('utils.economy_observability_dry_run')
except Exception as e:
    fail(f'[3] import utility failed: {e}')
    mod = None

if mod is not None:
    for name in ('build_audit_event_preview', 'build_metric_sample_preview',
                 'build_observability_dry_run_envelope', 'build_config_block'):
        if not callable(getattr(mod, name, None)):
            fail(f'[3] utility missing callable: {name}')

    ae = mod.build_audit_event_preview(
        'material_raid_claim', 'validate-claim-request',
        outcome='success_preview_503',
        request_hash='a'*32, server_idempotency_key='b'*24,
        user_id='user_x', client_idempotency_key_present=True,
    )
    for fkey in FORBIDDEN_PII:
        if fkey in ae:
            fail(f'[3] audit_event must not contain PII key: {fkey}')
    for key, exp in [
        ('audit_event_kind', 'preview_invocation'),
        ('operation_family', 'material_raid_claim'),
        ('db_writes', 0), ('live_commit_executed', False),
        ('live_claim_executed', False), ('reward_granted', False),
        ('persisted', False), ('sink_emitted', False),
    ]:
        if ae.get(key) != exp:
            fail(f'[3] audit_event.{key} must be {exp!r} (got {ae.get(key)!r})')
    if not (ae.get('user_id_hashed') and len(ae['user_id_hashed']) == 32):
        fail('[3] audit_event.user_id_hashed must be sha256 32-char hex')

    # raw user_id NEVER in audit
    if 'user_id' in ae and ae['user_id_hashed'] == 'user_x':
        fail('[3] audit_event must hash user_id, not store raw')

    ms = mod.build_metric_sample_preview('gem_socket_commit', 'validate-request')
    counters = ms.get('counters') or {}
    for k in INVARIANT_ZERO:
        if counters.get(k) != 0:
            fail(f'[3] metric_sample.{k} must be 0 (got {counters.get(k)!r})')
    if ms.get('persisted') is not False:
        fail('[3] metric_sample.persisted must be false')
    if ms.get('shipped_to_external_sink') is not False:
        fail('[3] metric_sample.shipped_to_external_sink must be false')

    env = mod.build_observability_dry_run_envelope(
        'mail_reward_claim', 'idempotency-preview', 'idempotency-preview',
    )
    for key, exp in [
        ('enabled', True),
        ('audit_event_preview_created', True),
        ('metric_sample_preview_created', True),
        ('persistent_audit_write_enabled', False),
        ('alert_sink_live_enabled', False),
        ('dashboard_runtime_deployed', False),
        ('external_sink_shipping_enabled', False),
        ('raw_pii_in_payload', False),
        ('db_writes', 0),
    ]:
        if env.get(key) != exp:
            fail(f'[3] envelope.{key} must be {exp!r} (got {env.get(key)!r})')

    cfg = mod.build_config_block()
    if cfg.get('enabled') is not True:
        fail('[3] config_block.enabled must be true')
    if cfg.get('db_writes') != 0:
        fail('[3] config_block.db_writes must be 0')
    for k in ('persistent_audit_write_enabled', 'alert_sink_live_enabled',
              'dashboard_runtime_deployed', 'external_sink_shipping_enabled'):
        if cfg.get(k) is not False:
            fail(f'[3] config_block.{k} must be false')

# [4] route wire-up
for rel in ROUTES:
    src = read_text(rel)
    if 'from utils.economy_observability_dry_run import' not in src:
        fail(f'[4] route {rel} does not import economy_observability_dry_run')
    if '_v42_obs_envelope(' not in src:
        fail(f'[4] route {rel} does not use _v42_obs_envelope')
    if '_v42_obs_config_block()' not in src:
        fail(f'[4] route {rel} does not use _v42_obs_config_block')
    if 'observability_dry_run' not in src:
        fail(f'[4] route {rel} response missing observability_dry_run key')
    if 'raise HTTPException(status_code=503' not in src:
        fail(f'[4] route {rel} default 503 behavior removed')

# [5] marker invariants
marker = load_json(MARKER_REL)
for key, exp in [
    ('runtime_activation', False), ('db_writes', 0),
    ('persistent_audit_write_enabled', False),
    ('alert_sink_live_enabled', False),
    ('dashboard_runtime_deployed', False),
    ('external_sink_shipping_enabled', False),
    ('endpoint_paths_unchanged', True),
    ('feature_flags_unchanged', True),
    ('default_503_behavior_unchanged', True),
    ('all_8_operation_families_instrumented', True),
]:
    if marker.get(key) != exp:
        fail(f'[5] marker.{key} must be {exp!r}')
if len(marker.get('wired_routes') or []) != 8:
    fail('[5] marker.wired_routes must list exactly 8 routes')
miss_inv = INVARIANT_ZERO - set(marker.get('invariant_counters_must_remain_zero') or [])
if miss_inv:
    fail(f'[5] marker.invariant_counters_must_remain_zero missing: {sorted(miss_inv)}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN validator')
    sys.exit(1)

print('[PASS] PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN validator')
sys.exit(0)
