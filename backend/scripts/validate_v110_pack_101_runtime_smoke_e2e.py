#!/usr/bin/env python3
"""Pack 101 — Runtime smoke E2E result invariants."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_101_tower_progress_psp_migration_reward_quarantine/v110_pack_101_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing - run smoke first'
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['required_missing'] == []
assert d['tower_progress_server_scope_status'] == 'TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY'
assert d['tower_reward_live_status'] == 'REWARD_QUARANTINED_PENDING_LEDGER'
assert d['s1_s2_tower_isolation_verified'] is True
assert d['no_users_gold_gems_experience_mutation_from_tower_strict'] is True
assert d['no_legacy_db_tower_progress_write'] is True
assert d['no_premium_grant'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
assert d['client_cannot_grant_tower_reward'] is True
for k in [
    'tower_legacy_status_503_quarantined',
    'tower_legacy_battle_503_quarantined',
    'legacy_tower_progress_collection_empty',
    'preflight_default_off_503',
    'preflight_403_for_unmarked_user',
    'preflight_S1_success',
    'S1_initialized_S2_isolated_at_db_level',
    'strict_status_S2_uninitialized_after_S1_preflight',
    'preview_no_users_mutation_no_progress_advance_no_legacy_write',
    'users_gold_gems_experience_invariant_end_to_end',
    'pack_100_health_preserved',
    'pack_95_story_strict_preserved',
    'pack_93_wallet_split_preserved',
    'pack_94_equipment_preserved',
    'kill_switches_restored', 'cleanup_ok',
]:
    assert d['proofs'].get(k) is True, k
print('[v110 PACK_101_RUNTIME_SMOKE_E2E_VALIDATOR] OK legacy_quarantined strict_psp_scoped S1_S2_isolated no_users_mutation no_legacy_write pack_91_100_preserved')
