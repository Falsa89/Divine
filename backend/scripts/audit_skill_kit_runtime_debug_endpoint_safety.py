#!/usr/bin/env python3
"""
RM1.33-C — Debug Endpoint Safety Audit (READ-ONLY)
───────────────────────────────────────────────────────────────
Verifies the new debug route + endpoint behavior. NO mutation.

1.  Route file exists and contains ONLY GET routes (no POST/PUT/PATCH/DELETE).
2.  Route file has no DB write / no catalog write patterns.
3.  battle_engine.py / combat.tsx / battle_core.py do NOT import the route or adapter.
4.  Feature flag default OFF.
5.  Sample valid GETs return `runtime_candidate.enabled=false`,
    `runtime_candidate.reason=='feature_flag_off'`, cap policy inert.
6.  Forbidden aliases (borea / primordial_gaia / greek_boreas / olympian_borea)
    return 404 with `error=forbidden_legacy_hero_id`.
7.  5★ ultimate returns 404 with `error=invalid_slot` and
    `reason=invalid_slot_for_5star`.
8.  Missing hero_id / slot → 400. Invalid context → 400.
9.  Borea preview is catalog-only with `no_activation=true`.
10. `/api/heroes` count remains 100; Borea / legacy borea / primordial_gaia
    not visible.
11. Baseline v4 file present and unchanged identity.
12. No UI file references the new endpoint.

Exit 0 PASS, 1 FAIL.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.parse
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

ADAPTER_TOKENS = (
    'skill_kit_runtime_adapter',
    'skill_kit_cap_policy_adapter',
    'is_skill_kit_runtime_enabled',
    'SKILL_KIT_RUNTIME_ENABLED',
    'skill_kit_runtime_debug',
    'register_skill_kit_runtime_debug_routes',
    '/hero-skill-kits/runtime/debug/preview',
)
MUTATION_DECORATORS = (
    '.post(', '.put(', '.patch(', '.delete(',
    '@router.post', '@router.put', '@router.patch', '@router.delete',
)
DB_WRITE_PATTERNS = (
    'db.', 'await db', 'insert_one(', 'update_one(', 'update_many(',
    'delete_one(', 'delete_many(', 'replace_one(', 'find_one_and_update',
    'find_one_and_replace', 'find_one_and_delete', 'bulk_write(',
)
CATALOG_WRITE_PATTERNS = (
    '.write_text(', 'json.dump(', 'open(', '.write(',
)

BASE = 'http://localhost:8001'
DEBUG_PATH = '/api/hero-skill-kits/runtime/debug/preview'

failures: list[str] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None:
    failures.append(f'[{sec}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def _http_get(path: str, expect_status: int | None = None) -> tuple[int, dict | None]:
    url = BASE + path
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            body = r.read()
            return r.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
            data = json.loads(body) if body else None
        except Exception:
            data = None
        return e.code, data
    except Exception as e:
        return 0, {'_exception': repr(e)}


def main() -> int:
    # 1) Route file exists
    if not ROUTE_FILE.exists():
        fail('route', f'route file missing: {ROUTE_FILE}')
        return emit()
    src = ROUTE_FILE.read_text(encoding='utf-8')

    # 2) Only GET routes
    for tok in MUTATION_DECORATORS:
        if tok in src:
            fail('route', f'mutation decorator/method "{tok}" found in route file')
    if 'router.get(' not in src and '@router.get' not in src:
        fail('route', 'no router.get(...) decorator found in route file')
    if not any(f.startswith('[route]') for f in failures):
        info('route file: GET-only, no mutation decorators ✓')

    # 3) No DB write patterns in route file
    db_hits = [p for p in DB_WRITE_PATTERNS if p in src]
    if db_hits:
        fail('route', f'DB write patterns in route file: {db_hits}')
    cat_hits = [p for p in CATALOG_WRITE_PATTERNS if p in src]
    if cat_hits:
        fail('route', f'catalog write patterns in route file: {cat_hits}')
    if not any(f.startswith('[route]') and 'DB' in f for f in failures):
        info('route file: no DB writes / no catalog writes ✓')

    # 4) Adapter isolation — battle_engine / combat / battle_core
    for target in (BATTLE_ENGINE, COMBAT_TSX, BATTLE_CORE):
        t = target.read_text(encoding='utf-8') if target.exists() else ''
        for tok in ADAPTER_TOKENS:
            if tok in t:
                fail('isolation', f'{target.name} references {tok!r}')
    if not any(f.startswith('[isolation]') for f in failures):
        info('adapter/route isolation from battle runtime ✓')

    # 5) Feature flag default OFF (probe via HTTP)
    # 6) Sample valid GETs
    samples = [
        ('greek_atalanta', 'skill_2', 'pvp', 200),
        ('greek_athena', 'ultimate', 'boss', 200),
        ('greek_borea', 'ultimate', 'pvp', 200),
        ('norse_eir', 'skill_2', 'pve', 200),
    ]
    for hid, sl, ctx, expect in samples:
        path = f'{DEBUG_PATH}?hero_id={urllib.parse.quote(hid)}&slot={urllib.parse.quote(sl)}&context={ctx}'
        st, body = _http_get(path)
        if st != expect:
            fail('http_sample', f'{hid}.{sl} ({ctx}): expected {expect}, got {st} body={body!r}')
            continue
        if not isinstance(body, dict):
            fail('http_sample', f'{hid}.{sl}: response is not dict')
            continue
        env = body.get('safety_envelope') or {}
        if env.get('debug_only') is not True or env.get('read_only') is not True or env.get('method') != 'GET':
            fail('http_sample', f'{hid}.{sl}: safety_envelope missing debug_only/read_only/GET')
        if env.get('applied_to_combat') is not False or env.get('runtime_attached') is not False:
            fail('http_sample', f'{hid}.{sl}: safety_envelope must keep applied_to_combat=false / runtime_attached=false')
        if env.get('runtime_enabled') is not False:
            fail('http_sample', f'{hid}.{sl}: safety_envelope.runtime_enabled must be false')
        rc = body.get('runtime_candidate') or {}
        if rc.get('enabled') is not False or rc.get('reason') != 'feature_flag_off':
            fail('http_sample', f'{hid}.{sl}: runtime_candidate must be disabled (reason=feature_flag_off)')
        cap = body.get('cap_policy_preview') or {}
        if cap.get('applied_to_combat') is not False or cap.get('runtime_attached') is not False:
            fail('http_sample', f'{hid}.{sl}: cap_policy_preview not inert')
        if hid == 'greek_borea':
            bp = body.get('borea_preview') or {}
            if not (bp.get('catalog_only') is True and bp.get('no_activation') is True
                    and bp.get('borea_activation_allowed') is False
                    and bp.get('not_visible_in_heroes') is True):
                fail('http_sample', 'greek_borea preview must be catalog-only / no_activation=true')
            if bp.get('release_group') != 'launch_extra_premium':
                fail('http_sample', f'greek_borea preview release_group != launch_extra_premium (got {bp.get("release_group")!r})')
    if not any(f.startswith('[http_sample]') for f in failures):
        info(f'sample debug GETs: {len(samples)}/{len(samples)} 200 + inert runtime_candidate + cap policy inert ✓')

    # 7) Forbidden aliases — expect 404
    for alias in ('borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'):
        path = f'{DEBUG_PATH}?hero_id={urllib.parse.quote(alias)}&slot=skill_1&context=pvp'
        st, body = _http_get(path)
        if st != 404:
            fail('forbidden', f'alias {alias!r}: expected 404, got {st}')
            continue
        det = (body or {}).get('detail') or {}
        if det.get('error') != 'forbidden_legacy_hero_id' or det.get('fallback_disabled') is not True:
            fail('forbidden', f'alias {alias!r}: bad detail payload {det!r}')
    if not any(f.startswith('[forbidden]') for f in failures):
        info('forbidden aliases: 4/4 → 404 forbidden_legacy_hero_id (no fallback) ✓')

    # 8) 5★ ultimate → 404 invalid_slot
    path = f'{DEBUG_PATH}?hero_id=greek_atalanta&slot=ultimate&context=pvp'
    st, body = _http_get(path)
    if st != 404:
        fail('5star_ult', f'5★ ultimate expected 404, got {st}')
    else:
        det = (body or {}).get('detail') or {}
        if det.get('error') != 'invalid_slot' or det.get('reason') != 'invalid_slot_for_5star':
            fail('5star_ult', f'5★ ultimate bad detail {det!r}')
    if not any(f.startswith('[5star_ult]') for f in failures):
        info('5★ ultimate request: 404 invalid_slot_for_5star ✓')

    # 9) Missing param → 400; invalid context → 400
    st, body = _http_get(f'{DEBUG_PATH}?slot=skill_1&context=pvp')
    if st != 400:
        fail('bad_request', f'missing hero_id expected 400, got {st}')
    st, body = _http_get(f'{DEBUG_PATH}?hero_id=greek_atalanta&context=pvp')
    if st != 400:
        fail('bad_request', f'missing slot expected 400, got {st}')
    st, body = _http_get(f'{DEBUG_PATH}?hero_id=greek_atalanta&slot=skill_1&context=invalid_ctx')
    if st != 400:
        fail('bad_request', f'invalid context expected 400, got {st}')
    if not any(f.startswith('[bad_request]') for f in failures):
        info('400 on missing hero_id / missing slot / invalid context ✓')

    # 10) /api/heroes count + hidden
    st, body = _http_get('/api/heroes')
    heroes = body if isinstance(body, list) else ((body or {}).get('heroes') or (body or {}).get('data') or [])
    if len(heroes) != 100:
        fail('api_heroes', f'/api/heroes count != 100 (got {len(heroes)})')
    ids = [h.get('hero_id') or h.get('id') for h in heroes if isinstance(h, dict)]
    for forb in ('borea', 'greek_borea', 'primordial_gaia'):
        if forb in ids:
            fail('api_heroes', f'{forb} visible in /api/heroes')
    if not any(f.startswith('[api_heroes]') for f in failures):
        info('/api/heroes: count=100, borea/greek_borea/primordial_gaia hidden ✓')

    # 11) Baseline v4 sanity
    if not BASELINE_V4.exists():
        fail('baseline', 'baseline v4 missing')
    else:
        b4 = json.loads(BASELINE_V4.read_text(encoding='utf-8'))
        if b4.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
            fail('baseline', 'baseline v4 identity mismatch')
        else:
            info('baseline v4 present and identifiable ✓')

    # 12) UI does not reference the new endpoint
    debug_path_re = re.compile(re.escape('/api/hero-skill-kits/runtime/debug/preview'))
    for ui in (HSK_UI, DW_UI):
        text = ui.read_text(encoding='utf-8') if ui.exists() else ''
        if debug_path_re.search(text):
            fail('ui', f'{ui.name} references debug endpoint')
        for tok in ADAPTER_TOKENS:
            if tok in text:
                fail('ui', f'{ui.name} references adapter token {tok!r}')
    if not any(f.startswith('[ui]') for f in failures):
        info('UI files: no references to debug endpoint / adapter tokens ✓')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.33-C — Debug Endpoint Safety Audit')
        for f in failures:
            print(f'  - {f}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.33-C — Debug Endpoint Safety Audit')
    for i in infos:
        print(f'  i {i}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
