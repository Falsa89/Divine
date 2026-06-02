#!/usr/bin/env python3
"""Validator: PROJECT-LIVE-LEDGER-DESIGN-ONLY (v50 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/live_ledger_design_only_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/live_ledger_design_only_marker_v1.json')

REQUIRED_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim', 'gear_forge_fusion_commit',
    'rune_scroll_talisman_commit', 'artifact_upgrade_commit',
    'divine_weapon_upgrade_commit', 'battle_pass_reward_claim', 'mail_reward_claim',
}
REQUIRED_SCHEMAS = {'idempotency_ledger_entry', 'audit_event', 'rollback_record', 'operator_decision'}
REQUIRED_FORBIDDEN = {
    'no_runtime_ledger_creation', 'no_real_db_connection', 'no_mongo_url',
    'no_pymongo', 'no_motor', 'no_env_read', 'no_filesystem_writes',
    'no_live_apply', 'no_production_mutation', 'no_reward_grant',
    'no_endpoint_path_change', 'no_feature_flag_change', 'no_default_503_change',
    'no_server_py_change', 'no_frontend_change', 'no_battle_engine_change',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'live_ledger_design_only_v1'),
        ('dry_run_only', True),
        ('runtime_ledger_created', False),
        ('live_apply_allowed', False),
        ('live_implementation_deferred', True),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    schemas = d.get('schemas') or {}
    miss_s = REQUIRED_SCHEMAS - set(schemas.keys())
    if miss_s: fail(f'design schemas missing: {sorted(miss_s)}')
    for sname, sdef in schemas.items():
        if sdef.get('design_only') is not True: fail(f'schema {sname} design_only != true')
        if sdef.get('runtime_created') is not False: fail(f'schema {sname} runtime_created != false')
        if not sdef.get('required_fields'): fail(f'schema {sname} required_fields empty')
    # audit_event PII
    ae = schemas.get('audit_event') or {}
    if ae.get('pii_safe') is not True: fail('audit_event pii_safe != true')
    if ae.get('raw_payload_captured') is not False: fail('audit_event raw_payload_captured != false')
    # rollback_record
    rb = schemas.get('rollback_record') or {}
    if rb.get('actual_reversal_performed') is not False: fail('rollback_record actual_reversal_performed != false')
    # idempotency ttl
    il = schemas.get('idempotency_ledger_entry') or {}
    if il.get('ttl_design_seconds_default') != 86400: fail('idempotency_ledger_entry ttl_design_seconds_default != 86400')
    if il.get('unique_by') != ['ledger_key']: fail('idempotency_ledger_entry unique_by != [ledger_key]')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design operation_families len != 8 (got {len(fams)})')
    seen = set()
    for f in fams:
        name = f.get('operation_family')
        seen.add(name)
        for k, v in (
            ('runtime_ledger_created', False),
            ('live_apply_allowed', False),
            ('live_implementation_deferred', True),
            ('db_writes', 0),
        ):
            if f.get(k) != v: fail(f'design family {name} {k} != {v} (got {f.get(k)})')
        if name == 'battle_pass_reward_claim' and f.get('no_bp_delta_runtime') is not True:
            fail('design battle_pass_reward_claim must have no_bp_delta_runtime=true')
        if name == 'mail_reward_claim' and f.get('no_mail_state_mutation') is not True:
            fail('design mail_reward_claim must have no_mail_state_mutation=true')
    miss = REQUIRED_FAMILIES - seen
    if miss: fail(f'design operation_families missing: {sorted(miss)}')
    forb = set(d.get('forbidden') or [])
    m_for = REQUIRED_FORBIDDEN - forb
    if m_for: fail(f'design forbidden missing: {sorted(m_for)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'live_ledger_design_only_v1'),
        ('track', 'C'),
        ('operation_families_count', 8),
        ('runtime_ledger_created', False),
        ('live_apply_allowed', False),
        ('live_implementation_deferred', True),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('schemas_count', 4),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-LIVE-LEDGER-DESIGN-ONLY validator')
    sys.exit(1)
print('[PASS] PROJECT-LIVE-LEDGER-DESIGN-ONLY validator')
sys.exit(0)
