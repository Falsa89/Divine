#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Static anti-leak guard validator."""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = (
    'backend/server.py',
    'backend/battle_engine.py',
    'backend/routes/achievements.py',
    'frontend/src/hooks/useServerScope.ts',
    'frontend/src/utils/authTokenCompat.ts',
    'frontend/src/utils/serverSwitchRefreshGuard.ts',
    'frontend/app/(tabs)/_layout.tsx',
    'frontend/app/(tabs)/menu.tsx',
    'frontend/app/(tabs)/gacha.tsx',
    'frontend/app/(tabs)/battle.tsx',
)
for fp in FILES:
    raw = open(os.path.join(R, fp)).read()
    lines = []
    for ln in raw.split('\n'):
        s = ln.lstrip()
        if s.startswith('//') or s.startswith('#') or s.startswith('*'):
            continue
        lines.append(ln)
    c = '\n'.join(lines)
    # No silent ||"s1" fallback.
    assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None, f'{fp}: silent ||"s1"'
    assert re.search(r"\?\?\s*['\"]s1['\"]", c) is None, f'{fp}: silent ??"s1"'
    # No reward_live_general": True.
    assert 'reward_live_general": True' not in c and "reward_live_general': True" not in c
    # No release_readiness_claimed": True.
    assert 'release_readiness_claimed": True' not in c and "release_readiness_claimed': True" not in c
    # No public_launch_ready": True.
    assert 'public_launch_ready": True' not in c
print('[v110 PRE_QA_110_STATIC_ANTI_LEAK_GUARD] OK no_silent_s1_fallback no_reward_live_general_true no_release_readiness_claim_true no_public_launch_ready_true')
