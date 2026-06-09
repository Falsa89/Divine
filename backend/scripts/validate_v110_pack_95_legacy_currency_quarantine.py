#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_legacy_currency_quarantine_v1.json')))
eps = {e['endpoint']: e for e in d['endpoints']}
for k in ('/api/currency/earn-mission', '/api/currency/earn-dimension', '/api/currency/earn-pvp', '/api/currency/earn-guild'):
    assert eps[k]['blocker_when_server_id'] == 'LEGACY_CURRENCY_QUARANTINE_DEFERRED', k
assert eps['/api/currency/earn-mission']['pack_95_added'] is True
assert eps['/api/currency/earn-dimension']['pack_95_added'] is True
assert d.get('no_account_wide_write_when_server_id_present') is True
src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
for needle in ['/currency/earn-mission', '/currency/earn-dimension', '/currency/earn-pvp', '/currency/earn-guild']:
    assert needle in src
for needle in ['_slc_pack_95_legacy_currency_quarantine', '_slc_pack_94_legacy_currency_quarantine']:
    assert needle in src
print('[v110 PACK_95_LEGACY_CURRENCY_QUARANTINE] OK earn-mission earn-dimension quarantined earn-pvp earn-guild pack94_preserved')
