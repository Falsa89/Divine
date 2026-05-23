#!/usr/bin/env python3
# SLC-F RAIDS EQUIPMENT SCOPE POST-APPLY VALIDATOR (READ-ONLY)
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_raids_equipment_scope_post_apply_v1_result.json'
MARKER = SAFETY / 'slc_f_raids_equipment_scope_apply_marker_v1.json'
MARKER_0_1 = SAFETY / 'slc_f_batch_0_1_apply_marker_v1.json'
MARKER_1B = SAFETY / 'slc_f_batch_1b_apply_marker_v1.json'
MARKER_2 = SAFETY / 'slc_f_batch_2_apply_marker_v1.json'
MARKER_EQ = SAFETY / 'slc_f_equipment_scope_apply_marker_v1.json'
SLC_G_MARKER = SAFETY / 'slc_g_default_s1_migration_apply_result_v1.json'

EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'
EXPECTED_RAIDS_APPLY_ID = 'slc_f_raids_equipment_scope_20260523T184512Z_a46a6034'

ALLOWED_CHANGED = {'backend/routes/raids.py'}

FORBIDDEN_UNCHANGED = [
    'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py', 'backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py', 'backend/routes/combat.py',
    'backend/routes/equipment.py', 'backend/routes/forge.py',
    'backend/routes/sanctuary.py', 'backend/routes/player_faction_v2.py',
    'backend/routes/cosmetics.py',
    # NOTE: economy.py removed after V2 BLOCK_A authorized narrow daily_claims apply.
    'backend/routes/push_notifications.py', 'backend/routes/game_data.py',
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing', '/api/account/server-profiles', '/api/account/active-server']

MUST_STILL_HAVE_HELPER_IMPORT = [
    'backend/routes/items.py', 'backend/routes/forge.py', 'backend/routes/achievements.py',
    'backend/routes/level_sharing.py', 'backend/routes/social.py', 'backend/routes/soul_forge.py',
    'backend/routes/artifacts.py', 'backend/routes/guild.py',
]


def main() -> int:
    errs = []
    if not MARKER.exists():
        errs.append('apply_marker_missing')
    else:
        m = json.loads(MARKER.read_text())
        if m.get('scope') != 'RAIDS_EQUIPMENT_ONLY': errs.append('scope_not_RAIDS_EQUIPMENT_ONLY')
        if m.get('apply_id') != EXPECTED_RAIDS_APPLY_ID: errs.append(f'apply_id_mismatch:got={m.get("apply_id")}')
        if m.get('route_patch_applied') is not True: errs.append('route_patch_applied_must_be_true')
        if m.get('route_patch_applied_partial') is not True: errs.append('route_patch_applied_partial_must_be_true')
        if m.get('route_patch_applied_full') is not False: errs.append('route_patch_applied_full_must_be_false')
        if m.get('second_server_opening_allowed') is not False: errs.append('second_server_opening_allowed_must_be_false')
        if m.get('feature_flag_enabled') is not False: errs.append('feature_flag_enabled_must_be_false')
        if m.get('housing_runtime_implemented') is not False: errs.append('housing_runtime_implemented_must_be_false')
        if m.get('phase_11_executed') is not False: errs.append('phase_11_executed_must_be_false')
        if m.get('fallback_removed') is not False: errs.append('fallback_removed_must_be_false')
        cf = set(m.get('changed_files') or [])
        unauth = cf - ALLOWED_CHANGED
        if unauth: errs.append(f'unauthorized_changed_files:{sorted(unauth)}')
        if cf != ALLOWED_CHANGED: errs.append(f'changed_files_mismatch:got={sorted(cf)}')

    for path, label in [(MARKER_0_1, 'batch_0_1'), (MARKER_1B, 'batch_1b'), (MARKER_2, 'batch_2'), (MARKER_EQ, 'equipment_scope'), (SLC_G_MARKER, 'slc_g')]:
        if not path.exists(): errs.append(f'{label}_marker_missing')
    if SLC_G_MARKER.exists():
        sg = json.loads(SLC_G_MARKER.read_text())
        if sg.get('migration_id') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append(f'slc_g_migration_id_changed:got={sg.get("migration_id")}')
        if not sg.get('migration_applied'): errs.append('slc_g_migration_applied_not_true')

    # Forbidden files: no diff vs HEAD
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
        if 'def ensure_server_scope' not in ht: errs.append('helper_ensure_server_scope_missing')
        if 'LEGACY_DEFAULT_SERVER_ID' not in ht or '"s1"' not in ht: errs.append('helper_legacy_s1_missing')

    for f in MUST_STILL_HAVE_HELPER_IMPORT:
        text = (ROOT / f).read_text(errors='ignore')
        if 'from utils.server_scope import ensure_server_scope' not in text:
            errs.append(f'prior_apply_helper_import_missing_in:{f}')

    # Specific patch verification on raids.py
    raids_text = (ROOT / 'backend/routes/raids.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' not in raids_text:
        errs.append('raids_helper_import_missing')
    # Confirm the patch is present in the craft_exclusive_item flow
    if 'equip = ensure_server_scope(equip, uid)' not in raids_text:
        errs.append('raids_ensure_server_scope_call_missing')
    # Confirm the patched call is IMMEDIATELY before the insert_one
    pattern = r'equip = ensure_server_scope\(equip,\s*uid\)\s*\n\s*await db\.user_equipment\.insert_one\(equip\)'
    if not re.search(pattern, raids_text):
        errs.append('raids_patch_not_adjacent_to_insert_one')
    # Confirm exclusive_item business logic markers are still present (no logic mutation)
    for snippet in ['EXCLUSIVE_ITEMS', 'cost_gold = 20000', 'cost_gems = 50', 'is_exclusive', 'exclusive_hero']:
        if snippet not in raids_text:
            errs.append(f'raids_business_logic_marker_missing:{snippet}')
    # Confirm we did NOT add helper to combat.py
    combat_text = (ROOT / 'backend/routes/combat.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' in combat_text:
        errs.append('combat_unexpectedly_patched')

    out = {
        'task_origin': 'SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
