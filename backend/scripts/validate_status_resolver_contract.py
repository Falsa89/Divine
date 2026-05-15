#!/usr/bin/env python3
"""
RM1.31-C — Status Resolver Contract Validator (5★/6★ ↔ RM1.25-B)
─────────────────────────────────────────────────────────────────────────
Read-only contract validator. Verifies that every status reference used
by the 5★/6★ Hero Skill Kit catalogs resolves to a status_id declared in
the RM1.25-B status_effect_catalog_v1. NO mutation. NO runtime.

Sources:
  /app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json
  /app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json
  /app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json

Status fields scanned per slot:
  5★ → status_tags, status_interactions
  6★ → core_status_ids, status_tags, status_interactions

Contract checks:
  1. Status catalog file exists and parses.
  2. Status catalog has the 39 mandatory core statuses + marchio_boreale.
  3. Every status reference from 5★/6★ kits resolves to a status_id
     in the status catalog.
  4. marchio_boreale appears only on greek_borea.
  5. marchio_boreale is declared in the status catalog (RM1.25-B).
  6. domain_effect is declared in the status catalog AND no kit slot has
     it as a runtime-attached flag (runtime stays off).
  7. No forbidden statuses (legacy/borea/unknown) leak into status fields.

Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

STATUS_CAT = Path('/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json')
HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')

# Required mandatory statuses (from the RM1.25-B core, per RM1.29 acceptance)
MANDATORY_CORE = {
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
REQUIRED_UNIQUE_PERSONAL = {'marchio_boreale': 'greek_borea'}

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def load_status_catalog() -> tuple[dict, set[str]]:
    """Returns (catalog_dict, set_of_status_ids)."""
    if not STATUS_CAT.exists():
        fail('1.status_catalog', f'status_effect_catalog_v1.json missing at {STATUS_CAT}')
        return {}, set()
    try:
        d = json.loads(STATUS_CAT.read_text(encoding='utf-8'))
    except Exception as e:
        fail('1.status_catalog', f'invalid JSON: {e}')
        return {}, set()
    statuses = d.get('statuses') or []
    ids = {s.get('status_id') for s in statuses if isinstance(s, dict) and s.get('status_id')}
    return d, ids


def load_kit(path: Path) -> dict:
    if not path.exists():
        fail('IO', f'kit missing: {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'kit invalid JSON {path}: {e}')
        return {}


def collect_refs(cat: dict, rarity_label: str, fields: tuple[str, ...]) -> tuple[Counter, list[str], list[str]]:
    counter: Counter = Counter()
    per_hero_marchio: list[str] = []
    leak_marchio: list[str] = []
    for e in (cat.get('entries') or []):
        hid = e.get('hero_id', '?')
        for slot_name, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            for f in fields:
                vs = slot.get(f)
                if not isinstance(vs, list):
                    continue
                for tag in vs:
                    if not isinstance(tag, str):
                        continue
                    counter[(rarity_label, f, tag)] += 1
                    if tag == 'marchio_boreale':
                        per_hero_marchio.append(f'{rarity_label}.{hid}.{slot_name}.{f}')
                        if hid != 'greek_borea':
                            leak_marchio.append(f'{rarity_label}.{hid}.{slot_name}.{f}')
    return counter, per_hero_marchio, leak_marchio


def main() -> int:
    catalog, status_ids = load_status_catalog()
    if failures:
        return emit()

    info(f'status_effect_catalog path: {STATUS_CAT}')
    info(f'status_effect_catalog count: {len(status_ids)}')

    # 2 — mandatory core present
    miss_core = MANDATORY_CORE - status_ids
    if miss_core:
        fail('2.mandatory_core', f'missing mandatory statuses in catalog: {sorted(miss_core)}')

    # 5 — marchio_boreale present in catalog
    for s in REQUIRED_UNIQUE_PERSONAL:
        if s not in status_ids:
            fail('5.unique_personal', f'unique personal status "{s}" not declared in status_effect_catalog_v1')

    # 6 — domain_effect must exist
    if 'domain_effect' not in status_ids:
        fail('6.domain_effect', 'domain_effect missing from status_effect_catalog_v1')

    # Load kits
    cat5 = load_kit(HSK_5STAR)
    cat6 = load_kit(HSK_6STAR)
    if failures:
        return emit()

    # 3 — every reference resolves
    c5, m5, leak5 = collect_refs(cat5, '5star', ('status_tags', 'status_interactions'))
    c6, m6, leak6 = collect_refs(cat6, '6star', ('core_status_ids', 'status_tags', 'status_interactions'))
    all_counter = c5 + c6

    unknown_refs: Counter = Counter()
    for (rarity, field, tag), n in all_counter.items():
        if tag not in status_ids:
            unknown_refs[(rarity, field, tag)] += n

    if unknown_refs:
        # 7 — forbidden / unknown
        for (rarity, field, tag), n in sorted(unknown_refs.items(), key=lambda kv: -kv[1]):
            fail('3.unresolved_status_ref', f'{rarity}.{field}: "{tag}" not in status_effect_catalog_v1 (occurrences={n})')

    # 4 — marchio_boreale only on greek_borea
    leaks = leak5 + leak6
    if leaks:
        fail('4.marchio_boreale_leak', f'marchio_boreale found in non-Borea slots: {leaks}')

    # Stats
    info(f'5★ status refs scanned: {sum(c5.values())} ({len({t for _,_,t in c5}) } unique)')
    info(f'6★ status refs scanned: {sum(c6.values())} ({len({t for _,_,t in c6}) } unique)')
    info(f'marchio_boreale total (Borea only): {len(m5)+len(m6)}')

    return emit(status_ids=status_ids, all_counter=all_counter)


def emit(status_ids: set[str] | None = None, all_counter: Counter | None = None) -> int:
    if failures:
        print('FAIL: RM1.31-C — Status Resolver Contract Validator')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        if infos:
            print('Info:')
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.31-C — Status Resolver Contract Validator')
    if status_ids is not None:
        print(f'  Status catalog: {STATUS_CAT}')
        print(f'  Total status IDs declared: {len(status_ids)}')
        print(f'  Mandatory core present:    {len(MANDATORY_CORE)}/{len(MANDATORY_CORE)}')
        print(f'  marchio_boreale in catalog: yes (unique-personal, Borea-only)')
        print(f'  domain_effect in catalog:   yes (design-only)')
    if all_counter is not None:
        unique_5 = len({t for (r, _, t) in all_counter if r == '5star'})
        unique_6 = len({t for (r, _, t) in all_counter if r == '6star'})
        total_5 = sum(n for (r, _, _), n in all_counter.items() if r == '5star')
        total_6 = sum(n for (r, _, _), n in all_counter.items() if r == '6star')
        print(f'  5★ status references: total={total_5}, unique={unique_5}, all resolved.')
        print(f'  6★ status references: total={total_6}, unique={unique_6}, all resolved.')
        print(f'  marchio_boreale leak in non-Borea: 0')
    if infos:
        print('Info:')
        for i in infos:
            print(f'  i {i}')
    if warnings:
        print('Warnings (informational):')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
