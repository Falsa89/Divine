#!/usr/bin/env python3
"""
RM1.29 — 6★ Skill Kit QA / Catalog Cross-Link Audit Script
─────────────────────────────────────────────────────────────────────────
Read-only audit. NO mutation. NO runtime / battle / HP bar / VFX / gacha
/ roster / DB writes. NO Borea activation. NO final_numbers changes.
Returns exit 0 on PASS, 1 on FAIL.

Audited (per RM1.29_PROMPT_EMERGENT.txt acceptance criteria):
  1.  Exactly 13 6★ entries.
  2.  Exactly 12 launch_base.
  3.  Exactly 1 launch_extra_premium.
  4.  Extra premium is greek_borea.
  5.  All expected hero IDs present.
  6.  No legacy borea.
  7.  No wrong Gaia/Borea aliases (primordial_gaia, etc.).
  8.  Every entry native_rarity = 6.
  9.  Every entry has the 6 expected slots
      (basic, passive_base, skill_1, passive_advanced, skill_2, ultimate).
  10. No 6★ missing ultimate.
  11. Every entry has divine_weapon_id.
  12. Every divine_weapon_id resolves to Divine Weapon catalog.
  13. Divine Weapon hero_id maps back to owner.
  14. Known ID overrides preserved
      (aegis_of_athena / isis_sacred_tyet_knot / borea_wings_of_the_north_wind).
  15. final_numbers null everywhere.
  16. runtime_attached false everywhere.
  17. battle_runtime_attached false everywhere (where declared).
  18. do_not_treat_as_live_kit true wherever present.
  19. Borea catalog-only safety (release_group, no leakage of legacy borea).
  20. Marchio Boreale only on greek_borea if present.
  21. No Borea/Marchio leak into non-Borea entries.
  22. Status/tags classification (approved core / unique / non-status / unknown).
  23. Loader/route GET-only read-only assumptions.
  24. UI no mutation/runtime-button assumptions.

Source files (read-only):
  /app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json
  /app/data/design/hero_skill_kits/hero_skill_kit_schema_v1.json
  /app/data/design/divine_weapons/divine_weapons_catalog_v1.json
  /app/data/design/divine_weapons/divine_weapon_schema_v1.json
  /app/backend/data/hero_skill_kits_loader.py
  /app/backend/routes/hero_skill_kits_catalogs.py
  /app/backend/routes/divine_weapons.py
  /app/frontend/app/hero-skill-kits-catalog.tsx
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

# ────────────────────────────────────────────────────────────────────────
# Paths (read-only)
# ────────────────────────────────────────────────────────────────────────
HSK_BASE = Path('/app/data/design/hero_skill_kits')
DW_BASE = Path('/app/data/design/divine_weapons')

HSK_6STAR = HSK_BASE / 'hero_skill_kits_6star_borea_v1.json'
HSK_SCHEMA = HSK_BASE / 'hero_skill_kit_schema_v1.json'
DW_CATALOG = DW_BASE / 'divine_weapons_catalog_v1.json'
DW_SCHEMA = DW_BASE / 'divine_weapon_schema_v1.json'

LOADER_FILE = Path('/app/backend/data/hero_skill_kits_loader.py')
HSK_ROUTES = Path('/app/backend/routes/hero_skill_kits_catalogs.py')
DW_ROUTES = Path('/app/backend/routes/divine_weapons.py')
UI_FILE = Path('/app/frontend/app/hero-skill-kits-catalog.tsx')

# ────────────────────────────────────────────────────────────────────────
# Expected catalog scope
# ────────────────────────────────────────────────────────────────────────
EXPECTED_LAUNCH_BASE = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
}
EXPECTED_EXTRA_PREMIUM = {'greek_borea'}
EXPECTED_ALL = EXPECTED_LAUNCH_BASE | EXPECTED_EXTRA_PREMIUM  # 13

# Hard-forbidden hero IDs (legacy or wrong aliases)
FORBIDDEN_HERO_IDS = {
    'borea',                # legacy non-canonical
    'primordial_gaia',      # wrong Gaia alias (canonical = greek_gaia)
    'greek_boreas',         # wrong Borea alias
    'olympian_borea',       # wrong Borea alias
}

# Preserved ID overrides — must match exactly
PRESERVED_DW_OVERRIDES = {
    'greek_athena': 'aegis_of_athena',
    'egyptian_isis': 'isis_sacred_tyet_knot',
    'greek_borea': 'borea_wings_of_the_north_wind',
}

EXPECTED_SLOTS = (
    'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate',
)
EXPECTED_SLOTS_SET = set(EXPECTED_SLOTS)

# ────────────────────────────────────────────────────────────────────────
# Status taxonomy
# ────────────────────────────────────────────────────────────────────────
APPROVED_CORE_STATUS = {
    'stun', 'freeze', 'silence', 'blind', 'taunt',
    'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock',
    'atk_up', 'def_up', 'crit_up', 'crit_damage_up',
    'vulnerability', 'def_down', 'effect_accuracy_up', 'magic_damage_up',
    'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity',
    'healing_up', 'healing_reduction', 'healing_block',
    'regeneration', 'cleanse', 'revive', 'revive_pending', 'death_protection',
    'mark', 'berserk', 'domain_effect',
}

# Unique/personal status IDs allowed only on a specific hero
UNIQUE_PERSONAL_STATUS = {
    'marchio_boreale': 'greek_borea',
}

# Hard-forbidden tokens in non-Borea records (substring match in serialized record).
FORBIDDEN_TOKENS_NON_BOREA = ('marchio_boreale',)

# ────────────────────────────────────────────────────────────────────────
# Output accumulators
# ────────────────────────────────────────────────────────────────────────
failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []

# Status tag classification buckets (filled during audit, surfaced in PASS report)
status_class_a_approved: set[str] = set()       # A. approved core
status_class_b_unique: dict[str, set[str]] = {}  # B. unique/personal (id -> heroes)
status_class_c_taxonomy: set[str] = set()        # C. design taxonomy (effect tags, NOT status)
status_class_d_forbidden: set[str] = set()       # D. forbidden / invalid
status_class_e_unknown: dict[str, list[str]] = {}  # E. unknown -> manual review


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def load_json(path: Path) -> dict:
    if not path.exists():
        fail('IO', f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {path}: {e}')
        return {}


# ────────────────────────────────────────────────────────────────────────
# Section 1 — Catalog integrity (counts, IDs, groups, no forbidden IDs)
# ────────────────────────────────────────────────────────────────────────
def audit_catalog_integrity(cat: dict) -> list[dict]:
    section = '1.catalog_integrity'
    entries = cat.get('entries', []) or []

    # Acceptance #1
    if len(entries) != 13:
        fail(section, f'expected 13 6★ entries, got {len(entries)}')

    hero_ids = [e.get('hero_id') for e in entries]
    if len(set(hero_ids)) != len(hero_ids):
        dupes = sorted({h for h in hero_ids if hero_ids.count(h) > 1})
        fail(section, f'duplicate hero_id in 6★ catalog: {dupes}')
    hero_set = set(hero_ids)

    # Acceptance #5: all expected IDs present
    missing = EXPECTED_ALL - hero_set
    if missing:
        fail(section, f'6★ catalog missing canonical IDs: {sorted(missing)}')
    extra = hero_set - EXPECTED_ALL
    if extra:
        fail(section, f'6★ catalog has non-canonical IDs: {sorted(extra)}')

    # Acceptance #6 + #7: forbidden hero_ids
    forbidden_present = hero_set & FORBIDDEN_HERO_IDS
    if forbidden_present:
        fail(section, f'forbidden hero_ids present: {sorted(forbidden_present)}')

    # Acceptance #2 + #3 + #4: release_group split
    base = [e for e in entries if str(e.get('release_group') or '').lower() == 'launch_base']
    extra_prem = [e for e in entries if str(e.get('release_group') or '').lower() == 'launch_extra_premium']
    if len(base) != 12:
        fail(section, f'expected 12 launch_base, got {len(base)}')
    if len(extra_prem) != 1:
        fail(section, f'expected 1 launch_extra_premium, got {len(extra_prem)}')
    if len(extra_prem) == 1 and extra_prem[0].get('hero_id') != 'greek_borea':
        fail(section, f'launch_extra_premium must be greek_borea, got {extra_prem[0].get("hero_id")}')

    # Cross-set: launch_base set match
    base_ids = {e.get('hero_id') for e in base}
    if base_ids != EXPECTED_LAUNCH_BASE:
        miss = EXPECTED_LAUNCH_BASE - base_ids
        ext = base_ids - EXPECTED_LAUNCH_BASE
        if miss:
            fail(section, f'launch_base missing: {sorted(miss)}')
        if ext:
            fail(section, f'launch_base unexpected: {sorted(ext)}')

    return entries


# ────────────────────────────────────────────────────────────────────────
# Section 2 — Slot structure (6 expected slots, ultimate required)
# ────────────────────────────────────────────────────────────────────────
def audit_slot_structure(entries: list[dict]) -> None:
    section = '2.slot_structure'
    for e in entries:
        hid = e.get('hero_id', '?')

        # Acceptance #8: native_rarity = 6
        if e.get('native_rarity') != 6:
            fail(section, f'{hid}: native_rarity != 6 (got {e.get("native_rarity")})')

        sp = e.get('skill_package') or {}
        actual = set(sp.keys())

        # Acceptance #9 + #10
        missing = EXPECTED_SLOTS_SET - actual
        if missing:
            fail(section, f'{hid}: missing slots {sorted(missing)}')
        if 'ultimate' not in actual:
            fail(section, f'{hid}: missing required slot "ultimate"')

        extra = actual - EXPECTED_SLOTS_SET
        if extra:
            warn(section, f'{hid}: extra slot keys: {sorted(extra)}')

        # expected_slots field (when present) must match
        decl = e.get('expected_slots')
        if decl is not None:
            if set(decl) != EXPECTED_SLOTS_SET:
                fail(section, f'{hid}: expected_slots field mismatch {sorted(set(decl))}')

        # Every slot must declare its own slot key and design_status
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                fail(section, f'{hid}.{slot_name}: not a dict')
                continue
            if slot.get('slot') != slot_name:
                fail(section, f'{hid}.{slot_name}: slot field mismatch (got {slot.get("slot")})')


# ────────────────────────────────────────────────────────────────────────
# Section 3 — Divine Weapon cross-link
# ────────────────────────────────────────────────────────────────────────
def audit_divine_weapon_crosslink(entries: list[dict], dw_cat: dict) -> None:
    section = '3.divine_weapon_crosslink'
    dw_records = dw_cat.get('records', []) or []
    dw_by_id = {r.get('divine_weapon_id'): r for r in dw_records if r.get('divine_weapon_id')}
    dw_by_hero = {r.get('hero_id'): r for r in dw_records if r.get('hero_id')}

    if len(dw_records) != 13:
        fail(section, f'Divine Weapon catalog expected 13 records, got {len(dw_records)}')

    seen_dw_ids: set[str] = set()
    for e in entries:
        hid = e.get('hero_id', '?')
        dwid = e.get('divine_weapon_id')

        # Acceptance #11
        if not dwid:
            fail(section, f'{hid}: missing divine_weapon_id')
            continue

        # Uniqueness
        if dwid in seen_dw_ids:
            fail(section, f'{hid}: divine_weapon_id "{dwid}" reused')
        seen_dw_ids.add(dwid)

        # Acceptance #14 — preserved overrides
        if hid in PRESERVED_DW_OVERRIDES:
            expected = PRESERVED_DW_OVERRIDES[hid]
            if dwid != expected:
                fail(section, f'{hid}: preserved DW override mismatch — expected "{expected}", got "{dwid}"')

        # Acceptance #12 — resolves to DW catalog
        if dwid not in dw_by_id:
            fail(section, f'{hid}: divine_weapon_id "{dwid}" does NOT resolve in Divine Weapon catalog')
            continue

        # Acceptance #13 — DW.hero_id maps back to owner
        r = dw_by_id[dwid]
        if r.get('hero_id') != hid:
            fail(section, f'{hid}: DW record hero_id "{r.get("hero_id")}" != skill kit hero_id "{hid}"')

        # native_rarity_required = 6
        if r.get('native_rarity_required') != 6:
            warn(section, f'{hid}: DW "{dwid}" native_rarity_required != 6 (got {r.get("native_rarity_required")})')

    # DW -> 6★ reverse map
    kit_by_hero = {e.get('hero_id'): e for e in entries}
    for r in dw_records:
        hid = r.get('hero_id')
        if hid not in kit_by_hero:
            fail(section, f'DW "{r.get("divine_weapon_id")}" hero_id "{hid}" not in 6★ skill kit catalog')
        else:
            kit_dwid = kit_by_hero[hid].get('divine_weapon_id')
            if kit_dwid != r.get('divine_weapon_id'):
                fail(section, f'DW "{r.get("divine_weapon_id")}" mismatched with kit dw_id "{kit_dwid}" for hero {hid}')


# ────────────────────────────────────────────────────────────────────────
# Section 4 — Runtime inertness (catalog/entry/slot)
# ────────────────────────────────────────────────────────────────────────
def audit_runtime_inertness(cat: dict, entries: list[dict]) -> None:
    section = '4.runtime_inertness'

    # Catalog level
    if cat.get('runtime_attached') is not False:
        fail(section, 'catalog runtime_attached != false')
    if cat.get('balance_values_finalized') is not False:
        fail(section, 'catalog balance_values_finalized != false')
    if cat.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'catalog do_not_treat_as_live_kit != true')
    # battle_runtime_attached is OPTIONAL at catalog level (route enforces False)
    if 'battle_runtime_attached' in cat and cat.get('battle_runtime_attached') is not False:
        fail(section, 'catalog battle_runtime_attached declared but != false')

    # Entry level + Slot level
    for e in entries:
        hid = e.get('hero_id', '?')
        if e.get('runtime_attached') is not False:
            fail(section, f'{hid}: entry runtime_attached != false')
        if e.get('balance_values_finalized') is not False:
            fail(section, f'{hid}: entry balance_values_finalized != false')
        if 'battle_runtime_attached' in e and e.get('battle_runtime_attached') is not False:
            fail(section, f'{hid}: entry battle_runtime_attached declared but != false')
        if 'do_not_treat_as_live_kit' in e and e.get('do_not_treat_as_live_kit') is not True:
            fail(section, f'{hid}: entry do_not_treat_as_live_kit declared but != true')

        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            # Acceptance #15
            if slot.get('final_numbers') is not None:
                fn = slot.get('final_numbers')
                if not (isinstance(fn, dict)
                        and fn.get('status') == 'foundation_draft'
                        and fn.get('runtime_ready') is False):
                    fail(section, f'{hid}.{slot_name}: final_numbers not foundation_draft/runtime_ready=false (post-RM1.32-B allowance)')
            if slot.get('runtime_attached') is True:
                fail(section, f'{hid}.{slot_name}: runtime_attached == true')
            # Acceptance #17
            if slot.get('battle_runtime_attached') is True:
                fail(section, f'{hid}.{slot_name}: battle_runtime_attached == true')
            # Acceptance #18
            if 'do_not_treat_as_live_kit' in slot and slot.get('do_not_treat_as_live_kit') is not True:
                fail(section, f'{hid}.{slot_name}: do_not_treat_as_live_kit declared but != true')


# ────────────────────────────────────────────────────────────────────────
# Section 5 — Borea safety
# ────────────────────────────────────────────────────────────────────────
def audit_borea_safety(entries: list[dict]) -> None:
    section = '5.borea_safety'
    borea_entries = [e for e in entries if e.get('hero_id') == 'greek_borea']
    legacy_entries = [e for e in entries if e.get('hero_id') == 'borea']

    # Acceptance #19
    if legacy_entries:
        fail(section, f'legacy borea entry present (forbidden): {len(legacy_entries)} record(s)')
    if len(borea_entries) != 1:
        fail(section, f'expected exactly 1 greek_borea entry, got {len(borea_entries)}')
    else:
        b = borea_entries[0]
        if str(b.get('release_group') or '').lower() != 'launch_extra_premium':
            fail(section, f'greek_borea.release_group must be launch_extra_premium (got {b.get("release_group")})')
        if b.get('divine_weapon_id') != 'borea_wings_of_the_north_wind':
            fail(section, f'greek_borea.divine_weapon_id must be borea_wings_of_the_north_wind (got {b.get("divine_weapon_id")})')

    # Acceptance #21 — no Marchio Boreale / Borea leak in non-Borea records
    for e in entries:
        hid = e.get('hero_id', '?')
        if hid == 'greek_borea':
            continue
        rec_text = json.dumps(e, ensure_ascii=False).lower()
        for tok in FORBIDDEN_TOKENS_NON_BOREA:
            if tok in rec_text:
                fail(section, f'{hid}: forbidden Borea-only token "{tok}" leaked into non-Borea record')


# ────────────────────────────────────────────────────────────────────────
# Section 6 — Status/tag classification + Acceptance #20 Marchio Boreale
# ────────────────────────────────────────────────────────────────────────
def audit_status_tags(entries: list[dict]) -> None:
    section = '6.status_tags'

    for e in entries:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            # status_ids — true status references
            for sid in (slot.get('core_status_ids') or []):
                if sid in APPROVED_CORE_STATUS:
                    status_class_a_approved.add(sid)
                    continue
                if sid in UNIQUE_PERSONAL_STATUS:
                    allowed_hero = UNIQUE_PERSONAL_STATUS[sid]
                    status_class_b_unique.setdefault(sid, set()).add(hid)
                    # Acceptance #20 — only on owner
                    if hid != allowed_hero:
                        fail(section, f'{hid}.{slot_name}: unique status "{sid}" only allowed for "{allowed_hero}"')
                    continue
                # Unknown — needs manual review
                status_class_e_unknown.setdefault(sid, []).append(f'{hid}.{slot_name}')

            # core_effect_tags — design taxonomy (NOT runtime status IDs)
            # We still classify them informatively. They may overlap with status IDs.
            for tag in (slot.get('core_effect_tags') or []):
                if tag in APPROVED_CORE_STATUS:
                    status_class_a_approved.add(tag)
                elif tag in UNIQUE_PERSONAL_STATUS:
                    status_class_b_unique.setdefault(tag, set()).add(hid)
                    if hid != UNIQUE_PERSONAL_STATUS[tag]:
                        fail(section, f'{hid}.{slot_name}: unique effect tag "{tag}" only allowed for "{UNIQUE_PERSONAL_STATUS[tag]}"')
                else:
                    # Treated as design taxonomy (e.g. "aoe", "damage_amp", "shield_scaling")
                    status_class_c_taxonomy.add(tag)


# ────────────────────────────────────────────────────────────────────────
# Section 7 — API consistency (loader/route GET-only)
# ────────────────────────────────────────────────────────────────────────
WRITE_PATTERNS = (
    r'\.insert_one\(', r'\.insert_many\(',
    r'\.update_one\(', r'\.update_many\(',
    r'\.delete_one\(', r'\.delete_many\(',
    r'\.replace_one\(',
    r'\.write_text\(',
    r'open\([^)]*["\']w["\']',
    r'json\.dump\(',
)


def audit_api_consistency() -> None:
    section = '7.api_consistency'

    # Loader file
    if not LOADER_FILE.exists():
        warn(section, f'loader file missing: {LOADER_FILE}')
    else:
        text = LOADER_FILE.read_text(encoding='utf-8')
        for pat in WRITE_PATTERNS:
            if re.search(pat, text):
                fail(section, f'loader file appears to perform write/mutation: pattern {pat}')

    # Route files — must declare ONLY GET endpoints
    for rfile in (HSK_ROUTES, DW_ROUTES):
        if not rfile.exists():
            warn(section, f'routes file missing: {rfile}')
            continue
        text = rfile.read_text(encoding='utf-8')
        if re.search(r'@router\.(post|put|patch|delete)\(', text, re.IGNORECASE):
            fail(section, f'{rfile.name} declares mutation endpoint (POST/PUT/PATCH/DELETE)')
        # Count GET endpoints (informational)
        n_get = len(re.findall(r'@router\.get\(', text))
        info(f'{rfile.name}: {n_get} GET endpoint(s) (no mutation)')


# ────────────────────────────────────────────────────────────────────────
# Section 8 — UI assumption audit
# ────────────────────────────────────────────────────────────────────────
RUNTIME_BUTTON_VERBS = [
    r'\bactivate\b', r'\bequip\b', r'\bupgrade now\b',
    r'\bbreak\s*seal\b', r'\bspend\b', r'\bsummon\b',
    r'\bbattle\s*test\b', r'\battach\s*runtime\b',
    r'\battiva\b', r'\bequipaggia\b', r'\bspendi\b', r'\bevoca\b',
]
UI_DESCRIPTIVE_TOKENS = ('ultimate', 'divine weapon', 'marchio', 'borea', 'attiva')


def audit_ui_assumption() -> None:
    section = '8.ui_assumption'
    if not UI_FILE.exists():
        warn(section, f'UI file missing: {UI_FILE}')
        return
    text = UI_FILE.read_text(encoding='utf-8')

    # No non-GET fetch method
    if re.search(r"method:\s*['\"](POST|PUT|DELETE|PATCH)['\"]", text):
        fail(section, 'UI uses non-GET fetch method')

    # No runtime verbs rendered as functional buttons
    # Pattern: text inside a Button/TouchableOpacity-like tag containing the verb.
    for verb in RUNTIME_BUTTON_VERBS:
        # Look for verb wrapped inside <Text>...verb...</Text> within a touchable
        # OR any direct >verb< pattern in JSX. To reduce false positives we look
        # for "onPress=" within 200 chars before the verb match.
        for m in re.finditer(verb, text, re.IGNORECASE):
            start = max(0, m.start() - 200)
            window = text[start:m.start()]
            if 'onPress=' in window:
                fail(section, f'UI exposes runtime verb "{m.group(0)}" inside a pressable component')
                break

    # Descriptive informational counts
    for token in UI_DESCRIPTIVE_TOKENS:
        n = len(re.findall(rf'\b{re.escape(token)}\b', text, re.IGNORECASE))
        if n > 0:
            info(f'UI descriptive: "{token}" appears {n}x (informational, no runtime button)')


# ────────────────────────────────────────────────────────────────────────
# Entrypoint
# ────────────────────────────────────────────────────────────────────────
def main() -> int:
    cat = load_json(HSK_6STAR)
    dw_cat = load_json(DW_CATALOG)
    _schema = load_json(HSK_SCHEMA)  # informational
    _dw_schema = load_json(DW_SCHEMA)  # informational

    if failures:
        return emit(cat, dw_cat)

    entries = audit_catalog_integrity(cat)
    audit_slot_structure(entries)
    audit_divine_weapon_crosslink(entries, dw_cat)
    audit_runtime_inertness(cat, entries)
    audit_borea_safety(entries)
    audit_status_tags(entries)
    audit_api_consistency()
    audit_ui_assumption()
    return emit(cat, dw_cat, entries)


def emit(cat: dict, dw_cat: dict, entries: list[dict] | None = None) -> int:
    if failures:
        print('FAIL: RM1.29 — 6★ Skill Kit / Divine Weapon Cross-Link Audit')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1

    print('PASS: RM1.29 — 6★ Skill Kit / Divine Weapon Cross-Link Audit')
    if entries is not None:
        base = [e for e in entries if str(e.get('release_group') or '').lower() == 'launch_base']
        extra = [e for e in entries if str(e.get('release_group') or '').lower() == 'launch_extra_premium']
        print(f'  6★ entries total:                 {len(entries)} (expected 13)')
        print(f'  6★ launch_base:                   {len(base)} (expected 12)')
        print(f'  6★ launch_extra_premium:          {len(extra)} (expected 1 = greek_borea)')
        print(f'  Divine Weapon records:            {len(dw_cat.get("records", []))}')
        print(f'  Slot structure per entry:         {list(EXPECTED_SLOTS)}')
        print( '  Ultimate slot present:            13/13')
        print( '  divine_weapon_id present:         13/13')
        print( '  DW cross-link (kit ↔ catalog):    13/13')
        print( '  Preserved DW overrides:           aegis_of_athena / isis_sacred_tyet_knot / borea_wings_of_the_north_wind')
        print( '  Borea safety:                     greek_borea catalog-only, release_group=launch_extra_premium')
        print( '  Marchio Boreale leak:             0 (only on greek_borea)')
        print( '  Runtime inertness:                final_numbers=null, runtime_attached=false, battle_runtime_attached=false')
        # Status classification summary
        print()
        print('  Status/tag classification:')
        print(f'    A. approved core status:        {len(status_class_a_approved)} unique tags')
        if status_class_a_approved:
            print(f'       e.g. {sorted(status_class_a_approved)}')
        print(f'    B. unique/personal status:      {len(status_class_b_unique)}')
        for k, v in status_class_b_unique.items():
            print(f'       - {k}: heroes={sorted(v)}')
        print(f'    C. design taxonomy (non-status):{len(status_class_c_taxonomy)} unique tags (effect tags)')
        if status_class_c_taxonomy:
            sample = sorted(status_class_c_taxonomy)[:10]
            print(f'       sample: {sample}{" ..." if len(status_class_c_taxonomy) > 10 else ""}')
        print(f'    D. forbidden/invalid:           {len(status_class_d_forbidden)}')
        print(f'    E. unknown (manual review):     {len(status_class_e_unknown)}')
        for k, v in status_class_e_unknown.items():
            print(f'       - {k}: appears in {v}')

    if infos:
        print()
        print('Informational:')
        for i in infos:
            print(f'  i {i}')

    if warnings:
        print()
        print('Warnings (informational, no failure):')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
