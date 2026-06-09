#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_core_server_scope_sot_v1.json')))
sot_doc = os.path.join(R, d['sot_doc']); assert os.path.exists(sot_doc)
assert d.get('new_server_starts_fresh') is True
assert d.get('no_s1_s2_copy') is True
assert d.get('reward_live_off') is True
assert d.get('progress_live_off') is True
assert d.get('release_readiness_claimed') is False
assert 'gems' in d.get('account_wide', []) or any('gems' in x for x in d.get('account_wide', []))
assert any('soft_currencies' in x or 'soft' in x for x in d.get('server_scoped', []))
print('[v110 PACK_92_CORE_SERVER_SCOPE_SOT] OK sot_doc_present split_account_vs_server_documented')
