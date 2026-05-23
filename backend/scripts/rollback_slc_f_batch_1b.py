#!/usr/bin/env python3
# SLC-F BATCH-1B ROLLBACK SCRIPT (GATED)
# Gated env: SLC_F_BATCH_1B_ROLLBACK_APPROVAL=true AND SLC_F_BATCH_1B_ROLLBACK_ID=<apply_id>
import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
RESULT = ROOT / 'backend/reports/slc_f_batch_1b_rollback_result.json'
MARKER = ROOT / 'data/design/system_safety/slc_f_batch_1b_apply_marker_v1.json'
APPROVAL = 'SLC_F_BATCH_1B_ROLLBACK_APPROVAL'
ID_ENV = 'SLC_F_BATCH_1B_ROLLBACK_ID'
PATCHED_FILES = [
    'backend/routes/items.py','backend/routes/forge.py','backend/routes/achievements.py',
    'backend/routes/level_sharing.py','backend/routes/social.py','backend/routes/soul_forge.py',
    'backend/routes/artifacts.py','backend/routes/guild.py',
]

def fail(reason, extra=None):
    out = {'task_origin':'SLC-F-BATCH-1B-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED','reason':reason,
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),'extra':extra}
    RESULT.write_text(json.dumps(out, indent=2))
    print(f'ROLLBACK_NOT_APPROVED: {reason}')
    sys.exit(2)

def main():
    if os.environ.get(APPROVAL,'').lower() != 'true':
        fail(f'missing {APPROVAL}=true')
    apply_id = os.environ.get(ID_ENV,'').strip()
    if not apply_id: fail(f'missing {ID_ENV}')
    if not MARKER.exists():
        RESULT.write_text(json.dumps({'task_origin':'SLC-F-BATCH-1B-ROLLBACK','verdict':'ROLLBACK_NO_OP','reason':'marker_absent',
            'timestamp_utc':datetime.now(timezone.utc).isoformat()}, indent=2))
        print('ROLLBACK_NO_OP: marker absent'); return 0
    m = json.loads(MARKER.read_text())
    if m.get('apply_id') != apply_id: fail('apply_id_mismatch',{'live':m.get('apply_id'),'provided':apply_id})
    pre_head = m.get('git_head_before')
    if not pre_head: fail('git_head_before_missing_in_marker')
    logs = []
    for f in PATCHED_FILES:
        p = subprocess.run(['git','-C',str(ROOT),'checkout', pre_head, '--', f], capture_output=True, text=True)
        logs.append({'file':f,'rc':p.returncode,'stderr':p.stderr[:200]})
    MARKER.unlink()
    out = {'task_origin':'SLC-F-BATCH-1B-ROLLBACK','verdict':'ROLLBACK_APPLIED','apply_id':apply_id,'pre_head':pre_head,
           'logs':logs,'next_steps':['sudo supervisorctl restart backend','verify smoke + AF2-N + suite'],
           'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    RESULT.write_text(json.dumps(out, indent=2))
    print('ROLLBACK_APPLIED')
    for l in logs: print(f"  {l['file']}: rc={l['rc']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
