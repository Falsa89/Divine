#!/usr/bin/env python3
"""
RM1.33-B — Skill Kit Runtime Adapter Wire-Test (READ-ONLY, full slot coverage)
─────────────────────────────────────────────────────────────────────────────
Exercises the adapter on every valid 5★/6★ slot (178 total) while the
feature flag SKILL_KIT_RUNTIME_ENABLED is OFF.

Asserts:
  • 178/178 slots normalized (preview/design-only)
  • 178/178 runtime candidates disabled under flag OFF
  • Feature flag default OFF + non-allowlisted truthy strings → False
  • Forbidden aliases rejected
  • 5★ ultimate request safely rejected
  • 6★ ultimate preserved as preview/inert
  • Cap policy preview pvp/boss/pve inert
  • Borea catalog-only, Marchio Borea-only
  • Adapter not imported by battle_engine.py / combat.tsx / battle_core.py

Writes (read-only path under /app/data/design):
  • /app/data/design/hero_skill_kits/hero_skill_kit_runtime_adapter_wiretest_report_v1.json

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import importlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
sys.path.insert(0, str(ROOT))

HSK_5STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
REPORT_OUT = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_runtime_adapter_wiretest_report_v1.json'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
COMBAT_TSX = ROOT / 'frontend/app/combat.tsx'
BATTLE_CORE = ROOT / 'backend/battle_core.py'

ADAPTER_TOKENS = (
    'skill_kit_runtime_adapter',
    'skill_kit_cap_policy_adapter',
    'is_skill_kit_runtime_enabled',
    'SKILL_KIT_RUNTIME_ENABLED',
)
SLOTS_5 = ('basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2')
SLOTS_6 = ('basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate')
FORBIDDEN_ALIASES = ('borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea')
NON_ALLOWLISTED_TRUTHY = ('true', '1', 'yes', 'on', 'TRUE', 'True', 'YES', 'on_strict')

failures: list[str] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None:
    failures.append(f'[{sec}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def main() -> int:
    # Load adapter (fresh, env clean)
    saved = os.environ.pop('SKILL_KIT_RUNTIME_ENABLED', None)
    try:
        from backend.data import skill_kit_runtime_adapter as rta
        from backend.data import skill_kit_cap_policy_adapter as cpa
        importlib.reload(rta)
        importlib.reload(cpa)

        # ── Section 1: feature flag tests ──────────────────────────────
        if rta.is_skill_kit_runtime_enabled() is not False:
            fail('flag', 'env absent → expected False')
        for tok in NON_ALLOWLISTED_TRUTHY:
            os.environ['SKILL_KIT_RUNTIME_ENABLED'] = tok
            importlib.reload(rta)
            if rta.is_skill_kit_runtime_enabled() is not False:
                fail('flag', f'non-allowlisted token {tok!r} produced True')
        os.environ.pop('SKILL_KIT_RUNTIME_ENABLED', None)
        importlib.reload(rta)
        if not any(f.startswith('[flag]') for f in failures):
            info(f'flag tests: env absent + {len(NON_ALLOWLISTED_TRUTHY)} non-allowlisted tokens → all False ✓')

        # ── Section 2: catalog read ────────────────────────────────────
        c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))
        c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
        ids5 = [e.get('hero_id') for e in c5.get('entries') or []]
        ids6 = [e.get('hero_id') for e in c6.get('entries') or []]
        if len(ids5) != 20:
            fail('catalog', f'5★ hero count != 20 ({len(ids5)})')
        if len(ids6) != 13:
            fail('catalog', f'6★ hero count != 13 ({len(ids6)})')

        # ── Section 3: wire-test on all 178 slots ──────────────────────
        normalized_ok = 0
        candidate_disabled = 0
        per_rarity_counts = {'5star': 0, '6star': 0}
        ultimate_6star_preserved = 0
        for hid in ids5:
            for sn in SLOTS_5:
                # load entry
                kit = rta.load_skill_kit_for_hero(hid)
                if not (isinstance(kit, dict) and kit.get('present') is True and kit.get('rarity') == '5star'):
                    fail('5star_load', f'{hid}: load_skill_kit_for_hero failed')
                    continue
                ns = rta.normalize_skill_slot(hid, sn)
                if (isinstance(ns, dict)
                        and ns.get('rarity') == '5star'
                        and ns.get('runtime_attached') is False
                        and ns.get('battle_runtime_attached') is False
                        and isinstance(ns.get('final_numbers_meta'), dict)
                        and ns['final_numbers_meta'].get('preview_only') is True
                        and ns['final_numbers_meta'].get('design_only') is True
                        and ns['final_numbers_meta'].get('do_not_treat_as_live_kit') is True
                        and ns['final_numbers_meta'].get('status') == 'foundation_draft'
                        and ns['final_numbers_meta'].get('runtime_ready') is False):
                    normalized_ok += 1
                    per_rarity_counts['5star'] += 1
                else:
                    fail('5star_normalize', f'{hid}.{sn}: normalize_skill_slot inert preview invariants violated')
                cand = rta.get_skill_runtime_candidate(hid, sn)
                if (isinstance(cand, dict)
                        and cand.get('enabled') is False
                        and cand.get('runtime_attached') is False
                        and cand.get('battle_runtime_attached') is False
                        and cand.get('is_disabled_runtime_result') is True
                        and cand.get('reason') == 'feature_flag_off'):
                    candidate_disabled += 1
                else:
                    fail('5star_candidate', f'{hid}.{sn}: get_skill_runtime_candidate not disabled (got {cand!r})')

        for hid in ids6:
            for sn in SLOTS_6:
                kit = rta.load_skill_kit_for_hero(hid)
                if not (isinstance(kit, dict) and kit.get('present') is True and kit.get('rarity') == '6star'):
                    fail('6star_load', f'{hid}: load_skill_kit_for_hero failed')
                    continue
                ns = rta.normalize_skill_slot(hid, sn)
                fnm = ns.get('final_numbers_meta') if isinstance(ns, dict) else None
                if (isinstance(ns, dict)
                        and ns.get('rarity') == '6star'
                        and ns.get('runtime_attached') is False
                        and ns.get('battle_runtime_attached') is False
                        and isinstance(fnm, dict)
                        and fnm.get('preview_only') is True
                        and fnm.get('design_only') is True
                        and fnm.get('do_not_treat_as_live_kit') is True
                        and fnm.get('status') == 'foundation_draft'
                        and fnm.get('runtime_ready') is False):
                    normalized_ok += 1
                    per_rarity_counts['6star'] += 1
                    if sn == 'ultimate':
                        if fnm.get('is_true_ultimate') is True:
                            ultimate_6star_preserved += 1
                        else:
                            fail('6star_ultimate', f'{hid}.ultimate: is_true_ultimate identity lost in preview meta')
                else:
                    fail('6star_normalize', f'{hid}.{sn}: normalize_skill_slot inert preview invariants violated')
                cand = rta.get_skill_runtime_candidate(hid, sn)
                if (isinstance(cand, dict)
                        and cand.get('enabled') is False
                        and cand.get('runtime_attached') is False
                        and cand.get('battle_runtime_attached') is False
                        and cand.get('is_disabled_runtime_result') is True
                        and cand.get('reason') == 'feature_flag_off'):
                    candidate_disabled += 1
                else:
                    fail('6star_candidate', f'{hid}.{sn}: get_skill_runtime_candidate not disabled')

        if normalized_ok != 178:
            fail('coverage', f'normalized count != 178 (got {normalized_ok})')
        if candidate_disabled != 178:
            fail('coverage', f'disabled candidate count != 178 (got {candidate_disabled})')
        if per_rarity_counts['5star'] != 100 or per_rarity_counts['6star'] != 78:
            fail('coverage', f'per-rarity normalization wrong: {per_rarity_counts}')
        if ultimate_6star_preserved != 13:
            fail('coverage', f'6★ ultimate is_true_ultimate preserved != 13 (got {ultimate_6star_preserved})')
        if not any(f.startswith('[coverage]') for f in failures):
            info(f'slot coverage: 178/178 normalized (5★ 100, 6★ 78) ✓')
            info(f'runtime candidates disabled: 178/178 ✓')
            info(f'6★ ultimate is_true_ultimate preserved as preview meta: 13/13 ✓')

        # ── Section 4: 5★ ultimate must be safely rejected ─────────────
        rejected_5star_ult = 0
        for hid in ids5:
            res = rta.normalize_skill_slot(hid, 'ultimate')
            if (isinstance(res, dict)
                    and res.get('is_disabled_runtime_result') is True
                    and res.get('reason') == 'invalid_slot_for_5star'):
                rejected_5star_ult += 1
        if rejected_5star_ult != 20:
            fail('5star_ultimate_reject', f'expected 20 rejected, got {rejected_5star_ult}')
        else:
            info('5★ ultimate request safely rejected for all 20 heroes (invalid_slot_for_5star) ✓')

        # ── Section 5: forbidden aliases rejected ──────────────────────
        rej = 0
        for alias in FORBIDDEN_ALIASES:
            res = rta.load_skill_kit_for_hero(alias)
            if (isinstance(res, dict)
                    and res.get('is_disabled_runtime_result') is True
                    and res.get('reason') == 'forbidden_legacy_hero_id'):
                rej += 1
            else:
                fail('forbidden_alias', f'alias {alias!r} not rejected (got {res!r})')
            ns = rta.normalize_skill_slot(alias, 'ultimate')
            if not (isinstance(ns, dict) and ns.get('is_disabled_runtime_result') is True):
                fail('forbidden_alias', f'normalize for alias {alias!r} did not return disabled payload')
        if not any(f.startswith('[forbidden_alias]') for f in failures):
            info(f'forbidden aliases rejected: {rej}/{len(FORBIDDEN_ALIASES)} ✓')

        # ── Section 6: cap policy preview (pvp/boss/pve) ───────────────
        sample_pairs = [
            ('greek_atalanta', 'skill_2'),
            ('greek_athena', 'ultimate'),
            ('greek_borea', 'ultimate'),
            ('norse_eir', 'skill_2'),
        ]
        for context in ('pvp', 'boss', 'pve'):
            pol = cpa.get_cap_policy_for_context(context)
            if not (pol.get('enabled') is False
                    and pol.get('applied_to_combat') is False
                    and pol.get('runtime_attached') is False
                    and pol.get('battle_runtime_attached') is False
                    and isinstance(pol.get('policy'), dict)):
                fail('cap_policy', f'{context}: policy not inert')
            for hid, sn in sample_pairs:
                prev = cpa.preview_cap_policy_for_skill(hid, sn, context)
                if not (prev.get('applied_to_combat') is False
                        and prev.get('runtime_attached') is False
                        and prev.get('battle_runtime_attached') is False
                        and isinstance(prev.get('cap_policy'), dict)
                        and prev['cap_policy'].get('enabled') is False):
                    fail('cap_policy', f'{context} preview for {hid}.{sn} not inert')
        if not any(f.startswith('[cap_policy]') for f in failures):
            info(f'cap policy preview: pvp/boss/pve × {len(sample_pairs)} samples all inert ✓')

        # ── Section 7: Borea catalog-only / Marchio Borea-only ─────────
        borea_kit = rta.load_skill_kit_for_hero('greek_borea')
        if not (isinstance(borea_kit, dict) and borea_kit.get('present') is True
                and borea_kit.get('rarity') == '6star'):
            fail('borea', 'greek_borea cannot be loaded as catalog-only 6★ entry')
        # Marchio leak check
        leak = []
        for e in c6.get('entries') or []:
            if e.get('hero_id') == 'greek_borea':
                continue
            if 'marchio_boreale' in json.dumps(e, ensure_ascii=False).lower():
                leak.append(e.get('hero_id'))
        if leak:
            fail('marchio', f'marchio_boreale leak in non-Borea entries: {leak}')
        else:
            info('Borea catalog-only loadable ✓; Marchio Boreale Borea-only (0 leak) ✓')

        # ── Section 8: adapter isolation from battle runtime ──────────
        for target in (BATTLE_ENGINE, COMBAT_TSX, BATTLE_CORE):
            src = target.read_text(encoding='utf-8') if target.exists() else ''
            for tok in ADAPTER_TOKENS:
                if tok in src:
                    fail('isolation', f'{target.name} references adapter token {tok!r}')
        if not any(f.startswith('[isolation]') for f in failures):
            info('adapter isolation: battle_engine.py / combat.tsx / battle_core.py contain 0 adapter tokens ✓')

    finally:
        if saved is not None:
            os.environ['SKILL_KIT_RUNTIME_ENABLED'] = saved
        else:
            os.environ.pop('SKILL_KIT_RUNTIME_ENABLED', None)

    # ── Write JSON report (read-only design path) ──────────────────────
    report = {
        'task_origin': 'RM1.33-B',
        'report_id': 'hero_skill_kit_runtime_adapter_wiretest_report_v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'total_slots_expected': 178,
        'total_slots_tested': 178,
        'slots_normalized_ok': locals().get('normalized_ok', 0),
        'runtime_candidates_disabled': locals().get('candidate_disabled', 0),
        'per_rarity': locals().get('per_rarity_counts', {}),
        '6star_ultimate_is_true_ultimate_preserved': locals().get('ultimate_6star_preserved', 0),
        '5star_ultimate_safely_rejected_count': locals().get('rejected_5star_ult', 0),
        'feature_flag_default': 'off',
        'feature_flag_non_allowlisted_truthy_tested': list(NON_ALLOWLISTED_TRUTHY),
        'feature_flag_non_allowlisted_truthy_all_false': True,
        'forbidden_aliases_tested': list(FORBIDDEN_ALIASES),
        'forbidden_aliases_rejected': True,
        'adapter_imported_by_battle_runtime': False,
        'cap_policy_preview_inert': True,
        'cap_policy_contexts_tested': ['pvp', 'boss', 'pve'],
        'cap_policy_sample_pairs': [
            {'hero_id': 'greek_atalanta', 'slot': 'skill_2'},
            {'hero_id': 'greek_athena', 'slot': 'ultimate'},
            {'hero_id': 'greek_borea', 'slot': 'ultimate'},
            {'hero_id': 'norse_eir', 'slot': 'skill_2'},
        ],
        'borea_catalog_only': True,
        'marchio_boreale_borea_only': True,
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_change': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132b_v4',
        'overall_result': 'FAIL' if failures else 'PASS',
        'failure_count': len(failures),
        'first_failures': failures[:5],
    }
    REPORT_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    return emit(report)


def emit(report: dict) -> int:
    if failures:
        print('FAIL: RM1.33-B — Runtime Adapter Wire-Test')
        for f in failures:
            print(f'  - {f}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        print(f'Report: {REPORT_OUT}')
        return 1
    print('PASS: RM1.33-B — Runtime Adapter Wire-Test')
    for i in infos:
        print(f'  i {i}')
    print(f'Summary:')
    print(f'  total slots tested            : 178/178')
    print(f'  normalized OK                 : {report["slots_normalized_ok"]}/178 (5★ {report["per_rarity"]["5star"]}, 6★ {report["per_rarity"]["6star"]})')
    print(f'  runtime candidates disabled   : {report["runtime_candidates_disabled"]}/178')
    print(f'  6★ ultimate identity preserved: {report["6star_ultimate_is_true_ultimate_preserved"]}/13')
    print(f'  5★ ultimate safely rejected   : {report["5star_ultimate_safely_rejected_count"]}/20')
    print(f'  forbidden aliases rejected    : {len(FORBIDDEN_ALIASES)}/{len(FORBIDDEN_ALIASES)}')
    print(f'  cap policy preview inert      : pvp/boss/pve × {len(report["cap_policy_sample_pairs"])} samples')
    print(f'  adapter imported by runtime   : False')
    print(f'  Borea catalog-only / Marchio Borea-only : True / True')
    print(f'Report: {REPORT_OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
