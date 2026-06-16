#!/usr/bin/env python3
"""PRE_QA_P0 — validate_current_public_guardrail_snapshot_v1.

Verifica che il public_guardrail_current_snapshot_v1.json sia consistente con
le verita' attuali dei validator 119C/119D/120A/120B (cioe' che i conteggi
dichiarati nello snapshot corrispondano ai conteggi prodotti dai validator
attualmente passanti).

Logica:

  1. Carica public_guardrail_current_snapshot_v1.json.
  2. Carica i latest JSON di 119C/119D/120B (se esistono).
  3. Conferma:
     - public_menu.visible_categories_count == 119D.visible_category_count
     - public_menu.visible_items_count     == 119D.visible_item_count
     - classification_119d == 119D.classification_counter
     - tier_counts_120a tier_0/tier_1/tier_2/tier_3 == 120B.tier_counts
     - unsafe_exposed_count == 0
     - unknown_needs_review_count == 0
     - leaked_blocked_routes_count == 0
     - battle_preview_modes count == 5
     - economy_isolation tutti false
     - no_unlock_applied_in_this_pack tutti false
  4. Conferma i token canonici presenti nei file runtime senza modificarli
     (pre-battle-lobby.tsx, combat.tsx) - read-only check.

Onesto, read-only.
"""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
TRUTH_DIR = os.path.join(R, 'data', 'design', 'current_truth')
REPORTS_DIR = os.path.join(R, 'backend', 'reports')

GUARDRAIL_FP = os.path.join(TRUTH_DIR, 'public_guardrail_current_snapshot_v1.json')
D119D_LATEST = os.path.join(
    REPORTS_DIR, 'pre_qa_pack_119d_public_menu_route_health_latest.json')
D120B_LATEST = os.path.join(
    REPORTS_DIR,
    'pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json')

PB_LOBBY = os.path.join(R, 'frontend', 'app', 'pre-battle-lobby.tsx')
COMBAT = os.path.join(R, 'frontend', 'app', 'combat.tsx')

PB_TOKENS = ['is_preview', 'reward_policy', 'preview',
             'blocked_no_team_for_server', 'battle_engine_mode']
COMBAT_TOKENS = ['PREVIEW_REWARD_LOCK_ACTIVE', 'PREVIEW_NON_AUTHORITATIVE']


def _check_tokens(fp: str, tokens: list) -> dict:
    if not os.path.exists(fp):
        return {'exists': False, 'missing': tokens, 'found': []}
    src = open(fp, encoding='utf-8', errors='replace').read()
    missing = [t for t in tokens if t not in src]
    found = [t for t in tokens if t in src]
    return {'exists': True, 'missing': missing, 'found': found}


