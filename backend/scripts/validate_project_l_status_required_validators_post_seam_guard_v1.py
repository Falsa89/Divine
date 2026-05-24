#!/usr/bin/env python3
"""PROJECT_L Track D validator — REQUIRED validators post-seam guard."""
import json, re, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_status_required_validators_post_seam_guard_v1.json')
SUITE = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')
FORBIDDEN_IMPORTERS = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
)
ROUTES_DIR = Path('/app/backend/routes')
FORBIDDEN_PATTERNS = ('status_prefight_runtime_seam', 'status_first_slice_resolver_pure')
TICK_KEYWORDS = ('tick_loop', 'apply_dot', 'damage_over_time', 'heal_over_time')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _count_required_in_suite() -> int:
    txt = SUITE.read_text()
    # Extract slice between 'REQUIRED = [' and the first ']' that closes the block.
    s = txt.index('REQUIRED = [')
    e = txt.index(']', s)
    block = txt[s:e]
    return block.count("('") if "('" in block else block.count('("')


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_STATUS_REQUIRED_VALIDATORS_POST_SEAM_GUARD_READY': fail('verdict mismatch')
    if m.get('required_weakening') is not False: fail('required_weakening must be False')
    n = _count_required_in_suite()
    if n != 19: fail(f'REQUIRED count expected 19, observed {n}')
    # Scan forbidden runtime importers for resolver / seam leakage.
    for f in FORBIDDEN_IMPORTERS:
        if not f.exists(): continue
        t = f.read_text(encoding='utf-8', errors='ignore')
        for p in FORBIDDEN_PATTERNS:
            if p in t: fail(f'forbidden import "{p}" detected in {f}')
        for kw in TICK_KEYWORDS:
            # We don't forbid mention; we just verify the seam file has no such patterns (checked below).
            pass
    if ROUTES_DIR.exists():
        for r in ROUTES_DIR.rglob('*.py'):
            t = r.read_text(encoding='utf-8', errors='ignore')
            for p in FORBIDDEN_PATTERNS:
                if p in t: fail(f'forbidden import "{p}" detected in route {r}')
    # Seam must not contain DoT / tick / damage / heal formula constructs.
    seam_txt = Path('/app/backend/game_logic/status_prefight_runtime_seam.py').read_text(encoding='utf-8', errors='ignore')
    for kw in TICK_KEYWORDS:
        if kw in seam_txt: fail(f'seam contains forbidden keyword: {kw}')
    print('[PASS] PROJECT_L Track D post-seam guard READY: 19 REQUIRED intact; no live importers; no tick/DoT/formula keywords in seam')
    sys.exit(0)


if __name__ == '__main__': main()
