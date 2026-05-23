#!/usr/bin/env python3
# SLC-F BATCH-0/1 ROLLBACK SCRIPT (GATED)
# Reverte le modifiche fatte da SLC-F Batch-0/1 apply: rimuove l'import e i
# 5 helper calls in hero_progression.py + elimina il modulo helper utils/server_scope.py.
# Gated: richiede env SLC_F_BATCH_0_1_ROLLBACK_APPROVAL=true
#         AND   env SLC_F_BATCH_0_1_ROLLBACK_ID=<apply_id_originale>
# NO database write, solo file/code revert.
import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
REPORTS = ROOT / 'backend/reports'
RESULT = REPORTS / 'slc_f_batch_0_1_rollback_result.json'

APPROVAL_ENV = 'SLC_F_BATCH_0_1_ROLLBACK_APPROVAL'
ID_ENV = 'SLC_F_BATCH_0_1_ROLLBACK_ID'

APPLY_MARKER_FILE = ROOT / 'data/design/system_safety/slc_f_batch_0_1_apply_marker_v1.json'
HELPER_FILE = ROOT / 'backend/utils/server_scope.py'
ROUTE_FILE = ROOT / 'backend/routes/hero_progression.py'

def main():
    if os.environ.get(APPROVAL_ENV,'').lower() != 'true':
        print(f'ROLLBACK_NOT_APPROVED: env {APPROVAL_ENV} != true')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED',
            'reason':f'missing {APPROVAL_ENV}=true',
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        return 2
    apply_id = os.environ.get(ID_ENV,'').strip()
    if not apply_id:
        print(f'ROLLBACK_NOT_APPROVED: env {ID_ENV} missing')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED',
            'reason':f'missing {ID_ENV}',
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        return 2
    # Verify apply_id matches the marker file
    if not APPLY_MARKER_FILE.exists():
        print('ROLLBACK_NO_OP: no apply marker present, nothing to roll back')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_NO_OP',
            'reason':'apply_marker_absent',
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        return 0
    am = json.loads(APPLY_MARKER_FILE.read_text())
    if am.get('apply_id') != apply_id:
        print(f'ROLLBACK_NOT_APPROVED: id mismatch live={am.get("apply_id")} provided={apply_id}')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED',
            'reason':'apply_id_mismatch',
            'live_apply_id':am.get('apply_id'),'provided_apply_id':apply_id,
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        return 2

    # Use git to revert the changes to ROUTE_FILE and HELPER_FILE since the
    # apply commit. Strategy: git checkout the pre-apply HEAD for these paths.
    pre_head = am.get('git_head_before')
    if not pre_head:
        print('ROLLBACK_FAILED: no git_head_before in marker')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_FAILED',
            'reason':'git_head_before_missing',
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        return 2
    cmds = [
        ['git','-C',str(ROOT),'checkout', pre_head, '--', str(ROUTE_FILE.relative_to(ROOT))],
    ]
    logs = []
    for c in cmds:
        p = subprocess.run(c, capture_output=True, text=True)
        logs.append({'cmd':' '.join(c),'rc':p.returncode,'stderr':p.stderr[:200]})
    # Helper file: delete (it didn't exist pre-apply)
    helper_removed = False
    if HELPER_FILE.exists():
        HELPER_FILE.unlink()
        helper_removed = True
    # Remove apply marker file
    if APPLY_MARKER_FILE.exists():
        APPLY_MARKER_FILE.unlink()

    out = {
        'task_origin':'SLC-F-BATCH-0-1-ROLLBACK','verdict':'ROLLBACK_APPLIED',
        'apply_id':apply_id,'pre_head':pre_head,
        'helper_file_removed':helper_removed,
        'logs':logs,
        'next_steps':[
            'sudo supervisorctl restart backend',
            'verify /api/heroes=100, primordial_gaia=404, borea/greek_borea=200',
            'verify route_patch_applied=false in marker file (file now absent)',
        ],
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
    }
    RESULT.write_text(json.dumps(out, indent=2))
    print('ROLLBACK_APPLIED')
    for l in logs: print(f'  cmd={l["cmd"]} rc={l["rc"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
