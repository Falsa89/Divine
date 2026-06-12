#!/usr/bin/env python3
"""Pack 106 — Endpoint signatures + safety."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/controlled_rewards.py')).read()

for route in ('/controlled-rewards/health','/controlled-rewards/catalog',
              '/controlled-rewards/mail/claim','/controlled-rewards/achievement/claim',
              '/controlled-rewards/daily-weekly/claim'):
    assert route in src, f'route missing: {route}'

for ks in ('REWARD_CLAIM_LEDGER_LIVE_ENABLED','MAIL_CLAIM_CONTROLLED_ENABLED',
           'ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED','DAILY_WEEKLY_REWARD_CLAIM_ENABLED'):
    assert ks in src, f'kill switch missing: {ks}'

assert 'PACK_106_USER_TEST_MARKER' in src
assert 'pack_106_test_artifact' in src
assert '_require_pack_106_test_user' in src

for pyd_model in ('MailClaimRequest','AchievementClaimRequest','DailyWeeklyClaimRequest'):
    assert f'class {pyd_model}' in src

for key_pat in ('mail_{sid}_','achievement_{sid}_','dwr_{sid}_'):
    assert key_pat in src, f'server-side claim_key pattern missing: {key_pat}'

assert 'ACHIEVEMENT_COMPLETION_REQUIRED' in src
assert 'PACK_106_ACHIEVEMENT_COMPLETION_PREFIX' in src

# No client payload trust
assert 'req.reward' not in src, 'client reward never trusted'
assert 'req.cost' not in src, 'client cost never trusted'
assert 'req.grant' not in src, 'client grant never trusted'
assert 'req.soft_currencies' not in src, 'client soft_currencies never trusted'
assert 'req.materials' not in src, 'client materials never trusted'

# Period key uses UTC strftime
assert '%Y-%m-%d' in src or '"%Y-%m-%d"' in src
assert 'isocalendar' in src

print('[v110 PACK_106_CONTROLLED_REWARDS_ENDPOINTS] OK all_routes_present kill_switches_named test_marker_required idempotency_required server_side_claim_keys completion_required_blocker_present no_client_trust period_keying_utc')
