#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p)
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['no_double_daily_quest_reward'] is True
assert d['completion_proof_marker_enforced'] is True
required=['daily_quest_default_off_and_gated','quest_claim_completion_required_for_real_user','quest_id_not_whitelisted_blocked','first_quest_claim_test_proof_success','same_day_quest_replay_no_double_grant','psp_balance_unchanged_after_quest_replay','different_quest_same_day_grants_new','next_day_quest_simulation_grants_new','quest_cross_server_b_no_psp_409','test_completion_proof_forbidden_for_non_test_user','pack_97_daily_login_still_works','pack_96_premium_block_preserved','pack_95_story_strict_preserved','pack_95_shops_buy_quarantine_preserved','pack_94_equipment_loader_preserved','pack_93_wallet_split_preserved','quest_kill_switch_disable_re_blocks','kill_switches_restored_to_original','cleanup_ok']
for k in required: assert (d['proofs']or{}).get(k) is True, k
print('[v110 PACK_98_RUNTIME_SMOKE_E2E] OK completion_proof_marker_required no_double_grant cross_server_isolated pack_91_97_preserved cleanup')
