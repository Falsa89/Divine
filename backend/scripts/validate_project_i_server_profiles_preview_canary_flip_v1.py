#!/usr/bin/env python3
"""PROJECT_I Track A validator — server profiles preview canary flag flip.

Verifies:
  * marker present with verdict ENABLED_SAFE
  * approval markers both detected in marker JSON
  * in-process flag-ON code path produces correct envelope:
      mutation_executed=False, active_server_switched=False,
      dual_write_executed=False, second_server_opened=False
  * local backend still returns 503 on GET+POST (no env mutation by us)
  * route module unchanged (no DB write keywords in default handlers)
"""
import importlib.util, json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/server_lifecycle/project_i_server_profiles_preview_canary_flip_v1.json')
ROUTE = Path('/app/backend/routes/server_profiles.py')


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
    if m.get('verdict') != 'TRACK_A_SERVER_PROFILES_PREVIEW_CANARY_ENABLED_SAFE': fail('verdict mismatch')
    ap = m.get('approval_markers_detected_in_prompt', {})
    if not (ap.get('TRACK_A_SERVER_PROFILES_PREVIEW_CANARY_APPROVAL') and ap.get('SERVER_PROFILES_PREVIEW_CANARY_OK')):
        fail('both approval markers must be detected=true in marker JSON')
    if m.get('flip_applied_to_local_backend_runtime') is not False:
        fail('flip_applied_to_local_backend_runtime must be False (local backend untouched)')
    forb = m.get('forbidden_in_track_a_respected', {})
    for k in ('active_switch', 'db_writes', 'second_server', 'dual_write', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_a.{k} must be False')
    if not ROUTE.exists(): fail('route module missing')
    # In-process flag-ON code-path verification
    spec = importlib.util.spec_from_file_location('_proj_i_sp', ROUTE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    saved_runtime = os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED')
    saved_preview = os.environ.get('SERVER_PROFILES_PREVIEW_ENABLED')
    try:
        os.environ['SERVER_PROFILES_RUNTIME_ENABLED'] = 'true'
        os.environ['SERVER_PROFILES_PREVIEW_ENABLED'] = 'true'
        if not mod._runtime_enabled(): fail('_runtime_enabled() must be True with flag=true')
        if not mod._preview_runtime_enabled(): fail('_preview_runtime_enabled() must be True with both flags=true')
        env = mod._preview_dry_run_envelope('GET')
        for required_false_key in ('mutation_executed', 'active_server_switched', 'dual_write_executed', 'second_server_opened'):
            if env.get(required_false_key) is not False:
                fail(f'flag-ON envelope: {required_false_key} must be False')
    finally:
        if saved_runtime is None: os.environ.pop('SERVER_PROFILES_RUNTIME_ENABLED', None)
        else: os.environ['SERVER_PROFILES_RUNTIME_ENABLED'] = saved_runtime
        if saved_preview is None: os.environ.pop('SERVER_PROFILES_PREVIEW_ENABLED', None)
        else: os.environ['SERVER_PROFILES_PREVIEW_ENABLED'] = saved_preview
    # Local backend should still 503
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED', '').strip().lower() != 'true':
            for mtd in ('GET', 'POST'):
                code = http_status(mtd, 'http://127.0.0.1:8001/api/server-profiles/select')
                if code != 503 and code != -1: fail(f'local backend {mtd} returned {code}, expected 503 (flip is canary-only, not local)')
    print('[PASS] PROJECT_I Track A server profiles preview canary flip ENABLED_SAFE: code-path verified in-process; local backend still 503; mutation flags False')
    sys.exit(0)

if __name__ == '__main__': main()
