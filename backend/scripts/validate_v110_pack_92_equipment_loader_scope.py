#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_equipment_loader_scope_v1.json')))
assert d.get('server_id_param') is True
assert d.get('strict_filter_promotion_in_pack_92') is False
assert d.get('honest_deferred_blocker') == 'EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED'
assert d.get('migration_required') is True
assert d.get('false_filter_applied_true') is False
assert d.get('no_equip_unequip_forge_write_promotion_in_pack_92') is True
fp = os.path.join(R, d['file']); assert os.path.exists(fp)
src = open(fp).read()
assert 'EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED' in src
assert 'legacy_account_wide_deprecated' in src
print('[v110 PACK_92_EQUIPMENT_LOADER_SCOPE] OK honest_deferred_blocker migration_required no_strict_promotion no_write_promotion')
