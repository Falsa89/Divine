#!/usr/bin/env python3
"""PROJECT S Track F — rollback / deletion plan for the pure resolver module.

GATED. Removes ONLY the Project S-created pure resolver module and its markers,
leaving first-slice files untouched. Will NOT run unless the explicit env marker
is set:

    PROJECT_S_ROLLBACK_PURE_RESOLVER_OK=true

Usage:
    python3 rollback_project_s_status_second_slice_pure_resolver.py             # dry-run report only
    python3 rollback_project_s_status_second_slice_pure_resolver.py --execute   # GATED on env marker
"""
from __future__ import annotations

import argparse, os, sys
from pathlib import Path

TARGETS = (
    Path('/app/backend/game_logic/status_second_slice_resolver_pure.py'),
    Path('/app/data/design/status_effects/project_s_second_slice_resolver_spec_lock_v1.json'),
    Path('/app/data/design/status_effects/project_s_second_slice_resolver_module_v1.json'),
    Path('/app/data/design/status_effects/project_s_second_slice_golden_fixture_matrix_v1.json'),
    Path('/app/data/design/status_effects/project_s_second_slice_caps_stacking_v1.json'),
    Path('/app/data/design/status_effects/project_s_second_slice_runtime_no_import_guard_v1.json'),
    Path('/app/data/design/status_effects/project_s_second_slice_rollback_deletion_plan_v1.json'),
    Path('/app/data/design/project_management/project_s_second_slice_implementation_rc_gate_v1.json'),
    Path('/app/data/design/project_management/project_s_completion_and_next_pack_v1.json'),
)

FORBIDDEN_TO_DELETE = (
    Path('/app/backend/game_logic/status_first_slice_resolver_pure.py'),
    Path('/app/backend/game_logic/status_prefight_runtime_seam.py'),
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
)

GATE_ENV = 'PROJECT_S_ROLLBACK_PURE_RESOLVER_OK'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--execute', action='store_true', help='actually delete; GATED on env marker')
    args = ap.parse_args()

    # Defensive: never touch first-slice / battle runtime files.
    for p in FORBIDDEN_TO_DELETE:
        if p in TARGETS:
            print(f'[ABORT] internal logic error: {p} listed in TARGETS')
            return 4

    present = [p for p in TARGETS if p.exists()]
    print(f'[INFO] rollback dry-run: {len(present)} / {len(TARGETS)} project_s files present')
    for p in present:
        print(f'  - would delete: {p}')

    if not args.execute:
        print('[DRY-RUN] no files deleted; pass --execute (with env gate) for live deletion')
        return 0

    if os.environ.get(GATE_ENV, '').strip().lower() != 'true':
        print(f'[ABORT] --execute requires {GATE_ENV}=true (not set); refusing to delete')
        return 3

    deleted = 0
    for p in present:
        try:
            p.unlink()
            deleted += 1
            print(f'  [DEL] {p}')
        except Exception as e:
            print(f'  [ERR] {p}: {e}')
    print(f'[DONE] deleted {deleted} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
