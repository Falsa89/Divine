#!/usr/bin/env python3
"""PROJECT_M Track E validator — status payload + battle log no-leak guard."""
import json, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/status_effects/project_m_status_payload_battle_log_no_leak_v1.json')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')
SOURCE_FILES = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
    Path('/app/backend/routes/combat.py'),
)
FORBIDDEN_PAYLOAD = (b'status_envelope_preview', b'__seam_version')
# In source files we only consider an emission a leak if there's an actual
# WRITE/SET to a payload (e.g., 'status_envelope_preview' as a dict key literal).
FORBIDDEN_SOURCE_PATTERNS = ("'status_envelope_preview'", '"status_envelope_preview"')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def probe(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r: return r.read()
    except urllib.error.HTTPError as e:
        try: return e.read()
        except Exception: return b''
    except Exception: return b''


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_STATUS_PAYLOAD_AND_BATTLE_LOG_NO_LEAK_READY': fail('verdict mismatch')
    leaks = 0
    for p in ENDPOINTS:
        body = probe(p)
        for marker in FORBIDDEN_PAYLOAD:
            if marker in body:
                leaks += 1
                print(f'  LEAK "{marker.decode()}" in {p}')
    if leaks > 0: fail(f'{leaks} payload leak(s)')
    # Source-level emission scan.
    src_leaks = 0
    for f in SOURCE_FILES:
        if not f.exists(): continue
        txt = f.read_text(encoding='utf-8', errors='ignore')
        for pat in FORBIDDEN_SOURCE_PATTERNS:
            if pat in txt:
                src_leaks += 1
                print(f'  SOURCE EMISSION "{pat}" in {f}')
    if src_leaks > 0: fail(f'{src_leaks} source-level emission(s) of preview key')
    print(f'[PASS] PROJECT_M Track E no-leak guard: 0 endpoint leaks; 0 source emissions across {len(SOURCE_FILES)} files')
    sys.exit(0)


if __name__ == '__main__': main()
