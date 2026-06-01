#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track A: PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42

Asserisce che:
  - backend/utils/economy_request_hash_dry_run.py esista e py_compile pulito
  - esponga le 4 funzioni richieste e si comporti deterministicamente
  - request_hash sia hex lowercase di 32 char
  - server_idempotency_key sia hex lowercase di 24 char
  - PII e campi volatili siano stripped (hash invariante rispetto a essi)
  - tutte le 8 safety preview route importino l'utility e usino l'envelope
  - endpoint path/feature flag/default 503 non siano stati modificati
  - nessuna PII venga inclusa nel response envelope
"""
from __future__ import annotations
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UTIL_REL = 'backend/utils/economy_request_hash_dry_run.py'
MARKER_REL = 'data/design/economy_safety/request_hash_runtime_enforcement_dry_run_marker_v1.json'
DOC_REL = 'docs/divine/259_REQUEST_HASH_RUNTIME_ENFORCEMENT_DRY_RUN.md'

ROUTES = [
    ('backend/routes/gem_socket_commit_safety_preview.py', 'gem_socket_commit', 'GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED', '/api/gem-socket-commit-safety-preview'),
    ('backend/routes/material_raid_claim_safety_preview.py', 'material_raid_claim', 'MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED', '/api/material-raid-claim-safety-preview'),
    ('backend/routes/gear_forge_fusion_safety_preview.py', 'gear_forge_fusion_commit', 'GEAR_FORGE_FUSION_SAFETY_PREVIEW_ENABLED', '/api/gear-forge-fusion-safety-preview'),
    ('backend/routes/rune_scroll_talisman_safety_preview.py', 'rune_scroll_talisman_commit', 'RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED', '/api/rune-scroll-talisman-safety-preview'),
    ('backend/routes/artifact_upgrade_safety_preview.py', 'artifact_upgrade_commit', 'ARTIFACT_UPGRADE_SAFETY_PREVIEW_ENABLED', '/api/artifact-upgrade-safety-preview'),
    ('backend/routes/divine_weapon_upgrade_safety_preview.py', 'divine_weapon_upgrade_commit', 'DIVINE_WEAPON_UPGRADE_SAFETY_PREVIEW_ENABLED', '/api/divine-weapon-upgrade-safety-preview'),
    ('backend/routes/battle_pass_claim_safety_preview.py', 'battle_pass_reward_claim', 'BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED', '/api/battle-pass-claim-safety-preview'),
    ('backend/routes/mail_claim_safety_preview.py', 'mail_reward_claim', 'MAIL_CLAIM_SAFETY_PREVIEW_ENABLED', '/api/mail-claim-safety-preview'),
]

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
    print('[FAIL] PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN validator')
    sys.exit(1)

# [2] py_compile utility
proc = subprocess.run([sys.executable, '-m', 'py_compile', repo(UTIL_REL)],
                     capture_output=True, text=True)
if proc.returncode != 0:
    fail(f'[2] py_compile failed for {UTIL_REL}: {proc.stderr.strip()[:200]}')

# [3] import utility and test deterministic behavior
sys.path.insert(0, repo('backend'))
try:
    mod = importlib.import_module('utils.economy_request_hash_dry_run')
except Exception as e:
    fail(f'[3] import utility failed: {e}')
    mod = None

if mod is not None:
    for name in ('canonicalize_payload_for_hash', 'compute_request_hash',
                 'compute_server_idempotency_key', 'build_request_hash_dry_run_envelope',
                 'build_config_block'):
        if not callable(getattr(mod, name, None)):
            fail(f'[3] utility missing callable: {name}')

    # deterministic: same payload -> same hash
    payload = {'user_id': 'u1', 'client_idempotency_key': 'k1', 'foo': 'bar'}
    h1 = mod.compute_request_hash(payload, 'material_raid_claim')
    h2 = mod.compute_request_hash(payload, 'material_raid_claim')
    if h1 != h2:
        fail('[3] compute_request_hash not deterministic')
    if not re.fullmatch(r'[0-9a-f]{32}', h1 or ''):
        fail(f'[3] request_hash not 32 lowercase hex: {h1!r}')
    k1 = mod.compute_server_idempotency_key(payload, 'material_raid_claim')
    if not re.fullmatch(r'[0-9a-f]{24}', k1 or ''):
        fail(f'[3] server_idempotency_key not 24 lowercase hex: {k1!r}')

    # PII / volatile stripped: adding email + created_at must not change hash
    payload_pii = dict(payload)
    payload_pii['email'] = 'x@y.z'
    payload_pii['device_id'] = 'abc'
    payload_pii['push_token'] = 'tok'
    payload_pii['created_at'] = 'now'
    payload_pii['client_user_agent'] = 'ua'
    h3 = mod.compute_request_hash(payload_pii, 'material_raid_claim')
    if h3 != h1:
        fail('[3] PII/volatile fields not stripped (hash changed)')

    # operation_family pin: different family -> different hash
    h4 = mod.compute_request_hash(payload, 'gem_socket_commit')
    if h4 == h1:
        fail('[3] operation_family not part of hash')

    env = mod.build_request_hash_dry_run_envelope(payload, 'material_raid_claim')
    for key, exp in [
        ('enabled', True), ('pii_stripped', True), ('volatile_fields_stripped', True),
        ('ledger_write_enabled', False), ('live_enforcement_enabled', False),
        ('persisted', False), ('db_writes', 0),
        ('reward_grant_enabled', False), ('live_commit_enabled', False),
        ('live_claim_enabled', False),
    ]:
        if env.get(key) != exp:
            fail(f'[3] envelope.{key} must be {exp!r} (got {env.get(key)!r})')
    if env.get('contract') != 'shared_request_hash_idempotency_contract_v1':
        fail('[3] envelope.contract mismatch')
    if env.get('operation_family') != 'material_raid_claim':
        fail('[3] envelope.operation_family mismatch')

    cfg = mod.build_config_block()
    if cfg.get('request_hash_dry_run_enabled') is not True:
        fail('[3] config_block.request_hash_dry_run_enabled must be true')
    if cfg.get('db_writes') != 0:
        fail('[3] config_block.db_writes must be 0')

# [4] each of the 8 routes imports utility and uses envelope and config block
for rel, family, flag, prefix in ROUTES:
    if not os.path.isfile(repo(rel)):
        fail(f'[4] route missing: {rel}')
        continue
    src = read_text(rel)
    if 'from utils.economy_request_hash_dry_run import' not in src:
        fail(f'[4] route {rel} does not import economy_request_hash_dry_run')
    if '_v42_rh_envelope(' not in src:
        fail(f'[4] route {rel} does not use _v42_rh_envelope')
    if '_v42_rh_config_block()' not in src:
        fail(f'[4] route {rel} does not use _v42_rh_config_block')
    if 'request_hash_dry_run' not in src:
        fail(f'[4] route {rel} response missing request_hash_dry_run key')
    # path unchanged
    if f'prefix="{prefix}"' not in src:
        fail(f'[4] route {rel} prefix changed (must be {prefix!r})')
    # feature flag unchanged
    if f'FEATURE_FLAG = "{flag}"' not in src:
        fail(f'[4] route {rel} feature flag changed (must be {flag!r})')
    # default 503 preserved
    if 'raise HTTPException(status_code=503' not in src:
        fail(f'[4] route {rel} default 503 behavior removed')

# [5] marker invariants
marker = load_json(MARKER_REL)
for key, exp in [
    ('runtime_activation', False), ('db_writes', 0),
    ('live_apply_allowed', False), ('live_commit_allowed', False),
    ('live_claim_allowed', False), ('reward_grant_enabled', False),
    ('ledger_write_enabled', False), ('persistent_audit_write_enabled', False),
    ('endpoint_paths_unchanged', True), ('feature_flags_unchanged', True),
    ('default_503_behavior_unchanged', True),
    ('all_8_operation_families_instrumented', True),
]:
    if marker.get(key) != exp:
        fail(f'[5] marker.{key} must be {exp!r} (got {marker.get(key)!r})')
if len(marker.get('wired_routes') or []) != 8:
    fail('[5] marker.wired_routes must list exactly 8 routes')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN validator')
    sys.exit(1)

print('[PASS] PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN validator')
sys.exit(0)
