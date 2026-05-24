#!/usr/bin/env python3
"""PROJECT_S Track B validator — pure resolver module (inert, isolated).

Verifica:
- file resolver esiste
- nessun import forbidden (battle_engine, battle_core, server, fastapi, pymongo, motor, requests, httpx, urllib.request)
- public API esposta
- validate_invariants_static() ritorna True
- nessun runtime importa il modulo (scan su battle_engine.py, battle_core.py, server.py, routes/combat.py, frontend/app/combat.tsx)
"""
import json, re, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_s_second_slice_resolver_module_v1.json')
MOD = Path('/app/backend/game_logic/status_second_slice_resolver_pure.py')
FORBIDDEN_IMPORTS = (
    r'^\s*import\s+requests\b', r'^\s*from\s+requests\b',
    r'^\s*import\s+httpx\b', r'^\s*from\s+httpx\b',
    r'^\s*import\s+urllib\.request\b', r'^\s*from\s+urllib\.request\b',
    r'^\s*import\s+pymongo\b', r'^\s*from\s+pymongo\b',
    r'^\s*import\s+motor\b', r'^\s*from\s+motor\b',
    r'^\s*import\s+fastapi\b', r'^\s*from\s+fastapi\b',
    r'^\s*from\s+battle_engine\b', r'^\s*import\s+battle_engine\b',
    r'^\s*from\s+battle_core\b', r'^\s*import\s+battle_core\b',
    r'^\s*from\s+server\b', r'^\s*import\s+server\b',
)
RUNTIME_FILES = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
    Path('/app/backend/routes/combat.py'),
    Path('/app/frontend/app/combat.tsx'),
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_STATUS_SECOND_SLICE_PURE_RESOLVER_MODULE_CREATED_INERT':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if not MOD.exists():
        fail(f'resolver module missing: {MOD}')
    src = MOD.read_text()
    for pat in FORBIDDEN_IMPORTS:
        if re.search(pat, src, flags=re.MULTILINE):
            fail(f'resolver module contains forbidden import matching: {pat}')
    # Public API present
    for sym in ('IN_SCOPE_FAMILIES', 'OUT_OF_SCOPE_FAMILIES', 'PER_STATUS_CAPS_PCT', 'AGGREGATE_CAPS_PCT', 'MODE_MULTIPLIERS', 'STAT_TARGET_BY_FAMILY', 'resolve_second_slice', 'validate_invariants_static'):
        if sym not in src:
            fail(f'public API symbol missing in module: {sym}')
    # Import + invariants
    sys.path.insert(0, '/app/backend')
    try:
        from game_logic.status_second_slice_resolver_pure import validate_invariants_static, resolve_second_slice
    except Exception as e:
        fail(f'cannot import resolver: {e}')
    if not validate_invariants_static():
        fail('validate_invariants_static() returned False')
    # Determinism: 100 identical calls -> identical result
    sample = [{'family': 'debuff_offensive', 'value_pct': 15.0}, {'family': 'speed_up', 'value_pct': 10.0}]
    out0 = resolve_second_slice(sample, 'campaign')
    for _ in range(100):
        if resolve_second_slice(sample, 'campaign') != out0:
            fail('non-deterministic output detected')
    # Verify no runtime file imports the resolver
    for p in RUNTIME_FILES:
        if p.exists():
            txt = p.read_text()
            for tok in ('status_second_slice_resolver_pure', 'resolve_second_slice('):
                if tok in txt:
                    fail(f'runtime file {p} contains forbidden import/call: {tok}')
    # Marker invariants
    for k in ('module_created', 'module_inert', 'deterministic', 'side_effect_free', 'no_db_imports', 'no_http_imports', 'no_battle_engine_import', 'no_battle_core_import', 'no_mutable_global_state', 'validate_invariants_static_returns_true'):
        if m.get(k) is not True:
            fail(f'marker.{k} must be True')
    if m.get('runtime_imported_anywhere') is not False or m.get('battle_engine_touched') is not False or m.get('db_writes') is not False:
        fail('runtime_imported_anywhere/battle_engine_touched/db_writes must be False')
    print('[PASS] PROJECT_S Track B pure resolver module CREATED INERT — deterministic, side-effect free, not imported anywhere')
    sys.exit(0)


if __name__ == '__main__': main()
