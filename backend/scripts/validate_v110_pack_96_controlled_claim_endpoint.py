#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_controlled_claim_endpoint_v1.json')))
assert d.get('endpoint') == 'POST /api/rewards/claim'
assert d.get('auth_required') is True and d.get('psp_required') is True
assert d.get('idempotency_token_required') is True
assert d.get('source_must_be_allowlisted') is True
assert d.get('replay_check_via_ledger') is True
assert d.get('kill_switch_default') is False
assert d.get('blocker_when_disabled') == 'REWARD_CLAIM_LEDGER_LIVE_DISABLED'
assert d.get('approval_received') == 'AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_PACK_96'
assert d.get('writes_only_to_psp_soft_currencies') is True
assert d.get('writes_to_users_gold_gems') is False
src = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
for needle in ['REWARD_CLAIM_LEDGER_LIVE_DISABLED', 'PLAYER_SERVER_PROFILE_REQUIRED', 'IDEMPOTENCY_TOKEN_REQUIRED', 'REWARD_SOURCE_NOT_ALLOWLISTED', 'PREMIUM_GRANT_BLOCKED', '/rewards/claim', 'reward_claim_ledger']:
    assert needle in src, f'missing in route: {needle}'
print('[v110 PACK_96_CONTROLLED_CLAIM_ENDPOINT] OK kill_switch_default_off psp_required idempotency_required allowlist_enforced replay_safe premium_blocked')
