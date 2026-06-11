#!/usr/bin/env python3
"""Pack 103 - Static anti-leak guard."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ['backend/routes/tower_strict.py','backend/utils/reward_source_registry.py','backend/utils/daily_quest_events.py']:
    src=open(os.path.join(R,f)).read()
    for forb in ['server_id="s1"',"server_id='s1'",'"reward_live_general": True','"release_readiness_claimed": True']:
        assert forb not in src, f'{f} leak: {forb}'
print('[v110 PACK_103_STATIC_ANTI_LEAK] OK')
