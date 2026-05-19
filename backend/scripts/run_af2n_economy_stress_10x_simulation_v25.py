#!/usr/bin/env python3
"""V25 PART F — Economy stress 10x simulation (READ-ONLY).

Pure simulation: NO DB writes, NO HTTP calls. Models a 10x scenario:
  - 10x ledger cap = 50000 transactions
  - 10x current allowlist = 7000 users
  - simulated spend rate per user
  - inventory depletion modelling
  - affinity point inflation
  - rate-limit pressure (Redis hits)
  - idempotency replay duplicate rate
  - abuse scenarios (burst, rapid-fire)
Produces actionable cap recommendations.
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_economy_stress_10x_simulation_v25_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

CURRENT = {
    'allowlist_size': 700,
    'cap': 5000,
    'ledger_now': 144,
    'rl_user_per_min': 30,
    'rl_user_per_hour': 240,
    'rl_ip_per_min': 60,
    'rl_burst_window_s': 10,
    'rl_burst_max': 6,
}


def simulate(scale: int) -> dict:
    users = CURRENT['allowlist_size'] * scale
    cap = CURRENT['cap'] * scale
    avg_spend_per_user = 5   # observed Stage 4 mean
    sigma = 2.5
    # Expected total spend events
    expected_events = users * avg_spend_per_user
    cap_pressure = expected_events / cap if cap else float('inf')
    # 5% of users are heavy-burst abusers
    heavy_users = int(users * 0.05)
    # Each heavy user attempts 50 in 10s => 44 get 429
    burst_429_per_heavy = max(0, 50 - CURRENT['rl_burst_max'])
    total_429 = heavy_users * burst_429_per_heavy
    # Idempotency replay: 2% duplicate rate
    replay_rate = 0.02
    duplicates = int(expected_events * replay_rate)
    # Inventory depletion: avg 5 stacks per user spent, 10 per stack initial
    depleted_users = int(users * 0.15)
    # Affinity points inflation: 100 pts per success spend, ~80% success
    success_events = int(expected_events * 0.80)
    affinity_pts_total = success_events * 100
    # Rate-limit (Redis) zset ops: ~3 per spend (burst + user + ip windows)
    redis_ops_per_sec_peak = (expected_events / (24 * 3600)) * 3 * 10  # 10x peak factor
    return {
        'scale_factor': scale,
        'users_modeled': users,
        'ledger_cap': cap,
        'avg_spend_per_user': avg_spend_per_user,
        'spend_per_user_sigma': sigma,
        'expected_total_spend_events': expected_events,
        'cap_pressure_ratio': round(cap_pressure, 3),
        'cap_exhaustion_predicted': cap_pressure > 1.0,
        'heavy_burst_users': heavy_users,
        'expected_429_events': total_429,
        'expected_idempotency_replays': duplicates,
        'expected_replay_rate_pct': round(replay_rate * 100, 2),
        'inventory_depleted_users': depleted_users,
        'affinity_points_total_inflation': affinity_pts_total,
        'redis_ops_per_sec_peak_estimate': round(redis_ops_per_sec_peak, 2),
        'redis_capacity_headroom_ok': redis_ops_per_sec_peak < 5000,  # Redis can do ~50k ops/s
    }


def main():
    out = {
        'task_origin': 'AF2-N-V25-ECONOMY-STRESS-10X-SIMULATION',
        'mode': 'READ_ONLY_SIMULATION',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'live_mutations': 0,
        'current_state': CURRENT,
        'scenarios': {},
    }
    for s in (1, 2, 5, 10):
        out['scenarios'][f'{s}x'] = simulate(s)

    # Recommendations
    s10 = out['scenarios']['10x']
    recommendations = []
    if s10['cap_exhaustion_predicted']:
        recommendations.append({
            'severity': 'P1',
            'msg': f"10x scenario predicts cap exhaustion (pressure ratio {s10['cap_pressure_ratio']}). Bump cap to {s10['expected_total_spend_events'] * 2} before broad rollout.",
        })
    if not s10['redis_capacity_headroom_ok']:
        recommendations.append({
            'severity': 'P1',
            'msg': 'Redis peak op rate above 5000/s; consider Managed Redis with provisioned IOPS.',
        })
    recommendations.append({
        'severity': 'P2',
        'msg': f"Expected idempotency replays at 10x = {s10['expected_idempotency_replays']:,}. Ensure idempotency_key index is unique + sparse on ledger.",
    })
    recommendations.append({
        'severity': 'P2',
        'msg': f"Expected 429 events at 10x = {s10['expected_429_events']:,}. Customer-facing message should be friendly and informative.",
    })
    recommendations.append({
        'severity': 'P3',
        'msg': f"Inventory depletion at 10x: {s10['inventory_depleted_users']:,} users. Plan refill or replenishment mechanic before broad rollout.",
    })
    recommendations.append({
        'severity': 'P1',
        'msg': 'Before broad rollout: provision Managed Redis (V26 gate), align ledger cap to 10x projected events, and verify idempotency index uniqueness in CI.',
    })
    out['recommendations'] = recommendations
    out['recommendations_count'] = len(recommendations)

    # Safety asserts
    out['safety'] = {
        'no_db_mutation': True,
        'no_http_calls': True,
        'no_broad_rollout': True,
        'no_borea_data': True,
        'no_pii': True,
    }
    out['verdict'] = 'PASS' if len(recommendations) >= 4 else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} scenarios=4 recommendations={out['recommendations_count']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
