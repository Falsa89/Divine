#!/usr/bin/env python3
# SLC-F BATCH-1B POST-APPLY VALIDATOR (READ-ONLY)
import json, os, re, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_batch_1b_post_apply_v1_result.json'
MARKER = SAFETY / 'slc_f_batch_1b_apply_marker_v1.json'
MARKER_0_1 = SAFETY / 'slc_f_batch_0_1_apply_marker_v1.json'
SLC_G_MARKER = SAFETY / 'slc_g_default_s1_migration_apply_result_v1.json'
EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'

ALLOWED_CHANGED = {
    'backend/routes/items.py','backend/routes/forge.py','backend/routes/achievements.py',
    'backend/routes/level_sharing.py','backend/routes/social.py','backend/routes/soul_forge.py',
    'backend/routes/artifacts.py','backend/routes/guild.py',
}
FORBIDDEN_UNCHANGED = [
    'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py','backend/routes/affinity_gifts.py',
    'backend/routes/heroes.py','backend/routes/combat.py',
    'backend/routes/sanctuary.py',  # Skipped per Character Bible rule
    'backend/routes/player_faction_v2.py',  # Skipped per no-writes rule
]
FORBIDDEN_ROUTE_PATHS = ['/api/housing','/api/servers','/api/account/server-profiles','/api/account/active-server']

def main():
    errs = []
    if not MARKER.exists(): errs.append('apply_marker_missing')
    else:
        m = json.loads(MARKER.read_text())
        if m.get('scope') != 'BATCH_1B_ONLY': errs.append('scope_not_BATCH_1B_ONLY')
        if m.get('route_patch_applied_partial') is not True: errs.append('route_patch_applied_partial_not_true')
        if m.get('route_patch_applied_full') is not False: errs.append('route_patch_applied_full_must_be_false')
        if m.get('second_server_opening_allowed') is not False: errs.append('second_server_opening_allowed_must_be_false')
        if m.get('feature_flag_enabled') is not False: errs.append('feature_flag_enabled_must_be_false')
        if m.get('housing_runtime_implemented') is not False: errs.append('housing_runtime_implemented_must_be_false')
        cf = set(m.get('changed_files') or [])
        unauth = cf - ALLOWED_CHANGED
        if unauth: errs.append(f'unauthorized_changed_files:{sorted(unauth)}')
        skipped = m.get('routes_skipped_and_why') or []
        if not any('sanctuary' in s.get('family','') for s in skipped):
            errs.append('sanctuary_skip_not_documented')

    if not MARKER_0_1.exists(): errs.append('batch_0_1_marker_missing_preceding_apply')
    if not SLC_G_MARKER.exists(): errs.append('slc_g_migration_marker_missing')
    else:
        sg = json.loads(SLC_G_MARKER.read_text())
        if sg.get('migration_id') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append(f'slc_g_migration_id_changed:got={sg.get("migration_id")}')
        if not sg.get('migration_applied'): errs.append('slc_g_migration_applied_not_true')

    for f in FORBIDDEN_UNCHANGED:
        p = subprocess.run(['git','-C',str(ROOT),'diff','HEAD','--',f], capture_output=True, text=True)
        if p.stdout.strip(): errs.append(f'forbidden_file_diff_present:{f}')

    routes_dir = ROOT / 'backend' / 'routes'
    for f in list(routes_dir.glob('*.py')) + [ROOT/'backend/server.py']:
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

    # Verify each patched file actually imports the helper
    for f in sorted(ALLOWED_CHANGED):
        text = (ROOT / f).read_text(errors='ignore')
        if 'from utils.server_scope import ensure_server_scope' not in text:
            errs.append(f'helper_import_missing_in:{f}')

    out = {'task_origin':'SLC-F-BATCH-1B-POST-APPLY','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-BATCH-1B-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
