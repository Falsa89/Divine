#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
z = d.get('data_invariants_and_zero_forbidden_mutation', {})
for k in ('user_heroes_writes','users_writes','battle_history_writes','inventory_writes','equipment_writes'):
    assert z.get(k) == 0, f'{k} must be 0'
for k in ('reward_grant','progress_advance','premium_currency_grant','gacha_mutation','shop_mutation','vip_mutation','battle_pass_mutation','legacy_cleanup_executed','destructive_migration_executed','physical_normalization_executed_in_this_pack','bulk_psp_apply','copy_s1_to_s2_executed','starter_heroes_created','starter_premium_granted','player_level_mutation_on_existing_psp','user_heroes_mutation_on_existing'):
    assert z.get(k) is False, f'{k} must be false'
# Static: ensure fn non scrive user_heroes/users/inventory/equipment
src = open(os.path.join(R, 'backend/server.py')).read()
start = src.index('async def psp_ensure_fresh_start')
rest = src[start:]
end_candidates = []
for marker in ('\n@app.', '\n@router.', '\nasync def ', '\ndef '):
    idx = rest.find(marker, 100)
    if idx > 0: end_candidates.append(idx)
fn = rest[:min(end_candidates) if end_candidates else len(rest)]
for forbidden_collection_write in ('db.user_heroes.insert', 'db.user_heroes.update', 'db.user_heroes.delete', 'db.users.update', 'db.users.delete', 'db.inventory', 'db.user_equipment', 'db.battle_history'):
    assert forbidden_collection_write not in fn, f'ensure fn writes forbidden collection: {forbidden_collection_write}'
print('[v110 PACK_85_DATA_INVARIANTS_AND_ZERO_FORBIDDEN_MUTATION] OK user_heroes_writes=0 reward_grant=false legacy_cleanup=false no_S1_to_S2_copy ensure_fn_writes_only_psp')
