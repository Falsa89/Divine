#!/usr/bin/env python3
"""Pack 105 — Runtime smoke E2E result presence + integrity."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(R, 'data/design/v110_pack_105_forge_upgrade_fusion_strict_psp_material_ledger_spend/v110_pack_105_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(path), 'pack 105 smoke result missing'
d = json.load(open(path))
assert d['real_smoke_executed'] is True, f'smoke not green: {d.get("required_missing")}'
assert d['equipment_upgrade_strict_ready'] is True
assert d['forge_craft_strict_ready'] is True
assert d['equipment_fusion_strict_ready'] is True
assert d['s1_s2_isolation_verified'] is True
assert d['no_users_gold_gems_experience_mutation'] is True
assert d['no_premium_grant'] is True
assert d['no_iap_gacha_payment'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
assert d['client_payload_price_grant_ignored'] is True
assert d['psp_material_storage_active'] is True
for required in ('upgrade_S1_success','upgrade_replay_idempotent','upgrade_no_cross_server',
                 'forge_craft_S1_success','forge_craft_replay_idempotent','client_payload_ignored',
                 'fusion_S1_success','fusion_replay_idempotent','fusion_no_cross_server',
                 'users_invariant','pack_104_shop_still_works','pack_91_104_preserved'):
    assert d['proofs'].get(required) is True, f'missing proof: {required}'
print('[v110 PACK_105_RUNTIME_SMOKE_E2E] OK upgrade_ready forge_ready fusion_ready psp_materials S1_S2_isolated no_users_mutation no_premium client_payload_ignored pack_104_preserved')
