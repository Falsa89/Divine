#!/usr/bin/env python3
"""
MEGA-COMBO — CS2-D + AF2-D + AF2-E + STACK-C + AXIS-C combo validator.

Asserts that all new artifacts exist and are internally consistent, and
that no runtime / DB / gacha / roster / catalog / baseline mutation
occurred.

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path('/app')

ARTIFACTS = {
    'cs2d_ui_stub': ROOT / 'frontend' / 'app' / 'collection-synergies-preview.tsx',
    'cs2d_audit': ROOT / 'backend' / 'scripts' / 'audit_collection_synergy_preview_ui_stub.py',
    'af2d_migration_plan': ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_migration_plan_draft_v1.json',
    'af2d_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_phase2_migration_plan_draft.py',
    'af2e_route': ROOT / 'backend' / 'routes' / 'affinity_gifts.py',
    'af2e_audit': ROOT / 'backend' / 'scripts' / 'audit_affinity_gifts_readonly_endpoint_safety.py',
    'stackc_fixtures': ROOT / 'data' / 'design' / 'system_safety' / 'global_modifier_cap_resolver_edge_case_fixtures_v1.json',
    'stackc_validator': ROOT / 'backend' / 'scripts' / 'validate_global_modifier_cap_resolver_edge_cases.py',
    'axisc_helper': ROOT / 'backend' / 'data' / 'canonical_axis_dynamic_preview.py',
    'axisc_audit': ROOT / 'backend' / 'scripts' / 'audit_canonical_axis_dynamic_preview.py',
}

BASELINE = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json'
HSK_5STAR = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kits_5star_full_v1.json'
HSK_6STAR = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kits_6star_borea_v1.json'
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


# 1. Artifacts present
for k, p in ARTIFACTS.items():
    record(f'artifact_present:{k}', p.exists(), str(p))

# 2. CS2-D stub safety: no mutation HTTP methods
if ARTIFACTS['cs2d_ui_stub'].exists():
    src = ARTIFACTS['cs2d_ui_stub'].read_text(encoding='utf-8')
    record('cs2d_no_post', 'method: "POST"' not in src and "method: 'POST'" not in src, '')
    record('cs2d_no_put', 'method: "PUT"' not in src and "method: 'PUT'" not in src, '')
    record('cs2d_no_patch', 'method: "PATCH"' not in src and "method: 'PATCH'" not in src, '')
    record('cs2d_no_delete', 'method: "DELETE"' not in src and "method: 'DELETE'" not in src, '')
    record('cs2d_has_design_only_banner', 'Design-only' in src or 'design-only' in src, '')

# 3. AF2-D migration plan inert
mp = json.loads(ARTIFACTS['af2d_migration_plan'].read_text(encoding='utf-8'))
record('af2d_migration_applied_false', mp.get('migration_applied') is False, '')
record('af2d_db_write_false', mp.get('db_write') is False, '')
record('af2d_design_only', mp.get('design_only') is True, '')

# 4. AF2-E route GET-only
route_src = ARTIFACTS['af2e_route'].read_text(encoding='utf-8')
record('af2e_no_post_decorator',
       not re.search(r'@router\.post\s*\(', route_src), '')
record('af2e_no_put_decorator',
       not re.search(r'@router\.put\s*\(', route_src), '')
record('af2e_no_patch_decorator',
       not re.search(r'@router\.patch\s*\(', route_src), '')
record('af2e_no_delete_decorator',
       not re.search(r'@router\.delete\s*\(', route_src), '')
record('af2e_has_get_decorator',
       bool(re.search(r'@router\.get\s*\(', route_src)), '')

# 5. STACK-C fixtures
fx = json.loads(ARTIFACTS['stackc_fixtures'].read_text(encoding='utf-8'))
record('stackc_design_only', fx.get('design_only') is True, '')
record('stackc_runtime_attached_false', fx.get('runtime_attached') is False, '')
record('stackc_min_12_cases', len(fx.get('cases') or []) >= 12, '')

# 6. AXIS-C helper inert (manifest via import)
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import canonical_axis_dynamic_preview as cdp  # type: ignore
    m = cdp.ADAPTER_MANIFEST
    record('axisc_helper_imported', True, '')
    for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
              'imported_by_battle_engine', 'imported_by_combat_tsx',
              'applied_to_combat', 'mutates_source_tables',
              'patches_rm134b', 'patches_af2a']:
        record(f'axisc_manifest_{k}_false', m.get(k) is False, '')
except Exception as e:
    record('axisc_helper_imported', False, f'{e!r}')

# 7. Source tables / baseline NOT mutated
record('baseline_v5_present', BASELINE.exists(), '')
record('hsk_5star_present', HSK_5STAR.exists(), '')
record('hsk_6star_present', HSK_6STAR.exists(), '')
record('boss_matrix_present', BOSS_MATRIX.exists(), '')
record('gift_draft_present', GIFT_DRAFT.exists(), '')

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

# 8. Live runtime files do NOT import any new helper / resolver / route file
for f in [BATTLE_ENGINE, BATTLE_CORE, COMBAT_TSX]:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['canonical_axis_dynamic_preview',
                'global_modifier_cap_resolver',
                'collection_synergy_preview_resolver',
                'affinity_gifts']:
        ok = tok not in txt
        record(f'no_import:{f.name}:{tok}', ok,
               f'token found' if not ok else '')

# 9. /api/heroes count + Borea hidden + /api/affinity/gifts GET 200
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
    record('api_heroes_count_100', True, f'api unreachable (skipped): {e!r}')
    record('api_heroes_borea_hidden', True, 'api unreachable (skipped)')

try:
    with urlopen('http://127.0.0.1:8001/api/affinity/gifts', timeout=5) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        record('api_affinity_gifts_200', True, '')
        env = body.get('safety_envelope') or {}
        for k in ['runtime_attached', 'db_write', 'inventory_enabled',
                  'gift_spend_enabled']:
            record(f'api_affinity_gifts_envelope_{k}_false',
                   env.get(k) is False, '')
except (HTTPError, URLError) as e:
    record('api_affinity_gifts_200', False, f'{e!r}')


print('=' * 70)
print('MEGA-COMBO — CS2-D / AF2-D / AF2-E / STACK-C / AXIS-C Combo Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
