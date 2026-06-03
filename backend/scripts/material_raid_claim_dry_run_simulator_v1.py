#!/usr/bin/env python3
"""
v64 Track A — Material Raid Claim Dry-Run Simulator (in-memory).

DESIGN-ONLY / DRY-RUN.
- Nessun import pymongo/motor/redis.
- Nessuna lettura MONGO_URL.
- Nessuna write DB.
- Nessuna route runtime.
- Nessun import di server.py / battle_engine.py / route file.

Simula le 6 decisioni canoniche del futuro claim Material Raid usando solo
fixture locali e contratti v63 (idempotency / replay / ledger / canary scope).

Output evidence: data/design/economy/results/material_raid_claim_dry_run_simulator_result_v1.json
"""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
FIXTURE = os.path.join(ROOT, 'data/design/economy/material_raid_claim_canary_dry_run_fixture_v1.json')
SCENARIO = os.path.join(ROOT, 'data/design/economy/material_raid_claim_dry_run_scenario_matrix_v1.json')
CONTRACT = os.path.join(ROOT, 'data/design/economy/material_raid_claim_dry_run_request_response_contract_v1.json')
OUT = os.path.join(ROOT, 'data/design/economy/results/material_raid_claim_dry_run_simulator_result_v1.json')


def _hash(*parts: str) -> str:
    return hashlib.sha256(':'.join(parts).encode()).hexdigest()


def build_idempotency_key(req: dict) -> str:
    return _hash(
        req['user_id'], req['server_id'], req['material_raid_run_id'], req['mode_id'],
        req['reward_table_version'], req['preview_session_id'], req['claim_attempt_nonce'],
    )


def simulate(req: dict, state: dict, fixture: dict) -> dict:
    """In-memory decision logic mirroring v63 contracts. Zero side effects."""
    limits = fixture['limits']
    # Missing key check (highest priority)
    if not req.get('idempotency_key'):
        return {
            'dry_run_status': 'rejected',
            'would_create_ledger': False,
            'would_grant_rewards': False,
            'duplicate_status': 'none',
            'rollback_token_preview': None,
            'observation_window_ref': fixture['observation_window_ref'],
            'errors': ['missing_idempotency_key'],
            'decision': 'missing_idempotency_key_would_reject',
        }
    # Idempotency / replay (v63 Track B) BEFORE cap checks: an idempotent
    # retry must be detectable even when the user already hit the per-user cap.
    key = req['idempotency_key']
    payload_hash = req['payload_hash']
    if key in state['ledger']:
        existing = state['ledger'][key]
        if existing['payload_hash'] == payload_hash:
            return {
                'dry_run_status': 'duplicate_same_payload',
                'would_create_ledger': False,
                'would_grant_rewards': False,
                'duplicate_status': 'duplicate_same_payload',
                'rollback_token_preview': None,
                'observation_window_ref': fixture['observation_window_ref'],
                'errors': [],
                'decision': 'duplicate_same_payload_would_return_existing',
            }
        return {
            'dry_run_status': 'rejected',
            'would_create_ledger': False,
            'would_grant_rewards': False,
            'duplicate_status': 'duplicate_conflict',
            'rollback_token_preview': None,
            'observation_window_ref': fixture['observation_window_ref'],
            'errors': ['duplicate_conflict_different_payload'],
            'decision': 'duplicate_conflict_would_reject',
        }
    # Cap checks (canary scope from v63) only for genuinely new keys
    errors = []
    user_claims = state['per_user_claim_count'].get(req['user_id'], 0)
    total_claims = state['total_claim_count']
    if user_claims >= limits['max_claims_per_user']:
        errors.append('per_user_cap_exceeded')
    if total_claims >= limits['max_total_claims_first_wave']:
        errors.append('total_canary_cap_exceeded')
    if errors:
        return {
            'dry_run_status': 'rejected',
            'would_create_ledger': False,
            'would_grant_rewards': False,
            'duplicate_status': 'none',
            'rollback_token_preview': None,
            'observation_window_ref': fixture['observation_window_ref'],
            'errors': errors,
            'decision': 'over_canary_cap_would_reject',
        }
    # First valid claim path — stage only in-memory
    state['ledger'][key] = {
        'idempotency_key': key,
        'payload_hash': payload_hash,
        'user_id': req['user_id'],
        'status': 'staged_pending',  # simulated only, NEVER written to DB
    }
    state['per_user_claim_count'][req['user_id']] = user_claims + 1
    state['total_claim_count'] = total_claims + 1
    return {
        'dry_run_status': 'staged_pending',
        'would_create_ledger': True,
        'would_grant_rewards': False,
        'duplicate_status': 'none',
        'rollback_token_preview': 'rb_preview_' + key[:16],
        'observation_window_ref': fixture['observation_window_ref'],
        'errors': [],
        'decision': 'first_claim_would_stage',
    }


def main() -> int:
    if not os.path.exists(FIXTURE) or not os.path.exists(SCENARIO):
        print('FAIL: missing fixture or scenario matrix', file=sys.stderr)
        return 2
    fixture = json.load(open(FIXTURE))
    scenarios = json.load(open(SCENARIO))['scenarios']

    state = {'ledger': {}, 'per_user_claim_count': {}, 'total_claim_count': 0}
    results = []

    # Stage initial valid claims required by some scenarios
    for sc in scenarios:
        req = dict(sc['request'])
        if req.get('idempotency_key') == '__AUTO__':
            req['idempotency_key'] = build_idempotency_key(req)
        out = simulate(req, state, fixture)
        results.append({
            'scenario_id': sc['id'],
            'scenario_name': sc['name'],
            'expected_decision': sc['expected_decision'],
            'actual_decision': out['decision'],
            'match': out['decision'] == sc['expected_decision'],
            'dry_run_status': out['dry_run_status'],
            'duplicate_status': out['duplicate_status'],
            'would_create_ledger': out['would_create_ledger'],
            'would_grant_rewards': out['would_grant_rewards'],
            'errors': out['errors'],
        })

    summary = {
        'pack': 'MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION_PACK_v64',
        'simulator_version': 'material_raid_claim_dry_run_simulator_v1',
        'design_only': True,
        'dry_run_only': True,
        'live_apply_allowed': False,
        'db_writes': 0,
        'real_db_writes': 0,
        'mongo_url_used': False,
        'pymongo_used': False,
        'motor_used': False,
        'redis_used': False,
        'collection_created': False,
        'indexes_created': False,
        'reward_grant_executed': False,
        'inventory_mutation': False,
        'wallet_mutation': False,
        'total_scenarios': len(results),
        'matches': sum(1 for r in results if r['match']),
        'mismatches': sum(1 for r in results if not r['match']),
        'all_match': all(r['match'] for r in results),
        'all_would_grant_rewards_false': all(not r['would_grant_rewards'] for r in results),
        'final_ledger_size_simulated': len(state['ledger']),
        'final_total_claims_simulated': state['total_claim_count'],
        'results': results,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    print('SIMULATOR_OK matches=%d/%d mismatches=%d' % (
        summary['matches'], summary['total_scenarios'], summary['mismatches']))
    return 0 if summary['all_match'] and summary['all_would_grant_rewards_false'] else 1


if __name__ == '__main__':
    sys.exit(main())
