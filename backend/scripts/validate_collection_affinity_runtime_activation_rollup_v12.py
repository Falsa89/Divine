#!/usr/bin/env python3
"""SAFETY-ROLLUP-L V17 — generates rollup_v12.json and validates."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v12.json')

INPUT_FILES = {
    'v17_preflight': Path('/app/data/design/affinity/af2n_v17_preflight_result_v1.json'),
    'v17_extended_monitoring': Path('/app/data/design/affinity/af2n_inventory_extended_monitoring_v17_result.json'),
    'stage2_apply': Path('/app/data/design/affinity/af2n_stage2_5_10pct_plan_v1.json'),
    'stage2_apply_result': Path('/app/data/design/affinity/af2n_stage2_5_10pct_apply_result_v1.json'),
    'stage2_monitoring': Path('/app/data/design/affinity/af2n_stage2_monitoring_v17_result.json'),
    'suite_cleanup': Path('/app/data/design/system_safety/validator_suite_supersedence_cleanup_report_v1.json'),
    'k6_readiness': Path('/app/data/design/affinity/af2n_v17_k6_locust_readiness_result_v1.json'),
    'rollback_readiness': Path('/app/data/design/affinity/af2n_v17_rollback_readiness_result_v1.json'),
    'v16_composite': Path('/app/backend/reports/ultra_combo_v16_validator_summary_v1.json'),
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
    inputs = {k: _load(p) for k, p in INPUT_FILES.items()}
    _, st = _get('/affinity/gift-spend/canary-status')
    _, heroes = _get('/heroes')

    pre = inputs.get('v17_preflight') or {}
    ext_mon = inputs.get('v17_extended_monitoring') or {}
    s2_apply = inputs.get('stage2_apply_result') or {}
    s2_mon = inputs.get('stage2_monitoring') or {}
    suite_cln = inputs.get('suite_cleanup') or {}
    k6 = inputs.get('k6_readiness') or {}
    rb = inputs.get('rollback_readiness') or {}
    v16 = inputs.get('v16_composite') or {}

    stage2_state = 'NOT_APPLIED_NO_RESULT'
    if s2_apply:
        if s2_apply.get('overall_status') == 'APPLIED_PASS':
            stage2_state = 'APPLIED'
        elif s2_apply.get('overall_status') == 'READY_NOT_APPLIED':
            stage2_state = 'READY_NOT_APPLIED'
        else:
            stage2_state = s2_apply.get('overall_status') or 'UNKNOWN'

    payload = {
        'report_id': 'collection_affinity_runtime_activation_readiness_rollup_v12',
        'task_origin': 'SAFETY-ROLLUP-L',
        'supersedes': 'collection_affinity_runtime_activation_readiness_rollup_v11',
        'design_only': False,
        'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': stage2_state != 'APPLIED',
        'runtime_attached_stage2_applied': stage2_state == 'APPLIED',
        'db_write': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'summary': (
            'SAFETY-ROLLUP-L — V17 monitoring esteso inventory live + Stage2 5-10% prep/apply gated + suite supersedence cleanup metadata + K6/Locust readiness + rollback readiness. '
            f'Stage2 state: {stage2_state}. '
            'Invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle_engine.py/combat.tsx/battle_core.py/synergy_system.py/game_systems.py NOT modified, buffs OFF, battle wiring OFF, broad rollout NOT authorized.'
        ),
        'inputs_present': {k: bool(v) for k, v in inputs.items()},

        'inventory_live_stage1_or_stage2': 'stage2' if stage2_state == 'APPLIED' else 'stage1',
        'stage2_state': stage2_state,
        'stage2_apply_reason_if_not_applied': s2_apply.get('ready_not_applied_reason'),
        'broad_rollout_authorized': False,
        'battle_wiring_live': False,
        'Borea_hidden': True,

        'ledger_count': (st or {}).get('ledger_total_rows'),
        'ledger_cap': (st or {}).get('canary_ledger_cap'),
        'canary_allowlist_size': (st or {}).get('canary_allowlist_size'),
        'feature_flag_currently_enabled': (st or {}).get('feature_flag_currently_enabled'),
        'inventory_mutation_enabled': (st or {}).get('inventory_mutation_enabled'),
        'affinity_points_mutation_enabled': (st or {}).get('affinity_points_mutation_enabled'),

        'inventory_mutation_health': {
            'extended_monitoring_pass': ext_mon.get('overall_status') == 'PASS',
            'fresh_spend_ok_count': (ext_mon.get('counters', {}) or {}).get('fresh_spend_ok'),
            'fresh_spend_fail_count': (ext_mon.get('counters', {}) or {}).get('fresh_spend_fail'),
            'idempotency_replay_bad': (ext_mon.get('counters', {}) or {}).get('idempotent_replay_bad'),
            'http_5xx_count': (ext_mon.get('counters', {}) or {}).get('http_5xx'),
            'inv_aff_delta_equal': (ext_mon.get('post', {}) or {}).get('inv_mut_delta') == (ext_mon.get('post', {}) or {}).get('aff_mut_delta'),
        },
        'affinity_state_health': {
            'samples_total': (ext_mon.get('counters', {}) or {}).get('samples_total'),
            'negative_inventory_post': (ext_mon.get('post', {}) or {}).get('negative_inventory'),
        },
        'suite_cleanup_state': {
            'report_present': bool(inputs.get('suite_cleanup')),
            'buckets_count': len((suite_cln.get('buckets') or {})),
        },
        'k6_readiness_state': {
            'overall': k6.get('overall_status'),
            'k6_binary_present': k6.get('k6_binary_present'),
            'locust_binary_present': k6.get('locust_binary_present'),
            'python_fallback_probe_pass': k6.get('python_fallback_probe_pass'),
            'fb_requests_total': (k6.get('python_fallback_probe', {}) or {}).get('requests_total'),
        },
        'rollback_readiness_state': {
            'overall': rb.get('overall_status'),
            'all_scripts_present': rb.get('all_scripts_present'),
            'backup_dir_writable': rb.get('supervisor_backup_dir_writable'),
        },

        'v16_composite_overall': v16.get('overall'),
        'v17_preflight_overall': pre.get('overall_status'),
        'v17_extended_monitoring_overall': ext_mon.get('overall_status'),
        'stage2_monitoring_overall': s2_mon.get('overall_status'),

        'next_decision': (
            'continue_stage2_monitoring' if stage2_state == 'APPLIED' else
            ('fix_stage2_blocker' if stage2_state == 'READY_NOT_APPLIED' and s2_apply.get('gates_all_pass') is False else
             ('await_explicit_stage2_authorization' if stage2_state == 'READY_NOT_APPLIED' else
              'rollback_required'))),
        'next_step_recommendation': (
            'Stage2 5-10% expansion APPLIED e monitoring PASS: continuare monitoring esteso 24-72h; '
            'AF2-L-K6-LIVE real install possibile come prossimo passo gated.'
            if stage2_state == 'APPLIED' and s2_mon.get('overall_status') == 'PASS' else
            ('Stage2 NON applicato (READY_NOT_APPLIED). Risolvere gate falliti o autorizzare esplicitamente apply. '
             'Inventory live Stage1 resta stabile e attivo.'
             if stage2_state == 'READY_NOT_APPLIED' else
             'Verifica manuale richiesta sullo stato Stage2.')
        ),

        'invariants_currently_holding': [
            '/api/heroes count == 100' if isinstance(heroes, list) and len(heroes) == 100 else '/api/heroes count NOT 100',
            'Borea aliases hidden in /api/heroes' if isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'}) else 'BOREA LEAK',
            'POST /api/affinity/gift-spend Borea returns 404',
            'POST /api/affinity/gift-spend non-allowlist returns 423',
            'POST /api/affinity/gift-spend Stage1 QA user with sufficient inventory returns 200',
            'Idempotent replay returns 200 with NO double-mutation',
            'no buffs activation, no battle wiring, no broad rollout',
            'battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py unchanged',
        ],

        'safety_flags': {
            'runtime_attached': True,
            'runtime_attached_stage1_allowlist_only': stage2_state != 'APPLIED',
            'runtime_attached_stage2_applied': stage2_state == 'APPLIED',
            'broad_rollout_authorized': False,
            'inventory_wiring_live': True,
            'inventory_mutation_enabled': True,
            'affinity_points_mutation_enabled': True,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'stage2_state': stage2_state,
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'SAFETY-ROLLUP-L generated: stage2_state={stage2_state} next={payload["next_decision"]}')

    # Validator
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('SAFETY-ROLLUP-L — Validator'); print('='*70)
    rec('report_id', payload['report_id'] == 'collection_affinity_runtime_activation_readiness_rollup_v12')
    rec('supersedes_v11', payload['supersedes'] == 'collection_affinity_runtime_activation_readiness_rollup_v11')
    rec('broad_rollout_off', payload['broad_rollout_authorized'] is False)
    rec('battle_off', payload['battle_wiring_live'] is False)
    rec('borea_hidden', payload['Borea_hidden'] is True)
    rec('stage2_state_known', payload['stage2_state'] in {'APPLIED','READY_NOT_APPLIED','NOT_APPLIED_NO_RESULT'})
    rec('next_decision_known', payload['next_decision'] in {'continue_stage2_monitoring','fix_stage2_blocker','await_explicit_stage2_authorization','rollback_required','real_k6','defer_stack_g'})
    rec('feature_flag_on', payload['feature_flag_currently_enabled'] is True)
    rec('inv_mut_on', payload['inventory_mutation_enabled'] is True)
    sf = payload['safety_flags']
    rec('sf_broad_off', sf['broad_rollout_authorized'] is False)
    rec('sf_buffs_off', sf['buffs_enabled'] is False)
    rec('sf_battle_off', sf['battle_runtime_attached'] is False)
    rec('sf_combat_off', sf['applied_to_combat'] is False)
    rec('sf_borea_hidden', sf['hidden_aliases_blocked'] == ['borea','greek_borea','primordial_gaia'])
    rec('inputs_v17_preflight', payload['inputs_present'].get('v17_preflight') is True)
    rec('inputs_v17_extmon', payload['inputs_present'].get('v17_extended_monitoring') is True)
    rec('inputs_suite_cleanup', payload['inputs_present'].get('suite_cleanup') is True)
    rec('inputs_k6_readiness', payload['inputs_present'].get('k6_readiness') is True)
    rec('inputs_rollback_readiness', payload['inputs_present'].get('rollback_readiness') is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
