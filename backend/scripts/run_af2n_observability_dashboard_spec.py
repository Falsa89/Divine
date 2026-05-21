#!/usr/bin/env python3
"""V30 PART G — Observability dashboard spec generator (plan-only)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/observability/af2n_observability_dashboard_spec_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

PANELS = [
    {'id':'success_rate','title':'Gift-spend success rate (5m)','type':'graph','metric':'af2n_gift_spend_success_count','severity':'INFO'},
    {'id':'http_423','title':'HTTP 423 (disabled/non-allowlist)','type':'graph','metric':'af2n_gift_spend_http_423','severity':'INFO'},
    {'id':'http_429','title':'HTTP 429 (rate limit)','type':'graph','metric':'af2n_gift_spend_http_429','severity':'WARN'},
    {'id':'borea_attempts','title':'Borea alias attempts (must be 0 success)','type':'stat','metric':'af2n_borea_attempt_total','severity':'CRITICAL'},
    {'id':'redis_fail_open','title':'Rate-limit Redis fail-open','type':'stat','metric':'af2n_rate_limit_fail_open_total','severity':'CRITICAL'},
    {'id':'backend_not_redis','title':'Backend != redis','type':'singlestat','metric':'af2n_rate_limit_backend','severity':'CRITICAL'},
    {'id':'negative_inventory','title':'Negative inventory rows','type':'singlestat','metric':'af2n_negative_inventory_rows','severity':'CRITICAL'},
    {'id':'delta_mismatch','title':'Delta audit mismatches','type':'stat','metric':'af2n_delta_mismatch_total','severity':'HIGH'},
    {'id':'cap_pressure','title':'Ledger cap pressure (rows / cap)','type':'gauge','metric':'af2n_ledger_cap_pressure','severity':'WARN'},
    {'id':'p95_p99_latency','title':'Spend p95/p99 latency','type':'graph','metric':'af2n_gift_spend_latency_ms','severity':'INFO'},
    {'id':'http_5xx','title':'HTTP 5xx','type':'graph','metric':'af2n_gift_spend_http_5xx','severity':'CRITICAL'},
    {'id':'idempotent_replay','title':'Idempotent replay hits','type':'graph','metric':'af2n_idempotent_replay_total','severity':'INFO'},
]

ALERTS = [
    {'rule_id':'borea_success_alert','condition':'borea_attempts.success > 0','severity':'CRITICAL','action':'rollback_runtime'},
    {'rule_id':'unauthorized_spend_alert','condition':'non_allowlist.applied > 0','severity':'CRITICAL','action':'rollback_runtime'},
    {'rule_id':'backend_not_redis','condition':'backend != "redis"','severity':'HIGH','action':'restore_local_redis'},
    {'rule_id':'rate_limit_fail_open','condition':'fail_open_count > 0','severity':'HIGH','action':'restore_local_redis'},
    {'rule_id':'negative_inventory','condition':'negative_inventory_rows > 0','severity':'CRITICAL','action':'pause_writes'},
    {'rule_id':'cap_pressure_high','condition':'ledger_rows / cap > 0.8','severity':'MEDIUM','action':'consider_cap_raise_plan'},
    {'rule_id':'http_5xx_critical','condition':'5xx_per_5m > 10','severity':'CRITICAL','action':'page_oncall'},
]


def main():
    spec = {
        'task_origin':'AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC',
        'version':'v1',
        'mode':'PLAN_ONLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'panels': PANELS,
        'alerts': ALERTS,
        'panel_count': len(PANELS),
        'alert_count': len(ALERTS),
        'datasource_recommendation': 'Prometheus + Loki + Grafana; pushgateway optional for off-cluster bursts.',
        'safety': {
            'plan_only': True,
            'no_runtime_change': True,
            'no_secret_in_panels': True,
        },
        'verdict':'PASS',
    }
    OUT.write_text(json.dumps(spec, indent=2, default=str))
    print(f"verdict=PASS panels={len(PANELS)} alerts={len(ALERTS)} → {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
