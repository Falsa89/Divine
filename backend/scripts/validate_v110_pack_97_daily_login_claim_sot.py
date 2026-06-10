#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_daily_login_claim_sot_v1.json')))
assert d['source_id'] == 'daily_login_claim'
assert d['daily_key_computed_server_side'] is True
assert d['idempotency_token_derived_from_claim_key'] is True
assert d['no_double_claim_per_user_server_day'] is True
assert d['unique_index_fields'] == ['user_id', 'server_id', 'claim_key']
assert d['unique_index_partial_filter'] == {'claim_source': 'daily_login_claim'}
sot = os.path.join(R, 'docs/divine/117_DAILY_LOGIN_CLAIM_SOT.md')
assert os.path.exists(sot), sot
content = open(sot).read()
assert 'daily_login_<server_id>_<YYYY-MM-DD UTC>' in content
assert 'sha1(claim_key)' in content
print('[v110 PACK_97_DAILY_LOGIN_CLAIM_SOT] OK doc_present server_side_claim_key unique_index_defined')
