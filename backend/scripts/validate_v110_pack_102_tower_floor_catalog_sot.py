#!/usr/bin/env python3
"""Pack 102 — Tower Floor Catalog SOT presence + content."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'docs/divine/122_TOWER_FLOOR_CATALOG_SOT.md')
assert os.path.exists(p), 'Tower catalog SOT missing'
src=open(p).read()
for needle in [
    'Tower Floor Catalog SOT',
    'Torre launch base = 100 piani',
    '+20 o +30 piani per patch',
    'contenuto del floor è identico',
    'progressione resta server-scoped',
    'Enemy team **deterministici**',
    'NO boss mostri singoli',
    'team boss',
    'major boss team',
    'tower_v1_100_launch',
    'LAUNCH_BASE_HERO_IDS',
    'EXTRA_PREMIUM_HERO_IDS',
    'TEAM_SIZE = 6',
    'TOWER_REWARD_LIVE_GRANT' if False else 'NO tower reward live grant',
    'release readiness claim',
]:
    assert needle in src, needle
print('[v110 PACK_102_TOWER_FLOOR_CATALOG_SOT] OK 100_floors_canon hero_source_documented expansion_policy_documented S1_S2_isolation_documented')
