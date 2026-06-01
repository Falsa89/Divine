#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track A: PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_PACK_v43

Asserisce che:
  - backend/utils/economy_idempotency_replay_detection_dry_run.py esista e
    py_compile pulito
  - esponga le 2 funzioni richieste + costanti
  - i 4 detection statuses siano coperti deterministicamente in isolamento
  - preview_request mai bloccato
  - db_writes, persistent_ledger, redis, filesystem, live_enforcement = OFF
  - tutte le 8 safety preview route importino l'utility e usino l'envelope
  - endpoint path/feature flag/default 503 invariati
  - v42 request_hash + observability envelope invariati nei response
"""
from __future__ import annotations
import importlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UTIL_REL = 'backend/utils/economy_idempotency_replay_detection_dry_run.py'
DESIGN_REL = 'data/design/economy_safety/economy_idempotency_replay_detection_dry_run_v1.json'
DOC_REL = 'docs/divine/264_ECONOMY_IDEMPOTENCY_REPLAY_DETECTION_DRY_RUN.md'

ROUTES = [
    ('backend/routes/gem_socket_commit_safety_preview.py', 'gem_socket_commit', '/api/gem-socket-commit-safety-preview', 'GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/material_raid_claim_safety_preview.py', 'material_raid_claim', '/api/material-raid-claim-safety-preview', 'MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/gear_forge_fusion_safety_preview.py', 'gear_forge_fusion_commit', '/api/gear-forge-fusion-safety-preview', 'GEAR_FORGE_FUSION_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/rune_scroll_talisman_safety_preview.py', 'rune_scroll_talisman_commit', '/api/rune-scroll-talisman-safety-preview', 'RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/artifact_upgrade_safety_preview.py', 'artifact_upgrade_commit', '/api/artifact-upgrade-safety-preview', 'ARTIFACT_UPGRADE_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/divine_weapon_upgrade_safety_preview.py', 'divine_weapon_upgrade_commit', '/api/divine-weapon-upgrade-safety-preview', 'DIVINE_WEAPON_UPGRADE_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/battle_pass_claim_safety_preview.py', 'battle_pass_reward_claim', '/api/battle-pass-claim-safety-preview', 'BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED'),
    ('backend/routes/mail_claim_safety_preview.py', 'mail_reward_claim', '/api/mail-claim-safety-preview', 'MAIL_CLAIM_SAFETY_PREVIEW_ENABLED'),
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


# [1] file presence
for rel in (UTIL_REL, DESIGN_REL, DOC_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN validator')
    sys.exit(1)

# [2] py_compile
proc = subprocess.run([sys.executable, '-m', 'py_compile', repo(UTIL_REL)],
                     capture_output=True, text=True)
if proc.returncode != 0:
    fail(f'[2] py_compile failed: {proc.stderr.strip()[:200]}')

# [3] import + functional checks (isolated, deterministic)
sys.path.insert(0, repo('backend'))
try:
    mod = importlib.import_module('utils.economy_idempotency_replay_detection_dry_run')
except Exception as e:
    fail(f'[3] import utility failed: {e}')
    mod = None

if mod is not None:
    for name in ('build_replay_detection_dry_run_envelope', 'build_config_block',
                 '_test_reset', '_test_snapshot_size'):
        if not callable(getattr(mod, name, None)):
            fail(f'[3] utility missing callable: {name}')
    if getattr(mod, 'MAX_ENTRIES_DEFAULT', None) != 256:
        fail('[3] MAX_ENTRIES_DEFAULT must be 256')
    if getattr(mod, 'TTL_SECONDS_DEFAULT', None) != 60:
        fail('[3] TTL_SECONDS_DEFAULT must be 60')

    # All 4 detection statuses deterministically:
    mod._test_reset()
    e1 = mod.build_replay_detection_dry_run_envelope(
        'material_raid_claim', server_idempotency_key='IDEM_A',
        request_hash='HASH_A', client_idempotency_key_present=True,
    )
    e2 = mod.build_replay_detection_dry_run_envelope(
        'material_raid_claim', server_idempotency_key='IDEM_A',
        request_hash='HASH_A', client_idempotency_key_present=True,
    )
    e3 = mod.build_replay_detection_dry_run_envelope(
        'material_raid_claim', server_idempotency_key='IDEM_A',
        request_hash='HASH_DIFFERENT', client_idempotency_key_present=True,
    )
    e4 = mod.build_replay_detection_dry_run_envelope(
        'material_raid_claim', server_idempotency_key=None, request_hash=None,
    )
    if e1.get('detection_status') != 'new_key_preview':
        fail(f'[3] first call must be new_key_preview, got {e1.get("detection_status")!r}')
    if e2.get('detection_status') != 'same_key_same_hash_replay_preview':
        fail(f'[3] same key/hash must be replay, got {e2.get("detection_status")!r}')
    if e3.get('detection_status') != 'same_key_diff_hash_conflict_preview':
        fail(f'[3] same key/diff hash must be conflict, got {e3.get("detection_status")!r}')
    if e4.get('detection_status') != 'missing_key_preview':
        fail(f'[3] no key must be missing_key_preview, got {e4.get("detection_status")!r}')

    # Cross-family: same idem key in another family must be new_key_preview
    mod._test_reset()
    mod.build_replay_detection_dry_run_envelope('material_raid_claim',
        server_idempotency_key='X', request_hash='H1')
    e5 = mod.build_replay_detection_dry_run_envelope('gem_socket_commit',
        server_idempotency_key='X', request_hash='H1')
    if e5.get('detection_status') != 'new_key_preview':
        fail('[3] cross-family same idem key must be treated as new_key')

    # Invariants in every envelope:
    for tag, env in (('e1', e1), ('e2', e2), ('e3', e3), ('e4', e4), ('e5', e5)):
        for key, exp in [('db_writes', 0), ('persistent_ledger_enabled', False),
                         ('redis_enabled', False), ('live_enforcement_enabled', False),
                         ('preview_request_blocked', False),
                         ('not_shared_across_workers', True),
                         ('not_durable_across_restart', True),
                         ('persisted', False),
                         ('dry_run_only', True),
                         ('enabled', True),
                         ('max_entries', 256), ('ttl_seconds', 60)]:
            if env.get(key) != exp:
                fail(f'[3] envelope {tag}.{key} must be {exp!r} (got {env.get(key)!r})')

    # would_block_live mirrors conflict; would_replay_live mirrors replay
    if e2.get('would_replay_live') is not True or e3.get('would_block_live') is not True:
        fail('[3] would_replay_live/would_block_live wiring broken')

    # Cache size bounded
    mod._test_reset(max_entries=4, ttl_seconds=60)
    for i in range(20):
        mod.build_replay_detection_dry_run_envelope(
            'gem_socket_commit', server_idempotency_key=f'K{i}', request_hash=f'H{i}',
        )
    sz = mod._test_snapshot_size()
    if sz > 4:
        fail(f'[3] cache exceeded max_entries: {sz}')
    mod._test_reset()  # restore defaults

    # config_block invariants
    cfg = mod.build_config_block()
    for key, exp in [('enabled', True), ('dry_run_only', True),
                     ('persistent_ledger_enabled', False), ('redis_enabled', False),
                     ('db_writes', 0), ('max_entries', 256), ('ttl_seconds', 60),
                     ('not_shared_across_workers', True),
                     ('not_durable_across_restart', True),
                     ('live_enforcement_enabled', False)]:
        if cfg.get(key) != exp:
            fail(f'[3] config_block.{key} must be {exp!r}')
    statuses = set(cfg.get('detection_statuses') or [])
    for s in ('new_key_preview', 'same_key_same_hash_replay_preview',
              'same_key_diff_hash_conflict_preview', 'missing_key_preview'):
        if s not in statuses:
            fail(f'[3] config_block.detection_statuses missing {s}')

# [4] route wire-up (all 8)
for rel, family, prefix, flag in ROUTES:
    src = read_text(rel)
    if 'from utils.economy_idempotency_replay_detection_dry_run import' not in src:
        fail(f'[4] route {rel} does not import economy_idempotency_replay_detection_dry_run')
    if '_v43_replay_envelope(' not in src:
        fail(f'[4] route {rel} does not use _v43_replay_envelope')
    if '_v43_replay_config_block()' not in src:
        fail(f'[4] route {rel} does not use _v43_replay_config_block')
    n_assign = src.count('_v43_replay_env = _v43_replay_envelope(')
    if n_assign != 3:
        fail(f'[4] route {rel} must have exactly 3 _v43_replay_env assignments, got {n_assign}')
    n_resp = src.count('"idempotency_replay_detection_dry_run": _v43_replay_env')
    if n_resp != 3:
        fail(f'[4] route {rel} must have exactly 3 response keys, got {n_resp}')
    if '"idempotency_replay_detection_dry_run": _v43_replay_config_block()' not in src:
        fail(f'[4] route {rel} /config missing replay config block')
    # Untouched: endpoint path/flag/default 503
    if f'prefix="{prefix}"' not in src:
        fail(f'[4] route {rel} prefix changed (expected {prefix!r})')
    if f'FEATURE_FLAG = "{flag}"' not in src:
        fail(f'[4] route {rel} feature flag changed (expected {flag!r})')
    if 'raise HTTPException(status_code=503' not in src:
        fail(f'[4] route {rel} default 503 behavior removed')
    # v42 envelopes must remain (no removal/alteration)
    if 'request_hash_dry_run' not in src or 'observability_dry_run' not in src:
        fail(f'[4] route {rel} v42 envelopes missing')

# [5] design JSON invariants
design = load_json(DESIGN_REL)
for key, exp in [('runtime_activation', False), ('db_writes', 0)]:
    if design.get(key) != exp:
        fail(f'[5] design.{key} must be {exp!r}')
stor = design.get('storage') or {}
for key, exp in [('shared_across_workers', False), ('durable_across_restart', False),
                 ('max_entries', 256), ('ttl_seconds', 60),
                 ('persistent_ledger', False), ('redis', False),
                 ('filesystem', False), ('db', False)]:
    if stor.get(key) != exp:
        fail(f'[5] design.storage.{key} must be {exp!r}')
inv = design.get('safety_invariants') or {}
for key, exp in [('preview_request_never_blocked', True),
                 ('live_enforcement_disabled', True),
                 ('db_writes_zero', True),
                 ('persistent_ledger_disabled', True),
                 ('redis_disabled', True),
                 ('filesystem_writes_disabled', True),
                 ('reset_on_process_restart', True),
                 ('not_shared_across_workers', True)]:
    if inv.get(key) != exp:
        fail(f'[5] design.safety_invariants.{key} must be {exp!r}')
if not design.get('all_8_operation_families_covered'):
    fail('[5] design.all_8_operation_families_covered must be true')
statuses = set(design.get('detection_statuses') or [])
for s in ('new_key_preview', 'same_key_same_hash_replay_preview',
          'same_key_diff_hash_conflict_preview', 'missing_key_preview'):
    if s not in statuses:
        fail(f'[5] design.detection_statuses missing {s}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN validator')
    sys.exit(1)

print('[PASS] PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN validator')
sys.exit(0)
