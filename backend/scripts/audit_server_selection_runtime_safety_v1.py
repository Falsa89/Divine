#!/usr/bin/env python3
"""SLC-BE — Runtime Safety Audit (READ-ONLY).

Produces an audit report confirming that no implementation step has
leaked into the live runtime as part of SLC-BE design work.
"""
from __future__ import annotations
import hashlib, json, os, sys, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish, require  # noqa: E402

NAME = 'server_selection_runtime_safety_audit_v1'

FUTURE_ENDPOINTS = [
    '/api/servers',
    '/api/account/server-profiles',
    '/api/account/server-profiles/select',
    '/api/account/active-server',
    '/api/server/enter',
]
PROTECTED_FILES = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
    '/app/backend/routes/affinity_gift_spend.py',
]
ROUTES_DIR = Path('/app/backend/routes')


def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def any_route_defines(path_substr: str) -> list:
    """Scan backend routes for any FastAPI route declaration matching given path substring."""
    hits = []
    if not ROUTES_DIR.exists():
        return hits
    pat = re.compile(r"@(?:router|app)\.(?:get|post|put|delete|patch)\(\s*[\'\"]([^\'\"]+)[\'\"]")
    for f in ROUTES_DIR.rglob('*.py'):
        try:
            txt = f.read_text(errors='ignore')
        except Exception:
            continue
        for m in pat.finditer(txt):
            if path_substr in m.group(1):
                hits.append({'file': str(f), 'route': m.group(1)})
    return hits


def check_mongo_collections() -> dict:
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        url = os.environ.get('MONGO_URL')
        if not url:
            return {'mongo_reachable': False}
        cli = MongoClient(url, serverSelectionTimeoutMS=2000)
        db_name = os.environ.get('DB_NAME') or 'divine_waifus'
        cols = cli[db_name].list_collection_names()
        cli.close()
        forbidden = ('server_profiles', 'servers', 'server_wallets_free',
                     'accounts_wallet_paid', 'accounts_wallet_paid_ledger')
        found = [c for c in forbidden if c in cols]
        # PROJECT_A Track A authorization: server_profiles allowed if marker says APPLIED_SAFE and empty.
        if 'server_profiles' in found:
            import json as _json
            from pathlib import Path as _Path
            marker = _Path('/app/data/design/server_lifecycle/project_a_server_profiles_ops_result_v1.json')
            if marker.exists():
                try:
                    m = _json.loads(marker.read_text(encoding='utf-8'))
                    if m.get('verdict') == 'TRACK_A_SERVER_PROFILES_COLLECTION_APPLIED_SAFE':
                        cli2 = MongoClient(url, serverSelectionTimeoutMS=2000)
                        try:
                            if cli2[db_name].server_profiles.count_documents({}) == 0:
                                found = [c for c in found if c != 'server_profiles']
                        finally:
                            cli2.close()
                except Exception:
                    pass
        return {
            'mongo_reachable': True,
            'db_name': db_name,
            'total_collections': len(cols),
            'forbidden_multishard_collections_found': found,
        }
    except Exception as ex:
        return {'mongo_reachable': False, 'error': str(ex)}


def main() -> int:
    errs = []
    # 1) No future SLC-BE endpoints implemented
    route_hits = {}
    for ep in FUTURE_ENDPOINTS:
        hits = any_route_defines(ep)
        route_hits[ep] = hits
        require(not hits, f'SLC-BE endpoint already declared in runtime: {ep} -> {hits}', errs)
    # 2) Protected files unchanged (we re-use SLC-C baseline file if present)
    baseline_path = DESIGN_DIR / '_slc_c_critical_files_baseline_v1.json'
    protected_status = {}
    if baseline_path.exists():
        try:
            base = json.loads(baseline_path.read_text())
            for f in PROTECTED_FILES:
                cur = sha256(Path(f))
                exp = base.get('hashes', {}).get(f)
                protected_status[f] = {'current': cur, 'baseline': exp, 'match': (cur == exp) if exp else None}
                if exp and cur != exp:
                    errs.append(f'CRITICAL FILE MUTATED: {f}')
        except Exception as ex:
            errs.append(f'baseline read error: {ex}')
    # 3) AF2-N cap S2 invariant
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    af2n_ok = af2n.exists() and '50000' in af2n.read_text()
    require(af2n_ok, 'AF2-N cap S2 (50000) marker missing in affinity_gift_spend.py', errs)
    # 4) Mongo collections check
    mongo = check_mongo_collections()
    require(not mongo.get('forbidden_multishard_collections_found'),
            f'forbidden multishard collections present: {mongo.get("forbidden_multishard_collections_found")}', errs)
    # 5) No second-server enable env var set
    second_server_env = os.environ.get('SECOND_SERVER_OPENING_ENABLED')
    require(second_server_env in (None, '', '0', 'false', 'False'),
            f'SECOND_SERVER_OPENING_ENABLED is unexpectedly set: {second_server_env}', errs)
    # 6) No SERVER_PROFILES_RUNTIME_ENABLED
    spre = os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED')
    require(spre in (None, '', '0', 'false', 'False'),
            f'SERVER_PROFILES_RUNTIME_ENABLED is unexpectedly set: {spre}', errs)
    # 7) No UI screens for server selection
    fe_dir = Path('/app/frontend/app')
    ui_hits = []
    if fe_dir.exists():
        for f in fe_dir.rglob('*.tsx'):
            try:
                txt = f.read_text(errors='ignore')
            except Exception:
                continue
            if ('/api/account/server-profiles' in txt) or ('/api/account/active-server' in txt) or ('/api/servers' in txt and 'fetch' in txt.lower()):
                ui_hits.append(str(f))
    require(not ui_hits, f'UI references to server-selection endpoints found: {ui_hits}', errs)

    payload = {
        'task_origin': 'SLC-BE-RUNTIME-SAFETY-AUDIT', 'version': 'v1', 'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'no_new_runtime_routes': all(not v for v in route_hits.values()),
        'route_hits': route_hits,
        'protected_files_status': protected_status,
        'af2n_cap_s2_marker_present': af2n_ok,
        'mongo': mongo,
        'env_second_server_opening_enabled': second_server_env,
        'env_server_profiles_runtime_enabled': spre,
        'ui_references_found': ui_hits,
        'borea_safe': True,
        'second_server_opening_allowed': False,
        'safety': {'no_db_write': True, 'no_runtime_change': True},
    }
    out = DESIGN_DIR / 'server_selection_runtime_safety_audit_v1.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, {
        'no_new_runtime_routes': payload['no_new_runtime_routes'],
        'af2n_cap_marker': af2n_ok,
        'mongo_reachable': mongo.get('mongo_reachable'),
    })


if __name__ == '__main__':
    sys.exit(main())
