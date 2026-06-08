#!/usr/bin/env python3
# Pack 82 - Track 3: server-scoped player progress SOT formalized.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
sot = d.get('canonical_decision_server_player_progress', {})
assert sot, 'canonical_decision_server_player_progress missing'
stmt = sot.get('statement', '')
for must in ('Server-scoped player progress SOT', 'player_level', 'player_exp', 'roster', 'team', 'story_progress', 'PSP', 'NON in users.* global'):
    assert must in stmt, f'SOT statement missing token: {must}'
ex = sot.get('invariant_examples', [])
assert any('S1 livello 40 != S2 livello 40' in e for e in ex)
assert any('nuovo server' in e and 'livello 1' in e for e in ex)
assert sot.get('no_fallback_to_old_server_or_account_level') is True
# Validazione live: headers presenti nel codice route
src = open(os.path.join(R, 'backend/server.py')).read()
for h in ('"X-Player-Level"', '"X-Player-Exp"', '"X-Server-Progression-State"'):
    assert h in src, f'header {h} missing in route'
print('[v110 PACK_82_SERVER_PLAYER_PROGRESS_SOT] OK statement_canonical headers_present S1!=S2 fresh_start_documented')
