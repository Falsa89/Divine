#!/usr/bin/env python3
"""Pack 100 — Server-Scoped Progress Canon SOT presence + content."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'docs/divine/120_SERVER_SCOPED_PROGRESS_CANON_SOT.md')
assert os.path.exists(p), 'SOT canon file missing'
src=open(p).read()
for needle in [
    'Server-Scoped Progress Canon',
    '(user_id, server_id, feature_scope)',
    'Daily quest** su S1 NON sono completate su S2',
    'TOWER_PROGRESS_SERVER_SCOPE_DEFERRED',
    'REAL_COMPLETION_EVENT_READY',
    'COMPLETION_RUNTIME_DEFERRED',
    'daily_login_claim_success',
    'daily_quest_progress',
    'daily_quest_1',
    'daily_quest_2',
    'daily_quest_3',
    'NO reward live general',
    'release readiness claim',
]:
    assert needle in src, f'SOT canon missing: {needle}'
print('[v110 PACK_100_SERVER_SCOPED_PROGRESS_CANON_SOT] OK canon_user_server_scope tower_deferred quest1_real_completion_ready quest_2_3_deferred no_reward_live no_release_readiness')
