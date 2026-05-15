#!/usr/bin/env python3
"""
RM1.32-A-POST — 6★ Balance Readiness Audit (READ-ONLY)
─────────────────────────────────────────────────────────────────────────
Read-only audit that prepares the design context for the FUTURE 6★
Balance Pass Foundation (RM1.32-B). This script:

  • DOES NOT patch the 6★ catalog.
  • DOES NOT activate Borea.
  • DOES NOT write to DB / runtime / gacha / roster.
  • DOES NOT modify any file.

It validates the present catalog shape and confirms it matches the
declared readiness plan in
  /app/data/design/hero_skill_kits/hero_skill_kits_6star_balance_readiness_plan_v1.json

Checks:
  1. 13 6★ entries present
  2. 12 launch_base + 1 greek_borea launch_extra_premium
  3. 78 slots total (13 × 6)
  4. 6 slot names per entry: basic, passive_base, skill_1,
     passive_advanced, skill_2, ultimate
  5. 78/78 final_numbers currently null
  6. 13/13 divine_weapon_id present and cross-linked
  7. Marchio Boreale appears only on greek_borea
  8. core_status_ids resolve against status catalog (best-effort)
  9. core_effect_tags are taxonomy-only descriptors (no numeric mod)
 10. Borea remains catalog-only (release_group, hidden roster)
 11. Plan JSON declares no_patch=true and borea_activation=false
 12. Runtime flags false at top-level and at slot-level
 13. Recommended future structure echoed (suggested numeric range only)

Exit 0 on PASS, 1 on FAIL. NO writes.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

CATALOG_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')
STATUS_CATALOG = Path('/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json')
PLAN_JSON = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_balance_readiness_plan_v1.json')

EXPECTED_SLOT_NAMES = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'}
EXPECTED_ENTRIES = 13
EXPECTED_LAUNCH_BASE = 12
EXPECTED_LAUNCH_EXTRA_PREMIUM = 1
EXPECTED_SLOT_COUNT = 78
BOREA_HERO_ID = 'greek_borea'
FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'cannot read {p}: {e}')
        return None


def main() -> int:
    c6 = load_json(CATALOG_6STAR)
    dw = load_json(DW_CATALOG)
    status = load_json(STATUS_CATALOG) if STATUS_CATALOG.exists() else None
    plan = load_json(PLAN_JSON)

    if c6 is None or dw is None or plan is None:
        return emit()

    entries = c6.get('entries') or []

    # Check 1: entries count
    if len(entries) != EXPECTED_ENTRIES:
        fail('entries', f'6★ entry count != {EXPECTED_ENTRIES} (got {len(entries)})')
    else:
        info(f'6★ entries: {len(entries)} ✓')

    # Check 2: release groups split
    launch_base = [e for e in entries if e.get('release_group') == 'launch_base']
    launch_extra = [e for e in entries if e.get('release_group') == 'launch_extra_premium']
    if len(launch_base) != EXPECTED_LAUNCH_BASE:
        fail('release_groups', f'launch_base count != {EXPECTED_LAUNCH_BASE} (got {len(launch_base)})')
    if len(launch_extra) != EXPECTED_LAUNCH_EXTRA_PREMIUM:
        fail('release_groups', f'launch_extra_premium count != {EXPECTED_LAUNCH_EXTRA_PREMIUM} (got {len(launch_extra)})')
    if launch_extra and launch_extra[0].get('hero_id') != BOREA_HERO_ID:
        fail('release_groups', f"launch_extra_premium expected greek_borea, got {launch_extra[0].get('hero_id')}")
    else:
        info(f'release_groups split: {EXPECTED_LAUNCH_BASE} launch_base + {EXPECTED_LAUNCH_EXTRA_PREMIUM} launch_extra_premium (greek_borea) ✓')

    # Check 3 + 4: slot count and slot names
    total_slots = 0
    null_final_numbers = 0
    runtime_flags_violations = 0
    for e in entries:
        hid = e.get('hero_id', '?')
        if hid in FORBIDDEN_HERO_IDS:
            fail('forbidden_id', f'forbidden hero_id "{hid}" present')
        pkg = e.get('skill_package') or {}
        slot_names = set(pkg.keys())
        missing = EXPECTED_SLOT_NAMES - slot_names
        extra = slot_names - EXPECTED_SLOT_NAMES
        if missing:
            fail('slots', f'{hid}: missing slots {sorted(missing)}')
        if extra:
            fail('slots', f'{hid}: unexpected slots {sorted(extra)}')
        for sn, slot in pkg.items():
            if not isinstance(slot, dict):
                continue
            total_slots += 1
            if slot.get('final_numbers') is None:
                null_final_numbers += 1
            else:
                fail('final_numbers', f'{hid}.{sn}: final_numbers expected null in 6★ pre-RM1.32-B (got non-null)')
            if slot.get('runtime_attached') is True:
                runtime_flags_violations += 1
                fail('runtime', f'{hid}.{sn}: runtime_attached==true')
            if slot.get('battle_runtime_attached') is True:
                runtime_flags_violations += 1
                fail('runtime', f'{hid}.{sn}: battle_runtime_attached==true')

    if total_slots != EXPECTED_SLOT_COUNT:
        fail('slots', f'total slot count != {EXPECTED_SLOT_COUNT} (got {total_slots})')
    else:
        info(f'total 6★ slots: {total_slots} ✓')

    # Check 5: 78/78 null
    if null_final_numbers != EXPECTED_SLOT_COUNT:
        fail('final_numbers', f'expected {EXPECTED_SLOT_COUNT}/{EXPECTED_SLOT_COUNT} null final_numbers, got {null_final_numbers}')
    else:
        info(f'final_numbers null: {null_final_numbers}/{EXPECTED_SLOT_COUNT} ✓')

    # Check 6: divine_weapon_id cross-link
    dw_records = dw.get('records') or []
    dw_ids = {r.get('divine_weapon_id') for r in dw_records}
    crosslinked = 0
    for e in entries:
        hid = e.get('hero_id', '?')
        dwid = e.get('divine_weapon_id')
        if not dwid:
            fail('crosslink', f'{hid}: missing divine_weapon_id')
            continue
        if dwid not in dw_ids:
            fail('crosslink', f'{hid}: divine_weapon_id "{dwid}" not in DW catalog')
            continue
        crosslinked += 1
    if crosslinked == EXPECTED_ENTRIES:
        info(f'divine_weapon_id cross-links: {crosslinked}/{EXPECTED_ENTRIES} ✓')
    else:
        fail('crosslink', f'cross-linked DW count != {EXPECTED_ENTRIES} (got {crosslinked})')

    # Check 7: Marchio Boreale leak
    marchio_leak = []
    for e in entries:
        hid = e.get('hero_id')
        if hid == BOREA_HERO_ID:
            continue
        blob = json.dumps(e, ensure_ascii=False).lower()
        if 'marchio_boreale' in blob or 'marchio boreale' in blob:
            marchio_leak.append(hid)
    if marchio_leak:
        fail('marchio_leak', f'marchio_boreale leaked into non-Borea entries: {marchio_leak}')
    else:
        info('Marchio Boreale confined to greek_borea ✓')

    # Check 8: core_status_ids resolve (best-effort)
    if status:
        known_status_ids = set()
        for k in ('entries', 'records', 'statuses', 'items'):
            for r in (status.get(k) or []):
                if isinstance(r, dict):
                    sid = r.get('status_id') or r.get('id')
                    if sid:
                        known_status_ids.add(sid)
        if not known_status_ids:
            warn('status', 'status catalog has no recognizable id list; skipping core_status_ids resolve check')
        else:
            unresolved = []
            checked = 0
            for e in entries:
                hid = e.get('hero_id', '?')
                for sn, slot in (e.get('skill_package') or {}).items():
                    if not isinstance(slot, dict):
                        continue
                    for sid in (slot.get('core_status_ids') or []):
                        checked += 1
                        if sid not in known_status_ids:
                            unresolved.append(f'{hid}.{sn}:{sid}')
            if unresolved:
                warn('status', f'core_status_ids unresolved ({len(unresolved)}): first 5 -> {unresolved[:5]}')
            else:
                info(f'core_status_ids resolve: {checked} references all resolved ✓')
    else:
        warn('status', 'status catalog missing; skipping core_status_ids resolve check')

    # Check 9: core_effect_tags are descriptors (strings, no numeric modifier)
    bad_tags = []
    for e in entries:
        hid = e.get('hero_id', '?')
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            tags = slot.get('core_effect_tags') or []
            if not isinstance(tags, list):
                bad_tags.append(f'{hid}.{sn}: core_effect_tags not list')
                continue
            for t in tags:
                if not isinstance(t, str):
                    bad_tags.append(f'{hid}.{sn}: non-string tag {t!r}')
    if bad_tags:
        fail('tags', f'core_effect_tags taxonomy violation: {bad_tags[:5]}')
    else:
        info('core_effect_tags taxonomy: all string descriptors ✓')

    # Check 10: Borea catalog-only
    borea = next((e for e in entries if e.get('hero_id') == BOREA_HERO_ID), None)
    if borea is None:
        fail('borea', 'greek_borea entry missing in 6★ catalog')
    else:
        if borea.get('release_group') != 'launch_extra_premium':
            fail('borea', f"greek_borea release_group != 'launch_extra_premium' (got {borea.get('release_group')})")
        if borea.get('runtime_attached') is True or borea.get('battle_runtime_attached') is True:
            fail('borea', 'greek_borea runtime flags must remain false')
        info('greek_borea: catalog-only, launch_extra_premium, runtime_attached=false ✓')

    # Check 11: plan JSON declares no_patch, borea_activation=false
    sf = plan.get('safety_flags') or {}
    if plan.get('patch_needed') is not False:
        fail('plan', 'plan.patch_needed must be false')
    if sf.get('no_patch') is not True:
        fail('plan', 'plan.safety_flags.no_patch must be true')
    if sf.get('borea_activation') is not False:
        fail('plan', 'plan.safety_flags.borea_activation must be false')
    if sf.get('runtime_attached') is not False or sf.get('battle_runtime_attached') is not False:
        fail('plan', 'plan.safety_flags runtime_attached / battle_runtime_attached must be false')
    if plan.get('include_borea_as_catalog_only') is not True:
        fail('plan', 'plan.include_borea_as_catalog_only must be true')
    if plan.get('catalog_structure_snapshot', {}).get('expected_slot_count') != EXPECTED_SLOT_COUNT:
        fail('plan', f'plan.expected_slot_count must be {EXPECTED_SLOT_COUNT}')
    if not failures or all('plan' not in f for f in failures):
        info(f'plan: patch_needed=false, no_patch=true, borea_activation=false ✓')

    # Check 12: top-level runtime flags on 6★ catalog
    if c6.get('runtime_attached') is not False:
        fail('top_flags', '6★ top-level runtime_attached != false')
    if c6.get('battle_runtime_attached') is not False:
        fail('top_flags', '6★ top-level battle_runtime_attached != false')
    if c6.get('balance_values_finalized') is not False:
        fail('top_flags', '6★ top-level balance_values_finalized != false')
    if not [f for f in failures if 'top_flags' in f]:
        info('6★ top-level runtime flags: runtime_attached=false, battle_runtime_attached=false, balance_values_finalized=false ✓')

    # Check 13: recommended numeric range present (descriptive)
    rec = plan.get('recommended_numeric_range_principles') or {}
    if 'slot_archetypes' not in rec or not isinstance(rec['slot_archetypes'], dict):
        fail('plan', 'plan.recommended_numeric_range_principles.slot_archetypes missing or not dict')
    else:
        missing_arch = EXPECTED_SLOT_NAMES - set(rec['slot_archetypes'].keys())
        if missing_arch:
            fail('plan', f'slot_archetypes missing entries for: {sorted(missing_arch)}')
        else:
            info(f'plan.slot_archetypes covers all 6 slot types ✓')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.32-A-POST — 6★ Balance Readiness Audit')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.32-A-POST — 6★ Balance Readiness Audit')
    for i in infos:
        print(f'  i {i}')
    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'  ! {w}')
    print('Summary:')
    print(f'  expected entries        : {EXPECTED_ENTRIES} (12 launch_base + 1 launch_extra_premium=greek_borea)')
    print(f'  expected slot count     : {EXPECTED_SLOT_COUNT}')
    print(f'  final_numbers state     : 78/78 null (untouched, ready for RM1.32-B)')
    print(f'  borea_activation        : false (catalog-only)')
    print(f'  runtime flags           : false (entry + slot)')
    print(f'  patch_needed            : false (read-only audit)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
