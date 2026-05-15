#!/usr/bin/env python3
"""
RM1.33-G — 5★ Runtime Debug Snapshot Rejection Fixture v2 Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Validates `hero_skill_kit_runtime_debug_5star_snapshot_fixtures_v2.json` by
hitting the live debug preview endpoint for all 20 native 5★ heroes across
their 5 valid slots (100 cases) and their 1 invalid slot (`ultimate`, 20 cases),
verifying:
- Valid slots: HTTP 200, runtime disabled, cap policy inert, safety envelope OFF.
- Invalid ultimate: HTTP 404 with `reason=invalid_slot_for_5star`, no fallback,
  no payload, safety envelope inert.
- skill_2 not true ultimate equivalent.
- 0 Marchio Boreale / Borea / Divine Weapon / Domain leakage in 5★ payloads.

Writes a machine-readable result JSON at:
- /app/data/design/hero_skill_kits/hero_skill_kit_runtime_debug_5star_snapshot_result_v2.json

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
FIXTURE = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_runtime_debug_5star_snapshot_fixtures_v2.json'
RESULT_OUT = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_runtime_debug_5star_snapshot_result_v2.json'
CATALOG_5STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
API = 'http://localhost:8001/api'

# Forbidden patterns that must NEVER appear as status/effect application in 5★ responses.
# NOTE: declarative cap policy fields naming the Marchio invariant (e.g.
#       `marchio_boreale_max_stacks`, `marchio_owner_hero_id: "greek_borea"`) are
#       ALLOWED — they are read-only system invariants in the cap policy preview,
#       not Borea/Marchio application to the 5★ hero. We therefore check semantically:
#         - `marchio_boreale` must NOT appear in normalized_skill_slot.core_status_ids
#         - `marchio_boreale` must NOT appear in normalized_skill_slot.core_effect_tags
#         - hero_id fields must NOT swap to greek_borea
#         - runtime DW / Domain live fields must not be `true`
FORBIDDEN_STATUS_IDS_IN_5STAR = ('marchio_boreale',)
FORBIDDEN_EFFECT_TAGS_IN_5STAR = ('marchio_boreale', 'ultimate_signature_upgrade')
FORBIDDEN_HERO_ID_SWAP = ('greek_borea',)
FORBIDDEN_LIVE_RUNTIME_KEY_TRUE = (
    'divine_weapon_runtime_active',
    'domain_runtime_active',
    'live_numeric_modifier_applied',
    'is_true_ultimate',
)

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []
valid_results: list[dict] = []
invalid_results: list[dict] = []


def fail(sec: str, msg: str) -> None: failures.append(f'[{sec}] {msg}')
def warn(sec: str, msg: str) -> None: warnings.append(f'[{sec}] {msg}')
def info(msg: str) -> None: infos.append(msg)


def http_get(path: str, timeout: float = 6.0) -> tuple[int, dict | None]:
    """Return (status_code, body_json_or_None). Reads body even on 4xx."""
    try:
        req = urllib.request.Request(API + path, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8', errors='ignore')
            return e.code, json.loads(body)
        except Exception:
            return e.code, None
    except Exception as e:
        return -1, {'error': str(e)}


def has_forbidden_in_5star(body: dict, requested_hero_id: str) -> list[str]:
    """Return a list of forbidden semantic findings in a 5★ preview response.

    Allowed: declarative cap-policy invariant fields that mention
    'marchio_boreale_max_stacks' or 'marchio_owner_hero_id=greek_borea'
    (these are read-only invariants, not Marchio/Borea application).

    Forbidden: any application of Marchio/Borea/DW-Domain runtime to the 5★ hero.
    """
    findings = []
    nss = body.get('normalized_skill_slot') or {}
    # 1) status_ids must not contain marchio_boreale
    sids = nss.get('core_status_ids') or []
    for s in sids:
        if s in FORBIDDEN_STATUS_IDS_IN_5STAR:
            findings.append(f'core_status_ids contains {s!r}')
    # 2) effect_tags must not contain marchio_boreale or ultimate_signature_upgrade
    etags = nss.get('core_effect_tags') or []
    for t in etags:
        if t in FORBIDDEN_EFFECT_TAGS_IN_5STAR:
            findings.append(f'core_effect_tags contains {t!r}')
    # 3) hero_id must NOT be swapped to greek_borea anywhere
    for path, obj in (
        ('body', body),
        ('normalized_skill_slot', nss),
        ('runtime_candidate', body.get('runtime_candidate') or {}),
        ('cap_policy_preview', body.get('cap_policy_preview') or {}),
    ):
        if isinstance(obj, dict):
            hid = obj.get('hero_id')
            if hid in FORBIDDEN_HERO_ID_SWAP and hid != requested_hero_id:
                findings.append(f'{path}.hero_id swapped to {hid!r}')
    # 4) runtime-live flags must not be true anywhere in the response
    def _walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in FORBIDDEN_LIVE_RUNTIME_KEY_TRUE and v is True:
                    findings.append(f'{path}.{k}=true forbidden in 5★')
                if isinstance(v, (dict, list)):
                    _walk(v, f'{path}.{k}')
        elif isinstance(node, list):
            for i, it in enumerate(node):
                _walk(it, f'{path}[{i}]')
    _walk(body, '$')
    # 5) borea_preview presence in 5★ is a leak
    if body.get('borea_preview'):
        findings.append('borea_preview present in 5★ response')
    return findings


def check_valid_slot(hero_id: str, slot: str, context: str) -> dict:
    qs = urllib.parse.urlencode({'hero_id': hero_id, 'slot': slot, 'context': context})
    code, body = http_get(f'/hero-skill-kits/runtime/debug/preview?{qs}')
    rec = {
        'hero_id': hero_id, 'slot': slot, 'context': context,
        'http_status': code, 'pass_count': 0, 'fail_count': 0,
    }
    case = f'{hero_id}/{slot}'

    if code != 200:
        rec['fail_count'] += 1
        fail(case, f'expected http 200, got {code}')
        return rec
    rec['pass_count'] += 1

    if not isinstance(body, dict):
        rec['fail_count'] += 1
        fail(case, 'response not JSON object')
        return rec

    # rarity
    if body.get('rarity') != '5star':
        fail(case, f'rarity={body.get("rarity")!r} != "5star"')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    # normalized slot
    nss = body.get('normalized_skill_slot') or {}
    if nss.get('runtime_attached') is not False:
        fail(case, 'normalized_skill_slot.runtime_attached must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if nss.get('battle_runtime_attached') is not False:
        fail(case, 'normalized_skill_slot.battle_runtime_attached must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1

    # runtime_candidate
    rc = body.get('runtime_candidate') or {}
    if rc.get('enabled') is not False:
        fail(case, 'runtime_candidate.enabled must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if rc.get('reason') != 'feature_flag_off':
        fail(case, f'runtime_candidate.reason={rc.get("reason")!r} != feature_flag_off'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if rc.get('payload') is not None:
        fail(case, 'runtime_candidate.payload must be null'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if rc.get('feature_flag') != 'SKILL_KIT_RUNTIME_ENABLED':
        fail(case, 'runtime_candidate.feature_flag must be SKILL_KIT_RUNTIME_ENABLED'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if rc.get('feature_flag_value') is not False:
        fail(case, 'runtime_candidate.feature_flag_value must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if rc.get('is_disabled_runtime_result') is not True:
        fail(case, 'runtime_candidate.is_disabled_runtime_result must be true'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1

    # cap_policy_preview
    cpp = body.get('cap_policy_preview') or {}
    if cpp.get('applied_to_combat') is not False:
        fail(case, 'cap_policy_preview.applied_to_combat must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if cpp.get('runtime_attached') is not False:
        fail(case, 'cap_policy_preview.runtime_attached must be false'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1
    if cpp.get('preview_only') is not True:
        fail(case, 'cap_policy_preview.preview_only must be true'); rec['fail_count'] += 1
    else: rec['pass_count'] += 1

    # safety_envelope
    se = body.get('safety_envelope') or {}
    for k, want in (
        ('debug_only', True), ('read_only', True), ('runtime_enabled', False),
        ('applied_to_combat', False), ('db_write', False),
        ('catalog_write', False), ('roster_write', False),
        ('gacha_write', False), ('ui_runtime_control', False),
    ):
        if se.get(k) is not want:
            fail(case, f'safety_envelope.{k}={se.get(k)!r} expected {want!r}'); rec['fail_count'] += 1
        else:
            rec['pass_count'] += 1

    # skill_2 special checks: not true ultimate
    if slot == 'skill_2':
        # skill_type must NOT be 'ultimate' for a 5★ skill_2 preview
        skill_type = nss.get('skill_type')
        if skill_type == 'ultimate':
            fail(case, f'skill_2 normalized_skill_slot.skill_type=ultimate (5★ skill_2 must not be true ultimate)')
            rec['fail_count'] += 1
        else:
            rec['pass_count'] += 1
        # Optional literal check
        if nss.get('is_true_ultimate') is True:
            fail(case, 'skill_2 is_true_ultimate=true forbidden for 5★')
            rec['fail_count'] += 1
        else:
            rec['pass_count'] += 1

    # Forbidden semantic leaks in 5★ response
    hits = has_forbidden_in_5star(body, hero_id)
    if hits:
        fail(case, f'forbidden 5★ leak: {hits}')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    # borea_preview must not be present in 5★ payloads (extra explicit)
    if body.get('borea_preview') is not None and bool(body.get('borea_preview')):
        fail(case, 'borea_preview present in 5★ response (forbidden)')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    return rec


def check_invalid_ultimate(hero_id: str, context: str) -> dict:
    qs = urllib.parse.urlencode({'hero_id': hero_id, 'slot': 'ultimate', 'context': context})
    code, body = http_get(f'/hero-skill-kits/runtime/debug/preview?{qs}')
    rec = {
        'hero_id': hero_id, 'slot': 'ultimate', 'context': context,
        'http_status': code, 'pass_count': 0, 'fail_count': 0,
    }
    case = f'{hero_id}/ultimate(invalid)'

    if code != 404:
        fail(case, f'expected 404 for 5★ ultimate, got {code}')
        rec['fail_count'] += 1
        return rec
    rec['pass_count'] += 1

    if not isinstance(body, dict):
        fail(case, '404 response missing JSON body')
        rec['fail_count'] += 1
        return rec

    detail = body.get('detail') or {}
    # error / reason / rarity / fallback_disabled
    if detail.get('error') != 'invalid_slot':
        fail(case, f'detail.error={detail.get("error")!r} != invalid_slot')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1
    if detail.get('reason') != 'invalid_slot_for_5star':
        fail(case, f'detail.reason={detail.get("reason")!r} != invalid_slot_for_5star')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1
    if detail.get('rarity') != '5star':
        fail(case, f'detail.rarity={detail.get("rarity")!r} != 5star')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1
    if detail.get('fallback_disabled') is not True:
        fail(case, 'detail.fallback_disabled must be true')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    # No runtime_candidate payload
    if 'runtime_candidate' in detail and detail['runtime_candidate']:
        fail(case, 'invalid ultimate must not contain runtime_candidate')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1
    if 'normalized_skill_slot' in detail and detail['normalized_skill_slot']:
        fail(case, 'invalid ultimate must not contain normalized_skill_slot')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    # safety_envelope inert
    se = detail.get('safety_envelope') or {}
    for k, want in (
        ('debug_only', True), ('read_only', True), ('runtime_enabled', False),
        ('applied_to_combat', False), ('db_write', False),
        ('catalog_write', False), ('roster_write', False),
        ('gacha_write', False),
    ):
        if se.get(k) is not want:
            fail(case, f'safety_envelope.{k}={se.get(k)!r} expected {want!r}')
            rec['fail_count'] += 1
        else:
            rec['pass_count'] += 1

    # Forbidden semantic leaks in invalid response (DETAIL only)
    detail_findings = has_forbidden_in_5star(detail, hero_id)
    if detail_findings:
        fail(case, f'forbidden 5★ leak in invalid response: {detail_findings}')
        rec['fail_count'] += 1
    else:
        rec['pass_count'] += 1

    return rec


def main() -> int:
    if not FIXTURE.exists():
        fail('io', f'fixture missing: {FIXTURE}')
        return emit('FAIL')
    try:
        fx = json.loads(FIXTURE.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'fixture parse error: {e}')
        return emit('FAIL')

    if fx.get('fixture_id') != 'hero_skill_kit_runtime_debug_5star_snapshot_fixtures_v2':
        fail('meta', f'fixture_id mismatch: {fx.get("fixture_id")!r}')
    if fx.get('task_origin') != 'RM1.33-G':
        fail('meta', f'task_origin != RM1.33-G: {fx.get("task_origin")!r}')

    # 1. fixture hero ids vs catalog
    if not CATALOG_5STAR.exists():
        fail('io', f'5★ catalog missing: {CATALOG_5STAR}')
        return emit('FAIL')
    cat = json.loads(CATALOG_5STAR.read_text(encoding='utf-8'))
    cat_ids = sorted([e['hero_id'] for e in cat.get('entries') or []])
    fx_ids = sorted(fx.get('hero_ids') or [])
    if cat_ids != fx_ids:
        fail('fixture', f'fixture hero_ids != 5★ catalog hero_ids; cat-only={set(cat_ids)-set(fx_ids)} fx-only={set(fx_ids)-set(cat_ids)}')
    if len(fx_ids) != 20:
        fail('fixture', f'expected 20 fixture heroes, got {len(fx_ids)}')

    # 2. valid_slots / invalid_slots / context_routing
    valid_slots = fx.get('valid_slots') or []
    if valid_slots != ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2']:
        fail('fixture', f'valid_slots mismatch: {valid_slots}')
    invalid_slots = fx.get('invalid_slots') or []
    if invalid_slots != ['ultimate']:
        fail('fixture', f'invalid_slots mismatch: {invalid_slots}')
    ctx_routing = fx.get('context_routing') or {}
    for s in valid_slots + invalid_slots:
        if s not in ctx_routing:
            fail('fixture', f'context_routing missing slot {s}')

    # 3. Run 100 valid + 20 invalid against live endpoint
    for hero_id in fx_ids:
        for slot in valid_slots:
            ctx = ctx_routing.get(slot, 'pvp')
            valid_results.append(check_valid_slot(hero_id, slot, ctx))
        ctx_u = ctx_routing.get('ultimate', 'pvp')
        invalid_results.append(check_invalid_ultimate(hero_id, ctx_u))

    # 4. Coverage endpoint
    code, cov = http_get('/hero-skill-kits/runtime/debug/coverage')
    if code != 200 or not isinstance(cov, dict):
        fail('coverage', f'coverage endpoint not 200 (code={code})')
    else:
        info(f'coverage 5star_ultimate_safely_rejected_count={cov.get("5star_ultimate_safely_rejected_count")}')
        if cov.get('5star_ultimate_safely_rejected_count') != 20:
            fail('coverage', f'5star_ultimate_safely_rejected_count={cov.get("5star_ultimate_safely_rejected_count")} != 20')
        if cov.get('runtime_enabled') is not False:
            fail('coverage', 'coverage.runtime_enabled must be false')
        if cov.get('marchio_boreale_borea_only') is not True:
            fail('coverage', 'coverage.marchio_boreale_borea_only must be true')

    # 5. /api/heroes still 100, Borea hidden
    code, heroes = http_get('/heroes')
    if code != 200 or not isinstance(heroes, list):
        fail('heroes', f'/api/heroes not 200 list (code={code})')
    else:
        if len(heroes) != 100:
            fail('heroes', f'/api/heroes count={len(heroes)} != 100')
        ids = [h.get('id', '') for h in heroes]
        for forbidden in ('borea', 'greek_borea', 'primordial_gaia'):
            if forbidden in ids:
                fail('heroes', f'/api/heroes leaks {forbidden!r}')

    # 6. legacy aliases 404
    for alias in ('borea', 'primordial_gaia'):
        code, _ = http_get(f'/hero-skill-kits/catalogs/by-hero/{alias}')
        if code != 404:
            fail('legacy_alias', f'/hero-skill-kits/catalogs/by-hero/{alias} got {code} expected 404')

    # 7. baseline anchor file present
    if not BASELINE_V4.exists():
        fail('baseline', f'baseline v4 missing: {BASELINE_V4}')

    audit_result = 'PASS' if not failures else 'FAIL'

    # Aggregate counters
    valid_total = len(valid_results)
    valid_passing = sum(1 for r in valid_results if r['fail_count'] == 0)
    invalid_total = len(invalid_results)
    invalid_passing = sum(1 for r in invalid_results if r['fail_count'] == 0)
    skill2_count = sum(1 for r in valid_results if r['slot'] == 'skill_2')
    skill2_passing = sum(1 for r in valid_results if r['slot'] == 'skill_2' and r['fail_count'] == 0)

    result = {
        'result_id': 'hero_skill_kit_runtime_debug_5star_snapshot_result_v2',
        'task_origin': 'RM1.33-G',
        'fixture_id': fx.get('fixture_id'),
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'audit_result': audit_result,
        'totals': {
            'heroes_covered': len(fx_ids),
            'valid_slot_cases_total': valid_total,
            'valid_slot_cases_passing': valid_passing,
            'invalid_ultimate_cases_total': invalid_total,
            'invalid_ultimate_cases_passing': invalid_passing,
            'skill_2_cases_total': skill2_count,
            'skill_2_cases_passing_not_true_ultimate': skill2_passing,
            'marchio_borea_dw_domain_leaks_in_5star': sum(1 for r in valid_results + invalid_results if r['fail_count'] > 0 and any('forbidden tokens' in fmsg for fmsg in failures if r['hero_id'] in fmsg)),
        },
        'coverage_snapshot': {
            'runtime_enabled': cov.get('runtime_enabled') if isinstance(cov, dict) else None,
            '5star_ultimate_safely_rejected_count': cov.get('5star_ultimate_safely_rejected_count') if isinstance(cov, dict) else None,
            'marchio_boreale_borea_only': cov.get('marchio_boreale_borea_only') if isinstance(cov, dict) else None,
            'borea_catalog_only': cov.get('borea_catalog_only') if isinstance(cov, dict) else None,
        },
        'valid_results': valid_results,
        'invalid_results': invalid_results,
        'failures': failures,
        'warnings': warnings,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132b_v4',
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_mutation': True,
    }
    RESULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    return emit(audit_result)


def emit(audit_result: str) -> int:
    print('=' * 72)
    print('RM1.33-G 5★ Snapshot Rejection Fixture v2 Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    valid_total = len(valid_results)
    valid_passing = sum(1 for r in valid_results if r['fail_count'] == 0)
    invalid_total = len(invalid_results)
    invalid_passing = sum(1 for r in invalid_results if r['fail_count'] == 0)
    print(f'  Valid 5★ slot cases   : {valid_passing}/{valid_total} PASS')
    print(f'  Invalid ultimate cases: {invalid_passing}/{invalid_total} PASS')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures[:50]:
            print(f'  - {f}')
    print(f'\nResult: {RESULT_OUT}')
    print(f'\nRESULT: {audit_result}')
    return 0 if audit_result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
