#!/usr/bin/env python3
"""Validator: PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN (v50 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/manual_user_approval_handshake_dry_run_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/manual_user_approval_handshake_dry_run_marker_v1.json')

REQUIRED_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim', 'gear_forge_fusion_commit',
    'rune_scroll_talisman_commit', 'artifact_upgrade_commit',
    'divine_weapon_upgrade_commit', 'battle_pass_reward_claim', 'mail_reward_claim',
}
REQUIRED_PLACEHOLDERS = ['<operation_family>', '<transition>', '<checksum_sha256>', '<date>']
REQUIRED_TRANSITIONS = {
    'dry_run_to_staging_dry_run',
    'staging_dry_run_to_canary_dry_run',
    'canary_dry_run_to_canary_live_BLOCKED',
    'canary_live_to_live_BLOCKED',
}
REQUIRED_FORBIDDEN = {
    'no_endpoint', 'no_runtime_execution', 'no_automatic_approval',
    'no_real_db_connection', 'no_mongo_url', 'no_pymongo', 'no_motor',
    'no_env_read', 'no_filesystem_writes', 'no_db_writes', 'no_live_apply',
    'no_production_mutation', 'no_endpoint_path_change', 'no_feature_flag_change',
    'no_default_503_change', 'no_server_py_change', 'no_frontend_change',
    'no_battle_engine_change',
}
APPROVAL_TEMPLATE = 'I APPROVE <operation_family> <transition> WITH CHECKSUM <checksum_sha256> ON <date>'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'manual_user_approval_handshake_dry_run_v1'),
        ('dry_run_only', True),
        ('no_endpoint', True),
        ('no_runtime_execution', True),
        ('no_automatic_approval', True),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('live_apply_allowed', False),
        ('approval_phrase_template', APPROVAL_TEMPLATE),
        ('future_live_decision_requires_manual_user_approval', True),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    if d.get('approval_phrase_required_placeholders') != REQUIRED_PLACEHOLDERS:
        fail(f'design approval_phrase_required_placeholders mismatch (got {d.get("approval_phrase_required_placeholders")})')
    trans = set(d.get('transition_enum') or [])
    m_t = REQUIRED_TRANSITIONS - trans
    if m_t: fail(f'design transition_enum missing: {sorted(m_t)}')
    forb = set(d.get('forbidden') or [])
    m_for = REQUIRED_FORBIDDEN - forb
    if m_for: fail(f'design forbidden missing: {sorted(m_for)}')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design operation_families len != 8 (got {len(fams)})')
    seen = set()
    for f in fams:
        name = f.get('operation_family')
        seen.add(name)
        for k, v in (
            ('current_approval_state', 'pending'),
            ('approval_phrase_recorded', None),
            ('checksum_sha256_recorded', None),
            ('date_recorded', None),
            ('transition_recorded', None),
            ('db_writes', 0),
            ('live_apply_allowed', False),
        ):
            if f.get(k) != v: fail(f'design family {name} {k} != {v} (got {f.get(k)})')
        if name == 'battle_pass_reward_claim' and f.get('no_bp_delta_runtime') is not True:
            fail('design battle_pass_reward_claim must have no_bp_delta_runtime=true')
        if name == 'mail_reward_claim' and f.get('no_mail_state_mutation') is not True:
            fail('design mail_reward_claim must have no_mail_state_mutation=true')
    miss = REQUIRED_FAMILIES - seen
    if miss: fail(f'design operation_families missing: {sorted(miss)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'manual_user_approval_handshake_dry_run_v1'),
        ('track', 'D'),
        ('operation_families_count', 8),
        ('no_endpoint', True),
        ('no_runtime_execution', True),
        ('no_automatic_approval', True),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('live_apply_allowed', False),
        ('future_live_decision_requires_manual_user_approval', True),
        ('approval_phrase_template', APPROVAL_TEMPLATE),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN validator')
sys.exit(0)
