#!/usr/bin/env python3
"""Pack 109 — Tower RC audit (static)."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/tower_strict.py')).read()
for tok in ('/tower/strict/health', 'pack_103_test_artifact', 'TOWER_STRICT_PREFLIGHT_ENABLED',
            'server_id', 'reward_live_general'):
    assert tok in c, f'tower_strict missing {tok}'
import re
assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None
print('[v110 PACK_109_TOWER_RC] OK tower_strict_canonical_invariants_intact')
