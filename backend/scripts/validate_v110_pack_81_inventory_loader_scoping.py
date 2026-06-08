#!/usr/bin/env python3
# Pack 81 - Track 6: inventory/materials loader scoping (honest deferral).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
inv = d.get('core_loader_promotion_batch', {}).get('inventory', {})
assert inv.get('filter_applied') is False, 'inventory must declare filter_applied=false (deferred)'
assert inv.get('promotion_status', '').startswith('DEFERRED'), 'inventory must be DEFERRED'
assert 'reason' in inv and inv['reason']
print('[v110 PACK_81_INVENTORY_LOADER_SCOPING] OK inventory=DEFERRED honest reason_documented')
