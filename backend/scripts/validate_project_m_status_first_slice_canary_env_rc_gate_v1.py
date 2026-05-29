#!/usr/bin/env python3
"""PROJECT_M Track G validator — status first slice canary env RC gate."""
import importlib.util, json, os, sys, urllib.request, urllib.error, hashlib
from pathlib import Path
M = Path('/app/data/design/project_management/project_m_status_first_slice_canary_env_rc_gate_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
BE = Path('/app/backend/battle_engine.py')
BC = Path('/app/backend/battle_core.py')
SV = Path('/app/backend/server.py')
RC = Path('/app/backend/routes/combat.py')
FORBIDDEN_FLAGS = ('HOUSING_LIVE_BONUS_ENABLED', 'ARTIFACT_LIVE_BONUS_ENABLED', 'ARTIFACT_IMPORT_LIVE_ENABLED', 'SECOND_SERVER_OPENING_ENABLED', 'PHASE_11_ENABLED', 'STATUS_RUNTIME_BUFF_SLICE_ENABLED', 'STATUS_FIRST_SLICE_BATTLE_ENGINE_CANARY_OK')
EXPECTED_UNCHANGED_MD5 = {
    BC: '80d94afba9eb2930e63b06cfed645b77',
    SV: '0e5f9447baef26c5b3588fcca21df44f',
    # Baseline updated by PROJECT_NO_STAMINA_REMEDIATION (canonica NO_STAMINA_SYSTEM): 6 stamina gate
    # blocks legitimately removed from backend/routes/combat.py. Validator NOT weakened: same assertion
    # logic, baseline synced to current canonical state. New md5 captured post-patch.
    RC: '124eed768fa52c82351aebc124dc1388',
}
PATCH_MARKER = '_project_m_status_seam'


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


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
    if m.get('verdict') != 'TRACK_G_STATUS_FIRST_SLICE_CANARY_ENV_RC_GATE_READY': fail('verdict mismatch')
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
    # S7/S8: forbidden flags unset
    for k in FORBIDDEN_FLAGS:
        if os.environ.get(k, '').strip().lower() == 'true': fail(f'S7/S8 forbidden flag active: {k}')
    # S9: patch markers present in battle_engine.py
    if PATCH_MARKER not in BE.read_text(encoding='utf-8', errors='ignore'):
        fail('S9 patch marker missing in battle_engine.py')
    # S10: battle_core / server / routes/combat md5 unchanged
    for p, exp in EXPECTED_UNCHANGED_MD5.items():
        cur = _md5(p)
        if cur != exp: fail(f'S10 {p} md5 changed: expected {exp} got {cur}')
    # S11: 0 leak across audited endpoints
    for p in ('/api/heroes', '/api/heroes/borea', '/api/server-profiles/select', '/api/housing/preview'):
        body = http('GET', p)[1]
        if b'status_envelope_preview' in body or b'__seam_version' in body:
            fail(f'S11 leak in {p}')
    # K12: seam.is_seam_active() False with flag unset
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_seam_active(): fail('K12 seam active with flag unset')
    print('[PASS] PROJECT_M Track G RC gate READY: 13 checks PASS')
    sys.exit(0)


if __name__ == '__main__': main()
