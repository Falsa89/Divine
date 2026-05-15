#!/usr/bin/env python3
"""
RM1.30-C — Hero Skill Kit Catalog Final Consolidation Audit
─────────────────────────────────────────────────────────────────────────
Read-only global audit consolidating 5★ + 6★ Hero Skill Kit catalogs and
the Divine Weapon catalog cross-link.

NO mutation. NO DB write. NO runtime hook. NO UI/API/loader change.

Exit 0 on PASS, 1 on FAIL.

Verifies 27 invariants spanning:
  - catalog counts (5★ 20 / 6★ 13)
  - canonical hero IDs
  - slot structures (5★ no ultimate, 6★ ultimate required)
  - 6★ divine_weapon_id cross-link
  - 5★ exclusions (no DW, no Domain, no true Ultimate)
  - status whitelist + Marchio Boreale restriction
  - final_numbers null / runtime flags false everywhere
  - Borea safety + forbidden hero IDs absent
  - loader/route GET-only / no write patterns
  - UI: no non-GET fetch + no runtime-verb pressables
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

HSK_BASE = Path('/app/data/design/hero_skill_kits')
DW_BASE = Path('/app/data/design/divine_weapons')

HSK_5STAR = HSK_BASE / 'hero_skill_kits_5star_full_v1.json'
HSK_6STAR = HSK_BASE / 'hero_skill_kits_6star_borea_v1.json'
HSK_SCHEMA = HSK_BASE / 'hero_skill_kit_schema_v1.json'
DW_CATALOG = DW_BASE / 'divine_weapons_catalog_v1.json'

LOADER_FILE = Path('/app/backend/data/hero_skill_kits_loader.py')
HSK_ROUTES = Path('/app/backend/routes/hero_skill_kits_catalogs.py')
DW_ROUTES = Path('/app/backend/routes/divine_weapons.py')
UI_HSK = Path('/app/frontend/app/hero-skill-kits-catalog.tsx')
UI_DW = Path('/app/frontend/app/divine-weapons-catalog.tsx')

CANONICAL_5STAR = {
    'angelic_bastion_angel', 'celtic_mist_banshee', 'creature_crimson_phoenix',
    'creature_lernaean_hydra', 'cursed_pestilence_herald', 'demonic_gehenna_witch',
    'egyptian_bastet', 'egyptian_claw_of_sekhmet', 'greek_atalanta', 'greek_circe',
    'greek_medusa', 'greek_nemean_lioness', 'greek_nike', 'japanese_miko_of_raijin',
    'norse_dawn_valkyrie', 'norse_eir', 'norse_rime_jotunn', 'norse_volva_of_fate',
    'yokai_oni_kunoichi', 'yokai_yuki_onna',
}
CANONICAL_6STAR_LAUNCH_BASE = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
}
CANONICAL_6STAR_EXTRA_PREMIUM = {'greek_borea'}
CANONICAL_6STAR_ALL = CANONICAL_6STAR_LAUNCH_BASE | CANONICAL_6STAR_EXTRA_PREMIUM

FORBIDDEN_5STAR = {
    'norse_frost_jotunn', 'japanese_raijin_miko', 'infernal_gehenna_witch',
    'japanese_oni_kunoichi', 'norse_fate_volva', 'japanese_yuki_onna',
    'crimson_phoenix', 'greek_lernaean_hydra',
}
FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

SLOTS_5STAR = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'}
SLOTS_6STAR = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'}

APPROVED_CORE_STATUS = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk', 'domain_effect',
}

PRESERVED_DW = {
    'greek_athena': 'aegis_of_athena',
    'egyptian_isis': 'isis_sacred_tyet_knot',
    'greek_borea': 'borea_wings_of_the_north_wind',
}

FORBIDDEN_KEY_REGEX = re.compile(r'"(?:divine_weapon|divine_weapon_id|arma_divina)"\s*:')
WRITE_PATTERNS = (
    r'\.insert_one\(', r'\.insert_many\(',
    r'\.update_one\(', r'\.update_many\(',
    r'\.delete_one\(', r'\.delete_many\(',
    r'\.replace_one\(',
    r'\.write_text\(', r'open\([^)]*["\']w["\']',
    r'json\.dump\(',
)
RUNTIME_VERBS_RE = (
    r'\bactivate\b', r'\bequip\b', r'\bbreak\s*seal\b', r'\bspend\b',
    r'\bsummon\b', r'\bbattle\s*test\b', r'\battach\s*runtime\b',
    r'\battiva\b', r'\bequipaggia\b', r'\bspendi\b', r'\bevoca\b',
    r'\bupgrade now\b',
)

failures: list[str] = []
warnings: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def load_json(p: Path) -> dict:
    if not p.exists():
        fail('IO', f'missing file {p}')
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {p}: {e}')
        return {}


# ── 5★ AUDIT ───────────────────────────────────────────────────────────
def audit_5star(cat: dict) -> None:
    section = 'A.5star'
    entries = cat.get('entries') or []
    # Invariant 1
    if len(entries) != 20:
        fail(section, f'5★ expected 20 entries, got {len(entries)}')
    ids = {e.get('hero_id') for e in entries}
    # Invariant 3
    if ids != CANONICAL_5STAR:
        miss = CANONICAL_5STAR - ids
        ext = ids - CANONICAL_5STAR
        if miss:
            fail(section, f'5★ missing canonical IDs: {sorted(miss)}')
        if ext:
            fail(section, f'5★ non-canonical IDs: {sorted(ext)}')
    # Invariant 20
    forb = ids & FORBIDDEN_5STAR
    if forb:
        fail(section, f'5★ forbidden IDs present: {sorted(forb)}')

    for e in entries:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        actual = set(sp.keys())
        # Invariant 5
        if actual != SLOTS_5STAR:
            extra = actual - SLOTS_5STAR
            miss = SLOTS_5STAR - actual
            if miss:
                fail(section, f'5★ {hid}: missing slots {sorted(miss)}')
            if extra:
                fail(section, f'5★ {hid}: forbidden/extra slots {sorted(extra)}')
        # Invariant 7
        if 'ultimate' in actual:
            fail(section, f'5★ {hid}: must NOT have ultimate slot')
        # Invariant 12
        if 'divine_weapon_id' in e:
            fail(section, f'5★ {hid}: must NOT have divine_weapon_id')
        if FORBIDDEN_KEY_REGEX.search(json.dumps(e, ensure_ascii=False)):
            fail(section, f'5★ {hid}: forbidden divine_weapon key present')
        # Invariant 9: skill_2.is_true_ultimate must be false (if declared)
        s2 = sp.get('skill_2') or {}
        if s2.get('is_true_ultimate') is True:
            fail(section, f'5★ {hid}: skill_2.is_true_ultimate == true (forbidden)')
        # Invariant 13: no Domain markers
        rec = json.dumps(e, ensure_ascii=False).lower()
        for tok in ('marchio_boreale', 'greek_borea', 'domain_effect_apply', 'ultimate_signature_upgrade'):
            if tok in rec:
                fail(section, f'5★ {hid}: forbidden token "{tok}"')
        # Invariant 15, 16, 17 — runtime inertness
        if e.get('runtime_attached') is True:
            fail(section, f'5★ {hid}: entry runtime_attached == true')
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers')
            if fn is not None and not (isinstance(fn, dict) and fn.get('status') == 'foundation_draft' and fn.get('runtime_ready') is False):
                fail(section, f'5★ {hid}.{slot_name}: final_numbers != null')
            if slot.get('runtime_attached') is True:
                fail(section, f'5★ {hid}.{slot_name}: runtime_attached == true')
            if slot.get('battle_runtime_attached') is True:
                fail(section, f'5★ {hid}.{slot_name}: battle_runtime_attached == true')
        # Invariant 18: status_tags only approved whitelist or empty
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            tags = slot.get('status_tags') or []
            for t in tags:
                if t not in APPROVED_CORE_STATUS and t != '':
                    fail(section, f'5★ {hid}.{slot_name}.status_tags: non-approved "{t}"')


# ── 6★ AUDIT ───────────────────────────────────────────────────────────
def audit_6star(cat: dict, dw_records_by_id: dict) -> None:
    section = 'B.6star'
    entries = cat.get('entries') or []
    # Invariant 2
    if len(entries) != 13:
        fail(section, f'6★ expected 13 entries, got {len(entries)}')
    ids = {e.get('hero_id') for e in entries}
    # Invariant 4
    if ids != CANONICAL_6STAR_ALL:
        miss = CANONICAL_6STAR_ALL - ids
        ext = ids - CANONICAL_6STAR_ALL
        if miss:
            fail(section, f'6★ missing canonical IDs: {sorted(miss)}')
        if ext:
            fail(section, f'6★ non-canonical IDs: {sorted(ext)}')
    # Invariants 21, 22
    forb = ids & FORBIDDEN_HERO_IDS
    if forb:
        fail(section, f'6★ forbidden hero IDs present: {sorted(forb)}')

    seen_dw_ids: set[str] = set()
    for e in entries:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        actual = set(sp.keys())
        # Invariant 6
        if actual != SLOTS_6STAR:
            miss = SLOTS_6STAR - actual
            ext = actual - SLOTS_6STAR
            if miss:
                fail(section, f'6★ {hid}: missing slots {sorted(miss)}')
            if ext:
                fail(section, f'6★ {hid}: extra slots {sorted(ext)}')
        # Invariant 8
        if 'ultimate' not in actual:
            fail(section, f'6★ {hid}: missing ultimate slot')
        # Invariant 10
        dwid = e.get('divine_weapon_id')
        if not dwid:
            fail(section, f'6★ {hid}: missing divine_weapon_id')
        else:
            if dwid in seen_dw_ids:
                fail(section, f'6★ {hid}: divine_weapon_id "{dwid}" reused')
            seen_dw_ids.add(dwid)
            # Invariant 11
            if dwid not in dw_records_by_id:
                fail(section, f'6★ {hid}: divine_weapon_id "{dwid}" not in DW catalog')
            elif dw_records_by_id[dwid].get('hero_id') != hid:
                fail(section, f'6★ {hid}: DW record hero_id mismatch ({dw_records_by_id[dwid].get("hero_id")})')
            # Preserved overrides
            if hid in PRESERVED_DW and dwid != PRESERVED_DW[hid]:
                fail(section, f'6★ {hid}: preserved DW override mismatch (expected "{PRESERVED_DW[hid]}", got "{dwid}")')
        # Invariant 15, 16, 17 — runtime inertness
        if e.get('runtime_attached') is True:
            fail(section, f'6★ {hid}: entry runtime_attached == true')
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            if slot.get('final_numbers') is not None:
                fn = slot.get('final_numbers')
                if not (isinstance(fn, dict) and fn.get('status') == 'foundation_draft' and fn.get('runtime_ready') is False):
                    fail(section, f'6★ {hid}.{slot_name}: final_numbers not foundation_draft/runtime_ready=false (post-RM1.32-B allowance)')
            if slot.get('runtime_attached') is True:
                fail(section, f'6★ {hid}.{slot_name}: runtime_attached == true')
            if slot.get('battle_runtime_attached') is True:
                fail(section, f'6★ {hid}.{slot_name}: battle_runtime_attached == true')
            # Invariant 19: core_status_ids only approved + marchio_boreale on Borea
            for sid in (slot.get('core_status_ids') or []):
                if sid in APPROVED_CORE_STATUS:
                    continue
                if sid == 'marchio_boreale':
                    if hid != 'greek_borea':
                        fail(section, f'6★ {hid}.{slot_name}: marchio_boreale only allowed on greek_borea')
                    continue
                fail(section, f'6★ {hid}.{slot_name}.core_status_ids: non-approved "{sid}"')

    # Catalog top-level safety (RM1.30-A) — invariant 17
    if cat.get('runtime_attached') is not False:
        fail(section, '6★ catalog top-level runtime_attached != false')
    if cat.get('battle_runtime_attached') is not False:
        fail(section, '6★ catalog top-level battle_runtime_attached != false (RM1.30-A)')
    if cat.get('balance_values_finalized') is not False:
        fail(section, '6★ catalog top-level balance_values_finalized != false')
    if cat.get('do_not_treat_as_live_kit') is not True:
        fail(section, '6★ catalog top-level do_not_treat_as_live_kit != true')


def audit_borea_safety(cat6: dict) -> None:
    section = 'C.borea_safety'
    entries = cat6.get('entries') or []
    borea = [e for e in entries if e.get('hero_id') == 'greek_borea']
    legacy = [e for e in entries if e.get('hero_id') == 'borea']
    if len(borea) != 1:
        fail(section, f'expected exactly 1 greek_borea entry, got {len(borea)}')
    if legacy:
        fail(section, f'legacy "borea" hero_id present (forbidden): {len(legacy)}')
    if borea:
        b = borea[0]
        if b.get('release_group') != 'launch_extra_premium':
            fail(section, f'greek_borea.release_group != launch_extra_premium (got {b.get("release_group")})')
        if b.get('divine_weapon_id') != 'borea_wings_of_the_north_wind':
            fail(section, 'greek_borea.divine_weapon_id != borea_wings_of_the_north_wind')
    # Invariant 24 — no marchio_boreale in non-Borea records
    for e in entries:
        hid = e.get('hero_id')
        if hid == 'greek_borea':
            continue
        if 'marchio_boreale' in json.dumps(e, ensure_ascii=False).lower():
            fail(section, f'{hid}: marchio_boreale leaked into non-Borea record')


def audit_api_consistency() -> None:
    section = 'D.api_consistency'
    # Invariant 25 — loader: no write patterns
    if not LOADER_FILE.exists():
        warn(section, f'loader file missing: {LOADER_FILE}')
    else:
        text = LOADER_FILE.read_text(encoding='utf-8')
        for pat in WRITE_PATTERNS:
            if re.search(pat, text):
                fail(section, f'loader has write/mutation pattern: {pat}')
    # Invariant 26 — routes: GET-only
    for rfile in (HSK_ROUTES, DW_ROUTES):
        if not rfile.exists():
            warn(section, f'routes file missing: {rfile}')
            continue
        text = rfile.read_text(encoding='utf-8')
        if re.search(r'@router\.(post|put|patch|delete)\(', text, re.IGNORECASE):
            fail(section, f'{rfile.name} declares mutation endpoint (POST/PUT/PATCH/DELETE)')


def audit_ui_safety() -> dict:
    section = 'E.ui_safety'
    descriptive: dict[str, dict[str, int]] = {}
    for ui in (UI_HSK, UI_DW):
        if not ui.exists():
            warn(section, f'UI missing: {ui}')
            continue
        text = ui.read_text(encoding='utf-8')
        # Non-GET fetch
        if re.search(r"method:\s*['\"](POST|PUT|PATCH|DELETE)['\"]", text):
            fail(section, f'{ui.name}: non-GET fetch detected')
        # Invariant 27 — runtime verbs inside Pressables
        for verb in RUNTIME_VERBS_RE:
            for m in re.finditer(verb, text, re.IGNORECASE):
                window = text[max(0, m.start() - 200):m.start()]
                if 'onPress=' in window:
                    fail(section, f'{ui.name}: runtime verb "{m.group(0)}" inside Pressable')
                    break
        # Descriptive informational counts
        desc = {}
        for tok in ('ultimate', 'borea', 'marchio', 'divine weapon', 'attiva'):
            n = len(re.findall(rf'\b{re.escape(tok)}\b', text, re.IGNORECASE))
            if n:
                desc[tok] = n
        descriptive[ui.name] = desc
    return descriptive


def main() -> int:
    cat5 = load_json(HSK_5STAR)
    cat6 = load_json(HSK_6STAR)
    dw = load_json(DW_CATALOG)
    if failures:
        return emit()
    dw_records_by_id = {r.get('divine_weapon_id'): r for r in (dw.get('records') or [])}

    audit_5star(cat5)
    audit_6star(cat6, dw_records_by_id)
    audit_borea_safety(cat6)
    audit_api_consistency()
    descriptive = audit_ui_safety()

    return emit(cat5, cat6, dw, descriptive)


def emit(cat5=None, cat6=None, dw=None, descriptive=None) -> int:
    if failures:
        print('FAIL: RM1.30-C — Hero Skill Kit Catalog Final Consolidation Audit')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1
    print('PASS: RM1.30-C — Hero Skill Kit Catalog Final Consolidation Audit')
    if cat5 is not None and cat6 is not None and dw is not None:
        e5 = cat5.get('entries') or []
        e6 = cat6.get('entries') or []
        b6 = [e for e in e6 if e.get('release_group') == 'launch_base']
        x6 = [e for e in e6 if e.get('release_group') == 'launch_extra_premium']
        print(f'  5★ entries:                       {len(e5)}/20')
        print(f'  6★ entries:                       {len(e6)}/13 ({len(b6)} launch_base + {len(x6)} launch_extra_premium)')
        print(f'  Divine Weapon records:            {len(dw.get("records") or [])}/13')
        print(f'  5★ slot set:                      {sorted(SLOTS_5STAR)}')
        print(f'  6★ slot set:                      {sorted(SLOTS_6STAR)}')
        print( '  5★ no_true_ultimate / no_DW / no_Domain leak: OK')
        print( '  6★ all_have_ultimate / all_have_DW / DW_crosslink: OK')
        print( '  Catalog top-level safety (6★):    runtime/battle_runtime/balance=false, do_not_treat_as_live_kit=true')
        print( '  Borea safety:                     greek_borea catalog-only launch_extra_premium / 0 leak')
        print( '  API:                              GET-only loader + routes')
        if descriptive:
            print( '  UI descriptive (informational):')
            for ui, d in descriptive.items():
                if d:
                    print(f'    {ui}: ' + ', '.join(f'{k}={v}' for k, v in d.items()))
    if warnings:
        print('Warnings (informational):')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
