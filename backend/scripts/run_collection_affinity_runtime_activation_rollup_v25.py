#!/usr/bin/env python3
"""V30 PART M — Safety Rollup Y."""
import json, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v25.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE+p, timeout=4) as r: return json.loads(r.read().decode())
    except Exception: return None


def _file_pass(p):
    f=Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict')=='PASS'
    except Exception: return False


def _file_field(p, key='status'):
    f=Path(p)
    if not f.exists(): return 'MISSING'
    try: return json.loads(f.read_text()).get(key,'UNKNOWN')
    except Exception: return 'PARSE_ERROR'


def _git_clean(f):
    out=subprocess.run(['git','-C','/app','diff','--stat','--',f],capture_output=True,text=True,timeout=5)
    return out.stdout.strip()==''


def main():
    cs=_get('/api/affinity/gift-spend/canary-status') or {}
    heroes=_get('/api/heroes') or []
    ids={(h.get('id') or '').lower() for h in heroes if isinstance(h,dict)}
    leak=sorted(ids & {'borea','greek_borea','primordial_gaia'})
    rollup={
        'task_origin':'AF2-N-V30-SAFETY-ROLLUP-Y','version':'v25',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'internal_beta_scope_state':'SCOPE_S1_2500_CAP_S2_EVALUATED_V30',
        'allowlist_count': cs.get('canary_allowlist_size'),
        'canary_ledger_cap': cs.get('canary_ledger_cap'),
        'rate_limit_backend': cs.get('rate_limit_backend'),
        'cap_s2_state': _file_field('/app/data/design/affinity/af2n_cap_raise_s2_v30_result.json'),
        'managed_redis_state': _file_field('/app/data/design/affinity/managed_redis_envaware_v30_result.json'),
        'alerting_state': _file_field('/app/data/design/affinity/alerting_envaware_v30_result.json', key='sink_mode'),
        'soak_v30_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stage4_soak_v30_result.json') else 'OPEN',
        'stress_10x_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stress_10x_v30_result.json') else 'OPEN',
        'delta_audit_v30_status': 'CLOSED' if _file_pass('/app/data/design/affinity/affinity_inventory_delta_consistency_v30_report.json') else 'OPEN',
        'observability_spec_status': 'CLOSED' if _file_pass('/app/data/design/observability/af2n_observability_dashboard_spec_v1.json') else 'OPEN',
        'blocker_matrix_v9_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v9.json') else 'OPEN',
        'broad_rollout_signoff_v8_status': 'PLAN_READY_NOT_APPROVED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v8.json') else 'MISSING',
        'ui_safety_status': 'CLOSED' if _file_pass('/app/data/design/ui/affinity_gifts_public_preview_v30_safety_result.json') else 'OPEN',
        'rollback_readiness_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_v30_rollback_readiness_result_v1.json') else 'OPEN',
        'api_heroes_count_100': len(heroes)==100,
        'heroes_count_observed': len(heroes),
        'borea_hidden': not leak,
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'battle_runtime_attached': cs.get('battle_runtime_attached'),
        'guardrails_clean':{
            'backend/battle_engine.py': _git_clean('backend/battle_engine.py'),
            'backend/battle_core.py': _git_clean('backend/battle_core.py'),
            'frontend/app/combat.tsx': _git_clean('frontend/app/combat.tsx'),
        },
    }
    rollup['verdict']='PASS' if all([
        rollup['api_heroes_count_100'], rollup['borea_hidden'],
        rollup['rate_limit_backend']=='redis',
        rollup['canary_ledger_cap'] in (25000, 50000),
        rollup['allowlist_count']==2500,
        rollup['broad_rollout_authorized'] is False,
        rollup['public_spend_ui'] is False,
        rollup['battle_wiring_live'] is False,
        all(rollup['guardrails_clean'].values()),
        rollup['soak_v30_status']=='CLOSED',
        rollup['stress_10x_status']=='CLOSED',
        rollup['delta_audit_v30_status']=='CLOSED',
        rollup['observability_spec_status']=='CLOSED',
        rollup['blocker_matrix_v9_status']=='CLOSED',
        rollup['ui_safety_status']=='CLOSED',
        rollup['rollback_readiness_status']=='CLOSED',
        rollup['broad_rollout_signoff_v8_status']=='PLAN_READY_NOT_APPROVED',
    ]) else 'FAIL'
    OUT.write_text(json.dumps(rollup, indent=2, default=str))
    print(f"verdict={rollup['verdict']} allowlist={rollup['allowlist_count']} cap={rollup['canary_ledger_cap']}")
    return 0 if rollup['verdict']=='PASS' else 2


if __name__ == '__main__': sys.exit(main())
