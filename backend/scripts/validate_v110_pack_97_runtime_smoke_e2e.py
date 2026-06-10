#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing'
d = json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['no_premium_grant'] is True and d['no_double_daily_reward'] is True
assert d['no_reward_live_general'] is True
assert d['test_artifact_marker'] == 'pack_97_test_artifact'
required = [
    'both_kill_switches_default_off', 'register_ok', 'ensure_psp_a_ok', 'mark_pack_97_ok',
    'claim_blocked_when_global_off', 'claim_blocked_when_only_global_on',
    'both_kill_switches_enabled', 'daily_preflight_indices_ok',
    'first_daily_claim_success_with_fixed_reward',
    'same_day_replay_no_double_grant', 'psp_balance_unchanged_after_replay',
    'ledger_single_row_for_daily_key', 'client_token_cannot_bypass_daily_idempotency',
    'next_day_simulation_grants_new_claim', 'psp_balance_doubled_after_next_day_claim',
    'next_day_same_day_replay_idempotent', 'cross_server_b_no_psp_409',
    'cross_server_isolation_independent_claim_per_server',
    'day_override_forbidden_for_non_test_user',
    'pack_96_premium_block_preserved', 'pack_95_story_strict_preserved',
    'pack_94_equipment_loader_preserved', 'pack_93_wallet_split_preserved',
    'pack_95_shops_buy_quarantine_preserved',
    'daily_kill_switch_disable_re_blocks',
    'kill_switches_restored_to_original', 'cleanup_ok',
]
for k in required:
    assert (d['proofs'] or {}).get(k) is True, k
print('[v110 PACK_97_RUNTIME_SMOKE_E2E] OK first_real_daily_claim no_double_grant cross_server_isolated next_day_simulation day_override_marker_required no_premium pack_91_93_94_95_96_preserved cleanup')
