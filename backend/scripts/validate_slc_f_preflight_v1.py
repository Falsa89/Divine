#!/usr/bin/env python3
"""SLC-F preflight (read-only): verify baseline before SLC-F can run."""
from __future__ import annotations
import json, os, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, CANON_DIR, finish, require  # noqa: E402

NAME = 'slc_f_preflight_v1'


def fetch(path: str, timeout: float = 4.0):
    try:
        with urllib.request.urlopen('http://localhost:8001' + path, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def main() -> int:
    errs = []
    # 1) canonical index present
    canon = CANON_DIR / 'benchmark_canonical_index_v1.json'
    require(canon.exists(), f'canonical index missing: {canon}', errs)
    # 2) SLC-C combo result present and PASS
    slc_c = SLC_DIR / '_slc_c_combo_v1_result.json'
    if slc_c.exists():
        d = json.loads(slc_c.read_text())
        require(d.get('status') == 'PASS', f'SLC-C combo status != PASS: {d.get("status")}', errs)
    else:
        errs.append(f'SLC-C combo result missing: {slc_c}')
    # 3) SLC-BE combo result
    slc_be = SLC_DIR / '_slc_be_combo_v1_result.json'
    if slc_be.exists():
        d = json.loads(slc_be.read_text())
        require(d.get('status') == 'PASS', f'SLC-BE combo status != PASS: {d.get("status")}', errs)
    # 4) API smoke
    code_h, body_h = fetch('/api/heroes')
    heroes_count = None
    if code_h == 200:
        try:
            data = json.loads(body_h)
            heroes = data if isinstance(data, list) else data.get('heroes', [])
            heroes_count = len(heroes)
        except Exception:
            pass
    require(heroes_count == 100, f'/api/heroes count != 100 (got {heroes_count})', errs)
    code_pg, _ = fetch('/api/heroes/primordial_gaia')
    if code_pg:
        require(code_pg == 404, f'/api/heroes/primordial_gaia must be 404 (got {code_pg})', errs)
    # 5) AF2-N cap marker
    af2n = Path('/app/backend/routes/affinity_gift_spend.py')
    if af2n.exists():
        require('50000' in af2n.read_text(), 'AF2-N cap S2 (50000) missing in affinity_gift_spend.py', errs)
    # 6) env flags unset
    for flag in ('SERVER_PROFILES_RUNTIME_ENABLED', 'SECOND_SERVER_OPENING_ENABLED'):
        v = os.environ.get(flag)
        require(v in (None, '', '0', 'false', 'False'), f'{flag} unexpectedly set: {v}', errs)
    return finish(NAME, errs, extra={'heroes_count': heroes_count, 'primordial_gaia_status': code_pg})


if __name__ == '__main__':
    sys.exit(main())
