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
    if FORBIDDEN_RESOLVER_FILE.exists():
        fail(f'forbidden second-slice resolver file already exists (must NOT exist after Project R): {FORBIDDEN_RESOLVER_FILE}')
    if m.get('battle_engine_to_be_mutated_in_this_pack') is not False:
        fail('battle_engine_to_be_mutated_in_this_pack must be False')
    if m.get('import_in_battle_engine') is not False:
        fail('import_in_battle_engine must be False')
    if m.get('flag_gated_in_future') is not True:
        fail('flag_gated_in_future must be True')
    # Scan battle_engine.py: must NOT contain second-slice resolver import or flag
    if BATTLE_ENGINE.exists():
        src = BATTLE_ENGINE.read_text()
        for tok in FORBIDDEN_IMPORT_TOKENS:
            if tok in src:
                fail(f'battle_engine.py contains forbidden second-slice token: {tok}')
    staged = m.get('staged_path') or []
    if len(staged) < 6:
        fail('staged_path must include at least 6 stages (design -> prod)')
    print('[PASS] PROJECT_R Track D resolver extension design READY — no resolver file, no battle_engine mutation, no second-slice import')
    sys.exit(0)


if __name__ == '__main__':
    main()
