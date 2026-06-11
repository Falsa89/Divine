#!/usr/bin/env python3
"""Pack 101 — Story/Daily/Tower server-scope cross validator (canon consistente)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Tower SOT Pack 101 esiste
assert os.path.exists(os.path.join(R,'docs/divine/121_TOWER_SERVER_SCOPED_PROGRESS_SOT.md'))
# Server-Scope Progress Canon Pack 100 esiste e include tower
canon=open(os.path.join(R,'docs/divine/120_SERVER_SCOPED_PROGRESS_CANON_SOT.md')).read()
assert 'TOWER_PROGRESS_SERVER_SCOPE_DEFERRED' in canon
# Pack 99 tracker server-scoped chiave canonica
tr=open(os.path.join(R,'backend/routes/daily_quest_tracker.py')).read()
assert '"user_id"' in tr and '"server_id"' in tr
# Pack 95 story strict server-scoped
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
assert 'pack_95_strict_story_progress_write' in combat
# Tower strict route esiste
assert os.path.exists(os.path.join(R,'backend/routes/tower_strict.py'))
# Tutti i sistemi player-facing live (daily login, daily quest, tower strict) usano server_id
for f in ['backend/routes/daily_login_claim.py','backend/routes/daily_quest_claim.py','backend/routes/daily_quest_tracker.py','backend/routes/tower_strict.py']:
    src=open(os.path.join(R,f)).read()
    assert 'server_id' in src, f'{f}: server_id required'
    assert 'SERVER_ID_REQUIRED' in src, f'{f}: SERVER_ID_REQUIRED guard'
print('[v110 PACK_101_STORY_DAILY_TOWER_CROSS_VALIDATOR] OK story_server_scoped daily_server_scoped tower_strict_server_scoped canon_consistent')
