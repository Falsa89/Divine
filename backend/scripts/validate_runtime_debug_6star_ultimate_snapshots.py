#!/usr/bin/env python3
"""
RM1.33-F — 6★ Ultimate Runtime Debug Snapshot Fixture v2 Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Validates `hero_skill_kit_runtime_debug_6star_ultimate_snapshot_fixtures_v2.json`
by calling the live debug preview endpoint for each of the 13 native 6★
ultimate slots and verifying the inert contract.

Also writes a machine-readable result JSON at:
- /app/data/design/hero_skill_kits/hero_skill_kit_runtime_debug_6star_ultimate_snapshot_result_v2.json

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
FIXTURE = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_runtime_debug_6star_ultimate_snapshot_fixtures_v2.json'
RESULT_OUT = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_runtime_debug_6star_ultimate_snapshot_result_v2.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
API = 'http://localhost:8001/api'

EXPECTED_HERO_IDS = (
    'greek_athena', 'mesopotamian_tiamat', 'egyptian_sekhmet',
    'greek_artemis', 'japanese_raijin', 'japanese_susanoo',
    'celtic_morrigan', 'greek_gaia', 'japanese_amaterasu',
    'egyptian_isis', 'cursed_pestilence_horseman',
    'primordial_nyx', 'greek_borea',
)

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []
case_results: list[dict] = []


def fail(sec: str, msg: str) -> None: failures.append(f'[{sec}] {msg}')
def warn(sec: str, msg: str) -> None: warnings.append(f'[{sec}] {msg}')
def info(msg: str) -> None: infos.append(msg)


def http_get(path: str, timeout: float = 6.0) -> tuple[int, dict | None]:
    try:
        req = urllib.request.Request(API + path, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return -1, {'error': str(e)}


def check_case(case: dict) -> dict:
    hero_id = case['hero_id']
    slot = case['slot']
    context = case['context']
    exp = case['expected']
    qs = urllib.parse.urlencode({'hero_id': hero_id, 'slot': slot, 'context': context})
    code, body = http_get(f'/hero-skill-kits/runtime/debug/preview?{qs}')

    rec = {
        'case_id': case['case_id'],
        'hero_id': hero_id,
        'slot': slot,
        'context': context,
        'http_status': code,
        'pass_count': 0,
        'fail_count': 0,
        'details': [],
    }

    def assert_eq(name: str, got, want):
        ok = (got == want)
        rec['details'].append({'check': name, 'got': got, 'want': want, 'ok': ok})
        if ok:
            rec['pass_count'] += 1
        else:
            rec['fail_count'] += 1
            fail(case['case_id'], f'{name}: got={got!r} want={want!r}')

    # 1. HTTP status
    assert_eq('http_status', code, exp.get('http_status', 200))
    if body is None or not isinstance(body, dict):
        fail(case['case_id'], 'response not JSON')
        return rec

    # 2. rarity
    assert_eq('rarity', body.get('rarity'), exp.get('rarity'))

    # 3. normalized_skill_slot
    nss = body.get('normalized_skill_slot') or {}
    exp_nss = exp.get('normalized_skill_slot') or {}
    for k in ('slot', 'skill_type', 'runtime_attached', 'battle_runtime_attached'):
        if k in exp_nss:
            assert_eq(f'normalized_skill_slot.{k}', nss.get(k), exp_nss[k])

    # 4. runtime_candidate
    rc = body.get('runtime_candidate') or {}
    exp_rc = exp.get('runtime_candidate') or {}
    for k in ('enabled', 'reason', 'feature_flag', 'feature_flag_value',
              'payload', 'is_disabled_runtime_result',
              'runtime_attached', 'battle_runtime_attached'):
        if k in exp_rc:
            assert_eq(f'runtime_candidate.{k}', rc.get(k), exp_rc[k])

    # 5. cap_policy_preview
    cpp = body.get('cap_policy_preview') or {}
    exp_cpp = exp.get('cap_policy_preview') or {}
    for k in ('applied_to_combat', 'runtime_attached', 'battle_runtime_attached', 'preview_only'):
        if k in exp_cpp:
            assert_eq(f'cap_policy_preview.{k}', cpp.get(k), exp_cpp[k])

    # 6. safety_envelope
    se = body.get('safety_envelope') or {}
    exp_se = exp.get('safety_envelope') or {}
    for k in ('debug_only', 'read_only', 'runtime_enabled', 'applied_to_combat',
              'db_write', 'catalog_write', 'roster_write', 'gacha_write',
              'ui_runtime_control'):
        if k in exp_se:
            assert_eq(f'safety_envelope.{k}', se.get(k), exp_se[k])

    # 7. borea_preview (only on greek_borea case)
    if hero_id == 'greek_borea':
        bp = body.get('borea_preview') or {}
        exp_bp = exp.get('borea_preview') or {}
        for k in ('no_activation', 'not_visible_in_heroes', 'marchio_boreale_owner_only',
                  'borea_activation_allowed', 'catalog_only', 'release_group'):
            if k in exp_bp:
                assert_eq(f'borea_preview.{k}', bp.get(k), exp_bp[k])

    # 8. Marchio leak check: marchio_boreale must NOT appear in core_status_ids of non-Borea heroes
    core_sids = (nss.get('core_status_ids') or [])
    has_marchio = ('marchio_boreale' in core_sids)
    expected_marchio = exp.get('marchio_boreale_in_core_status_ids', False)
    assert_eq('marchio_boreale_in_core_status_ids', has_marchio, expected_marchio)

    return rec


def main() -> int:
    if not FIXTURE.exists():
        fail('io', f'fixture missing: {FIXTURE}')
        return emit(audit_result='FAIL')
    try:
        fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'fixture parse error: {e}')
        return emit(audit_result='FAIL')

    if fixture.get('fixture_id') != 'hero_skill_kit_runtime_debug_6star_ultimate_snapshot_fixtures_v2':
        fail('meta', f"fixture_id mismatch: {fixture.get('fixture_id')!r}")
    if fixture.get('task_origin') != 'RM1.33-F':
        fail('meta', f"task_origin != RM1.33-F: {fixture.get('task_origin')!r}")

    cases = fixture.get('cases') or []
    if len(cases) != 13:
        fail('fixture', f'expected 13 cases, got {len(cases)}')
    hero_ids = [c.get('hero_id') for c in cases]
    if set(hero_ids) != set(EXPECTED_HERO_IDS):
        fail('fixture', f'hero_id set mismatch: extra={set(hero_ids)-set(EXPECTED_HERO_IDS)} missing={set(EXPECTED_HERO_IDS)-set(hero_ids)}')
    if len([c for c in cases if c.get('slot') == 'ultimate']) != 13:
        fail('fixture', 'all 13 cases must have slot=ultimate')

    # 1. Coverage endpoint global check
    code, cov = http_get('/hero-skill-kits/runtime/debug/coverage')
    if code != 200 or not isinstance(cov, dict):
        fail('coverage', f'coverage endpoint not 200 (code={code})')
    else:
        info(f'coverage 6star_ultimate_is_true_ultimate_preserved={cov.get("6star_ultimate_is_true_ultimate_preserved")}')
        if cov.get('6star_ultimate_is_true_ultimate_preserved') != 13:
            fail('coverage', f'6star_ultimate_is_true_ultimate_preserved={cov.get("6star_ultimate_is_true_ultimate_preserved")} != 13')
        if cov.get('marchio_boreale_borea_only') is not True:
            fail('coverage', 'marchio_boreale_borea_only must be true')
        if cov.get('borea_catalog_only') is not True:
            fail('coverage', 'borea_catalog_only must be true')
        if cov.get('runtime_enabled') is not False:
            fail('coverage', 'runtime_enabled must be false')

    # 2. Per-case checks
    for case in cases:
        rec = check_case(case)
        case_results.append(rec)

    # 3. Marchio leak count across non-Borea cases
    leak_count = 0
    for r in case_results:
        if r['hero_id'] == 'greek_borea':
            continue
        for det in r['details']:
            if det['check'] == 'marchio_boreale_in_core_status_ids' and det['got'] is True:
                leak_count += 1
    if leak_count != 0:
        fail('marchio_leak', f'{leak_count} non-Borea cases leak marchio_boreale into core_status_ids')

    # 4. /api/heroes still 100, Borea hidden
    code, heroes = http_get('/heroes')
    if code != 200 or not isinstance(heroes, list):
        fail('heroes', f'/api/heroes not list 200 (code={code})')
    else:
        if len(heroes) != 100:
            fail('heroes', f'/api/heroes count={len(heroes)} != 100')
        ids = [h.get('id', '') for h in heroes]
        for forbidden in ('borea', 'greek_borea', 'primordial_gaia'):
            if forbidden in ids:
                fail('heroes', f'/api/heroes leaks {forbidden!r}')

    # 5. legacy aliases 404
    for alias in ('borea', 'primordial_gaia'):
        code, _ = http_get(f'/hero-skill-kits/catalogs/by-hero/{alias}')
        if code != 404:
            fail('legacy_alias', f'/hero-skill-kits/catalogs/by-hero/{alias} got {code} expected 404')

    # 6. baseline v4 anchor present
    if not BASELINE_V4.exists():
        fail('baseline', f'baseline v4 missing: {BASELINE_V4}')

    audit_result = 'PASS' if not failures else 'FAIL'
    # Write result JSON
    result = {
        'result_id': 'hero_skill_kit_runtime_debug_6star_ultimate_snapshot_result_v2',
        'task_origin': 'RM1.33-F',
        'fixture_id': fixture.get('fixture_id'),
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'audit_result': audit_result,
        'total_cases': len(cases),
        'cases_pass': sum(1 for r in case_results if r['fail_count'] == 0),
        'cases_fail': sum(1 for r in case_results if r['fail_count'] > 0),
        'marchio_leak_count_non_borea': leak_count,
        'coverage_snapshot': {
            'runtime_enabled': cov.get('runtime_enabled') if isinstance(cov, dict) else None,
            '6star_ultimate_is_true_ultimate_preserved': cov.get('6star_ultimate_is_true_ultimate_preserved') if isinstance(cov, dict) else None,
            'borea_catalog_only': cov.get('borea_catalog_only') if isinstance(cov, dict) else None,
            'marchio_boreale_borea_only': cov.get('marchio_boreale_borea_only') if isinstance(cov, dict) else None,
        },
        'case_results': case_results,
        'failures': failures,
        'warnings': warnings,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132b_v4',
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_mutation': True,
    }
    RESULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    return emit(audit_result=audit_result)


def emit(audit_result: str) -> int:
    print('=' * 72)
    print('RM1.33-F 6★ Ultimate Snapshot Fixture v2 Validator')
    print('=' * 72)
    for i in infos:
        print(f'INFO: {i}')
    for r in case_results:
        status = 'PASS' if r['fail_count'] == 0 else 'FAIL'
        print(f'  {status}  {r["case_id"]:50s}  http={r["http_status"]}  pass={r["pass_count"]}  fail={r["fail_count"]}')
    for w in warnings:
        print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures[:50]:
            print(f'  - {f}')
    print(f'\nResult: {RESULT_OUT}')
    print(f'\nRESULT: {audit_result}')
    return 0 if audit_result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
