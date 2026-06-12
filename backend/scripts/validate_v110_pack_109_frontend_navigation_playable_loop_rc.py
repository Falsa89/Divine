#!/usr/bin/env python3
"""Pack 109 — Frontend Navigation/Playable Loop RC audit."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
plm = open(os.path.join(R, 'backend/routes/playable_loop_map.py')).read()
for s in ('"home"', '"lobby"', '"daily"', '"tower"', '"shop"', '"forge"', '"rewards"', '"guild"', '"arena"', '"pvp"', '"event"'):
    assert s in plm
for bad in ('"status": "READY"', "'status': 'READY'"):
    assert bad not in plm, 'false-ready label found'
flags = open(os.path.join(R, 'frontend/src/utils/playableLoopFlags.ts')).read()
assert 'isFalseReadyClaim' in flags
assert 'PLAYABLE_LOOP_STATUS_COPY' in flags
print('[v110 PACK_109_FRONTEND_NAVIGATION_PLAYABLE_LOOP_RC] OK eleven_surfaces no_false_ready helpers_present')
