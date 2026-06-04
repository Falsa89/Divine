#!/usr/bin/env python3
"""v94 — Reward/score runtime dry-run simulator (local-only, no DB writes).

Simula 10 scenari di reward/score claim:
- story_victory_reward
- tower_floor_reward
- arena_win_loss_mmr
- raid_boss_contribution
- guild_war_score
- event_currency
- duplicate_claim_replay
- malformed_claim
- over_cap_claim
- unauthorized_claim

Nessuna scrittura DB. Output JSON in data/design/reward_runtime/v94_reward_score_dry_run_result_v1.json
"""
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'data', 'design', 'reward_runtime', 'v94_reward_score_dry_run_result_v1.json')

DRY_RUN_ONLY = True
LIVE_GRANT = False
CANARY_ALLOWLIST = {'qa_alias_canary_001'}

# In-memory idempotency keys (per-run, no DB)
_idempotency_seen = set()


def simulate_claim(user_alias, reward_type, source_id, claim_data=None):
    claim_data = claim_data or {}
    epoch_day = '2026-06-04'
    idem_key = f"{user_alias}::{reward_type}::{source_id}::{epoch_day}"

    # unauthorized
    if user_alias not in CANARY_ALLOWLIST and claim_data.get('require_canary', False):
        return {'status': 'REJECT', 'error': 'REWARD_UNAUTHORIZED', 'live_grant': False, 'db_writes': 0}

    # malformed
    if not reward_type or not source_id:
        return {'status': 'REJECT', 'error': 'MALFORMED_REWARD_CLAIM', 'live_grant': False, 'db_writes': 0}

    # over-cap
    if claim_data.get('amount', 0) > claim_data.get('cap', 999999):
        return {'status': 'REJECT', 'error': 'REWARD_CAP_EXCEEDED', 'live_grant': False, 'db_writes': 0}

    # duplicate
    if idem_key in _idempotency_seen:
        return {'status': 'REJECT', 'error': 'DUPLICATE_CLAIM_REPLAY', 'idempotency_receipt': idem_key, 'live_grant': False, 'db_writes': 0}

    _idempotency_seen.add(idem_key)
    return {'status': 'PASS_DRY_RUN', 'idempotency_key': idem_key, 'live_grant': False, 'db_writes': 0, 'would_apply_if_canary_enabled': False}


def main():
    results = []
    user = 'qa_alias_canary_001'
    results.append({'case': 'story_victory_reward', 'result': simulate_claim(user, 'story_reward', 'enc_story_1_1_intro_grunts')})
    results.append({'case': 'tower_floor_reward', 'result': simulate_claim(user, 'tower_reward', 'enc_tower_S01_F10_mid_boss')})
    results.append({'case': 'arena_win_loss_mmr', 'result': simulate_claim(user, 'arena_reward_and_mmr', 'arena_bot_mid_001')})
    results.append({'case': 'raid_boss_contribution', 'result': simulate_claim(user, 'raid_boss_reward', 'enc_raid_world_boss_01', {'amount': 1000, 'cap': 10000})})
    results.append({'case': 'guild_war_score', 'result': simulate_claim(user, 'guild_reward_and_score', 'gw_defense_team_design_v1')})
    results.append({'case': 'event_currency', 'result': simulate_claim(user, 'event_currency', 'event_summer_invasion_stage_01')})
    # duplicate
    results.append({'case': 'duplicate_claim_replay', 'result': simulate_claim(user, 'story_reward', 'enc_story_1_1_intro_grunts')})
    # malformed
    results.append({'case': 'malformed_claim', 'result': simulate_claim(user, '', 'src_x')})
    # over-cap
    results.append({'case': 'over_cap_claim', 'result': simulate_claim(user, 'event_currency', 'event_x', {'amount': 99999, 'cap': 100})})
    # unauthorized
    results.append({'case': 'unauthorized_claim', 'result': simulate_claim('not_in_canary', 'guild_reward_and_score', 'gw_x', {'require_canary': True})})

    total = len(results)
    pass_count = sum(1 for r in results if r['result']['status'] in ('PASS_DRY_RUN',))
    reject_count = sum(1 for r in results if r['result']['status'] == 'REJECT')
    live_grant_any = any(r['result'].get('live_grant', False) for r in results)
    db_writes_total = sum(r['result'].get('db_writes', 0) for r in results)

    output = {
        'simulator': 'v94_reward_score_runtime_dry_run',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'total_cases': total,
        'pass_dry_run_cases': pass_count,
        'reject_cases': reject_count,
        'live_grant_emitted': live_grant_any,
        'db_writes_total': db_writes_total,
        'dry_run_only': DRY_RUN_ONLY,
        'live_grant': LIVE_GRANT,
        'cases': results,
        'safety': {'db_writes': 0, 'reward_live': False, 'ranking_live': False, 'guild_score_mutation': 0, 'event_currency_live': False},
    }
    with open(OUT, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"OK simulate_v94_reward_score_runtime_dry_run total={total} pass={pass_count} reject={reject_count} live_grant={live_grant_any} db_writes={db_writes_total}")


if __name__ == '__main__':
    main()
