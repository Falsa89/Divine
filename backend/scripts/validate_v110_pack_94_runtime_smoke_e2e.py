#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_94_equipment_backfill_strict_currency_quarantine/v110_pack_94_runtime_smoke_e2e_result_v1.json')
d = json.load(open(p))
assert d.get('real_smoke_executed') is True
proofs = d.get('proofs', {})
required = ['register_ok','ensure_psp_a_ok','mark_and_seed_pack_94_ok','equipment_loader_strict_real_filter','equipment_loader_unknown_server_blocker','equipment_unequip_strict_success','equipment_unequip_psp_required','legacy_currency_earn_pvp_quarantine','legacy_currency_earn_guild_quarantine','legacy_earn_pvp_legacy_path_unchanged','pack_92_wallet_split_preserved','pack_93_story_write_blocker_preserved','pack_90_buy_strict_preserved','cleanup_ok']
for k in required: assert proofs.get(k) is True, f'{k} missing: {proofs.get(k)}'
print('[v110 PACK_94_RUNTIME_SMOKE_E2E] OK 14/14 proofs equipment_strict_loader_write legacy_currency_quarantine pack_90_92_93_preserved')
