#!/usr/bin/env python3
import json, os, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, CANON_DIR, finish, require  # noqa: E402

NAME = 'slc_d_preflight_v1'


def fetch(path):
    try:
        with urllib.request.urlopen('http://localhost:8001' + path, timeout=4) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def main() -> int:
    errs = []
    require((CANON_DIR / 'benchmark_canonical_index_v1.json').exists(), 'canonical index missing', errs)
    for needed in ('_slc_c_combo_v1_result.json', '_slc_be_combo_v1_result.json', '_slc_f_route_patch_dryrun_combo_v1_result.json'):
        p = SLC_DIR / needed
        require(p.exists(), f'baseline missing: {p}', errs)
        if p.exists():
            d = json.loads(p.read_text())
            require(d.get('status') == 'PASS', f'{needed} status != PASS', errs)
    code, body = fetch('/api/heroes')
    hc = None
    if code == 200:
        try:
            data = json.loads(body)
            heroes = data if isinstance(data, list) else data.get('heroes', [])
            hc = len(heroes)
        except Exception:
            pass
    require(hc == 100, f'/api/heroes count != 100 (got {hc})', errs)
    code_pg, _ = fetch('/api/heroes/primordial_gaia')
    if code_pg:
        require(code_pg == 404, f'/api/heroes/primordial_gaia must be 404 (got {code_pg})', errs)
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    if af2n.exists():
        require('50000' in af2n.read_text(), 'AF2-N cap S2 (50000) missing', errs)
    for flag in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SECOND_SERVER_OPENING_ENABLED'):
        v = os.environ.get(flag)
        require(v in (None, '', '0', 'false', 'False'), f'{flag} unexpectedly set: {v}', errs)
    return finish(NAME, errs, extra={'heroes_count': hc, 'primordial_gaia': code_pg})


if __name__ == '__main__':
    sys.exit(main())
