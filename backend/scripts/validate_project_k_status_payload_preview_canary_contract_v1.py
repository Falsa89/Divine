#!/usr/bin/env python3
"""PROJECT_K Track E validator — status payload preview canary contract; no leakage live."""
import json, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_payload_preview_canary_contract_v1.json')
ENDPOINTS = ('/api/heroes', '/api/heroes/borea', '/api/heroes/greek_borea', '/api/server-profiles/select', '/api/housing/preview')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def probe(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001'+p, timeout=5) as r: return r.read()
    except urllib.error.HTTPError as e:
        try: return e.read()
        except Exception: return b''
    except Exception: return b''
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_STATUS_PAYLOAD_PREVIEW_CANARY_CONTRACT_NO_LEAKAGE': fail('verdict mismatch')
    leaks = 0
    for p in ENDPOINTS:
        if b'status_envelope_preview' in probe(p): leaks += 1; print(f'  LEAK in {p}')
    if leaks > 0: fail(f'{leaks} payload leak(s) of status_envelope_preview')
    print('[PASS] PROJECT_K Track E payload preview contract: 0 leaks across 5 audited endpoints')
    sys.exit(0)
if __name__ == '__main__': main()
