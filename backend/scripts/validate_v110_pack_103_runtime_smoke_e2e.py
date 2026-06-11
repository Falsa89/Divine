#!/usr/bin/env python3
"""Pack 103 - Smoke E2E result invariants."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_103_tower_execute_floor_claim_ledger_daily_quest_2/v110_pack_103_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p)
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['required_missing'] == []
assert d['tower_execute_ready'] is True
assert d['daily_quest_2_status'] == 'REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR'
assert d['s1_s2_isolation_verified'] is True
assert d['no_users_mutation'] is True
assert d['no_premium_grant'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
for k in ['execute_floor_1_S1_success','S1_advanced_S2_untouched','replay_same_token_idempotent','replay_diff_token_same_floor_idempotent','no_double_grant_after_replay','tracker_S1_quest_2_completed','tracker_S2_uncontaminated','daily_quest_2_claim_via_tracker','users_invariant','legacy_tower_503_preserved','pack_102_catalog_preserved','pack_100_daily_login_preserved','cleanup_ok']:
    assert d['proofs'].get(k) is True, k
print('[v110 PACK_103_SMOKE_E2E_VALIDATOR] OK')
