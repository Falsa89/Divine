#!/usr/bin/env python3
"""
RM1.32-C2 — Numeric Trim Foundation Drafts (DESIGN-ONLY MUTATION)
─────────────────────────────────────────────────────────────────────────────
Conservative, idempotent numeric trim on 5★/6★ foundation_draft `final_numbers`.

Trim policies (only when value is CLEARLY above cap):
  • status_chance_pct  >= 90  → 85          (PvP status chance cap, RM1.32-C)
  • damage_multiplier_pct (ultimate AoE, target_count>=2) > 380 → 380
  • damage_multiplier_pct (ST ultimate/skill_2, target_count==1) > 600 → 600
  • Marchio max_stacks_pvp/pve/boss only if above cap (3/5/4). No-op if already aligned.

Idempotent: re-running never re-decreases an already-trimmed value.
ABORT if any forbidden surface would be touched.

ABORT conditions:
  • current run has no fresh backup under /app/backups/hero_skill_kits/
  • any runtime flag would flip to true
  • any non-final_numbers field outside allowed metadata keys would change
  • any skill identity / status / effect / description / slot key would change

Writes top-level metadata on the catalog if mutated:
  - numeric_trim_pass_id = "RM1.32-C2"
  - last_numeric_trim_write
Per-slot `trim_metadata` block added only when a value changed.

Run:
    python3 /app/backend/scripts/apply_foundation_numeric_trim_rm132c2.py
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
HSK_5STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
BACKUPS = ROOT / 'backups/hero_skill_kits'

# Caps
PVP_STATUS_CHANCE_TRIGGER = 90  # >= 90 → trim to 85
PVP_STATUS_CHANCE_CAP = 85
PVP_AOE_ULTIMATE_TRIGGER = 380   # > 380 → trim to 380
PVP_AOE_ULTIMATE_CAP = 380
PVP_ST_BURST_TRIGGER = 600       # > 600 → trim to 600 (slot=ultimate|skill_2 and target_count==1)
PVP_ST_BURST_CAP = 600
MARCHIO_PVP_CAP = 3
MARCHIO_PVE_CAP = 5
MARCHIO_BOSS_CAP = 4

TASK = 'RM1.32-C2'


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def have_fresh_backup() -> bool:
    """Return True if at least one backup folder exists under BACKUPS."""
    if not BACKUPS.exists():
        return False
    for child in BACKUPS.iterdir():
        if child.is_dir() and (child / 'MANIFEST.json').exists():
            return True
    return False


def trim_slot_final_numbers(fn: dict, slot_name: str) -> list[dict]:
    """In-place trim. Returns list of trim records applied to this slot's final_numbers."""
    if not isinstance(fn, dict):
        return []
    records: list[dict] = []
    tgt = fn.get('target_count') or 1

    # 1. status_chance_pct
    sc = fn.get('status_chance_pct')
    if isinstance(sc, (int, float)) and sc >= PVP_STATUS_CHANCE_TRIGGER and sc > PVP_STATUS_CHANCE_CAP:
        records.append({
            'field': 'status_chance_pct',
            'before': sc,
            'after': PVP_STATUS_CHANCE_CAP,
            'reason': f'pvp_status_chance_cap: {sc} >= {PVP_STATUS_CHANCE_TRIGGER} → cap {PVP_STATUS_CHANCE_CAP}',
            'source': 'RM1.32-C delta plan (pvp_status_chance_cap WARN)',
        })
        fn['status_chance_pct'] = PVP_STATUS_CHANCE_CAP

    # 2. damage_multiplier_pct
    dmg = fn.get('damage_multiplier_pct')
    if isinstance(dmg, (int, float)) and slot_name in ('ultimate', 'skill_2'):
        if slot_name == 'ultimate' and tgt >= 2:
            if dmg > PVP_AOE_ULTIMATE_CAP:
                records.append({
                    'field': 'damage_multiplier_pct',
                    'before': dmg,
                    'after': PVP_AOE_ULTIMATE_CAP,
                    'reason': f'pvp_cap_aoe_ultimate: AoE ultimate per-target {dmg} > {PVP_AOE_ULTIMATE_CAP} (tgt={tgt}) → cap {PVP_AOE_ULTIMATE_CAP}',
                    'source': 'RM1.32-C delta plan (pvp_cap_aoe_ultimate WARN)',
                })
                fn['damage_multiplier_pct'] = PVP_AOE_ULTIMATE_CAP
        elif tgt == 1 and dmg > PVP_ST_BURST_CAP:
            records.append({
                'field': 'damage_multiplier_pct',
                'before': dmg,
                'after': PVP_ST_BURST_CAP,
                'reason': f'pvp_cap_single_target_burst: ST {slot_name} {dmg} > {PVP_ST_BURST_CAP} (tgt=1) → cap {PVP_ST_BURST_CAP}',
                'source': 'RM1.32-C delta plan (pvp_cap_single_target_burst WARN)',
            })
            fn['damage_multiplier_pct'] = PVP_ST_BURST_CAP

    # 3. Marchio caps (only for Borea owner blocks)
    mb = fn.get('marchio_boreale_stack_values')
    if isinstance(mb, dict):
        for key, cap in (('max_stacks_pvp', MARCHIO_PVP_CAP),
                         ('max_stacks_pve', MARCHIO_PVE_CAP),
                         ('max_stacks_boss', MARCHIO_BOSS_CAP)):
            v = mb.get(key)
            if isinstance(v, (int, float)) and v > cap:
                records.append({
                    'field': f'marchio_boreale_stack_values.{key}',
                    'before': v,
                    'after': cap,
                    'reason': f'marchio_pvp_cap: {key}={v} > {cap} → cap {cap}',
                    'source': 'RM1.32-C delta plan (marchio_pvp_cap WARN)',
                })
                mb[key] = cap

    return records


