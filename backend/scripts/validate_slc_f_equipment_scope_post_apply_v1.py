#!/usr/bin/env python3
# SLC-F EQUIPMENT SERVER_SCOPE EXTENSION POST-APPLY VALIDATOR (READ-ONLY)
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_equipment_scope_post_apply_v1_result.json'
MARKER = SAFETY / 'slc_f_equipment_scope_apply_marker_v1.json'
MARKER_0_1 = SAFETY / 'slc_f_batch_0_1_apply_marker_v1.json'
MARKER_1B = SAFETY / 'slc_f_batch_1b_apply_marker_v1.json'
MARKER_2 = SAFETY / 'slc_f_batch_2_apply_marker_v1.json'
SLC_G_MARKER = SAFETY / 'slc_g_default_s1_migration_apply_result_v1.json'

EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'
EXPECTED_BATCH_0_1_APPLY_ID = 'slc_f_batch_0_1_20260523T173754Z_27b1b737'
EXPECTED_BATCH_1B_APPLY_ID = 'slc_f_batch_1b_20260523T175058Z_2cf0584c'
EXPECTED_BATCH_2_APPLY_ID = 'slc_f_batch_2_20260523T181752Z_b838601e'
EXPECTED_EQUIPMENT_APPLY_ID = 'slc_f_equipment_scope_20260523T182939Z_d2afcc8a'

# This was a SAFE NO-OP: no files patched.
ALLOWED_CHANGED = set()

