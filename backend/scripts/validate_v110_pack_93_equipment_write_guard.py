#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_equipment_write_guard_v1.json')))
assert d.get('no_equip_unequip_forge_write_promotion_in_pack_93') is True
assert d.get('false_readiness') is False
superseded = d.get('superseded_by_pack_94_backfill_executed') is True
for e in d.get('endpoints', []):
    assert e.get('server_id_query_param_added') is True
    if not superseded:
        assert e.get('blocker') == 'EQUIPMENT_SERVER_SCOPE_MIGRATION_REQUIRED'
eq_src = open(os.path.join(R, 'backend/routes/equipment.py')).read()
if not superseded:
    assert 'EQUIPMENT_SERVER_SCOPE_MIGRATION_REQUIRED' in eq_src
    assert '_slc_pack_93_equipment_write_guard' in eq_src
else:
    assert '_slc_pack_94_equipment_strict_write' in eq_src and '_slc_pack_94_equipment_strict_unequip' in eq_src
print('[v110 PACK_93_EQUIPMENT_WRITE_GUARD] OK server_id_aware_blocker_or_pack_94_strict_promotion no_promotion no_false_readiness')
