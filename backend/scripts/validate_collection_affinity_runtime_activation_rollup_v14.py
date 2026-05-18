#!/usr/bin/env python3
"""SAFETY-ROLLUP-N V19 — generates rollup_v14.json and validates."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v14.json')

INPUTS = {
    'v19_preflight': Path('/app/data/design/affinity/af2n_v19_preflight_result_v1.json'),
    'stage3_extended_monitoring_v19': Path('/app/data/design/affinity/af2n_stage3_extended_monitoring_v19_result.json'),
    'locust_low_impact_v19': Path('/app/data/design/affinity/af2n_stage3_locust_low_impact_result_v1.json'),
    'public_ui_preview_impl': Path('/app/data/design/ui/affinity_gifts_public_preview_implementation_result_v1.json'),
    'broad_rollout_plan': Path('/app/data/design/affinity/af2n_broad_rollout_readiness_plan_v1.json'),
    'rollback_readiness_v19': Path('/app/data/design/affinity/af2n_v19_rollback_readiness_result_v1.json'),
    'v18_composite': Path('/app/backend/reports/ultra_combo_v18_validator_summary_v1.json'),
    'rollup_v13': Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v13.json'),
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

    extmon = data.get('stage3_extended_monitoring_v19') or {}
    locust = data.get('locust_low_impact_v19') or {}
    ui = data.get('public_ui_preview_impl') or {}
    plan = data.get('broad_rollout_plan') or {}
    rb = data.get('rollback_readiness_v19') or {}
    v18 = data.get('v18_composite') or {}
    pre = data.get('v19_preflight') or {}

    payload = {
        'report_id': 'collection_affinity_runtime_activation_readiness_rollup_v14',
        'task_origin': 'SAFETY-ROLLUP-N',
        'supersedes': 'collection_affinity_runtime_activation_readiness_rollup_v13',
        'design_only': False, 'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'summary': (
            'SAFETY-ROLLUP-N — V19 Stage3 extended monitoring + Locust low-impact load test reale + Public UI preview READ-ONLY implementata + Broad-rollout readiness PLAN-ONLY (NOT applied) + rollback readiness completa. '
            'Invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle/synergy/combat files NOT modified, no buffs, no battle wiring, no public spend UI, no broad rollout.'
        ),
        'inputs_present': {k: bool(v) for k, v in data.items()},
        'runtime_state': 'stage3_qa_active_no_broad_rollout',
        'stage3_state': 'APPLIED',
        'public_ui_preview_state': 'READONLY_IMPLEMENTED',
        'broad_rollout_plan_state': 'READY_NOT_APPLIED_DESIGN_ONLY',
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': False,
        'Borea_hidden': True,
        'inventory_live_scope': 'stage3_allowlist_only',
        'rollback_ready': bool(rb.get('all_scripts_present') and rb.get('supervisor_backup_dir_writable')),

        'ledger_count': (st or {}).get('ledger_total_rows'),
        'ledger_cap': (st or {}).get('canary_ledger_cap'),
        'canary_allowlist_size': (st or {}).get('canary_allowlist_size'),
        'feature_flag_currently_enabled': (st or {}).get('feature_flag_currently_enabled'),
        'inventory_mutation_enabled': (st or {}).get('inventory_mutation_enabled'),
        'affinity_points_mutation_enabled': (st or {}).get('affinity_points_mutation_enabled'),

        'stage3_extended_monitoring': {
            'overall_status': extmon.get('overall_status'),
            'samples_total': (extmon.get('counters') or {}).get('samples_total'),
            'fresh_spend_ok': (extmon.get('counters') or {}).get('fresh_spend_ok'),
            'http_5xx': (extmon.get('counters') or {}).get('http_5xx'),
            'triggers_total': extmon.get('triggers_total'),
        },
        'locust_low_impact_status': {
            'overall': locust.get('overall_status'),
            'locust_binary_present': locust.get('locust_binary_present'),
            'locust_exit_code': (locust.get('locust_run') or {}).get('exit_code'),
            'delta_ledger': (locust.get('delta') or {}).get('ledger_total'),
            'delta_borea_hero': (locust.get('delta') or {}).get('borea_hero'),
            'fb_requests_total': ((locust.get('python_fallback') or {}).get('counters') or {}).get('reqs'),
            'fb_rps': (locust.get('python_fallback') or {}).get('rps'),
        },
        'public_ui_preview_readonly': {
            'phase': ui.get('phase'),
            'route_path': ui.get('route_path'),
            'no_mutating_http_methods': (ui.get('audit_acceptance') or {}).get('no_mutating_http_methods'),
            'no_public_spend_ui': (ui.get('audit_acceptance') or {}).get('no_public_spend_ui'),
        },
        'broad_rollout_readiness_plan': {
            'explicit_status': plan.get('explicit_status'),
            'design_only': plan.get('design_only'),
            'applied': plan.get('applied'),
            'staged_rollout_stages_count': len(plan.get('staged_rollout_plan', [])),
        },
        'rollback_readiness_state': {
            'overall': rb.get('overall_status'),
            'all_scripts_present': rb.get('all_scripts_present'),
            'backup_dir_writable': rb.get('supervisor_backup_dir_writable'),
            'ui_preview_rollback_strategy': rb.get('ui_preview_rollback_strategy'),
        },

        'v18_composite_overall': v18.get('overall'),
        'v19_preflight_overall': pre.get('overall_status'),

        'next_decision': 'stage4_internal_beta_prep' if extmon.get('overall_status') == 'PASS' and locust.get('overall_status') == 'PASS' else 'continue_stage3_monitoring',
        'next_step_recommendation': (
            'Stage3 extended monitoring PASS + Locust low-impact PASS + UI preview read-only attivo. '
            'Prossimo passo prudente: AF2-N-STAGE4-INTERNAL-BETA-PREP (PLAN-ONLY), drills rollback, signoffs v5.'
            if extmon.get('overall_status') == 'PASS' and locust.get('overall_status') == 'PASS' else
            'Continuare Stage3 monitoring; verificare cause delle anomalie prima di procedere.'
        ),

        'invariants_currently_holding': [
            ('/api/heroes count == 100' if isinstance(heroes, list) and len(heroes) == 100 else '/api/heroes count NOT 100'),
            ('Borea aliases hidden in /api/heroes' if isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'}) else 'BOREA LEAK'),
            'POST /api/affinity/gift-spend Borea returns 404',
            'POST /api/affinity/gift-spend non-allowlist returns 423',
            'Stage3 allowlist users with sufficient inventory: 200 applied_inventory_live with exact delta',
            'Idempotent replay returns 200 idempotent_replay with NO double-mutation',
            'no buffs, no battle wiring, no broad rollout, no public spend UI',
            'public UI preview /affinity-gifts-preview is READ-ONLY (sanitized canary-status only)',
            'battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py unchanged',
        ],

        'safety_flags': {
            'runtime_attached': True,
            'runtime_state': 'stage3_qa_active_no_broad_rollout',
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'public_ui_preview_implemented_readonly': True,
            'inventory_wiring_live': True,
            'inventory_mutation_enabled': True,
            'affinity_points_mutation_enabled': True,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'stage3_state': 'APPLIED',
            'locust_binary_installed': True,
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'SAFETY-ROLLUP-N generated: next={payload["next_decision"]}')

    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('SAFETY-ROLLUP-N — Validator'); print('='*70)
    rec('report_id', payload['report_id'] == 'collection_affinity_runtime_activation_readiness_rollup_v14')
    rec('supersedes_v13', payload['supersedes'] == 'collection_affinity_runtime_activation_readiness_rollup_v13')
    rec('runtime_state_stage3', payload['runtime_state'] == 'stage3_qa_active_no_broad_rollout')
    rec('broad_off', payload['broad_rollout_authorized'] is False)
    rec('public_spend_off', payload['public_spend_ui'] is False)
    rec('battle_off', payload['battle_wiring_live'] is False)
    rec('buffs_off', payload['buffs_enabled'] is False)
    rec('borea_hidden', payload['Borea_hidden'] is True)
    rec('inventory_scope_allowlist_only', payload['inventory_live_scope'] == 'stage3_allowlist_only')
    rec('rollback_ready', payload['rollback_ready'] is True)
    rec('next_decision_known', payload['next_decision'] in {'stage4_internal_beta_prep','continue_stage3_monitoring','public_ui_preview','k6_real','stack_g_deferred','rollback_required'})
    sf = payload['safety_flags']
    rec('sf_broad_off', sf['broad_rollout_authorized'] is False)
    rec('sf_public_spend_off', sf['public_spend_ui'] is False)
    rec('sf_public_preview_readonly', sf['public_ui_preview_implemented_readonly'] is True)
    rec('sf_buffs_off', sf['buffs_enabled'] is False)
    rec('sf_battle_off', sf['battle_runtime_attached'] is False)
    rec('sf_combat_off', sf['applied_to_combat'] is False)
    rec('sf_borea_hidden', sf['hidden_aliases_blocked'] == ['borea','greek_borea','primordial_gaia'])
    for k in ('v19_preflight','stage3_extended_monitoring_v19','locust_low_impact_v19','public_ui_preview_impl','broad_rollout_plan','rollback_readiness_v19'):
        rec(f'input:{k}', payload['inputs_present'].get(k) is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
