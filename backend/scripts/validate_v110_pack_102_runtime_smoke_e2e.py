#!/usr/bin/env python3
"""Pack 102 — Runtime smoke E2E result invariants."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_102_tower_100_floor_catalog/v110_pack_102_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing - run smoke first'
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['required_missing'] == []
assert d['catalog_version'] == 'tower_v1_100_launch'
assert d['total_launch_floors'] == 100
assert d['all_enemy_teams_deterministic'] is True
assert d['all_enemy_hero_ids_valid_official_eligible'] is True
assert d['boss_floors_are_team_boss_not_true_monster'] is True
assert d['floor_content_identical_across_servers'] is True
assert d['progress_server_scoped_s1_s2'] is True
assert d['no_users_gold_gems_experience_mutation_from_tower'] is True
assert d['tower_reward_live_status'] == 'REWARD_QUARANTINED_PENDING_LEDGER'
assert d['no_premium_grant'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
for k in [
    'catalog_summary_100_floors_deterministic',
    'all_100_floors_valid_no_dup_no_premium_boss_team_only',
    'floor_100_major_boss_rarity_6_all_official',
    'catalog_floor_50_deterministic_5x',
    'preview_floor_1_with_catalog',
    'preview_floor_100_strongest_launch',
    'users_gold_gems_experience_invariant',
    'preflight_S1_no_S2_contamination',
    'preview_no_progress_advance',
    'pack_95_story_strict_preserved',
    'pack_100_preserved',
    'pack_101_tower_strict_health_preserved',
    'kill_switch_restored', 'cleanup_ok',
]:
    assert d['proofs'].get(k) is True, k
print('[v110 PACK_102_RUNTIME_SMOKE_E2E_VALIDATOR] OK 100_deterministic team_bosses S1_S2_isolated no_users_mutation no_reward_live pack_91_101_preserved')
