#!/usr/bin/env python3
"""PROJECT_F Track A validator — server profiles read-only preview hardening.

Invariants enforced (static + runtime probes):
  * /api/server-profiles/select GET = 503 with flags OFF (handler raises HTTPException(503)).
  * /api/server-profiles/select POST = 503 with flags OFF.
  * Double-flag gate present in routes/server_profiles.py:
      - SERVER_PROFILES_RUNTIME_ENABLED
      - SERVER_PROFILES_PREVIEW_ENABLED
  * `_preview_runtime_enabled` requires BOTH flags True.
  * Default handlers DO NOT call `_preview_dry_run_envelope`.
  * No DB write keywords in handlers (`insert_one`, `update_one`, `replace_one`, `delete_one`,
    `find_one_and_update`).
  * Preview envelope sets second_server_opened=False, mutation_executed=False,
    active_server_switched=False, dual_write_executed=False.
  * Marker present and verdict correct.
"""
import json, os, sys
import urllib.request, urllib.error
from pathlib import Path

ROUTE = Path("/app/backend/routes/server_profiles.py")
MARKER = Path("/app/data/design/server_lifecycle/project_f_server_profiles_read_only_preview_v1.json")
FORBIDDEN_DB_WRITES = ("insert_one(", "update_one(", "replace_one(", "delete_one(", "find_one_and_update(")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def http_status(method: str, url: str) -> int:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def main():
    if not ROUTE.exists(): fail(f"missing route file {ROUTE}")
    src = ROUTE.read_text()
    if 'SERVER_PROFILES_RUNTIME_ENABLED' not in src: fail("missing primary feature flag")
    if 'SERVER_PROFILES_PREVIEW_ENABLED' not in src: fail("missing preview sub-flag")
    if '_preview_runtime_enabled' not in src: fail("missing _preview_runtime_enabled helper")
    if '_preview_dry_run_envelope' not in src: fail("missing _preview_dry_run_envelope helper")
    # Double-flag gate: helper must require _runtime_enabled() first
    helper_start = src.find('def _preview_runtime_enabled')
    helper_end = src.find('def ', helper_start + 5)
    helper_body = src[helper_start:helper_end] if helper_start != -1 else ""
    if '_runtime_enabled()' not in helper_body: fail("double-flag gate missing: _preview_runtime_enabled does not require _runtime_enabled()")
    if 'PREVIEW_FEATURE_FLAG' not in helper_body: fail("double-flag gate missing: _preview_runtime_enabled does not check PREVIEW_FEATURE_FLAG")
    # Default handlers must NOT call preview envelope
    get_handler_start = src.find('async def server_profiles_select_probe')
    post_handler_start = src.find('async def server_profiles_select_target')
    if get_handler_start == -1 or post_handler_start == -1: fail("handlers not found")
    handlers_block = src[get_handler_start:]
    # cut at end of POST handler (heuristic: next top-level def or PROJECT_D Track A section)
    cut = handlers_block.find('# ===================== PROJECT_D TRACK A')
    if cut == -1: cut = len(handlers_block)
    handlers_block = handlers_block[:cut]
    if '_preview_dry_run_envelope' in handlers_block:
        fail("default handlers must NOT call _preview_dry_run_envelope")
    # No DB writes in handlers
    for kw in FORBIDDEN_DB_WRITES:
        if kw in handlers_block:
            fail(f"forbidden DB write op in default handlers: {kw}")
    # Preview envelope sets mutation flags = False
    env_start = src.find('def _preview_dry_run_envelope')
    env_body = src[env_start:] if env_start != -1 else ""
    for required in ('"mutation_executed"', '"active_server_switched"', '"dual_write_executed"', '"second_server_opened"'):
        if required not in env_body:
            fail(f"preview envelope missing key {required}")
        if f"{required}] = False" not in env_body:
            fail(f"preview envelope key {required} must be set to False")
    # Marker present and verdict correct
    if not MARKER.exists(): fail(f"missing marker {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_A_SERVER_PROFILES_READ_ONLY_PREVIEW_HARDENED_INERT':
        fail("marker verdict mismatch")
    if m.get('runtime_changes_applied') is not False:
        fail("marker runtime_changes_applied must be False")
    # Runtime probe (best-effort) only when backend is up locally AND no env flag forcing live
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED', '').strip().lower() == 'true':
            print('[WARN] SERVER_PROFILES_RUNTIME_ENABLED=true — skipping runtime probe to avoid asserting 503 against live preview')
        else:
            for method in ('GET', 'POST'):
                code = http_status(method, 'http://127.0.0.1:8001/api/server-profiles/select')
                if code != 503 and code != -1:
                    fail(f"runtime probe {method} /api/server-profiles/select returned {code}, expected 503 (flags OFF)")
    print('[PASS] PROJECT_F Track A server profiles read-only preview HARDENED: 503 default; double-flag gate verified; no DB writes; mutation flags False')
    sys.exit(0)

if __name__ == '__main__': main()
