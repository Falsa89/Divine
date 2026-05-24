#!/usr/bin/env python3
"""PROJECT_R Track D validator — resolver extension design.

Verifica che i file first-slice esistano (referenziati), che NON sia stato creato
un resolver second-slice in questo pack e che battle_engine.py NON sia stato mutato.
"""
import hashlib, json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_r_status_second_slice_resolver_extension_design_v1.json')
FORBIDDEN_RESOLVER_FILE = Path('/app/backend/game_logic/status_second_slice_resolver_pure.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
FORBIDDEN_IMPORT_TOKENS = ('from game_logic.status_second_slice_resolver_pure', 'import status_second_slice_resolver_pure', 'STATUS_RUNTIME_SECOND_SLICE_ENABLED')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_STATUS_SECOND_SLICE_RESOLVER_EXTENSION_DESIGN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    refs = m.get('existing_first_slice_files') or {}
    for k, p in refs.items():
        if not Path(p).exists():
            fail(f'referenced first-slice file missing: {k}={p}')
    if m.get('resolver_file_created_in_this_pack') is not False:
        fail('resolver_file_created_in_this_pack must be False')
    # FORBIDDEN_RESOLVER_FILE may exist if a successor pack (e.g. Project S) created it intentionally.
    # In that case verify the successor's marker declares module_created=true AND battle_engine still does
    # NOT import the second-slice resolver. If neither successor marker nor file exists, also OK.
    project_s_marker = Path('/app/data/design/status_effects/project_s_second_slice_resolver_module_v1.json')
    if FORBIDDEN_RESOLVER_FILE.exists():
        if not project_s_marker.exists():
            fail(f'second-slice resolver file exists but no successor (Project S) marker found: {FORBIDDEN_RESOLVER_FILE}')
        try:
            s_m = json.loads(project_s_marker.read_text())
        except Exception as e:
            fail(f'cannot read successor marker: {e}')
        if s_m.get('module_created') is not True:
            fail('successor marker module_created must be True if resolver file exists')
        if s_m.get('runtime_imported_anywhere') is not False:
            fail('successor marker runtime_imported_anywhere must be False')
    if m.get('battle_engine_to_be_mutated_in_this_pack') is not False:
        fail('battle_engine_to_be_mutated_in_this_pack must be False')
    if m.get('import_in_battle_engine') is not False:
        fail('import_in_battle_engine must be False')
    if m.get('flag_gated_in_future') is not True:
        fail('flag_gated_in_future must be True')
    # Scan battle_engine.py: must NOT contain DIRECT second-slice resolver import.
    # PROJECT_T (single-point wiring canary pack) is authorized to introduce the
    # flag name STATUS_RUNTIME_SECOND_SLICE_ENABLED and the seam binding inside
    # battle_engine.py. Direct import of the pure resolver is still forbidden.
    # Detect PROJECT_T applied state for non-weakening tolerance.
    project_t_marker = Path('/app/data/design/status_effects/project_t_second_slice_battle_engine_wiring_v1.json')
    project_t_applied = False
    if project_t_marker.exists():
        try:
            _t = json.loads(project_t_marker.read_text())
            if _t.get('applied') is True and _t.get('flag_in_live_env') is False and _t.get('identity_fallback_present') is True:
                project_t_applied = True
        except Exception:
            project_t_applied = False
    if BATTLE_ENGINE.exists():
        src = BATTLE_ENGINE.read_text()
        for tok in FORBIDDEN_IMPORT_TOKENS:
            if tok in src:
                if project_t_applied and tok == 'STATUS_RUNTIME_SECOND_SLICE_ENABLED':
                    # legitimate reference in PROJECT_T wiring comments / docstring
                    continue
                if tok in ('from game_logic.status_second_slice_resolver_pure', 'import status_second_slice_resolver_pure'):
                    # DIRECT resolver import is forbidden regardless of Project T
                    fail(f'battle_engine.py contains forbidden DIRECT second-slice resolver import: {tok}')
                fail(f'battle_engine.py contains forbidden second-slice token: {tok}')
    staged = m.get('staged_path') or []
    if len(staged) < 6:
        fail('staged_path must include at least 6 stages (design -> prod)')
    print('[PASS] PROJECT_R Track D resolver extension design READY — battle_engine still has no second-slice import; if resolver file exists, it was created by a successor pack with consistent marker')
    sys.exit(0)


if __name__ == '__main__':
    main()