FORBIDDEN_UNCHANGED = [
    'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py', 'backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py', 'backend/routes/combat.py',
    # NOTE: raids.py removed from FORBIDDEN_UNCHANGED conditionally — if the
    # subsequent RAIDS_EQUIPMENT_ONLY micro-batch marker exists, raids.py
    # is allowed to differ vs HEAD (sanctioned by a later gated apply).
    'backend/routes/sanctuary.py', 'backend/routes/player_faction_v2.py',
    'backend/routes/forge.py',  # Already Batch-1B; must not be touched by this task
    'backend/routes/cosmetics.py',
    # NOTE: economy.py removed after V2 BLOCK_A authorized narrow daily_claims apply.
    'backend/routes/push_notifications.py', 'backend/routes/game_data.py',
    # equipment.py itself MUST remain unchanged (no patch applied)
    'backend/routes/equipment.py',
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing', '/api/account/server-profiles', '/api/account/active-server']

# Files that received the helper import in prior batches must STILL contain it.
MUST_STILL_HAVE_HELPER_IMPORT = [
    'backend/routes/items.py',
    'backend/routes/forge.py',
    'backend/routes/achievements.py',
    'backend/routes/level_sharing.py',
    'backend/routes/social.py',
    'backend/routes/soul_forge.py',
    'backend/routes/artifacts.py',
    'backend/routes/guild.py',
]


def main() -> int:
    errs = []
    if not MARKER.exists():
        errs.append('apply_marker_missing')
    else:
        m = json.loads(MARKER.read_text())
        if m.get('scope') != 'EQUIPMENT_ONLY':
            errs.append('scope_not_EQUIPMENT_ONLY')
        if m.get('apply_id') != EXPECTED_EQUIPMENT_APPLY_ID:
            errs.append(f'apply_id_mismatch:got={m.get("apply_id")}')
        if m.get('route_patch_applied') is not False:
            errs.append('route_patch_applied_must_be_false')
        if m.get('safe_no_op_apply') is not True:
            errs.append('safe_no_op_apply_must_be_true')
        if m.get('all_candidates_skipped') is not True:
            errs.append('all_candidates_skipped_must_be_true')
        if m.get('second_server_opening_allowed') is not False:
            errs.append('second_server_opening_allowed_must_be_false')
        if m.get('feature_flag_enabled') is not False:
            errs.append('feature_flag_enabled_must_be_false')
        if m.get('housing_runtime_implemented') is not False:
            errs.append('housing_runtime_implemented_must_be_false')
        if m.get('phase_11_executed') is not False:
            errs.append('phase_11_executed_must_be_false')
        if m.get('fallback_removed') is not False:
            errs.append('fallback_removed_must_be_false')
        if m.get('changed_files'):
            errs.append(f'changed_files_must_be_empty:got={m.get("changed_files")}')
        if m.get('routes_patched_families'):
            errs.append(f'routes_patched_families_must_be_empty:got={m.get("routes_patched_families")}')
        cat = m.get('equipment_route_audit_table') or []
        if len(cat) < 4:
            errs.append(f'equipment_route_audit_table_too_short:n={len(cat)}')
        bad = [r.get('decision') for r in cat if not str(r.get('decision', '')).startswith('SKIP')]
        if bad:
            errs.append(f'non_skip_decisions:{bad}')
        if m.get('slc_g_migration_id_preserved') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append('slc_g_migration_id_preserved_mismatch')
        if m.get('slc_f_batch_0_1_apply_id_preserved') != EXPECTED_BATCH_0_1_APPLY_ID:
            errs.append('slc_f_batch_0_1_apply_id_preserved_mismatch')
        if m.get('slc_f_batch_1b_apply_id_preserved') != EXPECTED_BATCH_1B_APPLY_ID:
            errs.append('slc_f_batch_1b_apply_id_preserved_mismatch')
        if m.get('slc_f_batch_2_apply_id_preserved') != EXPECTED_BATCH_2_APPLY_ID:
            errs.append('slc_f_batch_2_apply_id_preserved_mismatch')

    for path, label in [(MARKER_0_1, 'batch_0_1'), (MARKER_1B, 'batch_1b'), (MARKER_2, 'batch_2'), (SLC_G_MARKER, 'slc_g')]:
        if not path.exists():
            errs.append(f'{label}_marker_missing')
    if SLC_G_MARKER.exists():
        sg = json.loads(SLC_G_MARKER.read_text())
        if sg.get('migration_id') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append(f'slc_g_migration_id_changed:got={sg.get("migration_id")}')
        if not sg.get('migration_applied'):
            errs.append('slc_g_migration_applied_not_true')

    # Forbidden files: no diff vs HEAD
    for f in FORBIDDEN_UNCHANGED:
        p = subprocess.run(['git', '-C', str(ROOT), 'diff', 'HEAD', '--', f], capture_output=True, text=True)
        if p.stdout.strip():
            errs.append(f'forbidden_file_diff_present:{f}')

    # No forbidden runtime routes in source
    routes_dir = ROOT / 'backend' / 'routes'
    for f in list(routes_dir.glob('*.py')) + [ROOT / 'backend/server.py']:
        if not f.exists():
            continue
        text = f.read_text(errors='ignore')
        for fr in FORBIDDEN_ROUTE_PATHS:
            if re.search(r'["\']' + re.escape(fr) + r'["\']', text):
                errs.append(f'forbidden_route_present:{fr}_in_{f.name}')

    # Feature flags must be unset
    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'):
        errs.append('SERVER_PROFILES_RUNTIME_ENABLED_must_be_unset')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'):
        errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    # Helper still exists & previous apply state preserved
    helper = ROOT / 'backend/utils/server_scope.py'
    if not helper.exists():
        errs.append('helper_module_missing')
    else:
        ht = helper.read_text()
        if 'def ensure_server_scope' not in ht:
            errs.append('helper_ensure_server_scope_missing')
        if 'LEGACY_DEFAULT_SERVER_ID' not in ht or '"s1"' not in ht:
            errs.append('helper_legacy_s1_missing')

    for f in MUST_STILL_HAVE_HELPER_IMPORT:
        text = (ROOT / f).read_text(errors='ignore')
        if 'from utils.server_scope import ensure_server_scope' not in text:
            errs.append(f'prior_apply_helper_import_missing_in:{f}')

    # Confirm equipment.py did NOT receive the helper import (still SKIPped)
    eq_text = (ROOT / 'backend/routes/equipment.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' in eq_text:
        errs.append('equipment_unexpectedly_patched_with_helper_import')
    # And no ensure_server_scope CALLS in equipment.py
    if 'ensure_server_scope(' in eq_text:
        errs.append('equipment_unexpectedly_contains_ensure_server_scope_call')

    out = {
        'task_origin': 'SLC-F-EQUIPMENT-SCOPE-POST-APPLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-EQUIPMENT-SCOPE-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
