#!/usr/bin/env python3
"""
RM1.33-H — Divine Weapon Preview Catalog-Only Safety Fixture Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Verifies that the 13 Divine Weapon records remain catalog-only / design-only /
runtime-off, that no equip/activate endpoint exists in route files, and that no
runtime Pressable exists in `divine-weapons-catalog.tsx`.

Writes result JSON:
- /app/data/design/divine_weapons/divine_weapon_preview_catalog_only_fixture_result_v1.json

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import json
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
FIXTURE = ROOT / 'data/design/divine_weapons/divine_weapon_preview_catalog_only_fixture_v1.json'
RESULT_OUT = ROOT / 'data/design/divine_weapons/divine_weapon_preview_catalog_only_fixture_result_v1.json'
DW_CATALOG = ROOT / 'data/design/divine_weapons/divine_weapons_catalog_v1.json'
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
ROUTES_DIR = ROOT / 'backend/routes'
UI_DW = ROOT / 'frontend/app/divine-weapons-catalog.tsx'
API = 'http://localhost:8001/api'

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(sec, msg): failures.append(f'[{sec}] {msg}')
def warn(sec, msg): warnings.append(f'[{sec}] {msg}')
def info(msg): infos.append(msg)


def http_get(path, timeout=6.0):
    try:
        with urllib.request.urlopen(API + path, timeout=timeout) as r:
            body = r.read().decode('utf-8', errors='ignore')
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return -1, {'error': str(e)}


def main() -> int:
    # 1. fixture present
    if not FIXTURE.exists():
        fail('io', f'fixture missing: {FIXTURE}')
        return emit('FAIL', {})
    try:
        fx = json.loads(FIXTURE.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'fixture parse error: {e}')
        return emit('FAIL', {})

    if fx.get('fixture_id') != 'divine_weapon_preview_catalog_only_fixture_v1':
        fail('meta', 'fixture_id mismatch')
    if fx.get('task_origin') != 'RM1.33-H':
        fail('meta', 'task_origin != RM1.33-H')
    if fx.get('baseline_anchor') != 'hero_skill_kit_catalog_baseline_rm132c2_v5':
        fail('meta', 'baseline_anchor != v5')
    for k, want in (('design_only', True), ('runtime_attached', False),
                    ('no_runtime_activation', True), ('no_db_write', True),
                    ('no_borea_activation', True)):
        if fx.get(k) is not want:
            fail('meta', f'fixture.{k} must be {want}')

    # 2. DW catalog records
    if not DW_CATALOG.exists():
        fail('io', f'DW catalog missing')
        return emit('FAIL', {})
    cat = json.loads(DW_CATALOG.read_text(encoding='utf-8'))
    records = cat.get('records') or []
    if len(records) != 13:
        fail('count', f'DW catalog count != 13 (got {len(records)})')
    fx_records = fx.get('records') or []
    if len(fx_records) != 13:
        fail('count', f'fixture records != 13 (got {len(fx_records)})')

    cat_ids = {r['divine_weapon_id'] for r in records}
    fx_ids = {r['divine_weapon_id'] for r in fx_records}
    if cat_ids != fx_ids:
        fail('match', f'fixture vs catalog id mismatch: extra={fx_ids-cat_ids} missing={cat_ids-fx_ids}')

    # 3. catalog-level safety flags
    cat_flags = (
        ('runtime_attached', False), ('battle_runtime_attached', False),
        ('hp_bar_runtime_attached', False), ('gacha_attached', False),
        ('roster_activation_attached', False), ('vfx_runtime_attached', False),
        ('borea_activation_allowed', False), ('balance_values_finalized', False),
        ('do_not_treat_as_live_power', True),
    )
    for k, want in cat_flags:
        if cat.get(k) is not want:
            fail('catalog_flags', f'DW catalog.{k}={cat.get(k)!r} expected {want}')

    # 4. per-record cross-checks
    by_owner_to_6star = set()
    h6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    six_star_ids = {e['hero_id'] for e in h6.get('entries') or []}
    rg_split = {'launch_base': 0, 'launch_extra_premium': 0}
    for r in records:
        wid = r.get('divine_weapon_id')
        owner = r.get('hero_id')
        if r.get('catalog_status') != 'catalog_only':
            fail('record', f'{wid} catalog_status != catalog_only (got {r.get("catalog_status")!r})')
        if r.get('runtime_attached') is not False:
            fail('record', f'{wid} runtime_attached must be false')
        if r.get('battle_runtime_attached') is not False:
            fail('record', f'{wid} battle_runtime_attached must be false')
        if r.get('balance_values_finalized') is not False:
            fail('record', f'{wid} balance_values_finalized must be false')
        if r.get('exclusive_to_hero') is not True:
            fail('record', f'{wid} exclusive_to_hero must be true')
        if owner not in six_star_ids:
            fail('crosslink', f'{wid} owner_hero_id {owner!r} not present in 6★ catalog')
        else:
            by_owner_to_6star.add(owner)
        rg = r.get('release_group')
        if rg in rg_split:
            rg_split[rg] += 1
        else:
            warn('record', f'{wid} release_group={rg!r} not in expected split')
        # safety_flags block
        sf = r.get('safety_flags') or {}
        for k, want in (('runtime_attached', False), ('battle_runtime_attached', False),
                        ('hp_bar_runtime_attached', False), ('vfx_runtime_attached', False),
                        ('gacha_attached', False), ('roster_activation_attached', False)):
            if sf.get(k) is not want:
                fail('record_safety', f'{wid}.safety_flags.{k}={sf.get(k)!r} expected {want}')
    if rg_split != fx.get('expected_release_group_split'):
        fail('rg_split', f'release_group split mismatch: got {rg_split}, expected {fx.get("expected_release_group_split")}')

    # 5. Borea special checks
    borea_rec = next((r for r in records if r['divine_weapon_id'] == 'borea_wings_of_the_north_wind'), None)
    if not borea_rec:
        fail('borea', 'borea_wings_of_the_north_wind record missing')
    else:
        if borea_rec.get('hero_id') != 'greek_borea':
            fail('borea', f'borea DW owner != greek_borea (got {borea_rec.get("hero_id")!r})')
        if borea_rec.get('release_group') != 'launch_extra_premium':
            fail('borea', 'borea DW release_group must be launch_extra_premium')

    # Legacy borea hero_id must not appear anywhere in DW catalog
    blob = json.dumps(cat, ensure_ascii=False)
    if '"borea"' in blob or '"legacy_borea"' in blob or '"primordial_gaia"' in blob:
        # token check (whole-token via json strings)
        for forbidden in ('"borea"', '"legacy_borea"', '"primordial_gaia"'):
            if forbidden in blob:
                fail('legacy', f'forbidden token {forbidden} present in DW catalog')

    # 6. Routes: no equip/activate endpoint
    if ROUTES_DIR.exists():
        for p in ROUTES_DIR.glob('*.py'):
            try:
                t = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for tok in fx.get('forbidden_runtime_route_tokens') or []:
                if tok in t:
                    fail('route', f'{p.name}: contains forbidden runtime token {tok!r}')

    # 7. UI: no runtime Pressable in divine-weapons-catalog.tsx
    if UI_DW.exists():
        ut = UI_DW.read_text(encoding='utf-8', errors='ignore')
        # No POST/PUT/PATCH/DELETE
        for verb in ("method: 'POST'", 'method: "POST"', "method: 'PUT'", "method: 'PATCH'", "method: 'DELETE'"):
            if verb in ut:
                fail('ui', f'UI uses forbidden HTTP verb: {verb}')
        for tok in fx.get('forbidden_ui_pressable_tokens') or []:
            if tok in ut:
                fail('ui', f'UI contains forbidden Pressable/action token: {tok!r}')

    # 8. API smoke: /api/heroes count 100 + Borea hidden + legacy 404
    code, heroes = http_get('/heroes')
    if code != 200 or not isinstance(heroes, list):
        fail('api', f'/api/heroes status={code}')
    else:
        if len(heroes) != 100:
            fail('api', f'/api/heroes count={len(heroes)} != 100')
        ids = [h.get('id', '') for h in heroes]
        for forbidden in ('borea', 'greek_borea', 'primordial_gaia'):
            if forbidden in ids:
                fail('api', f'/api/heroes leaks {forbidden!r}')
    # DW endpoints
    for ep in ('/divine-weapons/catalogs/summary', '/divine-weapons/catalogs/all',
               '/divine-weapons/catalogs/by-hero/greek_borea'):
        code, _ = http_get(ep)
        if code != 200:
            fail('api', f'{ep} got {code} expected 200')
    code, _ = http_get('/divine-weapons/catalogs/by-hero/borea')
    if code != 404:
        fail('api', f'/divine-weapons/catalogs/by-hero/borea got {code} expected 404')

    audit_result = 'PASS' if not failures else 'FAIL'
    result = {
        'result_id': 'divine_weapon_preview_catalog_only_fixture_result_v1',
        'task_origin': 'RM1.33-H',
        'fixture_id': fx.get('fixture_id'),
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'audit_result': audit_result,
        'total_dw_records': len(records),
        'fixture_records_matched': sorted(cat_ids & fx_ids),
        'release_group_split': rg_split,
        'borea_dw_safe': borea_rec is not None and borea_rec.get('hero_id') == 'greek_borea' and cat.get('borea_activation_allowed') is False,
        'no_legacy_borea_token': '"borea"' not in blob and '"legacy_borea"' not in blob,
        'six_star_owner_crosslinks_ok': by_owner_to_6star.issubset(six_star_ids) and len(by_owner_to_6star) == 13,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132c2_v5',
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_mutation': True,
        'failures': failures,
        'warnings': warnings,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return emit(audit_result, result)


def emit(audit_result: str, result: dict) -> int:
    print('=' * 72)
    print('RM1.33-H Divine Weapon Preview Catalog-Only Fixture Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures: print(f'  - {f}')
    if result:
        print(f'\n  total_dw_records       : {result.get("total_dw_records")}')
        print(f'  release_group_split    : {result.get("release_group_split")}')
        print(f'  borea_dw_safe          : {result.get("borea_dw_safe")}')
        print(f'  legacy borea absent    : {result.get("no_legacy_borea_token")}')
        print(f'  6★ owner crosslinks ok : {result.get("six_star_owner_crosslinks_ok")}')
    print(f'\nResult JSON: {RESULT_OUT}')
    print(f'\nRESULT: {audit_result}')
    return 0 if audit_result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