def main() -> int:
    failures = []
    if not os.path.exists(GUARDRAIL_FP):
        failures.append(f'guardrail snapshot mancante: {GUARDRAIL_FP}')
        return _emit(failures)

    g = json.load(open(GUARDRAIL_FP, encoding='utf-8'))

    # Cross-check con 119D latest
    if os.path.exists(D119D_LATEST):
        d119d = json.load(open(D119D_LATEST, encoding='utf-8'))
        if g['public_menu']['visible_categories_count'] != d119d.get('visible_category_count'):
            failures.append(
                f"visible_categories_count drift vs 119D: "
                f"{g['public_menu']['visible_categories_count']} vs "
                f"{d119d.get('visible_category_count')}")
        if g['public_menu']['visible_items_count'] != d119d.get('visible_item_count'):
            failures.append(
                f"visible_items_count drift vs 119D: "
                f"{g['public_menu']['visible_items_count']} vs "
                f"{d119d.get('visible_item_count')}")
        for k, v in (d119d.get('classification_counter') or {}).items():
            if g['classification_119d'].get(k) != v:
                failures.append(
                    f"classification_119d drift {k}: "
                    f"{g['classification_119d'].get(k)} vs {v}")
        if d119d.get('unsafe_exposed_count') != 0 or g.get('unsafe_exposed_count') != 0:
            failures.append('unsafe_exposed_count != 0')
        if d119d.get('unknown_count') != 0 or g.get('unknown_needs_review_count') != 0:
            failures.append('unknown_count != 0')
        if d119d.get('leaked_blocked_routes_count') != 0 or g.get('leaked_blocked_routes_count') != 0:
            failures.append('leaked_blocked_routes_count != 0')
    else:
        failures.append(f'119D latest non trovato: {D119D_LATEST}')

    if os.path.exists(D120B_LATEST):
        d120b = json.load(open(D120B_LATEST, encoding='utf-8'))
        tc = d120b.get('tier_counts', {})
        ours = g.get('tier_counts_120a', {})
        for k in ('tier_0_visual', 'tier_1_visual', 'tier_2_dry_run',
                  'tier_3_battle_preview'):
            if tc.get(k) != ours.get(k):
                failures.append(f'tier_count drift {k}: '
                                f'{ours.get(k)} vs {tc.get(k)}')
        if d120b.get('verdict') != 'PASS':
            failures.append(f'120B verdict != PASS: {d120b.get("verdict")!r}')
    else:
        failures.append(f'120B latest non trovato: {D120B_LATEST}')

    # Economy isolation: tutti i flag devono essere false.
    eco = g.get('economy_isolation') or {}
    for k, v in eco.items():
        if v is not False:
            failures.append(f'economy_isolation.{k} != false (val={v!r})')

    # Battle preview modes: 5 esatti.
    if len(g.get('battle_preview_modes') or []) != 5:
        failures.append(
            f'battle_preview_modes attesi 5, trovati '
            f'{len(g.get("battle_preview_modes") or [])}')

    # Battle preview guards.
    bg = g.get('battle_preview_guards') or {}
    for k in (
        'reward_grant_disabled', 'exp_progress_commit_disabled',
        'ranking_commit_disabled', 'battle_result_db_write_disabled',
        'authoritative_battle_runtime_disabled',
        'pre_battle_lobby_tokens_present_in_current_zip',
        'combat_tokens_present_in_current_zip',
    ):
        if bg.get(k) is not True:
            failures.append(f'battle_preview_guards.{k} != true (val={bg.get(k)!r})')

    # No unlock in this pack.
    no_unlock = g.get('no_unlock_applied_in_this_pack') or {}
    for k in (
        'runtime_unlock_applied', 'db_write_performed',
        'live_unlock_performed', 'reward_live_allowed',
        'gacha_shop_vip_bp_allowed', 'env_flag_changed',
    ):
        if no_unlock.get(k) is not False:
            failures.append(
                f'no_unlock_applied_in_this_pack.{k} != false '
                f'(val={no_unlock.get(k)!r})')

    # Read-only check token nei file runtime.
    pb_check = _check_tokens(PB_LOBBY, PB_TOKENS)
    combat_check = _check_tokens(COMBAT, COMBAT_TOKENS)
    if not pb_check['exists'] or pb_check['missing']:
        failures.append(
            f'pre-battle-lobby.tsx missing tokens: {pb_check["missing"]}')
    if not combat_check['exists'] or combat_check['missing']:
        failures.append(
            f'combat.tsx missing tokens: {combat_check["missing"]}')

    report = {
        'tool': 'validate_current_public_guardrail_snapshot_v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'inputs': {
            'guardrail_snapshot': os.path.relpath(GUARDRAIL_FP, R),
            'd119d_latest': os.path.relpath(D119D_LATEST, R)
                if os.path.exists(D119D_LATEST) else None,
            'd120b_latest': os.path.relpath(D120B_LATEST, R)
                if os.path.exists(D120B_LATEST) else None,
        },
        'pb_lobby_check': pb_check,
        'combat_check': combat_check,
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(
        REPORTS_DIR, 'current_public_guardrail_snapshot_audit_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('============== CURRENT PUBLIC GUARDRAIL SNAPSHOT AUDIT ==============')
    print(f"  verdict: {report['verdict']}")
    print(f"  failures: {len(failures)}")
    print(f"  pb_lobby tokens ok: {not pb_check['missing'] and pb_check['exists']}")
    print(f"  combat tokens ok:   {not combat_check['missing'] and combat_check['exists']}")
    print(f"  JSON:    {out_fp}")
    print('=====================================================================')

    if failures:
        print('')
        print('[v_p0_current_public_guardrail_snapshot] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1

    print('')
    print('[v_p0_current_public_guardrail_snapshot] OK '
          'unsafe_exposed=0 unknown=0 leaked=0 no_unlock_applied=true')
    return 0


def _emit(failures: list) -> int:
    print('[v_p0_current_public_guardrail_snapshot] FAIL')
    for f in failures:
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
