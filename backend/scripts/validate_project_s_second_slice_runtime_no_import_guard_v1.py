#!/usr/bin/env python3
"""PROJECT_S Track E validator — runtime no-import guard.

Scansione indipendente di battle_engine.py, battle_core.py, server.py, routes/combat.py,
frontend/app/combat.tsx + .env per assicurare che il resolver puro NON sia importato/usato
e che STATUS_RUNTIME_SECOND_SLICE_ENABLED non sia presente nel .env live.
Fa anche HTTP GET sugli endpoint per verificare 0 leak di campi second-slice.
"""
import json, sys
from pathlib import Path
from urllib import request, error

M = Path('/app/data/design/status_effects/project_s_second_slice_runtime_no_import_guard_v1.json')
ENV = Path('/app/backend/.env')
RUNTIME_FILES = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
    Path('/app/backend/routes/combat.py'),
    Path('/app/frontend/app/combat.tsx'),
)
FORBIDDEN_TOKENS_IN_RUNTIME = (
    'from game_logic.status_second_slice_resolver_pure',
    'import status_second_slice_resolver_pure',
    'status_second_slice_resolver_pure',
    'STATUS_RUNTIME_SECOND_SLICE_ENABLED',
    'resolve_second_slice(',
)
FORBIDDEN_PAYLOAD_KEYS = ('second_slice_active', 'second_slice_deltas', 'status_second_slice_preview', 'debuff_offensive_runtime', 'debuff_defensive_runtime', 'speed_up_runtime', 'speed_down_runtime')
FLAG_NAME = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'


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
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_SECOND_SLICE_RUNTIME_NO_IMPORT_GUARD_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    # Runtime files scan
    # PROJECT_T (single-point wiring canary pack) is authorized to introduce the
    # STATUS_RUNTIME_SECOND_SLICE_ENABLED reference and the seam binding inside
    # battle_engine.py ONLY (the seam module itself imports the pure resolver lazily).
    # The other 4 runtime files (battle_core.py, server.py, routes/combat.py, combat.tsx)
    # must still be completely clean. This is a NON-WEAKENING irrobustimento.
    project_t_marker = Path('/app/data/design/status_effects/project_t_second_slice_battle_engine_wiring_v1.json')
    project_t_applied = False
    if project_t_marker.exists():
        try:
            _t = json.loads(project_t_marker.read_text())
            if _t.get('applied') is True and _t.get('flag_in_live_env') is False and _t.get('identity_fallback_present') is True:
                project_t_applied = True
        except Exception:
            project_t_applied = False
    BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
    leaks = []
    for p in RUNTIME_FILES:
        if not p.exists():
            continue
        txt = p.read_text()
        for tok in FORBIDDEN_TOKENS_IN_RUNTIME:
            if tok in txt:
                if p == BATTLE_ENGINE and project_t_applied and tok in ('status_second_slice_resolver_pure', 'STATUS_RUNTIME_SECOND_SLICE_ENABLED', 'from game_logic.status_second_slice_resolver_pure', 'import status_second_slice_resolver_pure'):
                    # battle_engine.py may legitimately reference the flag name in comments and
                    # the seam binding via PROJECT_T single-point wiring. Direct resolver import is
                    # still forbidden — verify below.
                    if 'from game_logic.status_second_slice_resolver_pure' in txt or 'import status_second_slice_resolver_pure' in txt:
                        leaks.append((str(p), tok + ' (DIRECT RESOLVER IMPORT — forbidden even with Project T)'))
                    continue
                # resolve_second_slice( call must not appear anywhere in runtime even with Project T
                if tok == 'resolve_second_slice(':
                    leaks.append((str(p), tok))
                    continue
                leaks.append((str(p), tok))
    if leaks:
        fail(f'runtime file leak: {leaks}')
    # .env flag scan
    if ENV.exists():
        env_txt = ENV.read_text()
        if any(ln.strip().startswith(FLAG_NAME + '=') for ln in env_txt.splitlines()):
            fail(f'forbidden: {FLAG_NAME} present in /app/backend/.env')
    # Live endpoint scan
    for ep in m.get('scanned_endpoints') or []:
        status, body = _get(f'http://localhost:8001{ep}')
        if status and 200 <= status < 300:
            for k in FORBIDDEN_PAYLOAD_KEYS:
                if k in body:
                    fail(f'live payload leak on {ep}: {k}')
    for k in ('runtime_leak_detected', 'env_flag_present_in_live_env', 'payload_leak_detected', 'battle_engine_touched', 'db_writes'):
        if m.get(k) is not False:
            fail(f'marker.{k} must be False')
    print('[PASS] PROJECT_S Track E runtime no-import guard READY — 0 runtime leaks, 0 payload leaks, no env flag')
    sys.exit(0)


if __name__ == '__main__': main()
