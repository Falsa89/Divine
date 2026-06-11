#!/usr/bin/env python3
"""Pack 100 — Runtime smoke E2E result presence + invariants."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_100_daily_quest_gameplay_completion_events_first_real_task_loop/v110_pack_100_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing - run smoke first'
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['required_missing'] == []
assert d['daily_task_loop_ready'] is True
assert d['daily_quest_1_real_completion_event_ready'] is True
assert d['daily_quest_2_status'] == 'COMPLETION_RUNTIME_DEFERRED'
assert d['daily_quest_3_status'] == 'COMPLETION_RUNTIME_DEFERRED'
assert d['s1_s2_isolation_verified'] is True
assert d['story_strict_server_scope_verified'] is True
assert d['tower_progress_server_scope_status'] == 'TOWER_PROGRESS_SERVER_SCOPE_DEFERRED'
assert d['no_premium_grant'] is True
assert d['no_double_daily_quest_reward'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
assert d['client_cannot_fake_completion'] is True
for k in [
    'daily_login_S1_emits_event_completes_tracker_S1',
    'tracker_S1_quest1_completed_only',
    'S2_tracker_not_contaminated_by_S1',
    'claim_S1_via_runtime_tracker_real_grant',
    'replay_S1_claim_idempotent_no_double_grant',
    'psp_A_correct_sum_psp_B_isolated',
    'S2_claim_blocked_no_S1_leak',
    'daily_quest_2_remains_deferred',
    'daily_quest_3_remains_deferred',
    'client_spoof_blocked',
    'pack_96_premium_block_preserved',
    'pack_95_story_strict_S1_isolated_from_S2',
    'pack_93_94_preserved',
    'event_bridge_skipped_when_tracker_off_login_still_succeeds',
    'pack_97_daily_login_still_works',
    'kill_switches_restored_to_original',
    'cleanup_ok',
]:
    assert d['proofs'].get(k) is True, k
print('[v110 PACK_100_RUNTIME_SMOKE_E2E_VALIDATOR] OK loop_real_S1 isolation_S1_S2 quest_2_3_deferred client_spoof_blocked pack_93_99_preserved')
