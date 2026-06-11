#!/usr/bin/env python3
"""Pack 100 — Story/Tower server-scope audit and guards."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
# Story strict path (Pack 95) must remain server-scoped when server_id presente
assert 'if server_id and isinstance(server_id, str) and server_id.strip():' in combat
assert 'pack_95_strict_story_progress_write' in combat
assert 'psp.story_progress' in combat or 'story_progress.completed' in combat
# Tower battle is identified as account-wide LEAK (Pack 100 audit) and must NOT be 
# claimed as ready. SOT documenta TOWER_PROGRESS_SERVER_SCOPE_DEFERRED.
sot=open(os.path.join(R,'docs/divine/120_SERVER_SCOPED_PROGRESS_CANON_SOT.md')).read()
assert 'TOWER_PROGRESS_SERVER_SCOPE_DEFERRED' in sot
assert 'POST /api/tower/battle' in sot
assert 'LEAK PLAYER-FACING (DEFERRED)' in sot
# No reward for tower live activated
for forbidden_live_token in [
    'tower_rewards_live = true', 'tower_rewards_live=True',
    'tower_progress_live = true', 'tower_live=True',
]:
    assert forbidden_live_token not in combat
print('[v110 PACK_100_STORY_TOWER_SERVER_SCOPE_AUDIT] OK story_strict_server_scoped tower_leak_deferred sot_documented no_tower_live_grant')
