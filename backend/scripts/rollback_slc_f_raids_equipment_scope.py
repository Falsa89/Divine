#!/usr/bin/env python3
"""
SLC-F RAIDS EQUIPMENT SCOPE ROLLBACK SCRIPT (GATED)

Reverts the minimal +2-line patch applied to /app/backend/routes/raids.py:
  - removes the import line: 'from utils.server_scope import ensure_server_scope'
  - removes the call line: 'equip = ensure_server_scope(equip, uid)' inserted
    immediately before 'await db.user_equipment.insert_one(equip)' in
    craft_exclusive_item.

Guards (BOTH must be set; otherwise refuses to run):
  SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL=true
  SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_ID=slc_f_raids_equipment_scope_20260523T184512Z_a46a6034
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APPLY_ID = 'slc_f_raids_equipment_scope_20260523T184512Z_a46a6034'
RAIDS_PY = Path('/app/backend/routes/raids.py')
MARKER = Path('/app/data/design/system_safety/slc_f_raids_equipment_scope_apply_marker_v1.json')
ROLLBACK_MARKER = Path('/app/data/design/system_safety/slc_f_raids_equipment_scope_rollback_marker_v1.json')

IMPORT_LINE = 'from utils.server_scope import ensure_server_scope\n'
CALL_LINE = '        equip = ensure_server_scope(equip, uid)\n'


def main() -> int:
    if os.environ.get('SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL') != 'true':
        print('REFUSED: SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL must be set to "true"')
        return 2
    if os.environ.get('SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_ID') != APPLY_ID:
        print(f'REFUSED: SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_ID must equal "{APPLY_ID}"')
        return 2
    if not RAIDS_PY.exists():
        print(f'ERROR: {RAIDS_PY} not found')
        return 1

    text = RAIDS_PY.read_text()
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
        RAIDS_PY.write_text(new_text)
        print(f'OK: reverted raids.py (import_removed={removed_import}, call_removed={removed_call})')
    else:
        print('NOTE: no patch markers found in raids.py (already rolled back or never applied)')

    info = {
        'task_origin': 'SLC-F-RAIDS-EQUIPMENT-SCOPE-ROLLBACK',
        'rolled_back_at_utc': datetime.now(timezone.utc).isoformat(),
        'apply_id': APPLY_ID,
        'changed_files': ['backend/routes/raids.py'] if (removed_import or removed_call) else [],
        'raids_lines_reverted': {
            'import_removed': removed_import,
            'call_removed': removed_call,
        },
        'restore_steps': [
            'Removed: from utils.server_scope import ensure_server_scope',
            'Removed: equip = ensure_server_scope(equip, uid)',
            'No DB writes; no schema migration; no business logic touched.'
        ],
        'post_rollback_safety_checks': [
            'Confirm /api/heroes count == 100',
            'Confirm /api/heroes/primordial_gaia == 404',
            'Confirm /api/heroes/borea == 200 catalog-only inert',
            'Confirm AF2-N canary state preserved',
            'Confirm SLC-G migration_id preserved',
            'Confirm Batch-0/1, Batch-1B, Batch-2, Equipment-scope markers preserved',
            'Restart backend (sudo supervisorctl restart backend) and re-run suite'
        ]
    }
    ROLLBACK_MARKER.write_text(json.dumps(info, indent=2))
    print(f'Rollback marker written: {ROLLBACK_MARKER}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
