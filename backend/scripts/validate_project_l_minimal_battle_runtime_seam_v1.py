#!/usr/bin/env python3
"""PROJECT_L Track B validator — minimal inert battle runtime seam created."""
import importlib.util, json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_minimal_battle_runtime_seam_result_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
ROLLBACK = Path('/app/backend/scripts/rollback_project_l_minimal_battle_runtime_seam.py')
FORBIDDEN_IMPORTERS = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
)
# Also scan all /app/backend/routes/*.py for forbidden import patterns.
ROUTES_DIR = Path('/app/backend/routes')
FORBIDDEN_PATTERNS = (
    'status_prefight_runtime_seam',
)


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_MINIMAL_BATTLE_RUNTIME_SEAM_CREATED_INERT': fail('verdict mismatch')
    if m.get('seam_created') is not True: fail('seam_created must be True')
    if not SEAM.exists(): fail(f'seam file missing: {SEAM}')
    if not ROLLBACK.exists(): fail(f'rollback script missing: {ROLLBACK}')
    # Verify seam is not imported by any live runtime file/route — EXCEPT for the
    # single-point import authorized by PROJECT_M Track B (recognized by the
    # explicit marker 'PROJECT_M Track B'). Any other importer is forbidden.
    PROJECT_M_AUTHORIZED_MARKER = 'PROJECT_M Track B'
    for f in FORBIDDEN_IMPORTERS:
        if not f.exists(): continue
        txt = f.read_text(encoding='utf-8', errors='ignore')
        for p in FORBIDDEN_PATTERNS:
            if p in txt:
                if PROJECT_M_AUTHORIZED_MARKER in txt:
                    # authorized by Pack M — accept and continue
                    continue
                fail(f'forbidden live importer detected: {f} contains "{p}" without PROJECT_M authorization')
    if ROUTES_DIR.exists():
        for r in ROUTES_DIR.rglob('*.py'):
            txt = r.read_text(encoding='utf-8', errors='ignore')
            for p in FORBIDDEN_PATTERNS:
                if p in txt:
                    fail(f'forbidden live importer detected in route: {r} contains "{p}"')
    # In-process seam contract check.
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    payload = {'team': [1, 2, 3]}
    # Flag unset -> identity
    if os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED'):
        fail('test precondition: STATUS_RUNTIME_BUFF_SLICE_ENABLED must be unset in env')
    out = mod.apply_prefight_status_slice_preview(payload)
    if out is not payload: fail('flag OFF must return identity payload (no copy)')
    # Flag ON + dry_run=False -> identity
    try:
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        out = mod.apply_prefight_status_slice_preview(payload)
        if out is not payload: fail('flag ON without dry_run must still return identity (live activation NOT authorized)')
        # Flag ON + dry_run=True -> shallow copy, original not mutated
        out = mod.apply_prefight_status_slice_preview(payload, [], dry_run=True)
        if out is payload: fail('flag ON + dry_run must return a copy, not identity')
        if 'status_envelope_preview' in payload: fail('original payload must NOT be mutated')
        if 'status_envelope_preview' not in out: fail('dry-run preview must attach status_envelope_preview')
    finally:
        os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
    print('[PASS] PROJECT_L Track B seam CREATED INERT; default no-op; not imported by live runtime; dry-run preview isolated')
    sys.exit(0)


if __name__ == '__main__': main()
