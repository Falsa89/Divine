#!/usr/bin/env python3
"""
RM1.33-E — Debug Coverage Endpoint Safety Audit (READ-ONLY)
──────────────────────────────────────────────────────────────────────
Verifies the new coverage endpoint:
  GET /api/hero-skill-kits/runtime/debug/coverage

1.  Endpoint reachable, returns 200.
2.  Coverage totals 178/178 (normalized + disabled).
3.  runtime_enabled=false; applied_to_combat=false;
    adapter_imported_by_battle_runtime=false.
4.  Route file is GET-only; 0 mutation decorators.
5.  No DB / catalog write patterns in route file.
6.  /api/heroes count=100; Borea/legacy/Gaia hidden.
7.  Baseline v4 present and identifiable.
8.  UI catalog files do NOT reference the coverage endpoint.
9.  Snapshot validator passes.
10. battle_engine.py / combat.tsx / battle_core.py contain no adapter
    or coverage tokens.
"""
from __future__ import annotations
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path('/app')
ROUTE_FILE = ROOT / 'backend/routes/skill_kit_runtime_debug.py'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
COMBAT_TSX = ROOT / 'frontend/app/combat.tsx'
BATTLE_CORE = ROOT / 'backend/battle_core.py'
HSK_UI = ROOT / 'frontend/app/hero-skill-kits-catalog.tsx'
DW_UI = ROOT / 'frontend/app/divine-weapons-catalog.tsx'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
SNAPSHOT_VALIDATOR = ROOT / 'backend/scripts/validate_runtime_debug_snapshot_contract.py'

BASE = 'http://localhost:8001'
COVERAGE_PATH = '/api/hero-skill-kits/runtime/debug/coverage'

MUTATION_TOKENS = (
    '.post(', '.put(', '.patch(', '.delete(',
    '@router.post', '@router.put', '@router.patch', '@router.delete',
)
DB_WRITE_PATTERNS = (
    'db.', 'await db', 'insert_one(', 'update_one(', 'update_many(',
    'delete_one(', 'delete_many(', 'replace_one(', 'bulk_write(',
)
ADAPTER_TOKENS = (
    'skill_kit_runtime_adapter', 'skill_kit_cap_policy_adapter',
    'is_skill_kit_runtime_enabled', 'SKILL_KIT_RUNTIME_ENABLED',
    'skill_kit_runtime_debug', '/hero-skill-kits/runtime/debug/preview',
    '/hero-skill-kits/runtime/debug/coverage',
)

failures: list[str] = []
infos: list[str] = []


def fail(s, m): failures.append(f'[{s}] {m}')
def info(m): infos.append(m)


def _http_get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=8) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return 0, {'_exception': repr(e)}


