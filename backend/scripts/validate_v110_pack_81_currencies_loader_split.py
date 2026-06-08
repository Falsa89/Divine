#!/usr/bin/env python3
# Pack 81 - Track 7: currencies/wallet loader split (honest deferral).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
cur = d.get('core_loader_promotion_batch', {}).get('currencies', {})
assert cur.get('filter_applied') is False
assert cur.get('promotion_status', '').startswith('DEFERRED')
assert 'soft_currencies' in cur.get('reason', '') or 'hard currency' in cur.get('reason', '').lower() or 'PSP' in cur.get('reason', ''), 'currencies reason must reference PSP/soft/hard separation'
print('[v110 PACK_81_CURRENCIES_LOADER_SPLIT] OK currencies=DEFERRED honest split_rationale_documented')
