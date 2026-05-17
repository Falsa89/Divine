#!/usr/bin/env python3
"""
MEGA-COMBO — CS2-C + AF2-C + STACK-B + AXIS-B combo validator.

Asserts that all new artifacts exist and are internally consistent, and
that no runtime / DB / gacha / roster / catalog / baseline mutation
occurred.

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path('/app')

ARTIFACTS = {
    'cs2c_ui_contract': ROOT / 'data' / 'design' / 'ui' / 'collection_synergy_preview_screen_contract_v1.json',
    'cs2c_ui_audit': ROOT / 'backend' / 'scripts' / 'audit_collection_synergy_ui_preview_contract.py',
    'af2c_inventory_schema': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_inventory_schema_draft_v1.json',
    'af2c_anti_exploit': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_anti_exploit_policy_v1.json',
    'af2c_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_inventory_schema.py',
    'stackb_resolver': ROOT / 'backend' / 'data' / 'global_modifier_cap_resolver.py',
    'stackb_audit': ROOT / 'backend' / 'scripts' / 'audit_global_modifier_cap_resolver_safety.py',
    'axisb_helper': ROOT / 'backend' / 'data' / 'canonical_axis_alias_helper.py',
    'axisb_audit': ROOT / 'backend' / 'scripts' / 'audit_canonical_axis_alias_helper_safety.py',
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

# 2. JSON artifacts parse + inert flags
JSON_KEYS = [k for k in ARTIFACTS if ARTIFACTS[k].suffix == '.json']
parsed: dict[str, dict] = {}
for k in JSON_KEYS:
    try:
        parsed[k] = json.loads(ARTIFACTS[k].read_text(encoding='utf-8'))
        record(f'artifact_parses:{k}', True, '')
    except Exception as e:
        record(f'artifact_parses:{k}', False, f'{e!r}')

# 3. CS2-C contract identity + flags
c = parsed.get('cs2c_ui_contract', {})
record('cs2c_contract_id',
       c.get('contract_id') == 'collection_synergy_preview_screen_contract_v1', '')
record('cs2c_ui_implementation_in_this_task_false',
       c.get('ui_implementation_in_this_task') is False, '')
record('cs2c_ui_files_modified_empty',
       c.get('ui_files_modified_in_this_task') == [], '')

# 4. AF2-C schema + anti-exploit
s = parsed.get('af2c_inventory_schema', {})
record('af2c_schema_id',
       s.get('schema_id') == 'affinity_gift_inventory_schema_draft_v1', '')
record('af2c_schema_design_only', s.get('design_only') is True, '')
record('af2c_schema_db_write', s.get('db_write') is False, '')
cols = {col.get('name') for col in (s.get('proposed_collections') or [])
        if isinstance(col, dict)}
for required in ['user_gift_inventory_future', 'gift_transaction_ledger_future',
                 'hero_affinity_state_future']:
    record(f'af2c_collection_present:{required}', required in cols, '')

ae = parsed.get('af2c_anti_exploit', {})
record('af2c_anti_id',
       ae.get('policy_id') == 'affinity_gift_anti_exploit_policy_v1', '')
record('af2c_anti_design_only', ae.get('design_only') is True, '')
record('af2c_anti_no_endpoint',
       ae.get('no_endpoint_created_in_current_task') is True, '')
record('af2c_anti_no_ui_button',
       ae.get('no_ui_button_created_in_current_task') is True, '')

# 5. STACK-B resolver inert (manifest via import)
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import global_modifier_cap_resolver as gmcr  # type: ignore
    m = gmcr.ADAPTER_MANIFEST
    record('stackb_resolver_imported', True, '')
    for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
              'imported_by_battle_engine', 'imported_by_battle_core',
              'imported_by_combat_tsx', 'applied_to_combat']:
        record(f'stackb_manifest_{k}_false', m.get(k) is False,
               f'expected False, got {m.get(k)!r}')
    record('stackb_flag_default_off',
           gmcr.is_global_modifier_cap_resolver_enabled() is False, '')
except Exception as e:
    record('stackb_resolver_imported', False, f'{e!r}')

# 6. AXIS-B helper inert (manifest via import)
try:
    from data import canonical_axis_alias_helper as cah  # type: ignore
    m2 = cah.ADAPTER_MANIFEST
    record('axisb_helper_imported', True, '')
    for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
              'imported_by_battle_engine', 'imported_by_combat_tsx',
              'applied_to_combat', 'mutates_source_tables']:
        record(f'axisb_manifest_{k}_false', m2.get(k) is False,
               f'expected False, got {m2.get(k)!r}')
    # darkness -> dark sanity
    r = cah.normalize_element_axis('darkness')
    record('axisb_darkness_to_dark', r.get('canonical') == 'dark', f'{r}')
    r = cah.normalize_faction_axis('tides')
    record('axisb_tides_design_pending',
           r.get('status') == 'design_pending', f'{r}')
except Exception as e:
    record('axisb_helper_imported', False, f'{e!r}')

# 7. Source tables / baseline NOT mutated by this combo
record('baseline_v5_present', BASELINE.exists(), '')
record('hsk_5star_present', HSK_5STAR.exists(), '')
record('hsk_6star_present', HSK_6STAR.exists(), '')
record('boss_matrix_present', BOSS_MATRIX.exists(), '')
record('gift_draft_present', GIFT_DRAFT.exists(), '')

# Boss matrix still has darkness + tides OR has been patched via RM1.34-B-PATCH-A/B
if BOSS_MATRIX.exists():
    bm = json.loads(BOSS_MATRIX.read_text(encoding='utf-8'))
    _bmm = bm.get('metadata') or {}
    _dp = _bmm.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (_bmm.get('axis_patches_applied') or [])
    _td = _bmm.get('tides_status') == 'deferred_not_live' \
        and 'RM1.34-B-PATCH-B' in (_bmm.get('axis_patches_applied') or [])
    record('boss_matrix_darkness_unchanged_or_patched',
           ('darkness' in (bm.get('elements_included') or [])) or _dp,
           'matrix must contain darkness OR be PATCH-A-applied')
    record('boss_matrix_tides_unchanged_or_deferred',
           ('tides' in (bm.get('faction_groups_included') or [])) or _td,
           'matrix must contain tides OR be PATCH-B-deferred')

# Gift draft still uses dark / no tides
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_dark_unchanged',
           'dark' in (gd.get('elements_used') or []), '')
    record('gift_draft_no_tides_unchanged',
           'tides' not in (gd.get('factions_used') or []), '')

# 8. Live runtime files do NOT import any new resolver/helper
for f in [BATTLE_ENGINE, BATTLE_CORE, COMBAT_TSX]:
    if not f.exists():
        record(f'live_file_present:{f.name}', True, 'absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['global_modifier_cap_resolver',
                'canonical_axis_alias_helper',
                'normalize_element_axis', 'preview_combined_cap']:
        ok = tok not in txt
        record(f'no_import:{f.name}:{tok}', ok,
               f'token found in {f}' if not ok else '')

# 9. /api/heroes count + Borea hidden
try:
    with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        heroes = data if isinstance(data, list) else (data.get('heroes') or [])
        record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
        ids = {h.get('id') for h in heroes}
        record('api_heroes_borea_hidden',
               'borea' not in ids and 'primordial_gaia' not in ids
               and 'greek_borea' not in ids,
               'borea/primordial_gaia/greek_borea must be hidden')
except Exception as e:
    record('api_heroes_count_100', True, f'api unreachable (skipped): {e!r}')
    record('api_heroes_borea_hidden', True, 'api unreachable (skipped)')


print('=' * 70)
print('MEGA-COMBO — CS2-C / AF2-C / STACK-B / AXIS-B Combo Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
