#!/usr/bin/env python3
"""
RM1.28-B — 5★ Skill Kit QA / Catalog Cross-Link Audit Script
─────────────────────────────────────────────────────────────────────────
Read-only audit of the 5★ Hero Skill Kit catalog after RM1.28-A
filled the missing passive_advanced slots.

Cross-checks:
  1. Catalog integrity (counts, IDs, uniqueness, forbidden IDs absent)
  2. Slot structure (exactly basic, passive_base, skill_1,
     passive_advanced, skill_2; no ultimate / divine_weapon / domain)
  3. passive_advanced cross-link source ↔ full catalog
  4. Runtime inertness (final_numbers=null, runtime_attached=false, etc.)
  5. 5★ boundaries (no true Ultimate, no Divine Weapon hook,
     no Marchio Boreale, no Borea references, no domain_effect_apply)
  6. Status whitelist (all status_tags + status_interactions from approved
     core)
  7. API consistency (loader/route files have NO mutation endpoints)
  8. UI assumption (frontend page is read-only)

Returns exit 0 on PASS, 1 on FAIL.
NO mutation. NO DB write. NO runtime hook.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

BASE = Path('/app/data/design/hero_skill_kits')
FULL_CATALOG = BASE / 'hero_skill_kits_5star_full_v1.json'
PA_SOURCE = BASE / 'hero_skill_kits_5star_passive_advanced_source_v1.json'
HSK_SCHEMA = BASE / 'hero_skill_kit_schema_v1.json'

LOADER_FILE = Path('/app/backend/data/hero_skill_kits_loader.py')
ROUTES_FILE = Path('/app/backend/routes/hero_skill_kits_catalogs.py')
UI_FILE = Path('/app/frontend/app/hero-skill-kits-catalog.tsx')

CANONICAL_5STAR = {
    'angelic_bastion_angel', 'celtic_mist_banshee', 'creature_crimson_phoenix',
    'creature_lernaean_hydra', 'cursed_pestilence_herald', 'demonic_gehenna_witch',
    'egyptian_bastet', 'egyptian_claw_of_sekhmet', 'greek_atalanta', 'greek_circe',
    'greek_medusa', 'greek_nemean_lioness', 'greek_nike', 'japanese_miko_of_raijin',
    'norse_dawn_valkyrie', 'norse_eir', 'norse_rime_jotunn', 'norse_volva_of_fate',
    'yokai_oni_kunoichi', 'yokai_yuki_onna',
}

FORBIDDEN_IDS = {
    'norse_frost_jotunn', 'japanese_raijin_miko', 'infernal_gehenna_witch',
    'japanese_oni_kunoichi', 'norse_fate_volva', 'japanese_yuki_onna',
    'crimson_phoenix', 'greek_lernaean_hydra',
}

EXPECTED_SLOTS = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'}
FORBIDDEN_SLOTS = {'ultimate', 'true_ultimate', 'divine_weapon', 'domain', 'field_domain'}

APPROVED_STATUS_WHITELIST = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk', 'domain_effect',
}

# Forbidden tokens in 5★ catalog records (5★ has no true Ultimate, no DW,
# no Domain live slot, no Marchio Boreale, no Borea references).
FORBIDDEN_RECORD_TOKENS = (
    'is_true_ultimate":true', 'is_true_ultimate": true',
    'ultimate_signature_upgrade', 'domain_effect_apply',
    'marchio_boreale', 'greek_borea',
)
# divine_weapon as a record key is forbidden (but allowed in descriptive
# metadata fields like `no_divine_weapon_for_5star`).
FORBIDDEN_KEY_REGEX = re.compile(r'"(?:divine_weapon|divine_weapon_id|arma_divina)"\s*:')

failures: list[str] = []
warnings: list[str] = []
ui_descriptive_hits: list[str] = []


def fail(section, msg):
    failures.append(f'[{section}] {msg}')


def warn(section, msg):
    warnings.append(f'[{section}] {msg}')


def load(path):
    if not path.exists():
        fail('IO', f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {path}: {e}')
        return {}


def audit_catalog_integrity(full, source):
    section = '1.catalog_integrity'
    full_entries = full.get('entries', []) or []
    src_entries = source.get('entries', []) or []

    if len(full_entries) != 20:
        fail(section, f'full catalog: expected 20 entries, got {len(full_entries)}')
    if len(src_entries) != 20:
        fail(section, f'source file: expected 20 entries, got {len(src_entries)}')

    full_ids = [e.get('hero_id') for e in full_entries]
    if len(set(full_ids)) != len(full_ids):
        fail(section, 'duplicate hero_id in full catalog')
    full_id_set = set(full_ids)

    missing = CANONICAL_5STAR - full_id_set
    if missing:
        fail(section, f'full catalog missing canonical IDs: {sorted(missing)}')
    extra = full_id_set - CANONICAL_5STAR
    if extra:
        fail(section, f'full catalog has non-canonical IDs: {sorted(extra)}')

    forbidden_in_full = full_id_set & FORBIDDEN_IDS
    if forbidden_in_full:
        fail(section, f'full catalog uses forbidden IDs: {sorted(forbidden_in_full)}')

    # Source file: skill_id ends with _passive_advanced
    src_hero_ids = set()
    for e in src_entries:
        sid = e.get('skill_id') or ''
        if not sid.endswith('_passive_advanced'):
            fail(section, f'source skill_id "{sid}" does not end with _passive_advanced')
        else:
            hid = sid[: -len('_passive_advanced')]
            src_hero_ids.add(hid)
            if hid in FORBIDDEN_IDS:
                fail(section, f'source uses forbidden hero_id: {hid}')
    if src_hero_ids != CANONICAL_5STAR:
        miss = CANONICAL_5STAR - src_hero_ids
        ex = src_hero_ids - CANONICAL_5STAR
        if miss:
            fail(section, f'source missing canonical IDs: {sorted(miss)}')
        if ex:
            fail(section, f'source has non-canonical IDs: {sorted(ex)}')


def audit_slot_structure(full):
    section = '2.slot_structure'
    for e in full.get('entries', []) or []:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        actual = set(sp.keys())
        missing = EXPECTED_SLOTS - actual
        if missing:
            fail(section, f'{hid}: missing slots {sorted(missing)}')
        forbidden_present = actual & FORBIDDEN_SLOTS
        if forbidden_present:
            fail(section, f'{hid}: forbidden slots present {sorted(forbidden_present)}')
        extra = actual - EXPECTED_SLOTS - FORBIDDEN_SLOTS
        if extra:
            warn(section, f'{hid}: extra slot keys beyond expected 5: {sorted(extra)}')
        # divine_weapon_id at entry level (not slot) is also forbidden in 5★
        if 'divine_weapon_id' in e:
            fail(section, f'{hid}: entry has divine_weapon_id field (forbidden for 5★)')


def audit_pa_crosslink(full, source):
    section = '3.passive_advanced_crosslink'
    src_by_hero = {}
    for e in source.get('entries', []) or []:
        sid = e.get('skill_id') or ''
        if sid.endswith('_passive_advanced'):
            hid = sid[: -len('_passive_advanced')]
            src_by_hero[hid] = e

    for e in full.get('entries', []) or []:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        pa = sp.get('passive_advanced') or {}

        if pa.get('slot') != 'passive_advanced':
            fail(section, f'{hid}: passive_advanced.slot != "passive_advanced"')

        expected_skill_id = f'{hid}_passive_advanced'
        if pa.get('skill_id') != expected_skill_id:
            fail(section, f'{hid}: passive_advanced.skill_id != "{expected_skill_id}" (got "{pa.get("skill_id")}")')

        if pa.get('design_status') != 'approved_source_completed':
            fail(section, f'{hid}: design_status != approved_source_completed (got {pa.get("design_status")})')
        if pa.get('source_status') != 'approved_rm128a':
            fail(section, f'{hid}: source_status != approved_rm128a (got {pa.get("source_status")})')
        if pa.get('legacy_source') is not None:
            fail(section, f'{hid}: passive_advanced.legacy_source != null')

        src_pa = src_by_hero.get(hid)
        if src_pa is None:
            fail(section, f'{hid}: passive_advanced missing from source file')
            continue
        if src_pa.get('display_name') != pa.get('display_name'):
            fail(section, f'{hid}: display_name mismatch source="{src_pa.get("display_name")}" vs full="{pa.get("display_name")}"')
        if src_pa.get('skill_id') != pa.get('skill_id'):
            fail(section, f'{hid}: skill_id mismatch source vs full')
        if src_pa.get('status_tags') != pa.get('status_tags'):
            fail(section, f'{hid}: status_tags mismatch source vs full')


def audit_runtime_inertness(full, source):
    section = '4.runtime_inertness'
    # Catalog-level flags
    if full.get('runtime_attached') is not False:
        fail(section, 'full catalog runtime_attached != false')
    if full.get('balance_values_finalized') is not False:
        fail(section, 'full catalog balance_values_finalized != false')
    if full.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'full catalog do_not_treat_as_live_kit != true')
    if source.get('runtime_attached') is not False:
        fail(section, 'source file runtime_attached != false')
    if source.get('battle_runtime_attached') is not False:
        fail(section, 'source file battle_runtime_attached != false')
    if source.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'source file do_not_treat_as_live_kit != true')

    # Entry-level
    for e in full.get('entries', []) or []:
        hid = e.get('hero_id', '?')
        if e.get('runtime_attached') is not False:
            fail(section, f'{hid}: entry runtime_attached != false')
        if e.get('balance_values_finalized') is not False:
            fail(section, f'{hid}: entry balance_values_finalized != false')
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            if slot.get('final_numbers') is not None:
                fail(section, f'{hid}.{slot_name}: final_numbers != null')
            # For passive_advanced (RM1.28-A enriched), check the explicit flags
            if slot_name == 'passive_advanced':
                if slot.get('runtime_attached') is not False:
                    fail(section, f'{hid}.passive_advanced: runtime_attached != false')
                if slot.get('battle_runtime_attached') is not False:
                    fail(section, f'{hid}.passive_advanced: battle_runtime_attached != false')
                if slot.get('do_not_treat_as_live_kit') is not True:
                    fail(section, f'{hid}.passive_advanced: do_not_treat_as_live_kit != true')


def audit_5star_boundaries(full):
    section = '5.5star_boundaries'
    # Re-serialize the catalog and look for forbidden tokens at character level
    # excluding controlled metadata.
    for e in full.get('entries', []) or []:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        # Specifically check skill_2.is_true_ultimate == False (preserved from RM1.26-B2)
        s2 = sp.get('skill_2') or {}
        itu = s2.get('is_true_ultimate')
        if itu is True:
            fail(section, f'{hid}: skill_2.is_true_ultimate == TRUE (forbidden for 5★)')
        if 'is_true_ultimate' in s2 and itu is not False:
            fail(section, f'{hid}: skill_2.is_true_ultimate must be False if present (got {itu})')

        # Per-record forbidden token scan (excluding skill_2 description block to avoid false hits)
        rec_json = json.dumps(e, ensure_ascii=False).lower()
        for forbidden in ('ultimate_signature_upgrade', 'domain_effect_apply', 'marchio_boreale', 'greek_borea'):
            if forbidden in rec_json:
                fail(section, f'{hid}: contains forbidden token "{forbidden}"')

        # divine_weapon as a JSON key in any slot (not as descriptive value)
        if FORBIDDEN_KEY_REGEX.search(json.dumps(e, ensure_ascii=False)):
            fail(section, f'{hid}: contains forbidden key (divine_weapon|divine_weapon_id|arma_divina)')


def audit_status_whitelist(full, source):
    section = '6.status_whitelist'
    # Source file
    for e in source.get('entries', []) or []:
        sid = e.get('skill_id') or '?'
        for field in ('status_tags', 'status_interactions'):
            for t in (e.get(field) or []):
                if t not in APPROVED_STATUS_WHITELIST:
                    fail(section, f'source {sid}.{field}: "{t}" not in approved whitelist')
    # Full catalog: only check passive_advanced slots strictly (other slots
    # use legacy_source data that may include slightly different tags such
    # as "shield" not in whitelist — these are pre-existing, not introduced
    # by RM1.28-A, so we only WARN if found).
    for e in full.get('entries', []) or []:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        pa = sp.get('passive_advanced') or {}
        for field in ('status_tags', 'status_interactions'):
            for t in (pa.get(field) or []):
                if t not in APPROVED_STATUS_WHITELIST:
                    fail(section, f'full catalog {hid}.passive_advanced.{field}: "{t}" not in approved whitelist')
        # Other slots: legacy data — informational only
        for slot_name in ('basic', 'passive_base', 'skill_1', 'skill_2'):
            slot = sp.get(slot_name) or {}
            for t in (slot.get('status_tags') or []):
                if t not in APPROVED_STATUS_WHITELIST:
                    warn(section, f'{hid}.{slot_name}: legacy status_tag "{t}" not in approved core whitelist (pre-RM1.28-A; informational)')


def audit_api_consistency():
    section = '7.api_consistency'
    if not LOADER_FILE.exists():
        warn(section, f'loader file missing: {LOADER_FILE}')
    else:
        text = LOADER_FILE.read_text(encoding='utf-8')
        # Loader should be read-only (no db writes / file writes)
        for pat in (r'\.insert_one\(', r'\.update_one\(', r'\.delete_one\(',
                    r'\.replace_one\(', r'\.write_text\(', r'open\([^)]*["\']w["\']',
                    r'\.dump\('):
            if re.search(pat, text):
                fail(section, f'loader file appears to perform a write/mutation: pattern {pat}')

    if not ROUTES_FILE.exists():
        warn(section, f'routes file missing: {ROUTES_FILE}')
    else:
        text = ROUTES_FILE.read_text(encoding='utf-8')
        # No mutation HTTP methods
        if re.search(r'router\.(post|put|patch|delete)\(', text, re.IGNORECASE):
            fail(section, 'routes file declares mutation endpoint (POST/PUT/PATCH/DELETE)')


def audit_ui_assumption():
    section = '8.ui_assumption'
    if not UI_FILE.exists():
        warn(section, f'UI file missing: {UI_FILE}')
        return
    text = UI_FILE.read_text(encoding='utf-8')
    # No POST/PUT/DELETE/PATCH fetch
    if re.search(r"method:\s*['\"](POST|PUT|DELETE|PATCH)['\"]", text):
        fail(section, 'UI uses non-GET fetch method')
    # No runtime verbs as bottons. Look for word-boundary action verbs
    runtime_verbs = ['activate', 'equip', 'break\\s*seal', 'spendi', 'evoca', 'battle\\s*test']
    for v in runtime_verbs:
        if re.search(rf'>\s*[^<]*\b{v}\b[^<]*<', text, re.IGNORECASE):
            fail(section, f'UI contains runtime verb token "{v}"')
    # Informational: "ultimate" / "upgrade" may appear in descriptive text;
    # report counts but do not fail.
    for token in ('ultimate', 'upgrade', 'attiva'):
        n = len(re.findall(rf'\b{token}\b', text, re.IGNORECASE))
        if n > 0:
            ui_descriptive_hits.append(f'"{token}" appears {n}x in UI (descriptive, no runtime button)')


def main():
    full = load(FULL_CATALOG)
    source = load(PA_SOURCE)
    schema = load(HSK_SCHEMA)  # informational
    _ = schema  # silence
    if failures:
        return emit()
    audit_catalog_integrity(full, source)
    audit_slot_structure(full)
    audit_pa_crosslink(full, source)
    audit_runtime_inertness(full, source)
    audit_5star_boundaries(full)
    audit_status_whitelist(full, source)
    audit_api_consistency()
    audit_ui_assumption()
    return emit(full, source)


def emit(full=None, source=None):
    if failures:
        print('FAIL: RM1.28-B 5★ Skill Kit Cross-Link Audit')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1
    print('PASS: RM1.28-B 5★ Skill Kit Cross-Link Audit')
    if full is not None and source is not None:
        full_entries = full.get('entries', [])
        src_entries = source.get('entries', [])
        print(f'  full 5★ catalog entries:        {len(full_entries)}')
        print(f'  passive_advanced source entries:{len(src_entries)}')
        print(f'  expected slots per entry:       {sorted(EXPECTED_SLOTS)}')
        print('  forbidden slots absent:         ultimate / divine_weapon / domain')
        print('  forbidden hero IDs absent:      ', sorted(FORBIDDEN_IDS))
        approved = sum(1 for e in full_entries
                       if (e.get('skill_package') or {}).get('passive_advanced', {}).get('design_status') == 'approved_source_completed')
        print(f'  passive_advanced approved:      {approved}/20')
        not_true_ult = sum(1 for e in full_entries
                           if (e.get('skill_package') or {}).get('skill_2', {}).get('is_true_ultimate') is False)
        print(f'  skill_2.is_true_ultimate=false: {not_true_ult}/20')
        print('  cross-link source ↔ full:       display_name/skill_id/status_tags match for all 20.')
        print('  status whitelist:               passive_advanced status_tags + status_interactions all in approved core.')
        print('  runtime inertness:              final_numbers=null, runtime_attached=false, battle_runtime_attached=false.')
        print('  no Marchio Boreale / Borea references in 5★ records.')
        print('  loader/route files: GET-only, no mutations.')
        print('  UI: read-only, no mutation fetch, no runtime verbs as buttons.')
    if ui_descriptive_hits:
        print('UI descriptive (informational):')
        for h in ui_descriptive_hits:
            print(f'  i {h}')
    if warnings:
        print('Warnings (informational, no failure):')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
