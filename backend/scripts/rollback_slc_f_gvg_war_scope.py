#!/usr/bin/env python3
"""
SLC-F GVG WAR INSERT SCOPE ROLLBACK SCRIPT (GATED)

Reverts the minimal +2-line patch applied to /app/backend/routes/gvg.py:
  - removes the import line: 'from utils.server_scope import ensure_server_scope'
  - removes the call line: 'war = ensure_server_scope(war, current_user["id"])'
    inserted immediately before 'await db.gvg_wars.insert_one(war)'.

Guards (BOTH must be set; otherwise refuses to run):
  SLC_F_GVG_WAR_SCOPE_ROLLBACK_APPROVAL=true
  SLC_F_GVG_WAR_SCOPE_ROLLBACK_ID=slc_f_gvg_war_scope_20260523T192217Z_34999526
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APPLY_ID = 'slc_f_gvg_war_scope_20260523T192217Z_34999526'
GVG_PY = Path('/app/backend/routes/gvg.py')
MARKER = Path('/app/data/design/system_safety/slc_f_gvg_war_scope_apply_marker_v1.json')
ROLLBACK_MARKER = Path('/app/data/design/system_safety/slc_f_gvg_war_scope_rollback_marker_v1.json')

IMPORT_LINE = 'from utils.server_scope import ensure_server_scope\n'
CALL_LINE = '        war = ensure_server_scope(war, current_user["id"])\n'


def main() -> int:
    if os.environ.get('SLC_F_GVG_WAR_SCOPE_ROLLBACK_APPROVAL') != 'true':
        print('REFUSED: SLC_F_GVG_WAR_SCOPE_ROLLBACK_APPROVAL must be set to "true"')
        return 2
    if os.environ.get('SLC_F_GVG_WAR_SCOPE_ROLLBACK_ID') != APPLY_ID:
        print(f'REFUSED: SLC_F_GVG_WAR_SCOPE_ROLLBACK_ID must equal "{APPLY_ID}"')
        return 2
    if not GVG_PY.exists():
        print(f'ERROR: {GVG_PY} not found')
        return 1

    text = GVG_PY.read_text()
    new_text = text
    removed_import = False
    removed_call = False
    if IMPORT_LINE in new_text:
        new_text = new_text.replace(IMPORT_LINE, '', 1)
        removed_import = True
    if CALL_LINE in new_text:
        new_text = new_text.replace(CALL_LINE, '', 1)
        removed_call = True

    if new_text != text:
        GVG_PY.write_text(new_text)
        print(f'OK: reverted gvg.py (import_removed={removed_import}, call_removed={removed_call})')
    else:
        print('NOTE: no patch markers found in gvg.py (already rolled back or never applied)')

    info = {
        'task_origin': 'SLC-F-GVG-WAR-SCOPE-ROLLBACK',
        'rolled_back_at_utc': datetime.now(timezone.utc).isoformat(),
        'apply_id': APPLY_ID,
        'changed_files': ['backend/routes/gvg.py'] if (removed_import or removed_call) else [],
        'gvg_lines_reverted': {'import_removed': removed_import, 'call_removed': removed_call},
        'post_rollback_safety_checks': [
            'Confirm /api/heroes count == 100',
            'Confirm /api/heroes/primordial_gaia == 404',
            'Confirm /api/heroes/borea == 200 catalog-only inert',
            'Confirm AF2-N canary state preserved',
            'Confirm SLC-G migration_id preserved',
            'Confirm all prior SLC-F markers preserved',
            'Restart backend (sudo supervisorctl restart backend) and re-run suite'
        ]
    }
    ROLLBACK_MARKER.write_text(json.dumps(info, indent=2))
    print(f'Rollback marker written: {ROLLBACK_MARKER}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
