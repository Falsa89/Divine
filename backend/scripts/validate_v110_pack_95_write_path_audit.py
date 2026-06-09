#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_write_path_audit_v1.json')))
eps = {e['endpoint']: e for e in d['audited_endpoints']}
assert eps['POST /api/story/battle']['strict_server_scope'] is True
assert eps['POST /api/story/battle']['idempotency_required'] is True
assert eps['POST /api/story/battle']['grants_currency'] is False
assert eps['POST /api/shops/buy']['server_id_aware'] is True
assert eps['POST /api/soul-forge/retire']['server_id_aware'] is True
assert eps['POST /api/currency/earn-mission']['blocker_when_server_id'] == 'LEGACY_CURRENCY_QUARANTINE_DEFERRED'
assert eps['POST /api/currency/earn-dimension']['blocker_when_server_id'] == 'LEGACY_CURRENCY_QUARANTINE_DEFERRED'
assert d.get('no_account_wide_writes_for_server_bound_data') is True
assert d.get('no_premium_grant') is True
assert d.get('no_double_grant_possible') is True
assert d.get('hardcoded_s1_in_active_server_scoped_paths') is False
print('[v110 PACK_95_WRITE_PATH_AUDIT] OK story_strict legacy_quarantine_active no_account_wide_writes')
