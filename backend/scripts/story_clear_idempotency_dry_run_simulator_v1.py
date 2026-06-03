#!/usr/bin/env python3
"""v67 Story Clear Idempotency Dry-Run Simulator.

DESIGN-ONLY / DRY-RUN. In-memory only.
- No pymongo/motor/redis. No MONGO_URL. No DB writes.
- No import of server.py / battle_engine.py.
- Output: data/design/story/results/story_clear_idempotency_dry_run_simulator_result_v1.json
"""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
SCEN = os.path.join(ROOT, 'data/design/story/story_clear_idempotency_scenario_matrix_v1.json')
OUT = os.path.join(ROOT, 'data/design/story/results/story_clear_idempotency_dry_run_simulator_result_v1.json')


def H(*parts: str) -> str:
    return hashlib.sha256(':'.join(parts).encode()).hexdigest()


def build_key(req):
    return H(req['user_id'], req['server_id'], req['chapter_id'], req['node_id'],
             req['preview_session_id'], req['attempt_nonce'])


def simulate(req, state):
    if not req.get('idempotency_key'):
        return {'decision': 'missing_idempotency_key_would_reject',
                'dry_run_status': 'rejected', 'would_create_ledger': False,
                'would_grant_rewards': False, 'duplicate_status': 'none',
                'rollback_token_preview': None, 'errors': ['missing_idempotency_key']}
    key = req['idempotency_key']
    payload_hash = req['payload_hash']
    result_hash = req['result_hash']
    if key in state['ledger']:
        existing = state['ledger'][key]
        if existing['payload_hash'] == payload_hash and existing['result_hash'] == result_hash:
            return {'decision': 'duplicate_same_payload_would_return_existing',
                    'dry_run_status': 'duplicate_same_payload', 'would_create_ledger': False,
                    'would_grant_rewards': False, 'duplicate_status': 'duplicate_same_payload',
                    'rollback_token_preview': None, 'errors': []}
        if existing['payload_hash'] != payload_hash:
            return {'decision': 'duplicate_conflict_would_reject',
                    'dry_run_status': 'rejected', 'would_create_ledger': False,
                    'would_grant_rewards': False, 'duplicate_status': 'duplicate_conflict',
                    'rollback_token_preview': None, 'errors': ['duplicate_conflict_different_payload']}
        return {'decision': 'result_hash_mismatch_would_reject',
                'dry_run_status': 'rejected', 'would_create_ledger': False,
                'would_grant_rewards': False, 'duplicate_status': 'duplicate_conflict',
                'rollback_token_preview': None, 'errors': ['result_hash_mismatch']}
    state['ledger'][key] = {'payload_hash': payload_hash, 'result_hash': result_hash,
                            'node_id': req['node_id']}
    return {'decision': 'first_clear_would_stage',
            'dry_run_status': 'staged_pending', 'would_create_ledger': True,
            'would_grant_rewards': False, 'duplicate_status': 'none',
            'rollback_token_preview': 'rb_preview_story_' + key[:16], 'errors': []}


def main():
    if not os.path.exists(SCEN):
        print('FAIL: missing scenario matrix', file=sys.stderr); return 2
    scenarios = json.load(open(SCEN))['scenarios']
    state = {'ledger': {}}
    results = []
    for sc in scenarios:
        req = dict(sc['request'])
        if req.get('idempotency_key') == '__AUTO__':
            req['idempotency_key'] = build_key(req)
        out = simulate(req, state)
        results.append({
            'scenario_id': sc['id'], 'scenario_name': sc['name'],
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
        'pack': 'MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_AND_IDEMPOTENCY_SIMULATION_PACK_v67',
        'simulator_version': 'story_clear_idempotency_dry_run_simulator_v1',
        'design_only': True, 'dry_run_only': True, 'live_apply_allowed': False,
        'db_writes': 0, 'real_db_writes': 0, 'mongo_url_used': False,
        'pymongo_used': False, 'motor_used': False, 'redis_used': False,
        'collection_created': False, 'indexes_created': False,
        'reward_grant_executed': False, 'permanent_progress_written': False,
        'inventory_mutation': False, 'wallet_mutation': False,
        'total_scenarios': len(results),
        'matches': sum(1 for r in results if r['match']),
        'mismatches': sum(1 for r in results if not r['match']),
        'all_match': all(r['match'] for r in results),
        'all_would_grant_rewards_false': all(not r['would_grant_rewards'] for r in results),
        'final_ledger_size_simulated': len(state['ledger']),
        'results': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f: json.dump(summary, f, indent=2, sort_keys=True)
    print('SIMULATOR_OK matches=%d/%d' % (summary['matches'], summary['total_scenarios']))
    return 0 if summary['all_match'] and summary['all_would_grant_rewards_false'] else 1


if __name__ == '__main__':
    sys.exit(main())
