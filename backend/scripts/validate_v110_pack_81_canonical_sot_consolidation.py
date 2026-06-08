#!/usr/bin/env python3
# Pack 81 - Track 2: canonical SOT consolidation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
cd = d.get('canonical_decision', {})
assert cd, 'canonical_decision missing'
stmt = cd.get('statement', '')
for must in ('user_heroes', 'roster posseduto', 'livelli', 'stelle', 'build operative', 'team formation', 'battle player team source', 'SERVER-SCOPED'):
    assert must in stmt, f'canonical statement missing token: {must}'
assert 'account-wide' in stmt
aw = cd.get('account_wide_remaining', [])
for must in ('account identity', 'auth/login', 'entitlements globali', 'impostazioni account'):
    assert any(must in x for x in aw), f'account_wide_remaining missing: {must}'
legacy = cd.get('legacy_data_handling', '')
assert 'legacy' in legacy.lower() and 'final source' in legacy.lower()
print('[v110 PACK_81_CANONICAL_SOT_CONSOLIDATION] OK statement_complete account_wide_set_locked legacy_data_marked_non_final')
