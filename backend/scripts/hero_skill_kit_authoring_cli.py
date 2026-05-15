#!/usr/bin/env python3
"""
RM1.31-A — Hero Skill Kit Authoring CLI (READ + DRY-RUN ONLY)
─────────────────────────────────────────────────────────────────────────
WARNING: This CLI is READ/DRY-RUN-only and MUST NOT mutate catalog data,
DB, runtime, gacha, roster, Borea visibility, Character Bible, or assets.
Default mode = no write. Commands that imply change require --dry-run and
still do NOT touch the catalog.

Commands:
  summary
  list --rarity 5|6
  show --hero-id <id>
  validate-dry-run --hero-id <id>
  propose-add-slot --hero-id <id> --slot <slot> --dry-run
  propose-update-field --hero-id <id> --slot <slot> --field <f> --value <v> --dry-run
  export-report --out <path>   (writes ONLY to /app/backend/reports or /tmp)
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HSK_BASE = Path('/app/data/design/hero_skill_kits')
DW_BASE = Path('/app/data/design/divine_weapons')

HSK_5STAR = HSK_BASE / 'hero_skill_kits_5star_full_v1.json'
HSK_6STAR = HSK_BASE / 'hero_skill_kits_6star_borea_v1.json'
HSK_SCHEMA = HSK_BASE / 'hero_skill_kit_schema_v1.json'
DW_CATALOG = DW_BASE / 'divine_weapons_catalog_v1.json'

SAFE_REPORT_DIRS = (Path('/app/backend/reports'), Path('/tmp'))

# Rarity → slot expectation
RARITY_SLOTS = {
    5: ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'],
    6: ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'],
}

LEGACY_FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}
FROZEN_FIELDS = {'final_numbers', 'runtime_attached', 'battle_runtime_attached'}

MODULE_WARNING = (
    'RM1.31-A authoring CLI is READ/DRY-RUN-only and must not mutate catalog data.'
)


def load_json(p: Path) -> dict:
    if not p.exists():
        raise FileNotFoundError(f'missing catalog file: {p}')
    return json.loads(p.read_text(encoding='utf-8'))


def load_catalogs():
    return load_json(HSK_5STAR), load_json(HSK_6STAR), load_json(DW_CATALOG)


def find_entry(hero_id: str):
    cat5, cat6, _ = load_catalogs()
    for e in cat5.get('entries') or []:
        if e.get('hero_id') == hero_id:
            return e, '5star'
    for e in cat6.get('entries') or []:
        if e.get('hero_id') == hero_id:
            return e, '6star'
    return None, None


# ── Commands ──────────────────────────────────────────────────────────
def cmd_summary(_args):
    cat5, cat6, dw = load_catalogs()
    print(f'[INFO] {MODULE_WARNING}')
    print('=== Hero Skill Kit Catalog Summary ===')
    print(f'5★ entries:                  {len(cat5.get("entries") or [])} (expected 20)')
    print(f'6★ entries:                  {len(cat6.get("entries") or [])} (expected 13)')
    b6 = [e for e in (cat6.get('entries') or []) if e.get('release_group') == 'launch_base']
    x6 = [e for e in (cat6.get('entries') or []) if e.get('release_group') == 'launch_extra_premium']
    print(f'6★ launch_base:              {len(b6)} (expected 12)')
    print(f'6★ launch_extra_premium:     {len(x6)} (expected 1 = greek_borea)')
    print(f'DW records:                  {len(dw.get("records") or [])} (expected 13)')
    print()
    print('Safety flags (5★ catalog):')
    for k in ('runtime_attached', 'battle_runtime_attached', 'balance_values_finalized', 'do_not_treat_as_live_kit'):
        print(f'  {k} = {cat5.get(k, "<missing>")}')
    print('Safety flags (6★ catalog):')
    for k in ('runtime_attached', 'battle_runtime_attached', 'balance_values_finalized', 'do_not_treat_as_live_kit'):
        print(f'  {k} = {cat6.get(k, "<missing>")}')
    print()
    print('Borea visibility:            greek_borea is CATALOG-ONLY (launch_extra_premium).')
    print('                              NOT visible in /api/heroes. Legacy `borea` is forbidden.')
    print('CLI mode:                    READ + DRY-RUN-only. No writes.')
    return 0


def cmd_list(args):
    rarity = args.rarity
    if rarity not in (5, 6):
        print('FAIL: --rarity must be 5 or 6')
        return 2
    cat5, cat6, _ = load_catalogs()
    cat = cat5 if rarity == 5 else cat6
    print(f'=== {rarity}★ Hero List (READ-ONLY) ===')
    for i, e in enumerate(cat.get('entries') or [], 1):
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        slots = sorted(sp.keys())
        if rarity == 6:
            rg = e.get('release_group', '?')
            dwid = e.get('divine_weapon_id', '?')
            print(f'  {i:2d}. {hid:30s} rg={rg:22s} dw={dwid:35s} slots={len(slots)}')
        else:
            print(f'  {i:2d}. {hid:30s} slots={len(slots)} ({",".join(slots)})')
    return 0


def cmd_show(args):
    hid = args.hero_id
    if not hid:
        print('FAIL: --hero-id required')
        return 2
    if hid in LEGACY_FORBIDDEN_HERO_IDS:
        print(f'REJECTED: hero_id "{hid}" is a forbidden legacy/non-canonical alias.')
        print('  Allowed canonical alternatives: see `list --rarity 5` / `list --rarity 6`.')
        return 3
    entry, where = find_entry(hid)
    if entry is None:
        print(f'NOT FOUND: hero_id "{hid}" is not in 5★ or 6★ catalogs.')
        return 4
    print(f'[INFO] {MODULE_WARNING}')
    print(f'=== Hero kit: {hid} (found in {where}) ===')
    base_keys = ('hero_id', 'display_name', 'element', 'role', 'faction',
                 'release_group', 'native_rarity', 'divine_weapon_id',
                 'domain_id', 'runtime_attached', 'balance_values_finalized')
    for k in base_keys:
        if k in entry:
            print(f'  {k}: {entry.get(k)}')
    if hid == 'greek_borea':
        print('  ⚠  CATALOG-ONLY: greek_borea is launch_extra_premium and NOT active in /api/heroes/gacha/battle.')
    sp = entry.get('skill_package') or {}
    print(f'  skill_package slots ({len(sp)}):')
    for slot_name, slot in sp.items():
        if not isinstance(slot, dict):
            continue
        st = slot.get('skill_type') or '?'
        el = slot.get('element') or '?'
        ds = slot.get('design_status') or '?'
        print(f'    - {slot_name:18s} | type={st:12s} | element={el:10s} | design_status={ds:30s}')
        tags = slot.get('core_effect_tags') or slot.get('effect_tags') or []
        sids = slot.get('core_status_ids') or slot.get('status_tags') or []
        if tags:
            print(f'      effect_tags: {tags}')
        if sids:
            print(f'      status_ids:  {sids}')
    return 0


def cmd_validate_dry_run(args):
    hid = args.hero_id
    if not hid:
        print('FAIL: --hero-id required')
        return 2
    if hid in LEGACY_FORBIDDEN_HERO_IDS:
        print(f'REJECTED: hero_id "{hid}" is a forbidden legacy/non-canonical alias.')
        return 3
    entry, where = find_entry(hid)
    if entry is None:
        print(f'NOT FOUND: hero_id "{hid}" not in 5★ or 6★ catalog.')
        return 4
    print(f'[DRY-RUN] Validating "{hid}" in {where} (no writes).')
    rarity = 5 if where == '5star' else 6
    expected = set(RARITY_SLOTS[rarity])
    actual = set((entry.get('skill_package') or {}).keys())
    missing = expected - actual
    extra = actual - expected
    issues = []
    if missing:
        issues.append(f'missing slots: {sorted(missing)}')
    if extra:
        issues.append(f'unexpected slots: {sorted(extra)}')
    if rarity == 6 and not entry.get('divine_weapon_id'):
        issues.append('6★ entry missing divine_weapon_id')
    if rarity == 5 and 'divine_weapon_id' in entry:
        issues.append('5★ entry must NOT have divine_weapon_id')
    if entry.get('runtime_attached') is True:
        issues.append('entry runtime_attached==true (must be false in current stage)')
    if entry.get('balance_values_finalized') is True:
        issues.append('entry balance_values_finalized==true (must be false)')
    for sn, slot in (entry.get('skill_package') or {}).items():
        if not isinstance(slot, dict):
            continue
        if slot.get('final_numbers') is not None:
            issues.append(f'{sn}.final_numbers != null')
        if slot.get('runtime_attached') is True:
            issues.append(f'{sn}.runtime_attached==true')
        if slot.get('battle_runtime_attached') is True:
            issues.append(f'{sn}.battle_runtime_attached==true')
    if issues:
        print('DRY-RUN VALIDATION: ISSUES FOUND (no write performed):')
        for i in issues:
            print(f'  - {i}')
        return 1
    print('DRY-RUN VALIDATION: PASS — entry is structurally consistent with rarity rules.')
    return 0


def cmd_propose_add_slot(args):
    if not args.dry_run:
        print('REJECTED: propose-add-slot requires --dry-run (writes are not allowed in RM1.31-A).')
        return 5
    hid = args.hero_id
    slot = args.slot
    if hid in LEGACY_FORBIDDEN_HERO_IDS:
        print(f'REJECTED: hero_id "{hid}" is forbidden.')
        return 3
    entry, where = find_entry(hid)
    if entry is None:
        print(f'NOT FOUND: hero_id "{hid}" not in catalog.')
        return 4
    rarity = 5 if where == '5star' else 6
    allowed = set(RARITY_SLOTS[rarity])
    sp = entry.get('skill_package') or {}
    print(f'[DRY-RUN] propose-add-slot hero={hid} slot={slot} rarity={rarity}')
    if rarity == 5 and slot == 'ultimate':
        print('  REJECTED: 5★ heroes MUST NOT have an "ultimate" slot.')
        return 6
    if slot not in allowed:
        print(f'  REJECTED: slot "{slot}" is not in the allowed set for rarity {rarity}: {sorted(allowed)}')
        return 6
    if slot in sp:
        print(f'  INFO: slot "{slot}" already present on {hid} (no add would occur).')
        return 0
    print(f'  WOULD ALLOW: adding slot "{slot}" would be valid by rarity rules.')
    print('  NOTE: no write performed. CLI is dry-run-only.')
    return 0


def cmd_propose_update_field(args):
    if not args.dry_run:
        print('REJECTED: propose-update-field requires --dry-run.')
        return 5
    hid = args.hero_id
    slot = args.slot
    field = args.field
    value = args.value
    if hid in LEGACY_FORBIDDEN_HERO_IDS:
        print(f'REJECTED: hero_id "{hid}" is forbidden.')
        return 3
    entry, where = find_entry(hid)
    if entry is None:
        print(f'NOT FOUND: hero_id "{hid}" not in catalog.')
        return 4
    sp = entry.get('skill_package') or {}
    if slot not in sp:
        print(f'  REJECTED: slot "{slot}" not present on {hid}.')
        return 6
    if field in FROZEN_FIELDS:
        print(f'  REJECTED: field "{field}" is FROZEN in the catalog-only stage.')
        print('  These fields will only be touched by a future runtime/balance task.')
        return 7
    print(f'[DRY-RUN] propose-update-field hero={hid} slot={slot} field={field} value={value!r}')
    print(f'  WOULD CHECK: schema compliance for field "{field}" against hero_skill_kit_schema_v1.')
    print('  NOTE: no write performed. CLI is dry-run-only.')
    return 0


def cmd_export_report(args):
    out = Path(args.out).resolve()
    if not any(str(out).startswith(str(safe.resolve())) for safe in SAFE_REPORT_DIRS):
        print(f'REJECTED: --out "{out}" is outside the allowed report directories: {[str(s) for s in SAFE_REPORT_DIRS]}')
        return 8
    out.parent.mkdir(parents=True, exist_ok=True)
    cat5, cat6, dw = load_catalogs()
    report = {
        'report_id': 'authoring_cli_export',
        'task_origin': 'RM1.31-A',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'mode': 'READ_ONLY_DRY_RUN',
        'counts': {
            '5star_entries': len(cat5.get('entries') or []),
            '6star_entries': len(cat6.get('entries') or []),
            'divine_weapon_records': len(dw.get('records') or []),
        },
        '5star_hero_ids': sorted([e.get('hero_id') for e in (cat5.get('entries') or [])]),
        '6star_hero_ids': sorted([e.get('hero_id') for e in (cat6.get('entries') or [])]),
        'safety_flags_5star': {k: cat5.get(k) for k in ('runtime_attached', 'battle_runtime_attached', 'balance_values_finalized', 'do_not_treat_as_live_kit')},
        'safety_flags_6star': {k: cat6.get(k) for k in ('runtime_attached', 'battle_runtime_attached', 'balance_values_finalized', 'do_not_treat_as_live_kit')},
        'cli_warning': MODULE_WARNING,
    }
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'REPORT WRITTEN (read-only export): {out}  ({out.stat().st_size} bytes)')
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='hero_skill_kit_authoring_cli',
        description='RM1.31-A authoring CLI — READ/DRY-RUN-only.',
    )
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('summary')
    pl = sub.add_parser('list')
    pl.add_argument('--rarity', type=int, required=True)
    ps = sub.add_parser('show')
    ps.add_argument('--hero-id', required=True)
    pv = sub.add_parser('validate-dry-run')
    pv.add_argument('--hero-id', required=True)
    pa = sub.add_parser('propose-add-slot')
    pa.add_argument('--hero-id', required=True)
    pa.add_argument('--slot', required=True)
    pa.add_argument('--dry-run', action='store_true')
    pu = sub.add_parser('propose-update-field')
    pu.add_argument('--hero-id', required=True)
    pu.add_argument('--slot', required=True)
    pu.add_argument('--field', required=True)
    pu.add_argument('--value', required=True)
    pu.add_argument('--dry-run', action='store_true')
    pe = sub.add_parser('export-report')
    pe.add_argument('--out', required=True)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        'summary': cmd_summary,
        'list': cmd_list,
        'show': cmd_show,
        'validate-dry-run': cmd_validate_dry_run,
        'propose-add-slot': cmd_propose_add_slot,
        'propose-update-field': cmd_propose_update_field,
        'export-report': cmd_export_report,
    }
    return dispatch[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
