#!/usr/bin/env python3
"""Pack 101 — Tower strict preflight: gated, test-only, idempotent, no users.* mutation."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend/scripts'))
from _pack_101_validator_helpers import extract_async_fn_body
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
for needle in [
    'tower_strict_preflight',
    'TOWER_STRICT_PREFLIGHT_DISABLED',
    'PREFLIGHT_ENDPOINT_TEST_ONLY',
    'pack_101_test_artifact',
    'idempotent_replay',
    'player_server_profiles.update_one',
    'PLAYER_SERVER_PROFILE_REQUIRED',
]:
    assert needle in src, needle
body = extract_async_fn_body(src, 'tower_strict_preflight')
assert body, 'preflight fn not found'
assert 'if not _preflight_on()' in body, 'preflight not gated'
assert 'PREFLIGHT_ENDPOINT_TEST_ONLY' in body, 'test-only marker not enforced'
# Anti-leak: preflight non deve scrivere su users.* né concedere reward.
for forbidden in [
    'db.users.update_one', 'db.users.insert_one',
    'users.gold', 'users.gems', 'users.experience',
    'grant_fn', 'reward_claim_ledger',
]:
    assert forbidden not in body, f'preflight leak: {forbidden}'
print('[v110 PACK_101_TOWER_BACKFILL_PREFLIGHT] OK gated test_only marker_required idempotent no_users_mutation no_grant')
