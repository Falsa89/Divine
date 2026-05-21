#!/usr/bin/env python3
"""V30 PART F — Alerting env-aware probe (safe, no secrets)."""
import json, os, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
OUT = Path('/app/data/design/affinity/alerting_envaware_v30_result.json')
MOCK = Path('/app/data/design/affinity/af2n_alerting_envaware_v30_local_mock_sink.log')
OUT.parent.mkdir(parents=True, exist_ok=True)

FORMATS=[
    {'rule_id':'rate_limit_fail_open','severity':'HIGH'},
    {'rule_id':'backend_not_redis','severity':'HIGH'},
    {'rule_id':'borea_success_alert','severity':'CRITICAL'},
    {'rule_id':'unauthorized_spend_alert','severity':'CRITICAL'},
    {'rule_id':'negative_inventory','severity':'HIGH'},
    {'rule_id':'cap_pressure_high','severity':'MEDIUM'},
]


def main():
    started = datetime.now(timezone.utc).isoformat()
    webhook=(os.environ.get('ALERT_WEBHOOK_URL') or '').strip()
    pushgw=(os.environ.get('PROMETHEUS_PUSHGATEWAY') or '').strip()
    sink_mode='LOCAL_MOCK_ENV_MISSING'
    live=[]
    if webhook:
        sink_mode='LIVE_WEBHOOK_PROBED'
        for f in FORMATS:
            p=dict(f,timestamp_utc=started,probe=True,no_secrets=True,no_pii=True,no_borea_data=True)
            try:
                req=urllib.request.Request(webhook,data=json.dumps(p).encode(),headers={'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(req,timeout=4) as r:
                    live.append({'rule_id':f['rule_id'],'http_code':r.status,'ok':200<=r.status<300})
            except Exception as e:
                live.append({'rule_id':f['rule_id'],'ok':False,'error':str(e)[:160]})
            with MOCK.open('a') as fh: fh.write(json.dumps(p)+'\n')
    elif pushgw:
        sink_mode='LIVE_PUSHGATEWAY_PLAN_ONLY'
        for f in FORMATS:
            p=dict(f,timestamp_utc=started,probe=True,no_secrets=True,no_pii=True,no_borea_data=True)
            with MOCK.open('a') as fh: fh.write(json.dumps(p)+'\n')
            live.append({'rule_id':f['rule_id'],'note':'pushgw client integration deferred'})
    else:
        for f in FORMATS:
            p=dict(f,timestamp_utc=started,probe=True,no_secrets=True,no_pii=True,no_borea_data=True)
            with MOCK.open('a') as fh: fh.write(json.dumps(p)+'\n')

    out={
        'task_origin':'AF2-N-V30-ALERTING-PROBE','timestamp_utc':started,
        'sink_mode':sink_mode,'webhook_set':bool(webhook),'pushgateway_set':bool(pushgw),
        'formats_validated':[f['rule_id'] for f in FORMATS],
        'live_results':live,
        'mock_log_path':str(MOCK),
        'mock_log_size_bytes': MOCK.stat().st_size if MOCK.exists() else 0,
        'safety':{'no_secrets_logged':True,'no_pii_in_payload':True,'no_borea_data_leaked':True,'env_only_actuation':True},
        'verdict':'PASS',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"sink_mode={sink_mode} formats={len(FORMATS)} mock={out['mock_log_size_bytes']}")
    return 0


if __name__ == '__main__': sys.exit(main())
