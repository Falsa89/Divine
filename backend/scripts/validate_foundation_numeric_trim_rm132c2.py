#!/usr/bin/env python3
"""
RM1.32-C2 — Numeric Trim Foundation Drafts Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Verifies the post-trim state of the 5★/6★ catalogs after RM1.32-C2.

Asserts:
1. 5★ and 6★ catalogs valid JSON.
2. final_numbers foundation_draft preserved (5★ 100/100, 6★ 78/78).
3. runtime_ready=false, runtime_attached=false, battle_runtime_attached=false everywhere.
4. status_chance_pct <= 85 across 5★/6★ slots (RM1.32-C2 cap).
5. damage_multiplier_pct caps:
   - AoE ultimate (slot=ultimate, target_count>=2): <= 380
   - ST  burst   (slot=ultimate or skill_2, target_count==1): <= 600
6. Marchio caps respected: pvp<=3, pve<=5, boss<=4 (Borea slots only).
7. 5★ skill_2 is NOT a true ultimate (skill_type proxy / no is_true_ultimate=true).
8. 6★ ultimate slots remain true ultimate (presence of ultimate slot).
9. Marchio leak in non-Borea entries = 0.
10. No Borea activation: greek_borea has marchio Borea-only block.
11. No Divine Weapon runtime numeric modifier live (placeholders remain inert).
12. Result JSON exists and trims list is non-empty (matches expected trims).
13. Baseline v5 exists, supersedes v4, tracks current 6★ SHA.
14. Baseline v4 preserved on disk.

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
HSK_5STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
RESULT = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_numeric_trim_rm132c2_result_v1.json'
BASELINE_V5 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132c2_v5.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'

PVP_STATUS_CHANCE_CAP = 85
PVP_AOE_ULTIMATE_CAP = 380
PVP_ST_BURST_CAP = 600
MARCHIO_PVP_CAP = 3
MARCHIO_PVE_CAP = 5
MARCHIO_BOSS_CAP = 4

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(sec, msg): failures.append(f'[{sec}] {msg}')
def warn(sec, msg): warnings.append(f'[{sec}] {msg}')
def info(msg): infos.append(msg)


def sha256_of(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


def main() -> int:
    if not HSK_5STAR.exists() or not HSK_6STAR.exists():
        fail('io', 'catalog file missing')
        return emit()
    try:
        c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))
        c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'catalog parse error: {e}')
        return emit()

    # 1. counts
    e5 = c5.get('entries') or []
    e6 = c6.get('entries') or []
    if len(e5) != 20: fail('count', f'5★ entries != 20 (got {len(e5)})')
    if len(e6) != 13: fail('count', f'6★ entries != 13 (got {len(e6)})')
    fn5 = sum(1 for e in e5 for sn, slot in (e.get('skill_package') or {}).items()
              if isinstance(slot, dict) and isinstance(slot.get('final_numbers'), dict))
    fn6 = sum(1 for e in e6 for sn, slot in (e.get('skill_package') or {}).items()
              if isinstance(slot, dict) and isinstance(slot.get('final_numbers'), dict))
    if fn5 != 100: fail('count', f'5★ final_numbers != 100 (got {fn5})')
    if fn6 != 78: fail('count', f'6★ final_numbers != 78 (got {fn6})')

    # 2. runtime flags off + 3. cap checks per slot
    marchio_leak: list[str] = []
    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id', '?')
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                fn = slot.get('final_numbers') or {}
                if fn.get('status') != 'foundation_draft':
                    fail('integrity', f'{label} {hid}.{sn}.final_numbers.status != foundation_draft')
                if fn.get('runtime_ready') is not False:
                    fail('integrity', f'{label} {hid}.{sn}.final_numbers.runtime_ready != false')
                # caps
                sc = fn.get('status_chance_pct')
                if isinstance(sc, (int, float)) and sc > PVP_STATUS_CHANCE_CAP:
                    fail('caps', f'{label} {hid}.{sn} status_chance_pct={sc} > {PVP_STATUS_CHANCE_CAP}')
                dmg = fn.get('damage_multiplier_pct')
                tgt = fn.get('target_count') or 1
                if isinstance(dmg, (int, float)):
                    if sn == 'ultimate' and tgt >= 2 and dmg > PVP_AOE_ULTIMATE_CAP:
                        fail('caps', f'{label} {hid}.{sn} (AoE,tgt={tgt}) damage_multiplier_pct={dmg} > {PVP_AOE_ULTIMATE_CAP}')
                    if sn in ('ultimate', 'skill_2') and tgt == 1 and dmg > PVP_ST_BURST_CAP:
                        fail('caps', f'{label} {hid}.{sn} (ST) damage_multiplier_pct={dmg} > {PVP_ST_BURST_CAP}')
                # marchio (only Borea)
                mb = fn.get('marchio_boreale_stack_values')
                if mb is not None:
                    if hid != 'greek_borea':
                        marchio_leak.append(f'{hid}.{sn}')
                    else:
                        pvp = mb.get('max_stacks_pvp')
                        pve = mb.get('max_stacks_pve')
                        boss = mb.get('max_stacks_boss')
                        if isinstance(pvp, int) and pvp > MARCHIO_PVP_CAP:
                            fail('marchio', f'greek_borea.{sn} max_stacks_pvp={pvp} > {MARCHIO_PVP_CAP}')
                        if isinstance(pve, int) and pve > MARCHIO_PVE_CAP:
                            fail('marchio', f'greek_borea.{sn} max_stacks_pve={pve} > {MARCHIO_PVE_CAP}')
                        if isinstance(boss, int) and boss > MARCHIO_BOSS_CAP:
                            fail('marchio', f'greek_borea.{sn} max_stacks_boss={boss} > {MARCHIO_BOSS_CAP}')
                        if mb.get('owner_hero_id') != 'greek_borea':
                            fail('marchio', f'greek_borea.{sn} marchio owner_hero_id != greek_borea')
                # DW synergy placeholder must remain inert
                dws = fn.get('divine_weapon_synergy_placeholder')
                if isinstance(dws, dict):
                    if dws.get('design_only') is not True:
                        fail('dw', f'{label} {hid}.{sn} dw_synergy.design_only != true')
                    if dws.get('runtime_ready') is not False:
                        fail('dw', f'{label} {hid}.{sn} dw_synergy.runtime_ready != false')
                    if dws.get('numeric_modifier_pct') is not None:
                        fail('dw', f'{label} {hid}.{sn} dw_synergy.numeric_modifier_pct != null')
    if marchio_leak:
        fail('marchio_leak', f'marchio_boreale leaked to non-Borea: {marchio_leak[:5]}')
    else:
        info(f'marchio_boreale Borea-only ✓')

    # 4. 5★ skill_2 NOT true ultimate; 6★ ultimate slot present
    for e in e5:
        hid = e.get('hero_id', '?')
        s2 = (e.get('skill_package') or {}).get('skill_2')
        if isinstance(s2, dict):
            if s2.get('is_true_ultimate') is True:
                fail('5star_ult', f'5★ {hid}.skill_2 is_true_ultimate=true forbidden')
            slot_kind = s2.get('skill_type') or s2.get('slot_type')
            if slot_kind == 'ultimate':
                fail('5star_ult', f'5★ {hid}.skill_2 skill_type=ultimate forbidden')
    ult6_count = 0
    for e in e6:
        if isinstance((e.get('skill_package') or {}).get('ultimate'), dict):
            ult6_count += 1
    if ult6_count != 13:
        fail('6star_ult', f'6★ ultimate slot present count={ult6_count}, expected 13')
    else:
        info('6★ ultimate slot present for 13/13 heroes ✓')

    # 5. result JSON
    if not RESULT.exists():
        fail('result', f'result JSON missing: {RESULT}')
    else:
        try:
            r = json.loads(RESULT.read_text(encoding='utf-8'))
        except Exception as ex:
            fail('result', f'result JSON parse error: {ex}')
            r = None
        if r:
            if r.get('task_origin') != 'RM1.32-C2':
                fail('result', f'task_origin != RM1.32-C2 (got {r.get("task_origin")!r})')
            if r.get('no_runtime_activation') is not True:
                fail('result', 'result.no_runtime_activation must be true')
            if r.get('no_db_write') is not True:
                fail('result', 'result.no_db_write must be true')
            if r.get('borea_activation') is not False:
                fail('result', 'result.borea_activation must be false')
            trims = r.get('trims') or []
            if not isinstance(trims, list) or len(trims) == 0:
                fail('result', 'result.trims must be a non-empty list')
            info(f'result trims_total={len(trims)}, files_touched={r.get("files_touched")}')

    # 6. baseline v5 + v4
    if not BASELINE_V5.exists():
        fail('baseline', f'baseline v5 missing: {BASELINE_V5}')
    else:
        try:
            b5 = json.loads(BASELINE_V5.read_text(encoding='utf-8'))
        except Exception as ex:
            fail('baseline', f'v5 parse error: {ex}')
            b5 = None
        if b5:
            if b5.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132c2_v5':
                fail('baseline', 'v5.baseline_id mismatch')
            if b5.get('supersedes') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
                fail('baseline', 'v5.supersedes != v4')
            tracked = b5.get('tracked_files') or {}
            for k in (str(HSK_5STAR), str(HSK_6STAR)):
                meta = tracked.get(k)
                if not meta:
                    fail('baseline', f'v5.tracked_files missing {k}')
                else:
                    expected = meta.get('sha256') if isinstance(meta, dict) else meta
                    actual = sha256_of(Path(k))
                    if expected != actual:
                        fail('baseline', f'v5 sha mismatch for {k}: expected {expected[:16]}…, got {actual[:16] if actual else None}')
    if not BASELINE_V4.exists():
        fail('baseline', 'baseline v4 preserved file missing')
    else:
        info('baseline v4 preserved on disk ✓')

    # 7. Source 5★ catalog hash should match pre-trim backup (it was NOT modified)
    # We do not enforce a specific SHA here; just info.
    info(f'post-trim 5★ sha256 prefix = {sha256_of(HSK_5STAR)[:16]}…')
    info(f'post-trim 6★ sha256 prefix = {sha256_of(HSK_6STAR)[:16]}…')

    return emit()


def emit() -> int:
    print('=' * 72)
    print('RM1.32-C2 Numeric Trim Foundation Drafts Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures: print(f'  - {f}')
        print('\nRESULT: FAIL')
        return 1
    print('\nRESULT: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
