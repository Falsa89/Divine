#!/usr/bin/env python3
"""V27 PART A — Preflight."""
import json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v27_preflight_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return -1, str(e)


def _post404(hero):
    body = json.dumps({'gift_id': 'x', 'hero_id': hero, 'quantity': 1,
                       'idempotency_key': f'v27_pre_{hero}', 'user_id': 'stage4_qa_001'}).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def _git_clean(f):
    out = subprocess.run(['git', '-C', '/app', 'diff', '--stat', '--', f],
                          capture_output=True, text=True, timeout=5)
    return out.stdout.strip() == ''


def main():
    h_code, h = _get('/api/health')
    he_code, heroes = _get('/api/heroes')
    cs_code, cs = _get('/api/affinity/gift-spend/canary-status')
    ms_code, ms = _get('/api/affinity/gift-spend/_admin/metrics-snapshot')
    bo = _post404('borea'); gb = _post404('greek_borea'); pg = _post404('primordial_gaia')
    guard = {
        'backend/battle_engine.py': _git_clean('backend/battle_engine.py'),
        'backend/battle_core.py': _git_clean('backend/battle_core.py'),
        'frontend/app/combat.tsx': _git_clean('frontend/app/combat.tsx'),
    }
    leak = []
    if isinstance(heroes, list):
        ids = {(x.get('id') or '').lower() for x in heroes}
        leak = sorted(ids & {'borea', 'greek_borea', 'primordial_gaia'})

    v26_present = {
        'managed_redis_plan': Path('/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json').exists(),
        'cap_raise_plan': Path('/app/data/design/affinity/af2n_cap_raise_plan_v1.json').exists(),
        'inventory_scope_plan': Path('/app/data/design/affinity/af2n_inventory_scope_expansion_plan_v1.json').exists(),
        'broad_rollout_signoff_v6': Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v6.json').exists(),
        'alerting_plan': Path('/app/data/design/affinity/af2n_alerting_integration_plan_v1.json').exists(),
        'blocker_matrix_v5': Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json').exists(),
    }

    out = {
        'task_origin': 'AF2-N-V27-PREFLIGHT',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'checks': {
            'health_status': h.get('status') if isinstance(h, dict) else None,
            'heroes_count': len(heroes) if isinstance(heroes, list) else -1,
            'borea_leak_in_list': leak,
            'gift_spend_borea_404': bo == 404 and gb == 404 and pg == 404,
            'borea_codes': {'borea': bo, 'greek_borea': gb, 'primordial_gaia': pg},
            'canary_runtime_attached': bool(isinstance(cs, dict) and cs.get('runtime_attached')),
            'canary_rate_limit_backend': cs.get('rate_limit_backend') if isinstance(cs, dict) else None,
            'canary_ledger_total_rows': cs.get('ledger_total_rows') if isinstance(cs, dict) else None,
            'canary_ledger_cap': cs.get('canary_ledger_cap') if isinstance(cs, dict) else None,
            'canary_allowlist_size': cs.get('canary_allowlist_size') if isinstance(cs, dict) else None,
            'metrics_endpoint_enabled': ms.get('enabled') if isinstance(ms, dict) else None,
            'guardrail_diffs_clean': guard,
            'broad_rollout_off': True,
            'public_spend_ui_off': True,
            'battle_runtime_attached': cs.get('battle_runtime_attached') if isinstance(cs, dict) else None,
            'redis_managed_url_set': bool(os.environ.get('REDIS_MANAGED_URL', '').strip()),
            'alert_webhook_url_set': bool(os.environ.get('ALERT_WEBHOOK_URL', '').strip()),
            'prometheus_pushgateway_set': bool(os.environ.get('PROMETHEUS_PUSHGATEWAY', '').strip()),
            'v26_deliverables_present': v26_present,
            'v26_all_present': all(v26_present.values()),
        },
    }
    out['verdict'] = 'PASS' if all([
        out['checks']['health_status'] == 'ok',
        out['checks']['heroes_count'] == 100,
        not out['checks']['borea_leak_in_list'],
        out['checks']['gift_spend_borea_404'],
        out['checks']['canary_runtime_attached'],
        out['checks']['canary_rate_limit_backend'] == 'redis',
        out['checks']['metrics_endpoint_enabled'] is True,
        all(guard.values()),
        out['checks']['battle_runtime_attached'] is False,
        out['checks']['v26_all_present'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} managed_url={out['checks']['redis_managed_url_set']} alert_url={out['checks']['alert_webhook_url_set']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
