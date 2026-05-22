#!/usr/bin/env python3
"""SLC-F runtime safety audit (read-only)."""
from __future__ import annotations
import hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, finish, require, load  # noqa: E402

NAME = 'slc_f_runtime_safety_audit_v1'
ROUTES_DIR = Path('/app/backend/routes')
BASELINE_PATH = SLC_DIR / '_slc_c_critical_files_baseline_v1.json'
GUARDRAIL_FILE = SLC_DIR / 'slc_f_runtime_guardrail_policy_v1.json'
NEW_ROUTE_TOKENS = [
    '/api/server/enter', '/api/servers', '/api/account/server-profiles',
    '/api/account/server-profiles/select', '/api/account/active-server',
]


def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def any_route_defines(path_substr: str) -> list:
    if not ROUTES_DIR.exists():
        return []
    pat = re.compile(r"@(?:router|app)\.(?:get|post|put|delete|patch)\(\s*[\'\"]([^\'\"]+)[\'\"]")
    hits = []
    for f in ROUTES_DIR.rglob('*.py'):
        try:
            txt = f.read_text(errors='ignore')
        except Exception:
            continue
        for m in pat.finditer(txt):
            if path_substr in m.group(1):
                hits.append({'file': str(f), 'route': m.group(1)})
    return hits


def main() -> int:
    errs = []
    g = load(GUARDRAIL_FILE)
    # 1) Protected files match SLC-C baseline
    protected = g.get('protected_files', [])
    protected_status = {}
    if BASELINE_PATH.exists():
        base = json.loads(BASELINE_PATH.read_text())
        for f in protected:
            cur = sha256(Path(f))
            exp = base.get('hashes', {}).get(f)
            ok = (cur == exp) if exp else None
            protected_status[f] = {'current': cur, 'baseline': exp, 'match': ok}
            if exp and cur != exp:
                errs.append(f'CRITICAL FILE MUTATED: {f}')
    # 2) No future SLC-BE routes leaked
    route_hits = {}
    for tok in NEW_ROUTE_TOKENS:
        hits = any_route_defines(tok)
        route_hits[tok] = hits
        require(not hits, f'SLC-F: new route already declared in runtime: {tok} -> {hits}', errs)
    # 3) AF2-N markers intact
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    af2n_src = af2n.read_text() if af2n.exists() else ''
    require('50000' in af2n_src, 'AF2-N cap S2 50000 missing', errs)
    # 4) Feature flags unset
    for flag in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SECOND_SERVER_OPENING_ENABLED'):
        v = os.environ.get(flag)
        require(v in (None, '', '0', 'false', 'False'), f'{flag} unexpectedly set: {v}', errs)
    # 5) No SLC-F-created multishard collections in DB
    forbidden_cols_found = []
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        url = os.environ.get('MONGO_URL')
        if url:
            cli = MongoClient(url, serverSelectionTimeoutMS=2000)
            db_name = os.environ.get('DB_NAME') or 'divine_waifus'
            cols = cli[db_name].list_collection_names()
            cli.close()
            for c in ('server_profiles', 'servers', 'server_wallets_free',
                      'accounts_wallet_paid', 'accounts_wallet_paid_ledger'):
                if c in cols:
                    forbidden_cols_found.append(c)
    except Exception:
        pass
    require(not forbidden_cols_found, f'unexpected multishard collections in DB: {forbidden_cols_found}', errs)

    out = SLC_DIR / '_slc_f_runtime_safety_audit_v1_full_report.json'
    out.write_text(json.dumps({
        'task': NAME, 'mode': 'DESIGN_ONLY', 'utc': datetime.now(timezone.utc).isoformat(),
        'protected_files_status': protected_status,
        'route_hits_for_future_endpoints': route_hits,
        'af2n_cap_s2_marker_present': '50000' in af2n_src,
        'forbidden_multishard_collections_found': forbidden_cols_found,
        'route_patch_applied': False,
        'db_write': False,
    }, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, extra={
        'protected_files_match': all(s.get('match') in (True, None) for s in protected_status.values()),
        'route_patch_applied': False,
    })


if __name__ == '__main__':
    sys.exit(main())
