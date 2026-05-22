#!/usr/bin/env python3
"""Runtime safety audit for benchmark canonical pack (READ-ONLY)."""
from __future__ import annotations
import hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import CANON_DIR, finish, require  # noqa: E402

NAME = 'benchmark_canonical_runtime_safety_v1'
PROTECTED = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
    '/app/backend/routes/affinity_gift_spend.py',
]
BASELINE = Path('/app/data/design/server_lifecycle/_slc_c_critical_files_baseline_v1.json')


def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errs = []
    # Protected files vs SLC-C baseline
    protected_status = {}
    if BASELINE.exists():
        base = json.loads(BASELINE.read_text())
        for f in PROTECTED:
            cur = sha256(Path(f))
            exp = base.get('hashes', {}).get(f)
            protected_status[f] = {'match': (cur == exp) if exp else None}
            if exp and cur != exp:
                errs.append(f'CRITICAL FILE MUTATED: {f}')
    # AF2-N markers intact
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    af2n_src = af2n.read_text() if af2n.exists() else ''
    require('50000' in af2n_src, 'AF2-N cap S2 (50000) missing', errs)
    # No env flags enabled
    spre = os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED')
    second = os.environ.get('SECOND_SERVER_OPENING_ENABLED')
    require(spre in (None, '', '0', 'false', 'False'), f'SERVER_PROFILES_RUNTIME_ENABLED unexpectedly set: {spre}', errs)
    require(second in (None, '', '0', 'false', 'False'), f'SECOND_SERVER_OPENING_ENABLED unexpectedly set: {second}', errs)
    # Mongo: ensure no benchmark-canonical writes leaked
    benchmark_cols_found = []
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
            for c in cols:
                if c.startswith('benchmark_canonical') or c.startswith('sanctuary_housing') or c.startswith('live_special_modes'):
                    benchmark_cols_found.append(c)
    except Exception:
        pass
    require(not benchmark_cols_found, f'unexpected benchmark canonical collections in DB: {benchmark_cols_found}', errs)

    out = CANON_DIR / 'benchmark_canonical_runtime_safety_audit_v1.json'
    out.write_text(json.dumps({
        'task': NAME, 'mode': 'DESIGN_ONLY', 'utc': datetime.now(timezone.utc).isoformat(),
        'protected_files_status': protected_status,
        'af2n_cap_s2_marker_present': '50000' in af2n_src,
        'server_profiles_runtime_enabled': spre,
        'second_server_opening_enabled': second,
        'benchmark_collections_found': benchmark_cols_found,
    }, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, {
        'protected_files_match': all(s.get('match') in (True, None) for s in protected_status.values()),
    })


if __name__ == '__main__':
    sys.exit(main())
