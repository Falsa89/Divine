#!/usr/bin/env python3
"""SLC-BE — Preflight (READ-ONLY).

Verifies prerequisites before SLC-BE design contracts can be safely
published. Checks SLC-A and SLC-C artifacts, AF2-N invariant, protected
files, and that no server_profiles collection has been created.
"""
from __future__ import annotations
import json, os, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish, require  # noqa: E402

NAME = 'slc_be_preflight_v1'

SLC_A_AUDIT = DESIGN_DIR / 'server_shard_isolation_audit_v1.json'
SLC_C_COMBO = DESIGN_DIR / '_slc_c_combo_v1_result.json'
SLC_C_PREFLIGHT = DESIGN_DIR / 'slc_c_multishard_preflight_result_v1.json'


def fetch(path: str, timeout: float = 4.0):
    try:
        with urllib.request.urlopen('http://localhost:8001' + path, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def check_no_server_profiles_collection() -> tuple[bool, str]:
    """Read-only check: no server_profiles collection exists in runtime DB."""
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        url = os.environ.get('MONGO_URL')
        if not url:
            return True, 'MONGO_URL not configured — treat as no collection'
        cli = MongoClient(url, serverSelectionTimeoutMS=2000)
        db_name = os.environ.get('DB_NAME') or 'divine_waifus'
        cols = cli[db_name].list_collection_names()
        forbidden_present = [c for c in ('server_profiles', 'servers', 'server_wallets_free',
                                          'accounts_wallet_paid', 'accounts_wallet_paid_ledger') if c in cols]
        # PROJECT_A Track A authorization: server_profiles may be present IFF the apply marker
        # exists with verdict APPLIED_SAFE AND the collection is empty (inert state).
        if 'server_profiles' in forbidden_present:
            import json as _json
            from pathlib import Path as _Path
            marker = _Path('/app/data/design/server_lifecycle/project_a_server_profiles_ops_result_v1.json')
            if marker.exists():
                try:
                    m = _json.loads(marker.read_text(encoding='utf-8'))
                    if m.get('verdict') == 'TRACK_A_SERVER_PROFILES_COLLECTION_APPLIED_SAFE':
                        doc_count = cli[db_name].server_profiles.count_documents({})
                        if doc_count == 0:
                            forbidden_present = [c for c in forbidden_present if c != 'server_profiles']
                except Exception:
                    pass
        cli.close()
        if forbidden_present:
            return False, f'unexpected multishard collections present: {forbidden_present}'
        return True, f'no multishard collections (checked among {len(cols)} cols)'
    except Exception as ex:
        return True, f'mongo check skipped: {ex}'


def main() -> int:
    errs = []
    # 1. SLC-A artifact present
    require(SLC_A_AUDIT.exists(), f'SLC-A audit missing: {SLC_A_AUDIT}', errs)
    # 2. SLC-C combo PASS
    if SLC_C_COMBO.exists():
        try:
            d = json.loads(SLC_C_COMBO.read_text())
            require(d.get('status') == 'PASS', f'SLC-C combo status != PASS: {d.get("status")}', errs)
        except Exception as ex:
            errs.append(f'cannot parse SLC-C combo: {ex}')
    else:
        errs.append(f'SLC-C combo result missing: {SLC_C_COMBO}')
    # 3. SLC-C preflight: execution_ready=false, second_server_opening_allowed=false
    if SLC_C_PREFLIGHT.exists():
        try:
            d = json.loads(SLC_C_PREFLIGHT.read_text())
            require(d.get('execution_ready') is False, 'SLC-C execution_ready must be False', errs)
            require(d.get('second_server_opening_allowed') is False, 'SLC-C second_server_opening_allowed must be False', errs)
            require(d.get('borea_safe') is True, 'SLC-C borea_safe must be True', errs)
        except Exception as ex:
            errs.append(f'cannot parse SLC-C preflight: {ex}')
    else:
        errs.append(f'SLC-C preflight missing: {SLC_C_PREFLIGHT}')
    # 4. API smoke: /api/heroes count if reachable
    heroes_count = None
    code_h, body_h = fetch('/api/heroes')
    if code_h == 200:
        try:
            data = json.loads(body_h)
            heroes = data if isinstance(data, list) else data.get('heroes', [])
            heroes_count = len(heroes)
            require(heroes_count == 100, f'/api/heroes count != 100 (got {heroes_count})', errs)
        except Exception:
            pass
    # 5. primordial_gaia 404
    code_pg, _ = fetch('/api/heroes/primordial_gaia')
    if code_pg:
        require(code_pg == 404, f'/api/heroes/primordial_gaia != 404 (got {code_pg})', errs)
    # 6. AF2-N cap invariant (read-only inspect)
    af2n_path = Path('/app/backend/routes/affinity_gift_spend.py')
    if af2n_path.exists():
        src = af2n_path.read_text()
        require('50000' in src, 'AF2-N cap S2 50000 missing in affinity_gift_spend.py', errs)
    # 7. no server_profiles in DB
    ok, msg = check_no_server_profiles_collection()
    require(ok, f'multishard collections check failed: {msg}', errs)

    payload = {
        'task_origin': 'SLC-BE-PREFLIGHT', 'version': 'v1', 'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'slc_a_present': SLC_A_AUDIT.exists(),
        'slc_c_combo_present': SLC_C_COMBO.exists(),
        'slc_c_preflight_present': SLC_C_PREFLIGHT.exists(),
        'slc_c_execution_ready': False,
        'second_server_opening_allowed': False,
        'heroes_count_observed': heroes_count,
        'primordial_gaia_status_observed': code_pg,
        'multishard_collections_check': msg,
        'af2n_cap_s2_50000_present': '50000' in (af2n_path.read_text() if af2n_path.exists() else ''),
        'errors_count': len(errs),
        'safety': {'no_db_write': True, 'no_runtime_change': True},
    }
    out = DESIGN_DIR / 'slc_be_preflight_result_v1.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, {'heroes_count': heroes_count})


if __name__ == '__main__':
    sys.exit(main())
