#!/usr/bin/env python3
"""
SLC-F BATCH-2 ROLLBACK SCRIPT (GATED)

Batch-2 was a SAFE NO-OP apply: ALL candidate routes were classified as SKIP
per canonical SLC-F policy. No source files were modified during the apply.
Therefore this rollback is a marker-only revert. It removes/annotates the
apply marker so the apply is logically reverted. No code changes are needed.

Guards (BOTH must be set; otherwise refuses to run):
  SLC_F_BATCH_2_ROLLBACK_APPROVAL=true
  SLC_F_BATCH_2_ROLLBACK_ID=slc_f_batch_2_20260523T181752Z_b838601e
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APPLY_ID = 'slc_f_batch_2_20260523T181752Z_b838601e'
MARKER = Path('/app/data/design/system_safety/slc_f_batch_2_apply_marker_v1.json')
ROLLBACK_MARKER = Path('/app/data/design/system_safety/slc_f_batch_2_rollback_marker_v1.json')


def main() -> int:
    if os.environ.get('SLC_F_BATCH_2_ROLLBACK_APPROVAL') != 'true':
        print('REFUSED: SLC_F_BATCH_2_ROLLBACK_APPROVAL must be set to "true"')
        return 2
    if os.environ.get('SLC_F_BATCH_2_ROLLBACK_ID') != APPLY_ID:
        print(f'REFUSED: SLC_F_BATCH_2_ROLLBACK_ID must equal "{APPLY_ID}"')
        return 2
    if not MARKER.exists():
        print(f'WARN: apply marker not found at {MARKER} (nothing to revert)')
        return 0
    info = {
        'task_origin': 'SLC-F-BATCH-2-ROLLBACK',
        'rolled_back_at_utc': datetime.now(timezone.utc).isoformat(),
        'apply_id': APPLY_ID,
        'changed_files': [],
        'route_families_touched': [],
        'route_families_skipped': [
            'push_notifications', 'cosmetics_ownership', 'economy_paid_wallet',
            'game_data', 'equipment (out_of_scope)', 'unique_items (out_of_scope)',
            'synergies (no_writes)'
        ],
        'restore_steps': [
            'Apply was a SAFE NO-OP: no source files were patched.',
            'No file restoration is required.',
            'Marker file slc_f_batch_2_apply_marker_v1.json may remain on-disk for audit.'
        ],
        'post_rollback_safety_checks': [
            'Confirm /api/heroes count == 100',
            'Confirm /api/heroes/primordial_gaia == 404',
            'Confirm /api/heroes/borea == 200 (catalog-only inert)',
            'Confirm AF2-N canary state preserved',
            'Confirm SLC-G migration_id preserved',
            'Confirm Batch-0/1 and Batch-1B markers preserved'
        ],
        'post_rollback_expected_invariants': {
            'api_heroes_count': 100,
            'primordial_gaia_http': 404,
            'borea_http': 200,
            'greek_borea_http': 200,
            'server_profiles_runtime_enabled': False,
            'second_server_opening_enabled': False,
            'af2n_canary_state_preserved': True
        },
        'note': 'This rollback is gated. No automatic execution. Code state identical to pre-apply because Batch-2 made no code changes.'
    }
    ROLLBACK_MARKER.write_text(json.dumps(info, indent=2))
    print(f'OK: rollback marker written to {ROLLBACK_MARKER}')
    print('Rollback complete (no-op code-wise; marker-only annotation).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
