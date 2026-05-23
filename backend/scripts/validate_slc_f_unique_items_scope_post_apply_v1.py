#!/usr/bin/env python3
# SLC-F UNIQUE-ITEMS SERVER_SCOPE POST-APPLY VALIDATOR (READ-ONLY)
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_unique_items_scope_post_apply_v1_result.json'
MARKER = SAFETY / 'slc_f_unique_items_scope_apply_marker_v1.json'

EXPECTED_APPLY_ID = 'slc_f_unique_items_scope_20260523T193344Z_48aa4881'
EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'
ALLOWED_CHANGED = {'backend/routes/unique_items.py'}

PRIOR_MARKERS = [
    'slc_f_batch_0_1_apply_marker_v1.json',
    'slc_f_batch_1b_apply_marker_v1.json',
    'slc_f_batch_2_apply_marker_v1.json',
    'slc_f_equipment_scope_apply_marker_v1.json',
    'slc_f_raids_equipment_scope_apply_marker_v1.json',
    'slc_f_gvg_war_scope_apply_marker_v1.json',
    'slc_g_default_s1_migration_apply_result_v1.json',
]

FORBIDDEN_UNCHANGED = [
    'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py', 'backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py', 'backend/routes/combat.py',
    'backend/routes/equipment.py', 'backend/routes/forge.py',
    'backend/routes/raids.py', 'backend/routes/gvg.py',
    'backend/routes/sanctuary.py', 'backend/routes/player_faction_v2.py',
    'backend/routes/cosmetics.py', 'backend/routes/economy.py',
    'backend/routes/push_notifications.py', 'backend/routes/game_data.py',
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing', '/api/account/server-profiles', '/api/account/active-server']

MUST_STILL_HAVE_HELPER_IMPORT = [
    'backend/routes/items.py', 'backend/routes/forge.py', 'backend/routes/achievements.py',
    'backend/routes/level_sharing.py', 'backend/routes/social.py', 'backend/routes/soul_forge.py',
    'backend/routes/artifacts.py', 'backend/routes/guild.py', 'backend/routes/raids.py',
    'backend/routes/gvg.py',
]


def main() -> int:
    errs = []
    if not MARKER.exists():
        errs.append('apply_marker_missing')
    else:
        m = json.loads(MARKER.read_text())
        if m.get('scope') != 'UNIQUE_ITEMS_ONLY': errs.append('scope_not_UNIQUE_ITEMS_ONLY')
        if m.get('apply_id') != EXPECTED_APPLY_ID: errs.append(f'apply_id_mismatch:got={m.get("apply_id")}')
        if m.get('route_patch_applied') is not True: errs.append('route_patch_applied_must_be_true')
        if m.get('route_patch_applied_partial') is not True: errs.append('route_patch_applied_partial_must_be_true')
        if m.get('route_patch_applied_full') is not False: errs.append('route_patch_applied_full_must_be_false')
        if m.get('second_server_opening_allowed') is not False: errs.append('second_server_opening_allowed_must_be_false')
        if m.get('feature_flag_enabled') is not False: errs.append('feature_flag_enabled_must_be_false')
        if m.get('housing_runtime_implemented') is not False: errs.append('housing_runtime_implemented_must_be_false')
        if m.get('phase_11_executed') is not False: errs.append('phase_11_executed_must_be_false')
        if m.get('fallback_removed') is not False: errs.append('fallback_removed_must_be_false')
        cf = set(m.get('changed_files') or [])
        if cf != ALLOWED_CHANGED: errs.append(f'changed_files_mismatch:got={sorted(cf)}')
        cat = m.get('unique_items_target_surfaces_audit') or []
        if len(cat) != 2: errs.append(f'expected_2_target_surfaces:n={len(cat)}')
        for r in cat:
            if r.get('decision') != 'PATCH_NOW_SAFE':
                errs.append(f'non_patch_decision:{r.get("surface_id")}={r.get("decision")}')

    for p in PRIOR_MARKERS:
        if not (SAFETY / p).exists():
            errs.append(f'prior_marker_missing:{p}')

    slc_g = SAFETY / 'slc_g_default_s1_migration_apply_result_v1.json'
    if slc_g.exists():
        sg = json.loads(slc_g.read_text())
        if sg.get('migration_id') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append(f'slc_g_migration_id_changed:got={sg.get("migration_id")}')
        if not sg.get('migration_applied'): errs.append('slc_g_migration_applied_not_true')

    for f in FORBIDDEN_UNCHANGED:
        p = subprocess.run(['git', '-C', str(ROOT), 'diff', 'HEAD', '--', f], capture_output=True, text=True)
        if p.stdout.strip(): errs.append(f'forbidden_file_diff_present:{f}')

    routes_dir = ROOT / 'backend' / 'routes'
    for f in list(routes_dir.glob('*.py')) + [ROOT / 'backend/server.py']:
        if not f.exists(): continue
        text = f.read_text(errors='ignore')
        for fr in FORBIDDEN_ROUTE_PATHS:
            if re.search(r'["\']' + re.escape(fr) + r'["\']', text):
                errs.append(f'forbidden_route_present:{fr}_in_{f.name}')

    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'): errs.append('SERVER_PROFILES_RUNTIME_ENABLED_must_be_unset')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'): errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    helper = ROOT / 'backend/utils/server_scope.py'
    if not helper.exists(): errs.append('helper_module_missing')
    else:
        ht = helper.read_text()
        if 'def ensure_server_scope' not in ht: errs.append('helper_ensure_server_scope_missing')
        if 'LEGACY_DEFAULT_SERVER_ID' not in ht or '"s1"' not in ht: errs.append('helper_legacy_s1_missing')

    for f in MUST_STILL_HAVE_HELPER_IMPORT:
        text = (ROOT / f).read_text(errors='ignore')
        if 'from utils.server_scope import ensure_server_scope' not in text:
            errs.append(f'prior_apply_helper_import_missing_in:{f}')

    # Specific patch verification on unique_items.py
    ui_text = (ROOT / 'backend/routes/unique_items.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' not in ui_text:
        errs.append('unique_items_helper_import_missing')
    # Surface 1: crafted_doc + ensure_server_scope adjacent to insert_one
    pat1 = r'crafted_doc = ensure_server_scope\(crafted_doc,\s*uid\)\s*\n\s*await db\.unique_items_crafted\.insert_one\(crafted_doc\)'
    if not re.search(pat1, ui_text):
        errs.append('unique_items_craft_patch_not_adjacent')
    # Surface 2: $setOnInsert with ensure_server_scope({}, uid)
    pat2 = r'\$setOnInsert[\"\']\s*:\s*ensure_server_scope\(\{\},\s*uid\)'
    if not re.search(pat2, ui_text):
        errs.append('unique_items_equip_setOnInsert_missing')
    # Business logic markers preserved
    for snippet in ['UNIQUE_ITEMS', 'cost_gold = {1: 10000', 'cost_gems = {1: 10',
                    'Servono', 'Gia sbloccato', 'Oggetto non ancora sbloccato',
                    'Questo oggetto puo essere equipaggiato SOLO da', 'item["rarity"]']:
        if snippet not in ui_text:
            errs.append(f'unique_items_business_logic_marker_missing:{snippet}')
    # Inline insert_one literal must be gone
    if 'await db.unique_items_crafted.insert_one({' in ui_text:
        errs.append('unique_items_inline_insert_literal_still_present')
    # We did NOT touch combat.py
    if 'from utils.server_scope import ensure_server_scope' in (ROOT / 'backend/routes/combat.py').read_text(errors='ignore'):
        errs.append('combat_unexpectedly_patched')

    out = {
        'task_origin': 'SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
