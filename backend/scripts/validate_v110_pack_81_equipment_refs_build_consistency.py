#!/usr/bin/env python3
# Pack 81 - Track 9: equipment refs/build consistency (honest deferral).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
eq = d.get('core_loader_promotion_batch', {}).get('equipment_refs', {})
assert eq.get('filter_applied') is False
assert eq.get('promotion_status', '').startswith('DEFERRED')
assert 'reason' in eq and eq['reason']
# Nessun falso filter_applied=true emesso
flag = d.get('core_loader_promotion_batch', {}).get('false_filter_applied_true_emitted_anywhere')
assert flag is False, 'false_filter_applied_true must be false'
print('[v110 PACK_81_EQUIPMENT_REFS_BUILD_CONSISTENCY] OK equipment=DEFERRED honest no_false_filter_applied_true')