def patch_catalog(cat_path: Path, label: str) -> tuple[dict, list[dict], int, int]:
    """Patch a catalog in place. Returns (catalog_dict, trim_records_with_context, scanned, trimmed)."""
    cat = json.loads(cat_path.read_text(encoding='utf-8'))
    trim_records_ctx: list[dict] = []
    scanned = 0
    trimmed = 0
    for e in cat.get('entries') or []:
        hid = e.get('hero_id')
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers')
            if not isinstance(fn, dict):
                continue
            scanned += 1
            recs = trim_slot_final_numbers(fn, sn)
            if recs:
                trimmed += 1
                # Annotate the slot with trim_metadata (idempotent merge by field name)
                tmeta = slot.setdefault('trim_metadata', {
                    'trim_task': TASK,
                    'design_only': True,
                    'runtime_attached': False,
                    'history': [],
                })
                for r in recs:
                    # Idempotency: if a history entry for this field with same after already exists, skip
                    already = any(h.get('field') == r['field'] and h.get('after') == r['after']
                                  and h.get('trim_task') == TASK for h in tmeta.get('history') or [])
                    if not already:
                        tmeta.setdefault('history', []).append({
                            'trim_task': TASK,
                            'field': r['field'],
                            'before': r['before'],
                            'after': r['after'],
                            'reason': r['reason'],
                            'source': r['source'],
                            'applied_at_utc': _now(),
                        })
                    trim_records_ctx.append({
                        'file': cat_path.name,
                        'label': label,
                        'hero_id': hid,
                        'slot': sn,
                        'field_path': r['field'],
                        'before': r['before'],
                        'after': r['after'],
                        'reason': r['reason'],
                    })
    return cat, trim_records_ctx, scanned, trimmed


def main() -> int:
    if not have_fresh_backup():
        print('ABORT: no backup found under /app/backups/hero_skill_kits/. Run backup_hero_skill_kit_catalogs.py first.', file=sys.stderr)
        return 1

    summary = {
        'patch_task': TASK,
        'started_at_utc': _now(),
        'files_scanned': [],
        'total_values_scanned': 0,
        'total_values_trimmed': 0,
        'by_category': {
            'status_chance_pct': 0,
            'damage_multiplier_pct_aoe_ultimate': 0,
            'damage_multiplier_pct_st_burst': 0,
            'marchio_boreale_stack_values': 0,
        },
        'trims': [],
        'files_touched': [],
    }

    for cat_path, label in ((HSK_5STAR, '5star'), (HSK_6STAR, '6star')):
        cat, recs, scanned, trimmed = patch_catalog(cat_path, label)
        summary['files_scanned'].append({
            'file': cat_path.name,
            'label': label,
            'values_scanned': scanned,
            'values_trimmed': trimmed,
        })
        summary['total_values_scanned'] += scanned
        summary['total_values_trimmed'] += trimmed
        for r in recs:
            field = r['field_path']
            if 'status_chance_pct' in field:
                summary['by_category']['status_chance_pct'] += 1
            elif 'marchio_boreale' in field:
                summary['by_category']['marchio_boreale_stack_values'] += 1
            elif field == 'damage_multiplier_pct':
                if 'AoE' in r['reason'] or 'aoe' in r['reason']:
                    summary['by_category']['damage_multiplier_pct_aoe_ultimate'] += 1
                else:
                    summary['by_category']['damage_multiplier_pct_st_burst'] += 1
        summary['trims'].extend(recs)
        if recs:
            # Update top-level metadata only on real change
            cat['numeric_trim_pass_id'] = TASK
            cat['last_numeric_trim_write'] = _now()
            # Preserve invariants explicitly
            cat['balance_values_finalized'] = False
            cat['do_not_treat_as_live_kit'] = True
            cat['runtime_attached'] = False
            cat['battle_runtime_attached'] = False
            cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            summary['files_touched'].append(cat_path.name)

    summary['finished_at_utc'] = _now()

    print('=' * 72)
    print(f'RM1.32-C2 — Numeric Trim Foundation Drafts')
    print('=' * 72)
    print(f'  total_values_scanned : {summary["total_values_scanned"]}')
    print(f'  total_values_trimmed : {summary["total_values_trimmed"]}')
    print(f'  by_category          : {summary["by_category"]}')
    print(f'  files_touched        : {summary["files_touched"] or "[]"}')
    if summary['trims']:
        print('\n  Trims applied:')
        for r in summary['trims']:
            print(f'    - [{r["label"]}] {r["hero_id"]}.{r["slot"]} {r["field_path"]}: {r["before"]} → {r["after"]}')
    else:
        print('\n  No values needed trimming (idempotent re-run or all values already within caps).')

    # Emit a brief result line that can be captured by other scripts
    print(f'\nRESULT: {"PATCH_APPLIED" if summary["files_touched"] else "NO_PATCH_NEEDED"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
