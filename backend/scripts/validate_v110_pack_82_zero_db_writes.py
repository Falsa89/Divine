#!/usr/bin/env python3
# Pack 82 - Track 7: zero DB writes (NO physical PSP normalization).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
z = d.get('zero_mutation_economy_preservation', {})
for k in ('db_writes','psp_writes','user_heroes_writes','users_writes'):
    assert z.get(k) == 0, f'{k} must be 0'
for k in ('reward_grant','progress_advance','ledger_writes','premium_currency_grant','gacha_mutation','shop_mutation','vip_mutation','battle_pass_mutation','physical_psp_normalization_executed','legacy_cleanup_executed','destructive_migration_executed'):
    assert z.get(k) is False, f'{k} must be false'
# Verifica statica audit script -> nessuna scrittura
audit = open(os.path.join(R, 'backend/scripts/audit_v110_pack_82_psp_user_id_namespace.py')).read()
for forbidden in ('insert_one', 'update_one', 'delete_one', 'replace_one', 'insert_many', 'update_many', 'delete_many'):
    assert forbidden not in audit, f'audit script must be READ-ONLY: contains {forbidden}'
print('[v110 PACK_82_ZERO_DB_WRITES] OK no_psp_writes no_normalization no_destructive_migration audit_script_read_only')
