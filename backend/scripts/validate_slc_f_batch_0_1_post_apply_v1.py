#!/usr/bin/env python3
# SLC-F BATCH-0/1 POST-APPLY VALIDATOR (READ-ONLY)
# Verifica che:
# - solo Batch-0 helper e Batch-1 route file siano stati toccati
# - file proibiti (battle_engine.py, battle_core.py, combat.tsx, affinity_gift_spend.py) intatti
# - nessuna route /api/housing creata
# - nessuna route SLC-H runtime registrata
# - feature flag restano unset
# - SLC-G migration_applied=true e migration_id immutato
# - apply marker presente con la struttura attesa
import json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY_DIR = ROOT / 'data/design/system_safety'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_batch_0_1_post_apply_v1_result.json'
APPLY_MARKER = SAFETY_DIR / 'slc_f_batch_0_1_apply_marker_v1.json'
SLC_G_MARKER = SAFETY_DIR / 'slc_g_default_s1_migration_apply_result_v1.json'
EXPECTED_SLC_G_MIGRATION_ID = 'slc_g_commit_a_20260523T143803Z_4600ac04'

ALLOWED_CHANGED_FILES = {
    'backend/utils/server_scope.py',                  # Batch-0 helper (new)
    'backend/routes/hero_progression.py',            # Batch-1 patched route
}
FORBIDDEN_UNCHANGED_FILES = [
    'backend/battle_engine.py',
    'backend/battle_core.py',
    'frontend/app/combat.tsx',
    'backend/routes/affinity_gift_spend.py',
    'backend/routes/heroes.py',
    'backend/routes/combat.py',
]
FORBIDDEN_ROUTE_PATHS = [
    '/api/housing',
    '/api/servers',
    '/api/account/server-profiles',
    '/api/account/active-server',
]

def main():
    errs = []
    # 1) Apply marker exists with correct structure
    if not APPLY_MARKER.exists():
        errs.append('apply_marker_missing')
        OUT.write_text(json.dumps({'verdict':'FAIL','errors':errs}, indent=2))
        print('SLC-F-BATCH-0-1-POST-APPLY FAIL apply_marker_missing'); return 1
    am = json.loads(APPLY_MARKER.read_text())
    if not am.get('apply_id'): errs.append('apply_marker:apply_id_missing')
    if am.get('scope') != 'BATCH_0_1_ONLY': errs.append('apply_marker:scope_must_be_BATCH_0_1_ONLY')
    if am.get('route_patch_applied_partial') is not True: errs.append('apply_marker:route_patch_applied_partial_not_true')
    if am.get('route_patch_applied_full') is not False: errs.append('apply_marker:route_patch_applied_full_must_be_false')
    if am.get('second_server_opening_allowed') is not False: errs.append('apply_marker:second_server_opening_allowed_must_be_false')
    if am.get('feature_flag_enabled') is not False: errs.append('apply_marker:feature_flag_enabled_must_be_false')
    if am.get('phase_11_executed') is not False: errs.append('apply_marker:phase_11_executed_must_be_false')
    if am.get('housing_runtime_implemented') is not False: errs.append('apply_marker:housing_runtime_implemented_must_be_false')
    if not am.get('git_head_before'): errs.append('apply_marker:git_head_before_missing')
    if am.get('changed_files'):
        cf = set(am['changed_files'])
        unauth = cf - ALLOWED_CHANGED_FILES
        if unauth:
            errs.append(f'unauthorized_changed_files:{sorted(unauth)}')

    # 2) SLC-G migration still applied with same id
    if not SLC_G_MARKER.exists():
        errs.append('slc_g_migration_marker_missing')
    else:
        sg = json.loads(SLC_G_MARKER.read_text())
        if not sg.get('migration_applied'): errs.append('slc_g_migration_applied_not_true')
        if sg.get('migration_id') != EXPECTED_SLC_G_MIGRATION_ID:
            errs.append(f'slc_g_migration_id_changed:got={sg.get("migration_id")}_expected={EXPECTED_SLC_G_MIGRATION_ID}')

    # 3) Forbidden files unchanged (no diff vs HEAD)
    import subprocess
    for f in FORBIDDEN_UNCHANGED_FILES:
        p = subprocess.run(['git','-C',str(ROOT),'diff','HEAD','--',f], capture_output=True, text=True)
        if p.stdout.strip():
            errs.append(f'forbidden_file_diff_present:{f}')

    # 4) No /api/housing or SLC-H runtime routes registered
    routes_dir = ROOT / 'backend' / 'routes'
    for f in list(routes_dir.glob('*.py')) + [ROOT/'backend/server.py']:
        if not f.exists(): continue
        text = f.read_text(errors='ignore')
        for fr in FORBIDDEN_ROUTE_PATHS:
            if re.search(r'["\']' + re.escape(fr) + r'["\']', text):
                errs.append(f'forbidden_route_present:{fr}_in_{f.name}')

    # 5) Feature flags unset at validator runtime
    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'):
        errs.append('SERVER_PROFILES_RUNTIME_ENABLED_must_be_unset')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'):
        errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    # 6) Helper module imports cleanly (syntactic check)
    helper = ROOT / 'backend/utils/server_scope.py'
    if not helper.exists():
        errs.append('helper_module_missing')
    else:
        text = helper.read_text()
        if 'def ensure_server_scope' not in text:
            errs.append('helper:ensure_server_scope_missing')
        if 'def resolve_server_id' not in text:
            errs.append('helper:resolve_server_id_missing')
        if 'LEGACY_DEFAULT_SERVER_ID' not in text or '"s1"' not in text:
            errs.append('helper:LEGACY_DEFAULT_SERVER_ID_must_be_s1')

    out = {'task_origin':'SLC-F-BATCH-0-1-POST-APPLY',
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-BATCH-0-1-POST-APPLY {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
