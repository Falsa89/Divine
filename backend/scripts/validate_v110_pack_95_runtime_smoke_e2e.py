#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'runtime smoke result missing'
d = json.load(open(p))
assert d.get('real_smoke_executed') is True
assert d.get('test_only_writes') is True
assert d.get('no_production_user_writes') is True
assert d.get('test_artifact_marker') == 'pack_95_test_artifact'
proofs = d.get('proofs') or {}
required = [
    'register_ok', 'ensure_psp_a_ok', 'mark_pack_95_ok',
    'story_write_strict_requires_idempotency_token',
    'story_write_strict_unknown_server_psp_required',
    'story_write_strict_first_call_ok',
    'story_write_strict_idempotent_replay_no_double_grant',
    'reward_claim_ledger_single_entry_per_token',
    'story_write_strict_no_currency_grant',
    'story_write_strict_cross_server_isolation',
    'story_write_strict_psp_story_progress_advanced',
    'earn_mission_quarantine_when_server_id',
    'earn_dimension_quarantine_when_server_id',
    'earn_pvp_quarantine_pack_94_preserved',
    'earn_guild_quarantine_pack_94_preserved',
    'shops_buy_quarantine_when_server_id',
    'soul_forge_retire_quarantine_when_server_id',
    'pack_92_wallet_split_preserved',
    'pack_94_equipment_loader_strict_preserved',
    'pack_90_buy_strict_preserved',
    'no_account_wide_leak_smoke_path',
    'cleanup_ok',
]
for k in required:
    assert proofs.get(k) is True, f'proof missing/false: {k} = {proofs.get(k)}'
print('[v110 PACK_95_RUNTIME_SMOKE_E2E] OK story_write_strict reward_claim_ledger_idempotent legacy_quarantine pack_91_93_94_preserved no_production_writes cleanup_ok')
