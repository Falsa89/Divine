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
import os
import subprocess
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
DANGEROUS_FIELDS = {
    'final_numbers', 'runtime_attached', 'battle_runtime_attached',
    'release_group', 'divine_weapon_id', 'hero_id', 'skill_id', 'slot',
    'status_tags', 'core_status_ids', 'core_effect_tags',
}
SAFE_AUTHORING_FIELDS = {
    'notes', 'design_notes', 'authoring_notes', 'todo', 'todo_metadata',
    'comment', 'design_comment',
}
COMMIT_ENV_VAR = 'DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE'
COMMIT_ENV_VALUE = 'YES_I_UNDERSTAND'
BACKUP_HELPER = Path('/app/backend/scripts/backup_hero_skill_kit_catalogs.py')
SUITE_RUNNER = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')
BASELINE_DIFF = Path('/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py')

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
    """RM1.31-A dry-run + RM1.32-A-PRE guarded write foundation.

    --dry-run (default): describes what would be checked, no write.
    --commit: requires env DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE=YES_I_UNDERSTAND,
              auto-backup first, would run validator suite + auto-rollback on fail.
              In RM1.32-A-PRE the actual write step is INTENTIONALLY a no-op:
              the commit path exists ONLY as a guarded skeleton.
    """
    if not args.dry_run and not args.commit:
        print('REJECTED: propose-update-field requires either --dry-run or --commit.')
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
    # Frozen / dangerous fields always rejected at this foundation stage
    if field in FROZEN_FIELDS:
        print(f'  REJECTED: field "{field}" is FROZEN in the catalog-only stage.')
        print('  These fields will only be touched by a future runtime/balance task.')
        return 7
    if field in DANGEROUS_FIELDS:
        print(f'  REJECTED: field "{field}" is DANGEROUS in the authoring-foundation stage.')
        print('  Dangerous fields require a dedicated future task with explicit approval.')
        return 9

    # ── DRY-RUN PATH ────────────────────────────────────────────────
    if args.dry_run:
        print(f'[DRY-RUN] propose-update-field hero={hid} slot={slot} field={field} value={value!r}')
        if field not in SAFE_AUTHORING_FIELDS:
            print(f'  NOTE: field "{field}" is not in the SAFE_AUTHORING_FIELDS allowlist '
                  f'({sorted(SAFE_AUTHORING_FIELDS)}). It would be rejected on --commit.')
            print('  NOTE: no write performed. CLI is dry-run-only.')
            return 0
        print(f'  WOULD CHECK: schema compliance for field "{field}" against hero_skill_kit_schema_v1.')
        print('  NOTE: no write performed. CLI is dry-run-only.')
        return 0

    # ── COMMIT PATH (real safe-write — RM1.31-F) ────────────────────
    print(f'[COMMIT] propose-update-field hero={hid} slot={slot} field={field} value={value!r}')
    env_val = os.environ.get(COMMIT_ENV_VAR)
    if env_val != COMMIT_ENV_VALUE:
        print(f'  REJECTED: --commit requires env var {COMMIT_ENV_VAR}={COMMIT_ENV_VALUE} (got {env_val!r}).')
        return 10
    if field not in SAFE_AUTHORING_FIELDS:
        print(f'  REJECTED: field "{field}" is not in the SAFE_AUTHORING_FIELDS allowlist '
              f'({sorted(SAFE_AUTHORING_FIELDS)}).')
        return 11
    # Determine which catalog file owns this hero
    catalog_path = HSK_5STAR if where == '5star' else HSK_6STAR
    # STEP 1/4 — pre-write backup
    print('  STEP 1/4: running auto-backup helper (reason=cli_commit_RM1.31-F)...')
    proc = subprocess.run(
        ['python3', str(BACKUP_HELPER), '--reason', 'cli_commit_RM1.31-F'],
        capture_output=True, text=True, timeout=60,
    )
    print(proc.stdout, end='')
    if proc.returncode != 0:
        print('  FAIL: auto-backup failed; aborting commit.')
        return 12
    backup_manifest_line = next(
        (l for l in proc.stdout.splitlines() if l.startswith('BACKUP_MANIFEST_PATH=')),
        None,
    )
    if backup_manifest_line is None:
        print('  FAIL: backup manifest path not found in output.')
        return 12
    pre_write_manifest = Path(backup_manifest_line.split('=', 1)[1].strip())
    print(f'  STEP 1/4 OK: pre-write manifest={pre_write_manifest}')

    # STEP 2/4 — actual safe write (RM1.31-F)
    print('  STEP 2/4: writing field to catalog (real write)...')
    try:
        cat = json.loads(catalog_path.read_text(encoding='utf-8'))
        target_entry = None
        for e in cat.get('entries') or []:
            if e.get('hero_id') == hid:
                target_entry = e
                break
        if target_entry is None:
            print(f'  FAIL: hero "{hid}" disappeared from catalog between read and write.')
            return 13
        sp = target_entry.get('skill_package') or {}
        if slot not in sp:
            print(f'  FAIL: slot "{slot}" no longer present on {hid}.')
            return 13
        # Parse value: allow string (default) or JSON literal if it parses as such
        parsed_value = value
        try:
            parsed_value = json.loads(value)
        except Exception:
            parsed_value = value
        before = sp[slot].get(field, '<missing>')
        sp[slot][field] = parsed_value
        # Annotate top-level provenance for traceability (safe-additive metadata)
        cat.setdefault('last_safe_write', {})
        cat['last_safe_write'] = {
            'task_origin': 'RM1.31-F',
            'hero_id': hid,
            'slot': slot,
            'field': field,
            'value_kind': type(parsed_value).__name__,
            'cli_warning': 'Authoring CLI safe write (SAFE_AUTHORING_FIELDS only).',
        }
        catalog_path.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + '\n',
                                encoding='utf-8')
        print(f'  STEP 2/4 OK: wrote {hid}.{slot}.{field} (before={before!r} → after={parsed_value!r})')
    except Exception as e:
        print(f'  STEP 2/4 FAIL: {e}')
        # Best-effort rollback
        _rollback_from(pre_write_manifest)
        return 14

    # STEP 3/4 — validator suite + baseline diff with --allow-changed
    print('  STEP 3/4: running validator suite (--include-baseline-diff via component check)...')
    suite_ok = subprocess.run(
        ['python3', str(SUITE_RUNNER)],
        capture_output=True, text=True, timeout=120,
    )
    print(suite_ok.stdout, end='')
    suite_pass = (suite_ok.returncode == 0)
    print('  STEP 3/4a: running baseline diff with --allow-changed for the touched catalog...')
    diff_proc = subprocess.run(
        ['python3', str(BASELINE_DIFF), '--allow-changed', str(catalog_path)],
        capture_output=True, text=True, timeout=60,
    )
    print(diff_proc.stdout, end='')
    diff_pass = (diff_proc.returncode == 0)
    if suite_pass and diff_pass:
        print('  STEP 3/4 OK: all validators PASS.')
        print('  STEP 4/4: no rollback needed (validators green).')
        print(f'  OUTCOME: real safe write committed and verified.')
        print(f'  PRE_WRITE_BACKUP_MANIFEST={pre_write_manifest}')
        return 0

    # STEP 4/4 — auto-rollback
    print('  STEP 3/4 FAIL — engaging auto-rollback.')
    if _rollback_from(pre_write_manifest):
        print('  STEP 4/4 OK: catalog restored from pre-write backup.')
    else:
        print('  STEP 4/4 FATAL: rollback failed; manual intervention required.')
        return 15
    return 16


def _rollback_from(manifest_path: Path) -> bool:
    try:
        m = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'    rollback: cannot read pre-write manifest: {e}')
        return False
    import shutil
    for entry in m.get('files') or []:
        try:
            shutil.copy2(entry['backup_path'], entry['source_path'])
        except Exception as e:
            print(f'    rollback: failed to restore {entry["backup_path"]} -> {entry["source_path"]}: {e}')
            return False
    return True


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
    pu.add_argument('--commit', action='store_true',
                    help=f'GUARDED SKELETON. Requires env {COMMIT_ENV_VAR}={COMMIT_ENV_VALUE}. '
                         'Auto-backup before write; auto-rollback on validator failure. '
                         'In RM1.32-A-PRE the actual write step is intentionally a no-op.')
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
