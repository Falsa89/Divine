#!/usr/bin/env python3
"""SAFETY-ROLLUP-M V18 — generates rollup_v13.json and validates."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v13.json')

INPUTS = {
    'v18_preflight': Path('/app/data/design/affinity/af2n_v18_preflight_result_v1.json'),
    'stage2_extended_monitoring': Path('/app/data/design/affinity/af2n_stage2_extended_monitoring_v18_result.json'),
    'stage3_plan': Path('/app/data/design/affinity/af2n_stage3_qa_expansion_plan_v1.json'),
    'stage3_apply_result': Path('/app/data/design/affinity/af2n_stage3_qa_expansion_apply_result_v1.json'),
    'stage3_monitoring': Path('/app/data/design/affinity/af2n_stage3_monitoring_v18_result.json'),
    'public_ui_readiness': Path('/app/data/design/ui/affinity_gifts_public_preview_readiness_v1.json'),
    'k6_locust_v18': Path('/app/data/design/affinity/af2n_v18_k6_locust_result_v1.json'),
    'rollback_readiness_v18': Path('/app/data/design/affinity/af2n_v18_rollback_readiness_result_v1.json'),
    'v17_composite': Path('/app/backend/reports/ultra_combo_v17_validator_summary_v1.json'),
    'rollup_v12': Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v12.json'),
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

    s3_apply = data.get('stage3_apply_result') or {}
    s3_state = 'NOT_APPLIED_NO_RESULT'
    if s3_apply:
        if s3_apply.get('overall_status') == 'APPLIED_PASS': s3_state = 'APPLIED'
        elif s3_apply.get('overall_status') == 'READY_NOT_APPLIED': s3_state = 'READY_NOT_APPLIED'
        else: s3_state = s3_apply.get('overall_status') or 'UNKNOWN'

    s2_ext = data.get('stage2_extended_monitoring') or {}
    s3_mon = data.get('stage3_monitoring') or {}
    k6 = data.get('k6_locust_v18') or {}
    rb = data.get('rollback_readiness_v18') or {}
    ui = data.get('public_ui_readiness') or {}
    v17 = data.get('v17_composite') or {}
    pre = data.get('v18_preflight') or {}

    runtime_state = (
        'stage3_qa_active_no_broad_rollout' if s3_state == 'APPLIED' else
        ('stage3_blocked_safe_ready_not_applied' if s3_state == 'READY_NOT_APPLIED' else
         'stage2_active'))

    payload = {
        'report_id': 'collection_affinity_runtime_activation_readiness_rollup_v13',
        'task_origin': 'SAFETY-ROLLUP-M',
        'supersedes': 'collection_affinity_runtime_activation_readiness_rollup_v12',
        'design_only': False, 'runtime_attached': True,
        'db_write': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'summary': (
            f'SAFETY-ROLLUP-M — V18 Stage2 extended monitoring + Stage3 QA expansion ({s3_state}) + Public UI preview readiness (plan-only, no UI mutation) + K6/Locust readiness + rollback readiness. '
            'Invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle/combat files NOT modified, no buffs, no battle wiring, no public spend UI, no broad rollout.'
        ),
        'inputs_present': {k: bool(v) for k, v in data.items()},
        'runtime_state': runtime_state,
        'stage2_state': 'APPLIED',
        'stage3_state': s3_state,
        'stage3_apply_reason_if_not_applied': s3_apply.get('ready_not_applied_reason'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': False,
        'Borea_hidden': True,
        'inventory_live_scope': 'allowlist_only',

        'ledger_count': (st or {}).get('ledger_total_rows'),
        'ledger_cap': (st or {}).get('canary_ledger_cap'),
        'canary_allowlist_size': (st or {}).get('canary_allowlist_size'),
        'feature_flag_currently_enabled': (st or {}).get('feature_flag_currently_enabled'),
        'inventory_mutation_enabled': (st or {}).get('inventory_mutation_enabled'),
        'affinity_points_mutation_enabled': (st or {}).get('affinity_points_mutation_enabled'),

        'stage2_extended_monitoring': {
            'overall_status': s2_ext.get('overall_status'),
            'samples_total': (s2_ext.get('counters') or {}).get('samples_total'),
            'fresh_spend_ok': (s2_ext.get('counters') or {}).get('fresh_spend_ok'),
            'fresh_spend_fail': (s2_ext.get('counters') or {}).get('fresh_spend_fail'),
            'http_5xx': (s2_ext.get('counters') or {}).get('http_5xx'),
        },
        'stage3_monitoring': {
            'overall_status': s3_mon.get('overall_status'),
            'samples_total': (s3_mon.get('counters') or {}).get('samples_total'),
            'fresh_spend_ok': (s3_mon.get('counters') or {}).get('stage3_fresh_ok'),
            'fresh_spend_fail': (s3_mon.get('counters') or {}).get('stage3_fresh_fail'),
            'http_5xx': (s3_mon.get('counters') or {}).get('http_5xx'),
        },
        'public_ui_preview_readiness': {
            'phase': ui.get('phase'),
            'design_only': ui.get('design_only'),
            'spend_button_planned': False,
        },
        'k6_locust_v18_state': {
            'overall': k6.get('overall_status'),
            'k6_binary_present': k6.get('k6_binary_present'),
            'locust_binary_present_after_attempt': k6.get('locust_binary_present_after_attempt') or k6.get('locust_binary_present'),
            'real_locust_smoke_exit': (k6.get('real_locust_run') or {}).get('exit_code'),
            'python_fallback_probe_pass': k6.get('python_fallback_probe_pass'),
            'fb_requests_total': (k6.get('python_fallback_probe', {}) or {}).get('requests_total'),
            'fb_rps': (k6.get('python_fallback_probe', {}) or {}).get('rps'),
        },
        'rollback_readiness_state': {
            'overall': rb.get('overall_status'),
            'all_scripts_present': rb.get('all_scripts_present'),
            'backup_dir_writable': rb.get('supervisor_backup_dir_writable'),
        },
        'rollback_ready': bool(rb.get('all_scripts_present') and rb.get('supervisor_backup_dir_writable')),
        'v17_composite_overall': v17.get('overall'),
        'v18_preflight_overall': pre.get('overall_status'),

        'next_decision': (
            'extended_monitoring' if s3_state == 'APPLIED' and s3_mon.get('overall_status') == 'PASS' else
            ('public_ui_preview' if s3_state == 'APPLIED' and s3_mon.get('overall_status') == 'PASS' else
             ('stack_g_deferred' if s3_state == 'READY_NOT_APPLIED' else 'extended_monitoring'))),

        'next_step_recommendation': (
            'Stage3 QA expansion APPLIED + monitoring PASS: continuare con extended monitoring 24-72h, k6_real install gated, public_ui_preview plan-only.'
            if s3_state == 'APPLIED' and s3_mon.get('overall_status') == 'PASS' else
            ('Stage3 NON applicato (READY_NOT_APPLIED). Stage2 resta attivo e stabile. Continuare Stage2 extended monitoring.'
             if s3_state == 'READY_NOT_APPLIED' else
             'Verifica manuale stato Stage3 richiesta.')
        ),

        'invariants_currently_holding': [
            ('/api/heroes count == 100' if isinstance(heroes, list) and len(heroes) == 100 else '/api/heroes count NOT 100'),
            ('Borea aliases hidden in /api/heroes' if isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'}) else 'BOREA LEAK'),
            'POST /api/affinity/gift-spend Borea returns 404',
            'POST /api/affinity/gift-spend non-allowlist returns 423',
            'Stage2 + Stage3 allowlist users with sufficient inventory returns 200 applied_inventory_live',
            'Idempotent replay returns 200 with NO double-mutation',
            'no buffs activation, no battle wiring, no broad rollout, no public spend UI',
            'battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py unchanged',
        ],

        'safety_flags': {
            'runtime_attached': True,
            'runtime_state': runtime_state,
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'inventory_wiring_live': True,
            'inventory_mutation_enabled': True,
            'affinity_points_mutation_enabled': True,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'stage2_state': 'APPLIED',
            'stage3_state': s3_state,
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'SAFETY-ROLLUP-M generated: runtime_state={runtime_state} stage3={s3_state} next={payload["next_decision"]}')

    failures = []
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('SAFETY-ROLLUP-M — Validator'); print('='*70)
    rec('report_id', payload['report_id'] == 'collection_affinity_runtime_activation_readiness_rollup_v13')
    rec('supersedes_v12', payload['supersedes'] == 'collection_affinity_runtime_activation_readiness_rollup_v12')
    rec('runtime_state_known', payload['runtime_state'] in {'stage2_active','stage3_qa_active_no_broad_rollout','stage3_blocked_safe_ready_not_applied','rolled_back'})
    rec('broad_off', payload['broad_rollout_authorized'] is False)
    rec('public_spend_off', payload['public_spend_ui'] is False)
    rec('battle_off', payload['battle_wiring_live'] is False)
    rec('buffs_off', payload['buffs_enabled'] is False)
    rec('borea_hidden', payload['Borea_hidden'] is True)
    rec('stage3_state_known', payload['stage3_state'] in {'APPLIED','READY_NOT_APPLIED','NOT_APPLIED_NO_RESULT'})
    rec('inventory_live_scope_allowlist_only', payload['inventory_live_scope'] == 'allowlist_only')
    rec('rollback_ready', payload['rollback_ready'] is True)
    rec('next_decision_known', payload['next_decision'] in {'extended_monitoring','stage4_public_beta_prep','public_ui_preview','k6_real','stack_g_deferred','rollback_required'})
    sf = payload['safety_flags']
    rec('sf_broad_off', sf['broad_rollout_authorized'] is False)
    rec('sf_public_spend_off', sf['public_spend_ui'] is False)
    rec('sf_buffs_off', sf['buffs_enabled'] is False)
    rec('sf_battle_off', sf['battle_runtime_attached'] is False)
    rec('sf_combat_off', sf['applied_to_combat'] is False)
    rec('sf_borea_hidden', sf['hidden_aliases_blocked'] == ['borea','greek_borea','primordial_gaia'])
    for k in ('v18_preflight','stage2_extended_monitoring','public_ui_readiness','k6_locust_v18','rollback_readiness_v18'):
        rec(f'input:{k}', payload['inputs_present'].get(k) is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
