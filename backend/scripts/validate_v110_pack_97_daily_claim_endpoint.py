#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_daily_claim_endpoint_v1.json')))
assert d['endpoint'] == 'POST /api/daily-login/claim'
assert d['both_kill_switches_default_off'] is True
assert d['and_logic_required_for_executable'] is True
assert d['unique_index_db_level_anti_double_grant'] is True
assert d['client_token_ignored_server_side_derived'] is True
assert d['writes_only_to_psp_soft_currencies'] is True
assert d['writes_to_users_gold_gems'] is False
assert d['test_day_override_requires_user_marker'] == 'pack_97_test_artifact=true'
assert d['approval_received'] == 'AUTORIZZO_V110_DAILY_LOGIN_CLAIM_AND_FRONTEND_UNLOCK_PACK_97'
src = open(os.path.join(R, 'backend/routes/daily_login_claim.py')).read()
for needle in ['REWARD_CLAIM_LEDGER_LIVE_DISABLED', 'DAILY_LOGIN_CLAIM_DISABLED', 'PLAYER_SERVER_PROFILE_REQUIRED', 'DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER', 'compute_daily_claim_key', 'derive_idempotency_token_from_claim_key', '_slc_pack_97_daily_login_claim', 'pack_97_test_artifact', 'ux_user_server_claimkey_daily_login_pack97', 'partialFilterExpression']:
    assert needle in src, f'missing: {needle}'
print('[v110 PACK_97_DAILY_CLAIM_ENDPOINT] OK both_kill_switches_AND server_side_claim_key unique_index_partial test_marker_required psp_only_write')
