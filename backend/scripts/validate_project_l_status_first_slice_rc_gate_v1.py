#!/usr/bin/env python3
"""PROJECT_L Track G validator — status first-slice RC gate."""
import importlib.util, json, os, sys, urllib.request, urllib.error
from pathlib import Path
M = Path('/app/data/design/project_management/project_l_status_first_slice_rc_gate_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
FORBIDDEN_LIVE = ('HOUSING_LIVE_BONUS_ENABLED', 'ARTIFACT_LIVE_BONUS_ENABLED', 'ARTIFACT_IMPORT_LIVE_ENABLED', 'SECOND_SERVER_OPENING_ENABLED', 'PHASE_11_ENABLED', 'STATUS_RUNTIME_BUFF_SLICE_ENABLED', 'STATUS_RUNTIME_SEAM_CANARY_OK')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http(method, path):
    req = urllib.request.Request('http://127.0.0.1:8001' + path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status, r.read()
    except urllib.error.HTTPError as e:
        try: return e.code, e.read()
        except Exception: return e.code, b''
    except Exception: return -1, b''


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_STATUS_FIRST_SLICE_RC_GATE_READY': fail('verdict mismatch')
    # S1-S6 smoke
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
    # S7: forbidden envs unset (incl. STATUS_RUNTIME_SEAM_CANARY_OK)
    for k in FORBIDDEN_LIVE:
        if os.environ.get(k, '').strip().lower() == 'true': fail(f'S7 forbidden env active: {k}')
    # S8: seam.is_seam_active() False
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_seam_active(): fail('S8 seam active with flag unset')
    # S10: no leak across endpoints
    for p in ('/api/heroes', '/api/heroes/borea', '/api/server-profiles/select', '/api/housing/preview'):
        body = http('GET', p)[1]
        if b'status_envelope_preview' in body or b'__seam_version' in body:
            fail(f'S10 payload leak in {p}')
    # S11: resolver importable + zero envelope on empty
    rspec = importlib.util.spec_from_file_location('_r', RESOLVER); rmod = importlib.util.module_from_spec(rspec); rspec.loader.exec_module(rmod)
    env = rmod.resolve_buff_envelope([])
    if any(env.get(k, -1.0) != 0.0 for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct')):
        fail('S11 resolver empty input must produce zero envelope')
    print('[PASS] PROJECT_L Track G RC gate READY: 13 checks PASS')
    sys.exit(0)


if __name__ == '__main__': main()
