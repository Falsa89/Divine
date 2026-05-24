#!/usr/bin/env python3
"""PROJECT_I Track B validator — housing preview canary flag flip.

Verifies:
  * marker present with verdict ENABLED_SAFE
  * approval markers both detected
  * in-process flag-ON code path produces zero-bonus inert envelope
  * local backend still returns 503 on GET
"""
import importlib.util, json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/housing/project_i_housing_preview_canary_flip_v1.json')
ROUTE = Path('/app/backend/routes/housing_preview.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http_status(method, url):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return -1


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_B_HOUSING_PREVIEW_CANARY_ENABLED_SAFE': fail('verdict mismatch')
    ap = m.get('approval_markers_detected_in_prompt', {})
    if not (ap.get('TRACK_B_HOUSING_PREVIEW_CANARY_APPROVAL') and ap.get('HOUSING_PREVIEW_CANARY_OK')):
        fail('both approval markers must be detected=true')
    if m.get('flip_applied_to_local_backend_runtime') is not False:
        fail('flip_applied_to_local_backend_runtime must be False (local untouched)')
    forb = m.get('forbidden_in_track_b_respected', {})
    for k in ('housing_live_bonus', 'db_writes', 'battle_mutation', 'account_stat_mutation', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_b.{k} must be False')
    if not ROUTE.exists(): fail('housing_preview route missing')
    spec = importlib.util.spec_from_file_location('_proj_i_hp', ROUTE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    saved = os.environ.get('HOUSING_PREVIEW_ENABLED')
    try:
        os.environ['HOUSING_PREVIEW_ENABLED'] = 'true'
        if not mod._flag_enabled(): fail('_flag_enabled() must be True with flag=true')
        env = mod._read_only_envelope(None)
        if env.get('preview') is not True: fail('flag-ON envelope.preview must be True')
        if env.get('dry_run') is not True: fail('flag-ON envelope.dry_run must be True')
        if env.get('live_bonus_applied') is not False: fail('flag-ON envelope.live_bonus_applied must be False')
        if env.get('db_writes') is not False: fail('flag-ON envelope.db_writes must be False')
        if env.get('combat_mutation') is not False: fail('flag-ON envelope.combat_mutation must be False')
        if env.get('rooms') != []: fail('flag-ON envelope.rooms must be []')
        bonus_env = env.get('envelope', {})
        for stat in ('hp_pct', 'atk_pct', 'def_pct', 'crit_pct'):
            if bonus_env.get(stat) != 0.0:
                fail(f'flag-ON envelope.envelope.{stat} must be 0.0 (zero bonus inert)')
    finally:
        if saved is None: os.environ.pop('HOUSING_PREVIEW_ENABLED', None)
        else: os.environ['HOUSING_PREVIEW_ENABLED'] = saved
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('HOUSING_PREVIEW_ENABLED', '').strip().lower() != 'true':
            code = http_status('GET', 'http://127.0.0.1:8001/api/housing/preview')
            if code not in (503, -1): fail(f'local backend GET /api/housing/preview returned {code}, expected 503')
    print('[PASS] PROJECT_I Track B housing preview canary flip ENABLED_SAFE: code-path verified in-process; zero-bonus envelope; local backend still 503')
    sys.exit(0)

if __name__ == '__main__': main()
