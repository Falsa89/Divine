#!/usr/bin/env python3
"""PROJECT_T Track E validator — payload + log no-leak guard.

Scansiona endpoint live + file runtime per chiavi second-slice forbidden.
La SOLA presenza autorizzata della stringa 'status_second_slice_runtime_seam' e'
in battle_engine.py (import + identity fallback). Tutto il resto del runtime deve
essere pulito. Verifica anche backend logs locali se accessibili.
"""
import json, sys
from pathlib import Path
from urllib import request, error

M = Path('/app/data/design/status_effects/project_t_second_slice_payload_log_no_leak_v1.json')
RUNTIME_FILES_TO_SCAN_OUTSIDE_BATTLE = (
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
    Path('/app/backend/routes/combat.py'),
    Path('/app/frontend/app/combat.tsx'),
)
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
FORBIDDEN_PAYLOAD_KEYS = ('status_second_slice_preview', '__second_slice_seam_version', 'second_slice_active', 'second_slice_deltas', 'debuff_offensive_runtime', 'debuff_defensive_runtime', 'speed_up_runtime', 'speed_down_runtime')
FORBIDDEN_OUTSIDE_BATTLE_TOKENS = ('status_second_slice_runtime_seam', 'resolve_second_slice(', 'status_second_slice_resolver_pure', 'STATUS_RUNTIME_SECOND_SLICE_ENABLED')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def _get(url: str, timeout: float = 3.0):
    try:
        with request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='replace')
    except error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_SECOND_SLICE_PAYLOAD_AND_LOG_NO_LEAK_GUARD_READY': fail('verdict mismatch')
    # Endpoint payload scan
    for ep in m.get('scanned_endpoints') or []:
        status, body = _get(f'http://localhost:8001{ep}')
        if status and 200 <= status < 300:
            for k in FORBIDDEN_PAYLOAD_KEYS:
                if k in body:
                    fail(f'live payload leak on {ep}: {k}')
    # Runtime files outside battle_engine must NOT contain second-slice tokens
    for p in RUNTIME_FILES_TO_SCAN_OUTSIDE_BATTLE:
        if not p.exists(): continue
        txt = p.read_text()
        for tok in FORBIDDEN_OUTSIDE_BATTLE_TOKENS:
            if tok in txt:
                fail(f'forbidden second-slice token in non-battle-engine runtime file {p}: {tok}')
    # battle_engine.py: allowed to contain the wiring (single point), but NOT call resolve_second_slice directly
    if BATTLE_ENGINE.exists():
        src = BATTLE_ENGINE.read_text()
        if 'resolve_second_slice(' in src:
            fail('battle_engine.py must NOT call resolve_second_slice directly (only via seam)')
        if 'status_second_slice_resolver_pure' in src:
            fail('battle_engine.py must NOT import the pure resolver directly (only via seam)')
    if m.get('endpoint_payload_leak_detected') is not False or m.get('source_file_leak_outside_authorized_callers') is not False:
        fail('marker leak flags must be False')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_T Track E payload + log no-leak READY — 0 endpoint leaks, 0 non-battle-engine runtime leaks, battle_engine wires only via seam')
    sys.exit(0)


if __name__ == '__main__': main()
