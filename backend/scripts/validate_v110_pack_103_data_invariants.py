#!/usr/bin/env python3
"""Pack 103 - Data invariants."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
assert '"reward_live_general": False' in src
assert '"release_readiness_claimed": False' in src
assert '"premium_grant_blocked": True' in src
print('[v110 PACK_103_DATA_INVARIANTS] OK')
