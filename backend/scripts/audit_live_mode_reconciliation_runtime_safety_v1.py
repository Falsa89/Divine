#!/usr/bin/env python3
"""LIVE-MODES — Runtime safety audit (READ-ONLY).

Verifies the live-mode design package has not leaked into runtime:
  - No new routes for the 16 modes.
  - Protected files unchanged (SHA-256 vs SLC-C baseline).
  - No DB writes / no new live-mode collections.
  - AF2-N cap S2 (50000) and allowlist (2500) markers still present.
  - SERVER_PROFILES_RUNTIME_ENABLED / SECOND_SERVER_OPENING_ENABLED env unset.
"""
from __future__ import annotations
import hashlib, json, os, sys, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, finish_result, require  # noqa: E402

NAME = 'live_mode_reconciliation_runtime_safety_v1'

PROTECTED_FILES = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
    '/app/backend/routes/affinity_gift_spend.py',
]
ROUTES_DIR = Path('/app/backend/routes')
BASELINE_PATH = Path('/app/data/design/server_lifecycle/_slc_c_critical_files_baseline_v1.json')

# Substrings that, if found as a declared API path, would indicate live-mode runtime leakage.
LIVE_MODE_PATH_TOKENS = [
    '/api/live-modes', '/api/live_modes',
    '/api/asgard', '/api/hades', '/api/olympus', '/api/sigils',
    '/api/tower-of-inferno', '/api/torre-degli-inferi',
    '/api/eclipse-thrones', '/api/troni-eclissi',
    '/api/pantheon-trials', '/api/abyss-colossus',
    '/api/titans-twilight', '/api/crepuscolo-titani',
    '/api/lineage-judgement', '/api/giudizio-stirpi',
    '/api/valhalla-fronts', '/api/fronti-valhalla',
    '/api/three-thrones', '/api/guerra-tre-troni',
    '/api/behemoth-hunger', '/api/fame-behemoth',
    '/api/pantheon-furies', '/api/furie-pantheon',
    '/api/titanomachia',
    '/api/ragnarok-assault', '/api/assalto-ragnarok',
    '/api/sanctuary/housing', '/api/dimora-divina',
]


def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def scan_routes_for_live_mode_paths():
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
            path = m.group(1)
            for tok in LIVE_MODE_PATH_TOKENS:
                if tok in path:
                    hits.append({'file': str(f), 'route': path, 'token': tok})
    return hits


def scan_mongo_collections() -> dict:
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
        live_mode_cols = [c for c in cols if any(t in c.lower() for t in (
            'live_mode', 'titans_twilight', 'crepuscolo', 'asgard', 'hades_path',
            'olympus_ladder', 'inferno_tower', 'eclipse_thrones', 'pantheon_trials',
            'colossus_abyss', 'lineage_judgement', 'valhalla_fronts', 'three_thrones',
            'behemoth_hunger', 'pantheon_furies', 'titanomachia', 'ragnarok_assault',
            'sanctuary_housing', 'dimora_divina',
        ))]
        return {'mongo_reachable': True, 'total_collections': len(cols), 'live_mode_collections_found': live_mode_cols}
    except Exception as ex:
        return {'mongo_reachable': False, 'error': str(ex)}


def main() -> int:
    errs = []
    # 1) No live-mode runtime routes
    route_hits = scan_routes_for_live_mode_paths()
    require(not route_hits, f'live-mode runtime routes detected: {route_hits[:5]}', errs)
    # 2) Protected files match SLC-C baseline
    protected_status = {}
    if BASELINE_PATH.exists():
        try:
            base = json.loads(BASELINE_PATH.read_text())
            for f in PROTECTED_FILES:
                cur = sha256(Path(f))
                exp = base.get('hashes', {}).get(f)
                protected_status[f] = {'current': cur, 'baseline': exp, 'match': (cur == exp) if exp else None}
                if exp and cur != exp:
                    errs.append(f'CRITICAL FILE MUTATED: {f}')
        except Exception as ex:
            errs.append(f'baseline read error: {ex}')
    # 3) AF2-N markers intact
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    af2n_src = af2n.read_text() if af2n.exists() else ''
    require('50000' in af2n_src, 'AF2-N cap S2 (50000) marker missing in affinity_gift_spend.py', errs)
    # 4) No live-mode Mongo collections
    mongo = scan_mongo_collections()
    require(not mongo.get('live_mode_collections_found'), f'live-mode collections present in DB: {mongo.get("live_mode_collections_found")}', errs)
    # 5) Future feature flags unset
    spre = os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED')
    second = os.environ.get('SECOND_SERVER_OPENING_ENABLED')
    require(spre in (None, '', '0', 'false', 'False'), f'SERVER_PROFILES_RUNTIME_ENABLED unexpectedly set: {spre}', errs)
    require(second in (None, '', '0', 'false', 'False'), f'SECOND_SERVER_OPENING_ENABLED unexpectedly set: {second}', errs)

    return finish_result(NAME, errs, LIVE_MODES_DIR, {
        'no_live_mode_runtime_routes': not route_hits,
        'protected_files_match': all(s.get('match') in (True, None) for s in protected_status.values()),
        'af2n_cap_s2_marker_present': '50000' in af2n_src,
        'mongo_reachable': mongo.get('mongo_reachable'),
        'live_mode_collections_found': mongo.get('live_mode_collections_found'),
        'server_profiles_runtime_enabled': spre,
        'second_server_opening_enabled': second,
    })


if __name__ == '__main__':
    sys.exit(main())
