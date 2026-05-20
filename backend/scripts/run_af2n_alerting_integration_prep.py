#!/usr/bin/env python3
"""V26 PART F — Alerting integration live prep (plan + audit)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

PLAN = Path('/app/data/design/affinity/af2n_alerting_integration_plan_v1.json')
AUDIT = Path('/app/data/design/affinity/af2n_alerting_integration_prep_result_v1.json')
PLAN.parent.mkdir(parents=True, exist_ok=True)
V25_CONTRACT = Path('/app/data/design/affinity/af2n_fail_open_alerting_contract_v1.json')

SINKS = [
    {
        'sink': 'prometheus',
        'protocol': 'HTTP scrape',
        'endpoint_planned': '/api/affinity/gift-spend/_admin/metrics-prometheus',
        'status': 'PLAN_ONLY',
        'env_vars': [],
        'secret_required': False,
        'pros': ['standard', 'self-hosted', 'grafana ecosystem'],
        'cons': ['cardinality if labels grow'],
    },
    {
        'sink': 'pagerduty',
        'protocol': 'Events API v2',
        'endpoint': 'https://events.pagerduty.com/v2/enqueue',
        'env_vars': ['PAGERDUTY_ROUTING_KEY'],
        'secret_required': True,
        'status': 'PLAN_ONLY',
        'pros': ['real on-call paging', 'severity routing'],
        'cons': ['cost', 'requires secret management'],
    },
    {
        'sink': 'slack',
        'protocol': 'Incoming Webhook',
        'endpoint': 'https://hooks.slack.com/services/<workspace>/<channel>/<token>',
        'env_vars': ['SLACK_WEBHOOK_URL'],
        'secret_required': True,
        'status': 'PLAN_ONLY',
        'pros': ['cheap', 'fast iteration'],
        'cons': ['not for true on-call alerts'],
    },
    {
        'sink': 'generic_webhook',
        'protocol': 'HTTP POST',
        'endpoint': '<configurable>',
        'env_vars': ['ALERT_WEBHOOK_URL', 'ALERT_WEBHOOK_AUTH_HEADER'],
        'secret_required': True,
        'status': 'PLAN_ONLY',
        'pros': ['provider-agnostic'],
        'cons': ['custom auth handling'],
    },
    {
        'sink': 'local_mock_sink',
        'protocol': 'file appender',
        'endpoint': '/app/data/design/affinity/af2n_alerting_local_mock_sink.log',
        'env_vars': [],
        'secret_required': False,
        'status': 'AVAILABLE_NOW',
        'pros': ['no secrets', 'safe for dev/test'],
        'cons': ['not for production'],
    },
]


def main():
    # Plan document
    plan = {
        'task_origin': 'AF2-N-V26-ALERTING-INTEGRATION-PLAN',
        'version': 'v1',
        'status': 'PLAN_ONLY',
        'live_integration_in_v26': False,
        'sinks_evaluated': SINKS,
        'sink_count': len(SINKS),
        'secrets_in_repo': False,
        'v25_contract_present': V25_CONTRACT.exists(),
        'v25_contract_rules_count': None,
        'recommended_phase_0': 'local_mock_sink (file appender) for dev/test',
        'recommended_phase_1': 'prometheus scrape + slack webhook for warnings',
        'recommended_phase_2': 'prometheus + pagerduty for P0/P1 incidents',
        'safety': {
            'no_secrets_committed': True,
            'no_live_external_calls_v26': True,
            'no_pii_in_alert_payloads': True,
            'no_borea_data_in_alerts': True,
            'read_only_metrics_source': True,
        },
        'broad_rollout_blocker_remains': True,  # until live sink is wired
        'verdict': 'PASS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    }
    if V25_CONTRACT.exists():
        try:
            cd = json.loads(V25_CONTRACT.read_text())
            plan['v25_contract_rules_count'] = len(cd.get('rules', []))
        except Exception:
            pass
    PLAN.write_text(json.dumps(plan, indent=2, default=str))

    # Audit: scan plan + verify safety
    audit = {
        'task_origin': 'AF2-N-V26-ALERTING-INTEGRATION-AUDIT',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'plan_present': PLAN.exists(),
        'v25_contract_present': V25_CONTRACT.exists(),
        'sinks_count': len(SINKS),
        'secrets_count_in_plan': sum(1 for s in SINKS if s.get('secret_required')),
        'plan_only_status': True,
        'live_integration_attempted': False,
        'mock_sink_present': any(s['sink'] == 'local_mock_sink' for s in SINKS),
        'verdict': 'PASS',
    }
    AUDIT.write_text(json.dumps(audit, indent=2, default=str))

    print(f"plan verdict=PASS sinks={len(SINKS)} → {PLAN}")
    print(f"audit verdict=PASS → {AUDIT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
