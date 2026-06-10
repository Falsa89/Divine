#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f=os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')
src=open(f).read()
for needle in [
    'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED',
    'EXPO_PUBLIC_DAILY_HOME_UNLOCK',
    'DailyLoginClaimButton',
    'DailyQuestClaimButton',
    "if (!forceVisible && (!DAILY_HOME_UI_ENABLED || !DAILY_HOME_UNLOCKED))",
]:
    assert needle in src, needle
# Home tsx integration
home=open(os.path.join(R,'frontend/app/(tabs)/home.tsx')).read()
assert 'DailyHomeRewardSection' in home
# Default OFF policy
flag_a=os.path.join(R,'frontend/.env')
found_unsafe=False
if os.path.exists(flag_a):
    env=open(flag_a).read()
    # Ensure neither flag set to true by default in production env
    for line in env.splitlines():
        if line.strip().startswith('EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED='):
            if line.strip().split('=',1)[1].strip().lower() == 'true':
                found_unsafe=True
        if line.strip().startswith('EXPO_PUBLIC_DAILY_HOME_UNLOCK='):
            if line.strip().split('=',1)[1].strip().lower() == 'true':
                found_unsafe=True
assert not found_unsafe, 'Daily Home flags must remain default OFF in frontend .env'
print('[v110 PACK_99_DAILY_HOME_CONTROLLED_UNLOCK_STATIC] OK both_flags_default_off home_embed_gated no_production_leak')
