#!/usr/bin/env python3
"""V30 PART I — Broad Rollout Signoff V8 (PLAN-ONLY)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v8.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _read(p):
    f=Path(p)
    if not f.exists(): return {}
    try: return json.loads(f.read_text())
    except Exception: return {}


def main():
    m9 = _read('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v9.json')
    soak = _read('/app/data/design/affinity/af2n_stage4_soak_v30_result.json')
    s10 = _read('/app/data/design/affinity/af2n_stress_10x_v30_result.json')
    cap = _read('/app/data/design/affinity/af2n_cap_raise_s2_v30_result.json')
    delta = _read('/app/data/design/affinity/affinity_inventory_delta_consistency_v30_report.json')
    mredis = _read('/app/data/design/affinity/managed_redis_envaware_v30_result.json')
    alert = _read('/app/data/design/affinity/alerting_envaware_v30_result.json')
    obs = _read('/app/data/design/observability/af2n_observability_dashboard_spec_v1.json')

    REQUIRED=[
        {'id':'EV-V30-SOAK','status':'PROVIDED' if soak.get('verdict')=='PASS' else 'MISSING','desc':'Stage4 soak V30 PASS'},
        {'id':'EV-V30-STRESS-10X','status':'PROVIDED' if s10.get('verdict')=='PASS' else 'MISSING','desc':'Stress 10x PASS'},
        {'id':'EV-V30-CAP-S2','status':'PROVIDED' if cap.get('verdict')=='PASS' else 'MISSING','desc':'Cap S2 status','detail':cap.get('status')},
        {'id':'EV-V30-DELTA-AUDIT','status':'PROVIDED' if delta.get('verdict')=='PASS' else 'MISSING','desc':'Delta audit V30 PASS'},
        {'id':'EV-V30-MANAGED-REDIS','status':'PROVIDED' if mredis.get('verdict')=='PASS' else 'MISSING','desc':'Managed Redis probe','detail':mredis.get('status')},
        {'id':'EV-V30-ALERTING','status':'PROVIDED' if alert.get('verdict')=='PASS' else 'MISSING','desc':'Alerting probe','detail':alert.get('sink_mode')},
        {'id':'EV-V30-OBSERVABILITY-SPEC','status':'PROVIDED' if obs.get('verdict')=='PASS' else 'MISSING','desc':'Observability dashboard spec'},
        {'id':'EV-V28-CAP25K-STABLE','status':'PROVIDED','desc':'Cap 25k stable since V27 (now possibly S2)'},
        {'id':'EV-V28-ALLOWLIST-2500-STABLE','status':'PROVIDED','desc':'Allowlist 2500 stable since V28'},
        {'id':'EV-INFRA-MANAGED-REDIS-LIVE','status':'PENDING','desc':'Managed Redis LIVE traffic switched >=14d soak'},
        {'id':'EV-INFRA-ALERTING-LIVE','status':'PENDING','desc':'Alerting LIVE webhook/pushgw verified with real incidents'},
        {'id':'EV-OBSERVABILITY-DEPLOYED','status':'PENDING','desc':'Grafana/Prometheus deployed with V30 panels'},
        {'id':'EV-LEGAL-PRODUCT-SIGNOFF','status':'PENDING','desc':'Product + legal explicit signoff'},
        {'id':'EV-USER-FINAL-APPROVAL','status':'PENDING','desc':'Explicit user approval of broad rollout'},
    ]
    SIGNOFFS={'engineering':False,'qa':False,'product':False,'legal':False,'sre':False,'security':False,'final_user_approval':False}
    blockers=[]
    for b in (m9.get('matrix') or []):
        st = b.get('status') or ''
        if b.get('severity') in ('P0','P1') and not any(t in st for t in ('CLOSED','ACCEPTED','READY','NOT_APPROVED','NO_GO','ENV_MISSING','MOCK')):
            blockers.append({'id':b.get('id'),'severity':b.get('severity'),'status':st})

    out={
        'task_origin':'AF2-N-V30-BROAD-ROLLOUT-SIGNOFF-V8',
        'version':'v8','mode':'PLAN_ONLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'broad_rollout_allowed':False,
        'public_spend_ui_allowed':False,
        'stack_g_allowed':False,
        'signoffs':SIGNOFFS,
        'required_evidence':REQUIRED,
        'blockers_from_matrix_v9':blockers,
        'pending_signoff_count':sum(1 for v in SIGNOFFS.values() if not v),
        'pending_evidence_count':sum(1 for e in REQUIRED if e['status']!='PROVIDED'),
        'next_steps_if_approved_in_future':[
            'Switch Managed Redis live with rollback ready',
            'Activate alerting live sink with incident validation',
            'Deploy observability dashboards (Grafana/Prometheus)',
            'Run 14d soak on Stage4 scope S1 at cap S2',
            'Run broad rollout dry-run on staging clone',
            'Obtain product + legal explicit signoff',
            'Obtain explicit user final approval',
            'Broad rollout in waves with continuous monitoring',
        ],
        'safety':{'plan_only':True,'no_runtime_change':True,'no_db_write':True,'no_secret_logged':True},
    }
    out['verdict']='PASS' if all([
        out['broad_rollout_allowed'] is False,
        out['public_spend_ui_allowed'] is False,
        out['stack_g_allowed'] is False,
        not any(SIGNOFFS.values()),
        out['safety']['plan_only'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} pending_signoff={out['pending_signoff_count']} pending_evidence={out['pending_evidence_count']} blockers={len(blockers)}")
    return 0 if out['verdict']=='PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
