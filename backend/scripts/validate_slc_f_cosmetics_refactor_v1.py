#!/usr/bin/env python3
# SLC-F COSMETICS SCHEMA SPLIT REFACTOR POST-AUDIT VALIDATOR (READ-ONLY)
# Verifies the READY_NOT_APPLIED decision + zero runtime touch.
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_cosmetics_refactor_v1_result.json'
AUDIT = SAFETY / 'slc_f_cosmetics_refactor_audit_v1.json'
EXPECTED_AUDIT_ID = 'slc_f_cosmetics_refactor_20260523T200524Z_dee18b8c'

PRIOR_MARKERS = [
    'slc_g_default_s1_migration_apply_result_v1.json',
    'slc_f_batch_0_1_apply_marker_v1.json', 'slc_f_batch_1b_apply_marker_v1.json',
    'slc_f_batch_2_apply_marker_v1.json', 'slc_f_equipment_scope_apply_marker_v1.json',
    'slc_f_raids_equipment_scope_apply_marker_v1.json',
    'slc_f_minor_write_surfaces_audit_v1.json',
    'slc_f_gvg_war_scope_apply_marker_v1.json',
    'slc_f_unique_items_scope_apply_marker_v1.json',
    'slc_f_post_microbatch_consolidation_v1.json',
]

FORBIDDEN_UNCHANGED = [
    # ALL backend/routes/*.py must remain unchanged in this task.
    'backend/routes/cosmetics.py',
    'backend/routes/economy.py', 'backend/routes/combat.py',
    'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py', 'backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py', 'backend/routes/sanctuary.py', 'backend/routes/player_faction_v2.py',
    'backend/routes/push_notifications.py', 'backend/routes/game_data.py',
    'backend/routes/equipment.py', 'backend/routes/forge.py', 'backend/routes/raids.py',
    'backend/routes/gvg.py', 'backend/routes/unique_items.py',
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing', '/api/account/server-profiles', '/api/account/active-server']


def main() -> int:
    errs = []
    if not AUDIT.exists():
        errs.append('cosmetics_audit_json_missing')
        OUT.write_text(json.dumps({'verdict': 'FAIL', 'errors': errs}, indent=2))
        return 1
    a = json.loads(AUDIT.read_text())
    if a.get('scope') != 'COSMETICS_SCHEMA_SPLIT_ONLY': errs.append('scope_not_COSMETICS_SCHEMA_SPLIT_ONLY')
    if a.get('audit_id') != EXPECTED_AUDIT_ID: errs.append(f'audit_id_mismatch:got={a.get("audit_id")}')
    if a.get('decision') != 'READY_NOT_APPLIED': errs.append('decision_must_be_READY_NOT_APPLIED')
    if a.get('verdict') != 'SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR_READY_NOT_APPLIED':
        errs.append('verdict_must_be_READY_NOT_APPLIED')
    if a.get('runtime_files_modified') is not False: errs.append('runtime_files_modified_must_be_false')
    if a.get('db_writes_performed') is not False: errs.append('db_writes_performed_must_be_false')
    if a.get('migrations_performed') is not False: errs.append('migrations_performed_must_be_false')
    if a.get('changed_files'): errs.append('changed_files_must_be_empty')
    # Sections present
    for k in ['cosmetics_route_audit_table', 'ownership_vs_equipped_classification',
              'refactor_decision_table', 'reasons_blocking_apply', 'proposed_apply_blueprint']:
        if k not in a: errs.append(f'audit_section_missing:{k}')
    if len(a.get('cosmetics_route_audit_table') or []) < 4:
        errs.append('audit_table_too_short')
    if len(a.get('reasons_blocking_apply') or []) < 3:
        errs.append('reasons_blocking_apply_must_list_at_least_3_reasons')

    # Prior markers preserved
    for p in PRIOR_MARKERS:
        if not (SAFETY / p).exists():
            errs.append(f'prior_marker_missing:{p}')

    # Zero diff on all forbidden runtime files
    for f in FORBIDDEN_UNCHANGED:
        p = subprocess.run(['git', '-C', str(ROOT), 'diff', 'HEAD', '--', f], capture_output=True, text=True)
        if p.stdout.strip(): errs.append(f'forbidden_file_diff_present:{f}')

    # No forbidden routes in source
    routes_dir = ROOT / 'backend' / 'routes'
    for f in list(routes_dir.glob('*.py')) + [ROOT / 'backend/server.py']:
        if not f.exists(): continue
        text = f.read_text(errors='ignore')
        for fr in FORBIDDEN_ROUTE_PATHS:
            if re.search(r'["\']' + re.escape(fr) + r'["\']', text):
                errs.append(f'forbidden_route_present:{fr}_in_{f.name}')

    # Env flags must be unset
    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'): errs.append('SERVER_PROFILES_RUNTIME_ENABLED_must_be_unset')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'): errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    # cosmetics.py must NOT contain the helper import (still skipped)
    cos_text = (ROOT / 'backend/routes/cosmetics.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' in cos_text:
        errs.append('cosmetics_unexpectedly_imports_helper')
    if 'ensure_server_scope(' in cos_text:
        errs.append('cosmetics_unexpectedly_calls_helper')
    # Schema markers still original
    for snippet in ['owned_auras', 'owned_frames', 'active_aura', 'active_frame', 'user_cosmetics']:
        if snippet not in cos_text:
            errs.append(f'cosmetics_schema_marker_missing:{snippet}')

    out = {
        'task_origin': 'SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'decision_observed': 'READY_NOT_APPLIED',
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1 {out['verdict']} errors={len(errs)}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
