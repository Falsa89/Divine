#!/usr/bin/env python3
"""
SLC-F UNIQUE-ITEMS SERVER_SCOPE ROLLBACK SCRIPT (GATED)

Reverts the patch applied to /app/backend/routes/unique_items.py:
  - removes the import line: 'from utils.server_scope import ensure_server_scope'
  - restores the inline insert_one literal in craft_unique_item
  - removes $setOnInsert clause from the equip_unique_item upsert

Guards (BOTH must be set; otherwise refuses to run):
  SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_APPROVAL=true
  SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_ID=slc_f_unique_items_scope_20260523T193344Z_48aa4881
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APPLY_ID = 'slc_f_unique_items_scope_20260523T193344Z_48aa4881'
UI_PY = Path('/app/backend/routes/unique_items.py')
MARKER = Path('/app/data/design/system_safety/slc_f_unique_items_scope_apply_marker_v1.json')
ROLLBACK_MARKER = Path('/app/data/design/system_safety/slc_f_unique_items_scope_rollback_marker_v1.json')

IMPORT_LINE = 'from utils.server_scope import ensure_server_scope\n'

CRAFT_PATCHED = '''        # Craft
        crafted_doc = {
            "user_id": uid, "hero_name": req.hero_name, "item_name": item["name"],
            "crafted_at": datetime.utcnow(),
        }
        crafted_doc = ensure_server_scope(crafted_doc, uid)
        await db.unique_items_crafted.insert_one(crafted_doc)
'''
CRAFT_ORIGINAL = '''        # Craft
        await db.unique_items_crafted.insert_one({
            "user_id": uid, "hero_name": req.hero_name, "item_name": item["name"],
            "crafted_at": datetime.utcnow(),
        })
'''

EQUIP_PATCHED = '''            {"$set": {"user_hero_id": req.user_hero_id, "equipped_at": datetime.utcnow()},
             "$setOnInsert": ensure_server_scope({}, uid)},
'''
EQUIP_ORIGINAL = '''            {"$set": {"user_hero_id": req.user_hero_id, "equipped_at": datetime.utcnow()}},
'''


def main() -> int:
    if os.environ.get('SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_APPROVAL') != 'true':
        print('REFUSED: SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_APPROVAL must be set to "true"')
        return 2
    if os.environ.get('SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_ID') != APPLY_ID:
        print(f'REFUSED: SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_ID must equal "{APPLY_ID}"')
        return 2
    if not UI_PY.exists():
        print(f'ERROR: {UI_PY} not found')
        return 1

    text = UI_PY.read_text()
    new_text = text
    steps = {'import_removed': False, 'craft_restored': False, 'equip_restored': False}

    if IMPORT_LINE in new_text:
        new_text = new_text.replace(IMPORT_LINE, '', 1)
        steps['import_removed'] = True
    if CRAFT_PATCHED in new_text:
        new_text = new_text.replace(CRAFT_PATCHED, CRAFT_ORIGINAL, 1)
        steps['craft_restored'] = True
    if EQUIP_PATCHED in new_text:
        new_text = new_text.replace(EQUIP_PATCHED, EQUIP_ORIGINAL, 1)
        steps['equip_restored'] = True

    if new_text != text:
        UI_PY.write_text(new_text)
        print(f'OK: reverted unique_items.py {steps}')
    else:
        print('NOTE: no patch markers found in unique_items.py (already rolled back or never applied)')

    info = {
        'task_origin': 'SLC-F-UNIQUE-ITEMS-SCOPE-ROLLBACK',
        'rolled_back_at_utc': datetime.now(timezone.utc).isoformat(),
        'apply_id': APPLY_ID,
        'changed_files': ['backend/routes/unique_items.py'] if any(steps.values()) else [],
        'unique_items_steps_reverted': steps,
        'post_rollback_safety_checks': [
            'Confirm /api/heroes count == 100',
            'Confirm /api/heroes/primordial_gaia == 404',
            'Confirm /api/heroes/borea == 200 catalog-only inert',
            'Confirm AF2-N canary state preserved',
            'Confirm all prior SLC-F markers preserved',
            'Restart backend (sudo supervisorctl restart backend) and re-run suite'
        ]
    }
    ROLLBACK_MARKER.write_text(json.dumps(info, indent=2))
    print(f'Rollback marker written: {ROLLBACK_MARKER}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
