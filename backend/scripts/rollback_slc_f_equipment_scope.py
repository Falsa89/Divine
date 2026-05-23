#!/usr/bin/env python3
"""
SLC-F EQUIPMENT SERVER_SCOPE EXTENSION ROLLBACK SCRIPT (GATED)

This apply was a SAFE NO-OP: equipment.py contains only update_one calls
on existing documents (no insert/upsert), and patching would require inline
DB migration which is explicitly forbidden. No source files were modified.
Therefore this rollback is a marker-only revert.

Guards (BOTH must be set; otherwise refuses to run):
  SLC_F_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL=true
  SLC_F_EQUIPMENT_SCOPE_ROLLBACK_ID=slc_f_equipment_scope_20260523T182939Z_d2afcc8a
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APPLY_ID = 'slc_f_equipment_scope_20260523T182939Z_d2afcc8a'
MARKER = Path('/app/data/design/system_safety/slc_f_equipment_scope_apply_marker_v1.json')
ROLLBACK_MARKER = Path('/app/data/design/system_safety/slc_f_equipment_scope_rollback_marker_v1.json')


def main() -> int:
    if os.environ.get('SLC_F_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL') != 'true':
        print('REFUSED: SLC_F_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL must be set to "true"')
        return 2
    if os.environ.get('SLC_F_EQUIPMENT_SCOPE_ROLLBACK_ID') != APPLY_ID:
        print(f'REFUSED: SLC_F_EQUIPMENT_SCOPE_ROLLBACK_ID must equal "{APPLY_ID}"')
        return 2
    if not MARKER.exists():
        print(f'WARN: apply marker not found at {MARKER} (nothing to revert)')
        return 0
    info = {
        'task_origin': 'SLC-F-EQUIPMENT-SERVER-SCOPE-EXTENSION-ROLLBACK',
        'rolled_back_at_utc': datetime.now(timezone.utc).isoformat(),
        'apply_id': APPLY_ID,
        'changed_files': [],
        'equipment_write_surfaces_touched': [],
        'equipment_write_surfaces_skipped': ['EQ-W1', 'EQ-W2', 'EQ-W3', 'EQ-W4'],
        'restore_steps': [
            'Apply was a SAFE NO-OP: no source files were patched.',
            'No file restoration is required.',
            'Marker file slc_f_equipment_scope_apply_marker_v1.json may remain on-disk for audit.'
        ],
        'post_rollback_safety_checks': [
            'Confirm /api/heroes count == 100',
            'Confirm /api/heroes/primordial_gaia == 404',
            'Confirm /api/heroes/borea == 200 catalog-only inert',
            'Confirm AF2-N canary state preserved',
            'Confirm SLC-G migration_id preserved',
            'Confirm Batch-0/1, Batch-1B, Batch-2 markers preserved'
        ],
        'post_rollback_expected_invariants': {
            'api_heroes_count': 100,
            'primordial_gaia_http': 404,
            'borea_http': 200,
            'greek_borea_http': 200,
            'server_profiles_runtime_enabled': False,
            'second_server_opening_enabled': False,
            'af2n_canary_state_preserved': True,
            'equipment_business_logic_unchanged': True
        },
        'note': 'This rollback is gated. No automatic execution. Code state identical to pre-apply because equipment scope extension made no code changes.'
    }
    ROLLBACK_MARKER.write_text(json.dumps(info, indent=2))
    print(f'OK: rollback marker written to {ROLLBACK_MARKER}')
    print('Rollback complete (no-op code-wise; marker-only annotation).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
