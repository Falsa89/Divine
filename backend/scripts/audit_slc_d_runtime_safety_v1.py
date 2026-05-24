#!/usr/bin/env python3
"""Runtime safety audit for SLC-D (read-only)."""
from __future__ import annotations
import hashlib, json, os, sys, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, finish, require  # noqa: E402

NAME = 'slc_d_runtime_safety_audit_v1'
PROTECTED = [
    '/app/backend/battle_engine.py', '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx', '/app/backend/routes/affinity_gift_spend.py',
    '/app/backend/routes/heroes.py',
]
BASELINE = SLC_DIR / '_slc_c_critical_files_baseline_v1.json'
ROUTES = Path('/app/backend/routes')
MERGE_TOKENS = [
    '/api/admin/merge', '/api/merge/execute', '/api/server/merge',
    '/api/account/server-profiles', '/api/account/active-server', '/api/server/enter',
]


def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def route_hits(tok):
    if not ROUTES.exists():
        return []
    pat = re.compile(r"@(?:router|app)\.(?:get|post|put|delete|patch)\(\s*[\'\"]([^\'\"]+)[\'\"]")
    hits = []
    for f in ROUTES.rglob('*.py'):
        try:
            txt = f.read_text(errors='ignore')
        except Exception:
            continue
        for m in pat.finditer(txt):
            if tok in m.group(1):
                hits.append({'file': str(f), 'route': m.group(1)})
    return hits


def main() -> int:
    errs = []
    protected_status = {}
    if BASELINE.exists():
        base = json.loads(BASELINE.read_text())
        for f in PROTECTED:
            cur = sha256(Path(f))
            exp = base.get('hashes', {}).get(f)
            ok = (cur == exp) if exp else None
            protected_status[f] = {'match': ok}
            if exp and cur != exp:
                errs.append(f'CRITICAL FILE MUTATED: {f}')
    merge_route_hits = {}
    for tok in MERGE_TOKENS:
        h = route_hits(tok)
        merge_route_hits[tok] = h
        require(not h, f'merge runtime route detected: {tok} -> {h}', errs)
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    af2n_src = af2n.read_text() if af2n.exists() else ''
    require('50000' in af2n_src, 'AF2-N cap S2 50000 missing', errs)
    for flag in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SECOND_SERVER_OPENING_ENABLED', 'MERGE_RUNTIME_ENABLED'):
        v = os.environ.get(flag)
        require(v in (None, '', '0', 'false', 'False'), f'{flag} unexpectedly set: {v}', errs)
    forbidden_cols = []
    sp_doc_count = 0
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        url = os.environ.get('MONGO_URL')
        if url:
            cli = MongoClient(url, serverSelectionTimeoutMS=2000)
            db_name = os.environ.get('DB_NAME') or 'divine_waifus'
            cols = cli[db_name].list_collection_names()
            if 'server_profiles' in cols:
                sp_doc_count = cli[db_name].server_profiles.count_documents({})
            cli.close()
            for c in ('server_profiles','servers','server_wallets_free','accounts_wallet_paid',
                      'accounts_wallet_paid_ledger','server_merge_audit','merge_recovery_pool'):
                if c in cols:
                    forbidden_cols.append(c)
            # PROJECT_A Track A authorization: server_profiles allowed if APPLIED_SAFE marker + empty.
            if 'server_profiles' in forbidden_cols and sp_doc_count == 0:
                _marker = Path('/app/data/design/server_lifecycle/project_a_server_profiles_ops_result_v1.json')
                if _marker.exists():
                    try:
                        _m = json.loads(_marker.read_text(encoding='utf-8'))
                        if _m.get('verdict') == 'TRACK_A_SERVER_PROFILES_COLLECTION_APPLIED_SAFE':
                            forbidden_cols = [c for c in forbidden_cols if c != 'server_profiles']
                    except Exception:
                        pass
    except Exception:
        pass
    require(not forbidden_cols, f'unexpected runtime collections present: {forbidden_cols}', errs)
    out = SLC_DIR / '_slc_d_runtime_safety_audit_v1_full_report.json'
    out.write_text(json.dumps({
        'task': NAME, 'mode': 'DESIGN_ONLY', 'utc': datetime.now(timezone.utc).isoformat(),
        'protected_files_status': protected_status,
        'merge_route_hits': merge_route_hits,
        'af2n_cap_s2_marker_present': '50000' in af2n_src,
        'forbidden_collections_found': forbidden_cols,
        'merge_execution_allowed': False, 'db_write': False,
    }, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, extra={
        'protected_files_match': all(s.get('match') in (True, None) for s in protected_status.values()),
    })


if __name__ == '__main__':
    sys.exit(main())
