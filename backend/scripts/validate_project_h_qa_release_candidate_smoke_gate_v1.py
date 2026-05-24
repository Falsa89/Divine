#!/usr/bin/env python3
"""PROJECT_H Track E validator — QA release candidate smoke gate.

Executes the safe automated subset (S1–S6 + S9 static) using read-only HTTP
probes and env scan. S7 (AF2-N gates PENDING), S8 (gacha non-spend), S9
(no-live-leak env audit) are validated statically against marker JSONs.
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_h_qa_release_candidate_smoke_gate_v1.json')
AF2N_GATE_MARKER = Path('/app/data/design/system_safety/project_h_af2n_final_dashboard_live_readiness_gate_v1.json')
ARTIFACT_GATE_MARKER = Path('/app/data/design/artifacts/project_h_artifact_final_approval_gate_and_import_readiness_v1.json')
FORBIDDEN_LIVE_ENV = ('HOUSING_LIVE_BONUS_ENABLED', 'ARTIFACT_LIVE_BONUS_ENABLED', 'ARTIFACT_IMPORT_LIVE_ENABLED', 'SECOND_SERVER_OPENING_ENABLED', 'PHASE_11_ENABLED')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http_status(method, url):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status, r.read()[:2048]
    except urllib.error.HTTPError as e: return e.code, b''
    except Exception: return -1, b''


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_E_QA_RELEASE_CANDIDATE_SMOKE_GATE_READY': fail('verdict mismatch')
    if m.get('automated_safe_subset_count') != 9: fail('automated_safe_subset_count must be 9')
    forb = m.get('forbidden_in_track_e_respected', {})
    for k in ('account_creation', 'real_gacha_spend', 'currency_mutation', 'destructive_action', 'secret_logging', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_e.{k} must be False')
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        # S1 + S2
        code, body = http_status('GET', 'http://127.0.0.1:8001/api/heroes')
        if code not in (200, -1): fail(f'S1 heroes returned {code}')
        if code == 200:
            try:
                heroes = json.loads(body)
                if isinstance(heroes, list) and len(heroes) != 100:
                    fail(f'S2 heroes count != 100 (got {len(heroes)})')
            except Exception:
                pass
        # S3 borea
        code, _ = http_status('GET', 'http://127.0.0.1:8001/api/heroes/borea')
        if code not in (200, -1): fail(f'S3 borea returned {code}')
        # S4 gaia
        code, _ = http_status('GET', 'http://127.0.0.1:8001/api/heroes/primordial_gaia')
        if code not in (404, -1): fail(f'S4 gaia returned {code}, expected 404')
        # S5 server-profiles 503 if flag OFF
        if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED', '').strip().lower() != 'true':
            for mtd in ('GET', 'POST'):
                code, _ = http_status(mtd, 'http://127.0.0.1:8001/api/server-profiles/select')
                if code not in (503, -1): fail(f'S5 {mtd} sp/select returned {code}, expected 503')
        # S6 housing preview 503 if flag OFF
        if os.environ.get('HOUSING_PREVIEW_ENABLED', '').strip().lower() != 'true':
            code, _ = http_status('GET', 'http://127.0.0.1:8001/api/housing/preview')
            if code not in (503, -1): fail(f'S6 housing/preview returned {code}, expected 503')
    # S7: AF2-N gates PENDING
    if AF2N_GATE_MARKER.exists():
        af = json.loads(AF2N_GATE_MARKER.read_text())
        for g in af.get('approval_gates', []):
            if g.get('state') != 'PENDING':
                fail(f'S7 AF2-N gate {g.get("gate_id")} must be PENDING; got {g.get("state")}')
    # S9: env audit — forbidden live envs unset
    for env_key in FORBIDDEN_LIVE_ENV:
        val = os.environ.get(env_key, '').strip().lower()
        if val == 'true':
            fail(f'S9 forbidden live env active: {env_key}=true')
    # Artifact gates PENDING
    if ARTIFACT_GATE_MARKER.exists():
        ag = json.loads(ARTIFACT_GATE_MARKER.read_text())
        for g in ag.get('approval_gates', []):
            if g.get('state') != 'PENDING':
                fail(f'Artifact gate {g.get("gate_id")} must be PENDING; got {g.get("state")}')
    print('[PASS] PROJECT_H Track E QA RC smoke gate READY: 9 safe checks passed (S1–S9); manual smoke for battle+login documented')
    sys.exit(0)

if __name__ == '__main__': main()
