#!/usr/bin/env python3
# SLC-F GVG WAR INSERT SCOPE POST-APPLY VALIDATOR (READ-ONLY)
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_gvg_war_scope_post_apply_v1_result.json'
MARKER = SAFETY / 'slc_f_gvg_war_scope_apply_marker_v1.json'

EXPECTED_APPLY_ID = 'slc_f_gvg_war_scope_20260523T192217Z_34999526'
EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'
ALLOWED_CHANGED = {'backend/routes/gvg.py'}

PRIOR_MARKERS = [
    'slc_f_batch_0_1_apply_marker_v1.json',
    'slc_f_batch_1b_apply_marker_v1.json',
    'slc_f_batch_2_apply_marker_v1.json',
    'slc_f_equipment_scope_apply_marker_v1.json',
    'slc_f_raids_equipment_scope_apply_marker_v1.json',
    'slc_g_default_s1_migration_apply_result_v1.json',
]

FORBIDDEN_UNCHANGED = [
    'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py', 'backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py', 'backend/routes/combat.py',
    'backend/routes/equipment.py', 'backend/routes/forge.py', 'backend/routes/raids.py',
    'backend/routes/unique_items.py',
    'backend/routes/sanctuary.py', 'backend/routes/player_faction_v2.py',
    'backend/routes/cosmetics.py', 'backend/routes/economy.py',
    'backend/routes/push_notifications.py', 'backend/routes/game_data.py',
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing', '/api/account/server-profiles', '/api/account/active-server']

MUST_STILL_HAVE_HELPER_IMPORT = [
    'backend/routes/items.py', 'backend/routes/forge.py', 'backend/routes/achievements.py',
    'backend/routes/level_sharing.py', 'backend/routes/social.py', 'backend/routes/soul_forge.py',
    'backend/routes/artifacts.py', 'backend/routes/guild.py', 'backend/routes/raids.py',
]


def main() -> int:
    errs = []
    if not MARKER.exists():
        errs.append('apply_marker_missing')
    else:
        m = json.loads(MARKER.read_text())
        if m.get('scope') != 'GVG_WAR_ONLY': errs.append('scope_not_GVG_WAR_ONLY')
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

    # Specific patch verification on gvg.py
    gvg_text = (ROOT / 'backend/routes/gvg.py').read_text(errors='ignore')
    if 'from utils.server_scope import ensure_server_scope' not in gvg_text:
        errs.append('gvg_helper_import_missing')
    if 'war = ensure_server_scope(war, current_user["id"])' not in gvg_text:
        errs.append('gvg_ensure_server_scope_call_missing')
    pattern = r'war = ensure_server_scope\(war,\s*current_user\["id"\]\)\s*\n\s*await db\.gvg_wars\.insert_one\(war\)'
    if not re.search(pattern, gvg_text):
        errs.append('gvg_patch_not_adjacent_to_insert_one')
    # Business logic markers preserved
    for snippet in ['guild_a_id', 'guild_b_id', 'guild_a_score', 'guild_b_score',
                    'guild_a_attacks', 'guild_b_attacks', 'winner_guild_id', 'is_bot_guild']:
        if snippet not in gvg_text:
            errs.append(f'gvg_business_logic_marker_missing:{snippet}')
    # Confirm we did NOT touch user_mail.insert_one
    if gvg_text.count('user_mail.insert_one') != 1:
        errs.append(f'gvg_user_mail_insert_count_unexpected:{gvg_text.count("user_mail.insert_one")}')
    # And no ensure_server_scope near user_mail
    if re.search(r'ensure_server_scope.*\n\s*await db\.user_mail\.insert_one', gvg_text):
        errs.append('gvg_user_mail_unexpectedly_patched')

    out = {
        'task_origin': 'SLC-F-GVG-WAR-SCOPE-POST-APPLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-GVG-WAR-SCOPE-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
