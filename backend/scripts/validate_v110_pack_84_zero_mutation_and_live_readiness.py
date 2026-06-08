#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
z = d.get('zero_mutation_economy_preservation', {})
# PSP user_id writes ESPRESSAMENTE ammessi a 1690 (lo scope autorizzato)
assert z.get('psp_user_id_writes') == 1690, f'psp_user_id_writes must be exactly 1690; got {z.get("psp_user_id_writes")}'
# Ogni altra collezione: 0
for k in ('user_heroes_writes','users_writes','battle_history_writes','inventory_writes','equipment_writes','any_other_collection_writes','delete_operations'):
    assert z.get(k) == 0, f'{k} must be 0; got {z.get(k)}'
for k in ('reward_grant','progress_advance','ledger_writes','premium_currency_grant','gacha_mutation','shop_mutation','vip_mutation','battle_pass_mutation','legacy_cleanup_executed','destructive_migration_beyond_user_id_normalization','player_level_mutation','player_exp_mutation','s1_to_s2_copy','new_server_psp_creation'):
    assert z.get(k) is False, f'{k} must be false'
l = d.get('live_readiness_update', {})
for k in ('reward_live','progress_live','ledger_live','battle_engine_authoritative_live','release_readiness_claimed'):
    assert l.get(k) is False, f'{k} must be false'
print('[v110 PACK_84_ZERO_MUTATION_AND_LIVE_READINESS] OK psp_user_id_writes=1690 (authorized) other_collection_writes=0 reward/progress live=false')
