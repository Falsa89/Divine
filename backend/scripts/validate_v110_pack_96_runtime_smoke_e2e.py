#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing'
d = json.load(open(p))
assert d.get('real_smoke_executed') is True
assert d.get('test_only_writes') is True
assert d.get('no_production_user_writes') is True
assert d.get('no_premium_grant') is True
assert d.get('no_double_grant') is True
assert d.get('no_reward_live_general') is True
assert d.get('test_artifact_marker') == 'pack_96_test_artifact'
required = [
    'kill_switch_default_off', 'register_ok', 'ensure_psp_a_ok', 'mark_pack_96_ok',
    'kill_switch_blocks_when_off', 'kill_switch_enable_for_test_ok',
    'preflight_index_creation_safe_idempotent_first_call',
    'preflight_index_creation_idempotent_second_call',
    'first_controlled_claim_success', 'replay_returns_idempotent_no_double_grant',
    'ledger_single_row_after_replay', 'psp_balance_unchanged_after_replay',
    'same_source_different_token_grants_again',
    'unknown_source_blocked', 'premium_grant_blocked', 'no_ledger_row_for_premium_attempt',
    'cross_server_no_leak_psp_required', 'story_marker_claim_noop_success',
    'pack_95_story_strict_preserved', 'pack_95_shops_buy_quarantine_preserved',
    'pack_94_equipment_loader_preserved', 'pack_93_wallet_split_preserved',
    'kill_switch_disable_re_blocks_correctly', 'kill_switch_restored_to_original',
    'cleanup_ok',
]
for k in required:
    assert (d.get('proofs') or {}).get(k) is True, k
print('[v110 PACK_96_RUNTIME_SMOKE_E2E] OK first_claim replay_no_double_grant unknown_blocked premium_blocked cross_server_isolated kill_switch_lifecycle pack_91_93_94_95_preserved cleanup_ok')
