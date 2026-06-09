#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'runtime smoke result missing'
d = json.load(open(p))
assert d.get('real_smoke_executed') is True
assert d.get('test_only_writes') is True
assert d.get('no_production_user_writes') is True
proofs = d.get('proofs', {})
required = [
    'register_ok','ensure_psp_a_ok','mark_pack_93_ok',
    'wallet_spend_server_id_required','wallet_spend_psp_required','wallet_spend_currency_allowlist',
    'wallet_spend_amount_invalid','wallet_spend_idempotency_required','wallet_spend_insufficient_balance',
    'wallet_spend_real_psp_decrement','wallet_split_reflects_spend_real_decrement','wallet_spend_idempotency_replay_ok',
    'story_write_honest_deferred_blocker','equipment_unequip_write_blocker',
    'pack_92_wallet_split_preserved','pack_92_story_loader_preserved','pack_92_equipment_loader_deferred_preserved',
    'pack_90_buy_server_id_required_preserved','pack_90_buy_strict_preserved',
    'no_account_wide_leak_smoke_path','cleanup_ok',
]
for k in required:
    assert proofs.get(k) is True, f'proof {k} missing/false: {proofs.get(k)}'
assert d.get('test_artifact_marker') == 'pack_93_test_artifact'
print('[v110 PACK_93_RUNTIME_SMOKE_E2E] OK wallet_spend_strict_real story_write_deferred_blocker equipment_write_deferred_blocker pack_90_91_92_preserved no_production_writes')