def main() -> int:
    # 1) Coverage endpoint live
    st, body = _http_get(COVERAGE_PATH)
    if st != 200 or not isinstance(body, dict):
        fail('coverage', f'coverage endpoint expected 200 JSON, got {st} {type(body).__name__}')
        return emit()
    # 2/3) Required fields & values
    required = {
        'debug_only': True, 'read_only': True,
        'runtime_enabled': False, 'applied_to_combat': False,
        'runtime_attached': False, 'battle_runtime_attached': False,
        'total_slots_expected': 178, 'total_slots_tested': 178,
        'normalized_slots': 178, 'runtime_candidates_disabled': 178,
        'feature_flag_default': False,
        'forbidden_aliases_rejected': True,
        'adapter_imported_by_battle_runtime': False,
        'cap_policy_preview_inert': True,
        'borea_catalog_only': True,
        'no_runtime_activation': True,
        'db_write': False, 'catalog_write': False,
        'roster_write': False, 'gacha_write': False,
        'ui_runtime_control': False,
    }
    for k, v in required.items():
        if body.get(k) != v:
            fail('coverage', f'{k}: expected {v!r}, got {body.get(k)!r}')
    if not any(f.startswith('[coverage]') for f in failures):
        info('coverage endpoint: 178/178, runtime_enabled=false, applied_to_combat=false ✓')

    # 4) Route file GET-only
    src = ROUTE_FILE.read_text(encoding='utf-8') if ROUTE_FILE.exists() else ''
    if not src:
        fail('route', f'missing {ROUTE_FILE}')
    else:
        for tok in MUTATION_TOKENS:
            if tok in src:
                fail('route', f'mutation token {tok!r} found in route file')
        get_count = src.count('@router.get(') + src.count('router.get(')
        if get_count < 2:
            fail('route', f'expected ≥2 @router.get decorators (preview + coverage), got {get_count}')
        if '/hero-skill-kits/runtime/debug/coverage' not in src:
            fail('route', 'coverage path not declared in route file')
        if not any(f.startswith('[route]') for f in failures):
            info(f'route file: GET-only ({get_count} GET routes), coverage path declared ✓')

    # 5) Route file no DB writes
    if src:
        hits = [p for p in DB_WRITE_PATTERNS if p in src]
        if hits:
            fail('route', f'DB write patterns in route file: {hits}')

    # 6) /api/heroes
    st2, hbody = _http_get('/api/heroes')
    heroes = hbody if isinstance(hbody, list) else ((hbody or {}).get('heroes') or (hbody or {}).get('data') or [])
    if len(heroes) != 100:
        fail('api_heroes', f'/api/heroes count != 100 (got {len(heroes)})')
    ids = [h.get('hero_id') or h.get('id') for h in heroes if isinstance(h, dict)]
    for forb in ('borea', 'greek_borea', 'primordial_gaia'):
        if forb in ids:
            fail('api_heroes', f'{forb} visible')
    if not any(f.startswith('[api_heroes]') for f in failures):
        info('/api/heroes: count=100, Borea/legacy/Gaia hidden ✓')

    # 7) Baseline v4
    if not BASELINE_V4.exists():
        fail('baseline', 'baseline v4 missing')
    else:
        b4 = json.loads(BASELINE_V4.read_text(encoding='utf-8'))
        if b4.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
            fail('baseline', 'baseline v4 identity mismatch')
        else:
            info('baseline v4 present and identifiable ✓')

    # 8) UI no refs
    for ui in (HSK_UI, DW_UI):
        t = ui.read_text(encoding='utf-8') if ui.exists() else ''
        for tok in ADAPTER_TOKENS:
            if tok in t:
                fail('ui', f'{ui.name} references {tok!r}')
    if not any(f.startswith('[ui]') for f in failures):
        info('UI files: no references to debug endpoints / adapter tokens ✓')

    # 9) battle runtime isolation
    for target in (BATTLE_ENGINE, COMBAT_TSX, BATTLE_CORE):
        t = target.read_text(encoding='utf-8') if target.exists() else ''
        for tok in ADAPTER_TOKENS:
            if tok in t:
                fail('isolation', f'{target.name} references {tok!r}')
    if not any(f.startswith('[isolation]') for f in failures):
        info('battle_engine/combat/battle_core: no adapter/debug refs ✓')

    # 10) Snapshot validator
    if SNAPSHOT_VALIDATOR.exists():
        res = subprocess.run(['python3', str(SNAPSHOT_VALIDATOR)], capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            fail('snapshot_validator', f'returned non-zero ({res.returncode}); first line: {res.stdout.splitlines()[0] if res.stdout else "<empty>"}')
        else:
            info('snapshot contract validator (RM1.33-D): PASS ✓')
    else:
        fail('snapshot_validator', f'missing {SNAPSHOT_VALIDATOR}')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.33-E — Debug Coverage Endpoint Safety Audit')
        for f in failures:
            print(f'  - {f}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.33-E — Debug Coverage Endpoint Safety Audit')
    for i in infos:
        print(f'  i {i}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
