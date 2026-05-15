#!/usr/bin/env python3
"""
RM1.32-C — Boss / PvP / Domain Resistance & Cap Audit (READ-ONLY)
─────────────────────────────────────────────────────────────────────────
Read-only auditor that inspects the 5★ and 6★ foundation_draft values
and emits WARN findings useful for the design-only delta plan
(`hero_skill_kits_balance_cap_delta_plan_v1.json`).

NOTHING is written to catalogs / DB / runtime / gacha / roster.

Sections:
  1. Catalog integrity (5★ 100/100, 6★ 78/78 foundation_draft,
     runtime_ready=false, balance_values_finalized=false).
  2. Ultimate/burst spike audit.
  3. Control/status audit (freeze/stun/silence/...).
  4. Heal/shield/revive risk audit.
  5. Marchio Boreale Borea-only safety.
  6. Domain/effect policy audit.
  7. Divine Weapon synergy placeholders.
  8. Borea visibility / forbidden hero_ids.

Exit codes:
  0 on PASS (WARNs are non-fatal)
  1 on FAIL (only when a hard invariant is broken)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')
STATUS_CAT = Path('/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json')
BASELINE_V4 = Path('/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json')

FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

# Thresholds used for WARN flags (read-only, do not patch).
PVP_DMG_CAP_SINGLE_TARGET = 600   # PvP cap recommendation if ST damage_mult >= this
PVP_DMG_CAP_AOE_PER_TARGET = 380  # PvP cap recommendation if AoE damage_mult >= this
HIGH_STATUS_CHANCE = 90           # status_chance_pct >= this triggers PvP cap suggestion
HIGH_HEAL_MULT = 480
HIGH_SHIELD_MULT = 460
HARD_CONTROL_TAGS = {'freeze', 'stun', 'silence', 'taunt'}
SOFT_CONTROL_TAGS = {'slow', 'speed_down', 'healing_block', 'healing_reduction', 'curse'}
DOT_TAGS = {'poison', 'burn', 'frostbite', 'shock', 'bleed'}

failures: list[str] = []
warns: list[dict] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None:
    failures.append(f'[{sec}] {msg}')


def warn(section: str, hero_id: str, slot: str, code: str, message: str, value=None) -> None:
    warns.append({
        'section': section, 'hero_id': hero_id, 'slot': slot,
        'code': code, 'message': message, 'value': value,
    })


def info(msg: str) -> None:
    infos.append(msg)


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'cannot read {p}: {e}')
        return None


def main() -> int:
    c5 = load_json(HSK_5STAR)
    c6 = load_json(HSK_6STAR)
    dw = load_json(DW_CATALOG)
    status = load_json(STATUS_CAT) if STATUS_CAT.exists() else None
    baseline = load_json(BASELINE_V4)
    if any(x is None for x in (c5, c6, dw, baseline)):
        return emit()

    # ─── Section 1: catalog integrity ───────────────────────────────────
    section = '1.integrity'
    e5 = c5.get('entries') or []
    e6 = c6.get('entries') or []
    dwr = dw.get('records') or []
    if len(e5) != 20:
        fail(section, f'5★ entries != 20 (got {len(e5)})')
    if len(e6) != 13:
        fail(section, f'6★ entries != 13 (got {len(e6)})')
    if len(dwr) != 13:
        fail(section, f'DW records != 13 (got {len(dwr)})')

    fn5 = 0
    for e in e5:
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers')
            if not isinstance(fn, dict):
                fail(section, f'5★ {e.get("hero_id")}.{sn}: final_numbers missing')
                continue
            if fn.get('status') != 'foundation_draft' or fn.get('runtime_ready') is not False:
                fail(section, f'5★ {e.get("hero_id")}.{sn}: foundation_draft/runtime_ready=false expected')
            fn5 += 1
    if fn5 != 100:
        fail(section, f'5★ final_numbers count != 100 (got {fn5})')

    fn6 = 0
    for e in e6:
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers')
            if not isinstance(fn, dict):
                fail(section, f'6★ {e.get("hero_id")}.{sn}: final_numbers missing')
                continue
            if fn.get('status') != 'foundation_draft' or fn.get('runtime_ready') is not False:
                fail(section, f'6★ {e.get("hero_id")}.{sn}: foundation_draft/runtime_ready=false expected')
            fn6 += 1
    if fn6 != 78:
        fail(section, f'6★ final_numbers count != 78 (got {fn6})')

    for cat, label in ((c5, '5★'), (c6, '6★')):
        if cat.get('balance_values_finalized') is not False:
            fail(section, f'{label} balance_values_finalized != false')
        if cat.get('runtime_attached') is not False:
            fail(section, f'{label} runtime_attached != false')
        if cat.get('battle_runtime_attached') is not False:
            fail(section, f'{label} battle_runtime_attached != false')
    info('integrity: 5★ 100/100 + 6★ 78/78 foundation_draft, runtime_ready=false ✓')

    # ─── Section 2: ultimate/burst spike audit (6★ only — 5★ has no ult)─
    section = '2.burst'
    for e in e6:
        hid = e.get('hero_id', '?')
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers') or {}
            dmg = fn.get('damage_multiplier_pct')
            tgt = fn.get('target_count') or 1
            if dmg is None:
                continue
            # PvP cap suggestion: ST hits with dmg >= threshold
            if sn in ('ultimate', 'skill_2') and tgt == 1 and dmg >= PVP_DMG_CAP_SINGLE_TARGET:
                warn(section, hid, sn, 'pvp_cap_single_target_burst',
                     f'ST {sn} damage_multiplier_pct={dmg} ≥ {PVP_DMG_CAP_SINGLE_TARGET}; '
                     'recommend PvP damage cap or one-shot prevention rule',
                     value=dmg)
            if sn == 'ultimate' and tgt >= 2 and dmg >= PVP_DMG_CAP_AOE_PER_TARGET:
                warn(section, hid, sn, 'pvp_cap_aoe_ultimate',
                     f'AoE ultimate damage_multiplier_pct={dmg} ≥ {PVP_DMG_CAP_AOE_PER_TARGET} per target '
                     f'(tgt={tgt}); recommend PvP AoE damage cap',
                     value=dmg)
            if sn == 'ultimate' and dmg >= 600:
                warn(section, hid, sn, 'boss_mitigation_candidate',
                     f'ultimate dmg={dmg} is in high band; mark for boss damage-mitigation tuning',
                     value=dmg)

    # ─── Section 3: control/status audit ────────────────────────────────
    section = '3.control_status'
    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id', '?')
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                fn = slot.get('final_numbers') or {}
                core_ids = set(slot.get('core_status_ids') or [])
                hard = core_ids & HARD_CONTROL_TAGS
                soft = core_ids & SOFT_CONTROL_TAGS
                chance = fn.get('status_chance_pct')
                dur = fn.get('status_duration_turns')
                if hard:
                    warn(section, hid, sn, 'boss_resistance_hard_control',
                         f'{label} hard control {sorted(hard)} present; recommend boss resistance / immunity windows',
                         value={'hard': sorted(hard), 'chance': chance, 'dur': dur})
                if chance is not None and chance >= HIGH_STATUS_CHANCE:
                    warn(section, hid, sn, 'pvp_status_chance_cap',
                         f'{label} status_chance_pct={chance} ≥ {HIGH_STATUS_CHANCE}; recommend PvP cap (≤ 85)',
                         value=chance)
                if hard and dur is not None and dur >= 3:
                    warn(section, hid, sn, 'pvp_hard_control_duration_cap',
                         f'{label} hard control duration={dur} turns; recommend PvP cap at 1–2 turns',
                         value=dur)
                if soft:
                    warn(section, hid, sn, 'soft_control_review',
                         f'{label} soft control {sorted(soft)} present; verify stacking and cleanse rules at runtime',
                         value=sorted(soft))

    # ─── Section 4: heal/shield/revive audit ────────────────────────────
    section = '4.heal_shield_revive'
    revive_carriers = []
    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id', '?')
            blob = json.dumps(e, ensure_ascii=False).lower()
            if 'revive' in blob or 'death_protection' in blob:
                revive_carriers.append((label, hid))
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                fn = slot.get('final_numbers') or {}
                heal = fn.get('healing_multiplier_pct')
                shi = fn.get('shield_multiplier_pct')
                if heal is not None and heal >= HIGH_HEAL_MULT:
                    warn(section, hid, sn, 'pvp_heal_cap',
                         f'{label} healing_multiplier_pct={heal} ≥ {HIGH_HEAL_MULT}; recommend PvP heal cap (~−25%) and boss raid effectiveness cap',
                         value=heal)
                if shi is not None and shi >= HIGH_SHIELD_MULT:
                    warn(section, hid, sn, 'pvp_shield_cap',
                         f'{label} shield_multiplier_pct={shi} ≥ {HIGH_SHIELD_MULT}; recommend PvP shield cap and stacking rule',
                         value=shi)
    if revive_carriers:
        for label, hid in revive_carriers:
            warn(section, hid, '*', 'revive_loop_anti',
                 f'{label} {hid}: carries revive/death_protection semantics; recommend anti-loop rule (cooldown / per-battle cap)',
                 value=None)

    # ─── Section 5: Marchio Boreale Borea-only ──────────────────────────
    section = '5.marchio_boreale'
    leak_found = []
    borea_marchio_blocks = 0
    for e in e6:
        hid = e.get('hero_id')
        if hid == 'greek_borea':
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                fn = slot.get('final_numbers') or {}
                if fn.get('marchio_boreale_stack_values') is not None:
                    borea_marchio_blocks += 1
                    mb = fn['marchio_boreale_stack_values']
                    if mb.get('owner_hero_id') != 'greek_borea':
                        fail(section, f'greek_borea.{sn}: marchio owner_hero_id != greek_borea')
                    if mb.get('design_only') is not True or mb.get('runtime_ready') is not False:
                        fail(section, f'greek_borea.{sn}: marchio design_only/runtime_ready violation')
                    warn(section, hid, sn, 'marchio_pvp_cap',
                         f'Marchio stacks PvP={mb.get("max_stacks_pvp")}, PvE={mb.get("max_stacks_pve")}: '
                         f'confirm cap policy and team-wide damage amp prevention',
                         value={'pvp': mb.get('max_stacks_pvp'), 'pve': mb.get('max_stacks_pve')})
        else:
            blob = json.dumps(e, ensure_ascii=False).lower()
            if 'marchio_boreale' in blob or 'marchio boreale' in blob:
                leak_found.append(hid)
    if leak_found:
        fail(section, f'marchio_boreale leaked into non-Borea entries: {leak_found}')
    else:
        info(f'marchio_boreale: Borea-only ({borea_marchio_blocks} Borea slots with draft stack values) ✓')

    # ─── Section 6: domain/effect policy audit ──────────────────────────
    section = '6.domain'
    domain_hits = []
    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id', '?')
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                tags = [str(t).lower() for t in (slot.get('core_effect_tags') or [])]
                ids = [str(s).lower() for s in (slot.get('core_status_ids') or [])]
                if any('domain' in t for t in tags) or any('domain' in s for s in ids):
                    domain_hits.append((label, hid, sn,
                                        [t for t in tags if 'domain' in t],
                                        [s for s in ids if 'domain' in s]))
    if domain_hits:
        for label, hid, sn, t, s in domain_hits:
            warn(section, hid, sn, 'domain_stack_policy',
                 f'{label} domain-like tag detected (tags={t}, status={s}); recommend "one-domain-active OR strongest-wins" policy and duration cap',
                 value={'tags': t, 'status': s})
    else:
        info('domain: no domain-like tags or status IDs found in 5★/6★ ✓')

    # ─── Section 7: Divine Weapon synergy placeholders ──────────────────
    section = '7.dw_synergy'
    dw_5star_leak = []
    dw_6star_count = 0
    dw_6star_bad = []
    for e in e5:
        if 'divine_weapon_id' in e or 'divine_weapon' in json.dumps(e, ensure_ascii=False).lower():
            blob = json.dumps(e, ensure_ascii=False).lower()
            if 'divine_weapon_id' in blob:
                dw_5star_leak.append(e.get('hero_id'))
    if dw_5star_leak:
        fail(section, f'5★ entries reference divine_weapon_id (forbidden): {dw_5star_leak}')

    for e in e6:
        hid = e.get('hero_id', '?')
        for sn, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            fn = slot.get('final_numbers') or {}
            dws = fn.get('divine_weapon_synergy_placeholder')
            if dws is None:
                dw_6star_bad.append(f'{hid}.{sn}:missing')
                continue
            dw_6star_count += 1
            if dws.get('design_only') is not True:
                dw_6star_bad.append(f'{hid}.{sn}:design_only!=true')
            if dws.get('runtime_ready') is not False:
                dw_6star_bad.append(f'{hid}.{sn}:runtime_ready!=false')
            if dws.get('numeric_modifier_pct') is not None:
                dw_6star_bad.append(f'{hid}.{sn}:numeric_modifier_pct!=null')
    if dw_6star_bad:
        fail(section, f'6★ DW synergy placeholder violations: {dw_6star_bad[:5]}{" ..." if len(dw_6star_bad)>5 else ""}')
    if dw_6star_count == 78:
        info('DW synergy placeholders: 78/78 design_only=true, runtime_ready=false, numeric_modifier_pct=null ✓')
    warn('7.dw_synergy', '*', '*', 'dw_future_cap',
         'RECO: future runtime adapter must cap divine_weapon_synergy numeric modifier to ≤ +10% global; '
         'no live hooks until RM1.33-A feature flag SKILL_KIT_RUNTIME_ENABLED=false is flipped explicitly')

    # ─── Section 8: Borea safety / forbidden hero IDs ───────────────────
    section = '8.borea_safety'
    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id')
            if hid in FORBIDDEN_HERO_IDS and hid != 'greek_borea':
                fail(section, f'{label} forbidden hero_id present: {hid}')
    borea = next((e for e in e6 if e.get('hero_id') == 'greek_borea'), None)
    if borea is None:
        fail(section, 'greek_borea entry missing in 6★ catalog')
    else:
        if borea.get('release_group') != 'launch_extra_premium':
            fail(section, f"greek_borea release_group != 'launch_extra_premium'")
        if borea.get('runtime_attached') is True:
            fail(section, 'greek_borea runtime_attached==true')
        info('borea_safety: greek_borea catalog-only, launch_extra_premium, runtime_attached=false ✓')

    # ─── Section 9: baseline anchor sanity ──────────────────────────────
    section = '9.baseline_v4'
    if baseline.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
        fail(section, 'baseline_v4 file baseline_id mismatch')
    cnt = baseline.get('counts') or {}
    if cnt.get('5star_final_numbers_objects') != 100 or cnt.get('6star_final_numbers_objects') != 78:
        fail(section, f"baseline counts mismatch: {cnt}")
    info('baseline v4: anchor present, declared counts 5★=100 6★=78 ✓')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.32-C — Boss / PvP / Domain Cap Audit')
        for f in failures:
            print(f'  - {f}')
        if warns:
            print(f'WARNs (informational, {len(warns)}):')
            for w in warns[:20]:
                print(f'  ! [{w["section"]}/{w["code"]}] {w["hero_id"]}.{w["slot"]}: {w["message"]}')
            if len(warns) > 20:
                print(f'  ! ... (+{len(warns) - 20} more)')
        return 1

    # PASS
    print('PASS: RM1.32-C — Boss / PvP / Domain Cap Audit')
    for i in infos:
        print(f'  i {i}')
    # WARN summary by section/code
    by_section: dict[str, dict[str, int]] = {}
    for w in warns:
        by_section.setdefault(w['section'], {}).setdefault(w['code'], 0)
        by_section[w['section']][w['code']] += 1
    print(f'WARNs (informational, {len(warns)}):')
    for sec, codes in sorted(by_section.items()):
        for code, n in sorted(codes.items()):
            print(f'  ! [{sec}] {code}: {n} finding(s)')
    print('Recommendation: see hero_skill_kits_balance_cap_delta_plan_v1.json for design-only delta plan.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
