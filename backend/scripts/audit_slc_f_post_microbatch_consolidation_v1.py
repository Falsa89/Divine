#!/usr/bin/env python3
"""
SLC-F POST-MICROBATCH CONSOLIDATION AUDIT (READ-ONLY)

Verifica che tutti i 9 checkpoint SLC-F siano integri:
- 9 marker files on-disk e correttamente firmati
- 6 rollback scripts on-disk e gated
- 7 post-apply validators on-disk
- Helper module on-disk
- 11 file runtime patchati con helper import
- Audit JSON di consolidamento on-disk con risk ranking + recommended next

Questo script NON esegue patch runtime, NON scrive su DB, NON migra dati.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SAFETY = ROOT / 'data/design/system_safety'
SCRIPTS = ROOT / 'backend/scripts'
AUDIT_JSON = SAFETY / 'slc_f_post_microbatch_consolidation_v1.json'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_post_microbatch_consolidation_v1_result.json'

EXPECTED_MARKERS = [
    ('slc_g_default_s1_migration_apply_result_v1.json',     'slc_g_commit_a_20260523T143803Z_4600ac04',                  'migration_id'),
    ('slc_f_batch_0_1_apply_marker_v1.json',                'slc_f_batch_0_1_20260523T173754Z_27b1b737',                'apply_id'),
    ('slc_f_batch_1b_apply_marker_v1.json',                 'slc_f_batch_1b_20260523T175058Z_2cf0584c',                 'apply_id'),
    ('slc_f_batch_2_apply_marker_v1.json',                  'slc_f_batch_2_20260523T181752Z_b838601e',                  'apply_id'),
    ('slc_f_equipment_scope_apply_marker_v1.json',          'slc_f_equipment_scope_20260523T182939Z_d2afcc8a',         'apply_id'),
    ('slc_f_raids_equipment_scope_apply_marker_v1.json',    'slc_f_raids_equipment_scope_20260523T184512Z_a46a6034',    'apply_id'),
    ('slc_f_minor_write_surfaces_audit_v1.json',            'slc_f_minor_audit_20260523T190000Z_audit_only',            'audit_id'),
    ('slc_f_gvg_war_scope_apply_marker_v1.json',            'slc_f_gvg_war_scope_20260523T192217Z_34999526',            'apply_id'),
    ('slc_f_unique_items_scope_apply_marker_v1.json',       'slc_f_unique_items_scope_20260523T193344Z_48aa4881',       'apply_id'),
]

EXPECTED_ROLLBACK_SCRIPTS = [
    'rollback_slc_f_batch_0_1.py', 'rollback_slc_f_batch_1b.py', 'rollback_slc_f_batch_2.py',
    'rollback_slc_f_equipment_scope.py', 'rollback_slc_f_raids_equipment_scope.py',
    'rollback_slc_f_gvg_war_scope.py', 'rollback_slc_f_unique_items_scope.py',
]

EXPECTED_POST_APPLY_VALIDATORS = [
    'validate_slc_f_batch_0_1_post_apply_v1.py', 'validate_slc_f_batch_1b_post_apply_v1.py',
    'validate_slc_f_batch_2_post_apply_v1.py', 'validate_slc_f_equipment_scope_post_apply_v1.py',
    'validate_slc_f_raids_equipment_scope_post_apply_v1.py',
    'validate_slc_f_gvg_war_scope_post_apply_v1.py', 'validate_slc_f_unique_items_scope_post_apply_v1.py',
]

EXPECTED_HELPER_FILES = [
    'hero_progression.py', 'items.py', 'forge.py', 'achievements.py',
    'level_sharing.py', 'social.py', 'soul_forge.py', 'artifacts.py', 'guild.py',
    'raids.py', 'gvg.py', 'unique_items.py',
]


def main() -> int:
    errs = []

    if not AUDIT_JSON.exists():
        errs.append('consolidation_audit_json_missing')
        OUT.write_text(json.dumps({'verdict': 'FAIL', 'errors': errs}, indent=2))
        return 1

    audit = json.loads(AUDIT_JSON.read_text())
    if audit.get('scope') != 'POST_MICROBATCH_AUDIT_ONLY':
        errs.append('audit_scope_must_be_POST_MICROBATCH_AUDIT_ONLY')
    if audit.get('runtime_files_modified') is not False:
        errs.append('audit_must_assert_no_runtime_modifications')
    if audit.get('db_writes_performed') is not False:
        errs.append('audit_must_assert_no_db_writes')

    # Marker integrity
    for fname, expected_id, key in EXPECTED_MARKERS:
        p = SAFETY / fname
        if not p.exists():
            errs.append(f'marker_missing:{fname}')
            continue
        d = json.loads(p.read_text())
        if d.get(key) != expected_id:
            errs.append(f'marker_id_mismatch:{fname}:{key}=got_{d.get(key)}_want_{expected_id}')

    # Rollback scripts on-disk
    for s in EXPECTED_ROLLBACK_SCRIPTS:
        if not (SCRIPTS / s).exists():
            errs.append(f'rollback_script_missing:{s}')

    # Post-apply validators on-disk
    for v in EXPECTED_POST_APPLY_VALIDATORS:
        if not (SCRIPTS / v).exists():
            errs.append(f'post_apply_validator_missing:{v}')

    # Helper module on-disk
    helper = ROOT / 'backend/utils/server_scope.py'
    if not helper.exists():
        errs.append('helper_module_missing')
    else:
        ht = helper.read_text()
        if 'def ensure_server_scope' not in ht:
            errs.append('helper_ensure_server_scope_missing')
        if 'LEGACY_DEFAULT_SERVER_ID' not in ht or '"s1"' not in ht:
            errs.append('helper_legacy_s1_missing')

    # 12 expected helper-imported files
    for fname in EXPECTED_HELPER_FILES:
        text = (ROOT / 'backend/routes' / fname).read_text(errors='ignore')
        if 'from utils.server_scope import ensure_server_scope' not in text:
            errs.append(f'helper_import_missing_in:{fname}')

    # Count helper calls across the 12 files
    total_calls = 0
    for fname in EXPECTED_HELPER_FILES:
        text = (ROOT / 'backend/routes' / fname).read_text(errors='ignore')
        for line in text.splitlines():
            if 'ensure_server_scope(' in line and 'import' not in line:
                total_calls += 1
    # Expected total calls from JSON
    expected_calls = audit.get('helper_usage_matrix', {}).get('total_ensure_server_scope_calls')
    if expected_calls is not None and abs(total_calls - expected_calls) > 2:
        errs.append(f'helper_call_count_drift:rescan={total_calls}_vs_audit={expected_calls}')

    # Audit structure sanity
    for k in ['marker_matrix', 'runtime_patched_file_matrix', 'helper_usage_matrix',
              'no_op_skipped_matrix', 'remaining_work_matrix', 'risk_ranking',
              'summary_counts', 'recommended_next_gated_job']:
        if k not in audit:
            errs.append(f'audit_section_missing:{k}')

    if (audit.get('summary_counts') or {}).get('checkpoints_completed') != 9:
        errs.append('summary_counts_checkpoints_completed_must_be_9')

    out = {
        'task_origin': 'SLC-F-POST-MICROBATCH-CONSOLIDATION-AUDIT-V1',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'helper_calls_rescanned': total_calls,
        'consolidation_audit_path': str(AUDIT_JSON),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-POST-MICROBATCH-CONSOLIDATION-AUDIT-V1 {out['verdict']} errors={len(errs)} helper_calls={total_calls}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
