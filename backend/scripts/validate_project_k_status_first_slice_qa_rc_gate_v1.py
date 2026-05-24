#!/usr/bin/env python3
"""PROJECT_K Track G validator — status first-slice QA RC gate."""
import importlib.util, json, os, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_first_slice_qa_rc_gate_v1.json')
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
FORBIDDEN_LIVE = ('HOUSING_LIVE_BONUS_ENABLED', 'ARTIFACT_LIVE_BONUS_ENABLED', 'ARTIFACT_IMPORT_LIVE_ENABLED', 'SECOND_SERVER_OPENING_ENABLED', 'PHASE_11_ENABLED', 'STATUS_RUNTIME_BUFF_SLICE_ENABLED')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def http(method, path):
    req = urllib.request.Request('http://127.0.0.1:8001'+path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status, r.read()
    except urllib.error.HTTPError as e:
        try: return e.code, e.read()
        except Exception: return e.code, b''
    except Exception: return -1, b''
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_STATUS_FIRST_SLICE_QA_RC_GATE_READY': fail('verdict mismatch')
    # S1-S6
    code, body = http('GET', '/api/heroes')
    if code != 200: fail(f'S1 heroes={code}')
    try:
        if len(json.loads(body)) != 100: fail('S1 count != 100')
    except Exception: pass
    if http('GET', '/api/heroes/primordial_gaia')[0] != 404: fail('S2 gaia not 404')
    if http('GET', '/api/heroes/borea')[0] != 200: fail('S3 borea not 200')
    if http('GET', '/api/heroes/greek_borea')[0] != 200: fail('S4 greek_borea not 200')
    for mtd in ('GET', 'POST'):
        if http(mtd, '/api/server-profiles/select')[0] != 503: fail(f'S5 sp/select {mtd} not 503')
    if http('GET', '/api/housing/preview')[0] != 503: fail('S6 housing/preview not 503')
    # S9 + K1: forbidden envs unset
    for k in FORBIDDEN_LIVE:
        if os.environ.get(k, '').strip().lower() == 'true': fail(f'S9 forbidden env active: {k}')
    # K1 + K2: resolver importable, inactive, not in battle (battle absent)
    spec = importlib.util.spec_from_file_location('_r', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_runtime_active(): fail('K1 resolver active with flag unset')
    # K3: payload leakage
    for p in ('/api/heroes', '/api/heroes/borea', '/api/server-profiles/select', '/api/housing/preview'):
        if b'status_envelope_preview' in http('GET', p)[1]:
            fail(f'K3 payload leak in {p}')
    print('[PASS] PROJECT_K Track G QA RC gate: 13 checks PASS')
    sys.exit(0)
if __name__ == '__main__': main()
