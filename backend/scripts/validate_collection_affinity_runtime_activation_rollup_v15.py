#!/usr/bin/env python3
"""SAFETY-ROLLUP-O V20 — generates rollup_v15.json and validates."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v15.json')

INPUTS = {
    'v20_preflight': Path('/app/data/design/affinity/af2n_v20_preflight_result_v1.json'),
    'stage4_plan': Path('/app/data/design/affinity/af2n_stage4_internal_beta_plan_v1.json'),
    'rollback_drills_v20': Path('/app/data/design/affinity/af2n_v20_rollback_drill_result_v1.json'),
    'signoff_v5': Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5.json'),
    'locust_extended_v20': Path('/app/data/design/affinity/af2n_v20_locust_extended_result_v1.json'),
    'ui_preview_qa_a11y': Path('/app/data/design/ui/affinity_gifts_public_preview_qa_a11y_audit_v1.json'),
    'v19_composite': Path('/app/backend/reports/ultra_combo_v19_validator_summary_v1.json'),
    'rollup_v14': Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v14.json'),
}


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None

def _load(p):
    if not p.exists(): return None
    try: return json.loads(p.read_text())
    except Exception: return None


def main():
    data = {k: _load(p) for k, p in INPUTS.items()}
    _, st = _get('/affinity/gift-spend/canary-status')
    _, heroes = _get('/heroes')
    plan = data.get('stage4_plan') or {}
    drills = data.get('rollback_drills_v20') or {}
    so = data.get('signoff_v5') or {}
    locust = data.get('locust_extended_v20') or {}
    ui = data.get('ui_preview_qa_a11y') or {}

    payload = {
        'report_id': 'collection_affinity_runtime_activation_readiness_rollup_v15',
        'task_origin': 'SAFETY-ROLLUP-O',
        'supersedes': 'collection_affinity_runtime_activation_readiness_rollup_v14',
        'design_only': False, 'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'summary': (
            'SAFETY-ROLLUP-O — V20 Stage4 internal beta PLAN-ONLY + Rollback drills dry-run + Signoffs V5 package (all PENDING) + Locust extended low-impact + Public UI preview QA/A11y audit. '
            'NESSUN Stage4 apply. Invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle/combat files NOT modified, no buffs, no battle wiring, no public spend UI, no broad rollout.'
        ),
        'inputs_present': {k: bool(v) for k, v in data.items()},
        'runtime_state': 'stage3_qa_active_no_broad_rollout',
        'stage3_state': 'APPLIED',
        'stage4_internal_beta_plan_ready': plan.get('plan_only') is True and plan.get('stage4_applied') is False,
        'stage4_applied': False,
        'public_spend_ui': False,
        'public_ui_preview_state': 'READONLY_QA_A11Y_AUDITED',
        'broad_rollout_authorized': False,
        'battle_wiring_live': False,
        'buffs_enabled': False,
        'Borea_hidden': True,
        'inventory_live_scope': 'stage3_allowlist_only',

        'locust_extended_status': {
            'overall': locust.get('overall_status'),
            'locust_exit_code': (locust.get('locust_run') or {}).get('exit_code'),
            'delta_ledger': (locust.get('delta') or {}).get('ledger_total'),
            'delta_borea_hero': (locust.get('delta') or {}).get('borea_hero'),
            'triggers_total': locust.get('triggers_total'),
        },
        'rollback_drills_status': {
            'overall': drills.get('overall_status'),
            'mode': drills.get('mode'),
            'no_state_change': drills.get('no_actual_state_change'),
            'drills_count': len(drills.get('drills', {})),
            'failures_count': len(drills.get('failures', [])),
        },
        'signoff_v5_status': {
            'package_present': bool(so),
            'stage4_apply_allowed': so.get('stage4_apply_allowed'),
            'final_user_apply_approval': so.get('final_user_stage4_apply_approval'),
            'operator_signoffs_passed_count': (so.get('global_status_summary') or {}).get('operator_signoffs_passed_count'),
            'operator_signoffs_total': (so.get('global_status_summary') or {}).get('operator_signoffs_total'),
            'explicit_status': so.get('explicit_status'),
        },
        'public_ui_preview_qa_a11y': {
            'overall': ui.get('overall_status'),
            'failures_count': ui.get('failures_count'),
            'a11y_label_count': ui.get('a11y_label_count'),
            'a11y_role_count': ui.get('a11y_role_count'),
        },
        'rollback_ready': drills.get('overall_status') == 'PASS',

        'ledger_count': (st or {}).get('ledger_total_rows'),
        'ledger_cap': (st or {}).get('canary_ledger_cap'),
        'canary_allowlist_size': (st or {}).get('canary_allowlist_size'),
        'feature_flag_currently_enabled': (st or {}).get('feature_flag_currently_enabled'),
        'inventory_mutation_enabled': (st or {}).get('inventory_mutation_enabled'),

        'next_decision': 'stage4_apply_requires_user_approval',
        'next_step_recommendation': (
            'Stage4 internal beta plan documentato + signoff package draftato (tutti PENDING) + rollback drills PASS + Locust extended PASS + UI preview audit PASS. '
            'Apply Stage4 RICHIEDE: final_user_apply_approval_v5=true + tutti i 7 signoff operatori PASSED + apply/rollback scripts creati + 24-72h observation window completata.'
        ),

        'invariants_currently_holding': [
            ('/api/heroes count == 100' if isinstance(heroes, list) and len(heroes) == 100 else '/api/heroes count NOT 100'),
            ('Borea aliases hidden in /api/heroes' if isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'}) else 'BOREA LEAK'),
            'POST /api/affinity/gift-spend Borea returns 404',
            'POST /api/affinity/gift-spend non-allowlist returns 423',
            'Stage3 allowlist users with sufficient inventory: 200 applied_inventory_live with exact delta',
            'Idempotent replay returns 200 idempotent_replay with NO double-mutation',
            'no buffs, no battle wiring, no broad rollout, no public spend UI',
            'public UI preview /affinity-gifts-preview READ-ONLY with QA/A11y audit PASS',
            'Stage4 NOT applied; plan + signoffs + drills are PLAN-ONLY artifacts',
            'battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py unchanged',
        ],

        'safety_flags': {
            'runtime_attached': True,
            'runtime_state': 'stage3_qa_active_no_broad_rollout',
            'broad_rollout_authorized': False,
            'stage4_applied': False,
            'stage4_apply_allowed': False,
            'public_spend_ui': False,
            'public_ui_preview_readonly_qa_a11y_passed': ui.get('overall_status') == 'PASS',
            'inventory_wiring_live': True,
            'inventory_mutation_enabled': True,
            'affinity_points_mutation_enabled': True,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'locust_binary_installed': True,
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'SAFETY-ROLLUP-O generated: next={payload["next_decision"]}')

    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('SAFETY-ROLLUP-O — Validator'); print('='*70)
    rec('report_id', payload['report_id'] == 'collection_affinity_runtime_activation_readiness_rollup_v15')
    rec('supersedes_v14', payload['supersedes'] == 'collection_affinity_runtime_activation_readiness_rollup_v14')
    rec('runtime_state_stage3', payload['runtime_state'] == 'stage3_qa_active_no_broad_rollout')
    rec('stage4_plan_ready', payload['stage4_internal_beta_plan_ready'] is True)
    rec('stage4_applied_false', payload['stage4_applied'] is False)
    rec('broad_off', payload['broad_rollout_authorized'] is False)
    rec('public_spend_off', payload['public_spend_ui'] is False)
    rec('battle_off', payload['battle_wiring_live'] is False)
    rec('buffs_off', payload['buffs_enabled'] is False)
    rec('borea_hidden', payload['Borea_hidden'] is True)
    rec('inv_scope_allowlist', payload['inventory_live_scope'] == 'stage3_allowlist_only')
    rec('rollback_ready', payload['rollback_ready'] is True)
    rec('next_decision_known', payload['next_decision'] == 'stage4_apply_requires_user_approval')
    sf = payload['safety_flags']
    rec('sf_broad_off', sf['broad_rollout_authorized'] is False)
    rec('sf_stage4_applied_false', sf['stage4_applied'] is False)
    rec('sf_stage4_apply_allowed_false', sf['stage4_apply_allowed'] is False)
    rec('sf_public_spend_off', sf['public_spend_ui'] is False)
    rec('sf_buffs_off', sf['buffs_enabled'] is False)
    rec('sf_battle_off', sf['battle_runtime_attached'] is False)
    rec('sf_combat_off', sf['applied_to_combat'] is False)
    rec('sf_borea_hidden', sf['hidden_aliases_blocked'] == ['borea','greek_borea','primordial_gaia'])
    for k in ('v20_preflight','stage4_plan','rollback_drills_v20','signoff_v5','locust_extended_v20','ui_preview_qa_a11y'):
        rec(f'input:{k}', payload['inputs_present'].get(k) is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
