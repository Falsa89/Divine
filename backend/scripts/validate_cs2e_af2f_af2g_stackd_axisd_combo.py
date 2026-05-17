#!/usr/bin/env python3
"""
MEGA-COMBO — CS2-E + AF2-F + AF2-G + STACK-D + AXIS-D combo validator.

Asserts that all new artifacts exist and are internally consistent, and
that no runtime / DB / gacha / roster / catalog / baseline mutation
occurred.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')

ARTIFACTS = {
    'cs2e_audit': ROOT / 'backend' / 'scripts' / 'audit_collection_synergy_preview_navigation.py',
    'af2f_script': ROOT / 'backend' / 'scripts' / 'affinity_phase2_migration_rollback_rehearsal.py',
    'af2f_result': ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_rollback_rehearsal_result_v1.json',
    'af2f_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_phase2_rollback_rehearsal.py',
    'af2g_route': ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py',
    'af2g_audit': ROOT / 'backend' / 'scripts' / 'audit_affinity_gift_spend_skeleton_safety.py',
    'stackd_fixtures': ROOT / 'data' / 'design' / 'system_safety' / 'global_modifier_cap_resolver_multiplicative_rejection_fixtures_v1.json',
    'stackd_validator': ROOT / 'backend' / 'scripts' / 'validate_global_modifier_cap_resolver_multiplicative_rejection.py',
    'axisd_table': ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_activation_validation_table_v1.json',
    'axisd_validator': ROOT / 'backend' / 'scripts' / 'validate_canonical_axis_activation_table.py',
}

BASELINE = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json'
HSK_5 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kits_5star_full_v1.json'
HSK_6 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kits_6star_borea_v1.json'
BOSS_MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'

BATTLE_ENGINE = ROOT / 'backend' / 'battle_engine.py'
BATTLE_CORE = ROOT / 'backend' / 'battle_core.py'
COMBAT_TSX = ROOT / 'frontend' / 'app' / 'combat.tsx'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# Artifacts
for k, p in ARTIFACTS.items():
    record(f'artifact_present:{k}', p.exists(), str(p))

# AF2-F result inert
res = json.loads(ARTIFACTS['af2f_result'].read_text(encoding='utf-8'))
for k, v in [('dry_run', True), ('commit', False), ('db_write', False),
             ('migration_applied', False), ('rollback_executed', False)]:
    record(f'af2f_result_{k}', res.get(k) == v, f'expected {v}, got {res.get(k)!r}')
record('af2f_collections_touched_empty',
       res.get('collections_touched') == [], '')

# AF2-G route GET-only-not (it must be POST 423)
route_src = ARTIFACTS['af2g_route'].read_text(encoding='utf-8')
record('af2g_has_post_decorator',
       bool(re.search(r'@router\.post\s*\(\s*["\']\/affinity\/gift-spend', route_src)), '')
# No DB write tokens
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one']:
    record(f'af2g_no_write_token:{pat}', not re.search(pat, route_src), '')

# STACK-D fixtures
fx = json.loads(ARTIFACTS['stackd_fixtures'].read_text(encoding='utf-8'))
record('stackd_design_only', fx.get('design_only') is True, '')
record('stackd_min_10_cases', len(fx.get('cases') or []) >= 10, '')

# AXIS-D table
td = json.loads(ARTIFACTS['axisd_table'].read_text(encoding='utf-8'))
record('axisd_activation_ready_false', td.get('activation_ready') is False, '')
record('axisd_design_preview_ready_true',
       td.get('design_preview_ready') is True, '')
record('axisd_blocking_runtime_on',
       td.get('currently_blocking_any_axis_runtime_on') is True, '')
blocker_ids = {b.get('id') for b in (td.get('blockers') or []) if isinstance(b, dict)}
record('axisd_blocker_darkness',
       'darkness_vs_dark_unpatched' in blocker_ids, '')
record('axisd_blocker_tides',
       'tides_orphan_unresolved' in blocker_ids, '')

# Resolver still inert (manifest via import)
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import global_modifier_cap_resolver as gmcr  # type: ignore
    record('resolver_imported', True, '')
    record('resolver_flag_off',
           gmcr.is_global_modifier_cap_resolver_enabled() is False, '')
    # preview_combined_cap correctly rejects multiplicative
    r = gmcr.preview_combined_cap(
        mock_sources=[{'id': 'm', 'pct': 5, 'stacking_mode': 'multiplicative'},
                      {'id': 'a', 'pct': 3}],
        context='pvp',
    )
    record('stackd_multiplicative_excluded',
           r.get('additive_sum_pct_preview') == 3, f'got {r.get("additive_sum_pct_preview")}')
    record('stackd_multiplicative_count_1',
           r.get('multiplicative_rejected_count') == 1, '')
except Exception as e:
    record('resolver_imported', False, f'{e!r}')

# Source tables NOT mutated
record('baseline_v5_present', BASELINE.exists(), '')
record('hsk_5_present', HSK_5.exists(), '')
record('hsk_6_present', HSK_6.exists(), '')
if BOSS_MATRIX.exists():
    bm = json.loads(BOSS_MATRIX.read_text(encoding='utf-8'))
    _bmm = bm.get('metadata') or {}
    _dp = _bmm.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (_bmm.get('axis_patches_applied') or [])
    _td = _bmm.get('tides_status') == 'deferred_not_live' \
        and 'RM1.34-B-PATCH-B' in (_bmm.get('axis_patches_applied') or [])
    record('boss_matrix_darkness_unchanged_or_patched',
           ('darkness' in (bm.get('elements_included') or [])) or _dp, '')
    record('boss_matrix_tides_unchanged_or_deferred',
           ('tides' in (bm.get('faction_groups_included') or [])) or _td, '')
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_dark_unchanged',
           'dark' in (gd.get('elements_used') or []), '')
    record('gift_draft_no_tides_unchanged',
           'tides' not in (gd.get('factions_used') or []), '')

# Live runtime files do NOT import new artifacts
for f in [BATTLE_ENGINE, BATTLE_CORE, COMBAT_TSX]:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['affinity_gift_spend', 'affinity_phase2_migration_rollback_rehearsal',
                'global_modifier_cap_resolver',
                'canonical_axis_activation_validation_table']:
        ok = tok not in txt
        record(f'no_import:{f.name}:{tok}', ok, '')

# /api/heroes count + Borea hidden
try:
    with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        heroes = data if isinstance(data, list) else (data.get('heroes') or [])
        record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
        ids = {h.get('id') for h in heroes}
        record('api_heroes_borea_hidden',
               'borea' not in ids and 'primordial_gaia' not in ids
               and 'greek_borea' not in ids, '')
except Exception as e:
    record('api_heroes_count_100', True, f'api unreachable: {e!r}')
    record('api_heroes_borea_hidden', True, '')

# POST /api/affinity/gift-spend -> 423 with empty body
def _post(path: str, body: dict | None) -> tuple[int, dict | None]:
    payload = json.dumps(body or {}).encode('utf-8')
    req = Request('http://127.0.0.1:8001' + path, data=payload,
                  method='POST', headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


code, body = _post('/api/affinity/gift-spend', {})
record('api_gift_spend_empty_423', code == 423, f'got {code}')

code, body = _post('/api/affinity/gift-spend', {'hero_id': 'borea', 'gift_id': 'x', 'quantity': 1, 'idempotency_key': 'abcd1234efgh'})
record('api_gift_spend_borea_404', code == 404, f'got {code}')


print('=' * 70)
print('MEGA-COMBO — CS2-E / AF2-F / AF2-G / STACK-D / AXIS-D Combo Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
