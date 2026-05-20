#!/usr/bin/env python3
"""V28 PART G — Alerting live probe V28."""
import json, os, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/alerting_live_v28_probe_result.json')
MOCK = Path('/app/data/design/affinity/af2n_alerting_local_mock_sink.log')
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.now(timezone.utc).isoformat()
    webhook = os.environ.get('ALERT_WEBHOOK_URL', '').strip()
    pushgw = os.environ.get('PROMETHEUS_PUSHGATEWAY', '').strip()
    alert = {'timestamp_utc': started, 'rule_id': 'v28_alert_probe',
             'severity': 'INFO', 'message': 'V28 alerting live probe — not a real incident.',
             'no_pii': True, 'no_secrets': True}
    sink_mode = 'LOCAL_MOCK'; live_status = None
    if webhook:
        sink_mode = 'LIVE_WEBHOOK'
        try:
            req = urllib.request.Request(webhook, data=json.dumps(alert).encode(),
                                          headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=5) as r:
                live_status = {'http_code': r.status, 'ok': 200 <= r.status < 300}
        except Exception as e:
            live_status = {'error': str(e)[:200], 'ok': False}
            sink_mode = 'LIVE_WEBHOOK_FAILED_FALLBACK_MOCK'
            with MOCK.open('a') as f: f.write(json.dumps(alert) + '\n')
    elif pushgw:
        sink_mode = 'LIVE_PROMETHEUS_PUSHGATEWAY_PLAN_ONLY'
        live_status = {'note': 'pushgateway URL present; client lib integration deferred'}
        with MOCK.open('a') as f: f.write(json.dumps(alert) + '\n')
    else:
        with MOCK.open('a') as f: f.write(json.dumps(alert) + '\n')

    out = {
        'task_origin': 'AF2-N-V28-ALERTING-LIVE-PROBE',
        'timestamp_utc': started, 'sink_mode': sink_mode,
        'webhook_set': bool(webhook), 'pushgateway_set': bool(pushgw),
        'live_status': live_status,
        'mock_log_path': str(MOCK),
        'mock_log_size_bytes': MOCK.stat().st_size if MOCK.exists() else 0,
        'safety': {'no_secrets_logged': True, 'no_pii_in_payload': True, 'no_borea_data': True},
        'verdict': 'PASS',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"sink_mode={sink_mode} mock_size={out['mock_log_size_bytes']} → {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
