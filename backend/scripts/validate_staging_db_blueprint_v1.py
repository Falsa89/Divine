#!/usr/bin/env python3
"""Validator: PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY (v50 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/staging_db_blueprint_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/staging_db_blueprint_marker_v1.json')

REQUIRED_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim', 'gear_forge_fusion_commit',
    'rune_scroll_talisman_commit', 'artifact_upgrade_commit',
    'divine_weapon_upgrade_commit', 'battle_pass_reward_claim', 'mail_reward_claim',
}
REQUIRED_ISOLATION = {
    'separate_database_name_from_production',
    'separate_credentials_from_production',
    'network_isolated_or_local_only_during_simulation',
    'ephemeral_lifecycle_no_persistence_beyond_run',
    'no_shared_data_with_production_collections',
    'isolated_audit_sink_for_simulation_events',
}
REQUIRED_INFRA = {
    'persistent_audit_sink_isolated',
    'monitoring_sink_for_simulation',
    'observability_aggregation_dry_run_compatible',
    'alert_history_ring_buffer_dry_run_compatible',
    'telemetry_alerting_thresholds_dry_run_compatible',
    'audit_bundle_checksum_dry_run_verification',
}
REQUIRED_FORBIDDEN = {
    'no_real_db_connection', 'no_mongo_url', 'no_production_credentials',
    'no_pymongo', 'no_motor', 'no_env_read', 'no_db_writes', 'no_redis',
    'no_filesystem_writes', 'no_persistent_ledger', 'no_live_apply',
    'no_production_mutation', 'no_reward_grant', 'no_inventory_mutation',
    'no_endpoint_path_change', 'no_feature_flag_change', 'no_default_503_change',
    'no_safety_flag_change', 'no_server_py_change', 'no_frontend_change',
    'no_battle_engine_change', 'no_character_bible_change', 'no_final_numbers_change',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'staging_db_blueprint_v1'),
        ('dry_run_only', True),
        ('actual_staging_db_created', False),
        ('real_db_connection_used', False),
        ('production_db_credentials_allowed', False),
        ('mongo_url_allowed', False),
        ('pymongo_allowed', False),
        ('motor_allowed', False),
        ('env_read_allowed', False),
        ('filesystem_writes_allowed', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('live_enabled', False),
        ('safe_to_enable_live', False),
        ('live_apply_allowed', False),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    iso = set(d.get('isolation_requirements') or [])
    m_iso = REQUIRED_ISOLATION - iso
    if m_iso: fail(f'design isolation_requirements missing: {sorted(m_iso)}')
    infra = set(d.get('required_infrastructure') or [])
    m_inf = REQUIRED_INFRA - infra
    if m_inf: fail(f'design required_infrastructure missing: {sorted(m_inf)}')
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
            ('readiness', 'not_ready_until_manual_approval'),
            ('actual_staging_db_created', False),
            ('real_db_connection_used', False),
            ('db_writes', 0),
            ('live_enabled', False),
            ('safe_to_enable_live', False),
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
        ('contract_version', 'staging_db_blueprint_v1'),
        ('track', 'B'),
        ('operation_families_count', 8),
        ('actual_staging_db_created', False),
        ('real_db_connection_used', False),
        ('mongo_url_allowed', False),
        ('pymongo_allowed', False),
        ('motor_allowed', False),
        ('env_read_allowed', False),
        ('filesystem_writes_allowed', False),
        ('db_writes', 0),
        ('production_db_touched', False),
        ('live_enabled', False),
        ('safe_to_enable_live', False),
        ('live_apply_allowed', False),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY validator')
    sys.exit(1)
print('[PASS] PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY validator')
sys.exit(0)
