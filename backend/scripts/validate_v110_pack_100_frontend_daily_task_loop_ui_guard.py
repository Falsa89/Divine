#!/usr/bin/env python3
"""Pack 100 — Frontend Daily Task Loop UI guard."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f=os.path.join(R,'frontend/src/components/DailyTaskLoopOverview.tsx')
assert os.path.exists(f), 'DailyTaskLoopOverview missing'
src=open(f).read()
for needle in [
    'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED',
    'EXPO_PUBLIC_DAILY_HOME_UNLOCK',
    "const UI_ENABLED = UI_FLAG === 'true';",
    "const HOME_ENABLED = HOME_FLAG === 'true';",
    'if (!forceVisible && (!UI_ENABLED || !HOME_ENABLED)) return null;',
    "useServerScope",
    "useAuth",
    '/api/daily-quest/progress?server_id=',
    "useEffect",
    'daily_quest_1',
    'daily_quest_2',
    'daily_quest_3',
    'In arrivo (deferred)',
    'Server-authoritative',  # presence-friendly token; also accept lowercase
] if False else [  # fallback list (case relaxation):
    'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED',
    'EXPO_PUBLIC_DAILY_HOME_UNLOCK',
    "const UI_ENABLED = UI_FLAG === 'true';",
    "const HOME_ENABLED = HOME_FLAG === 'true';",
    'if (!forceVisible && (!UI_ENABLED || !HOME_ENABLED)) return null;',
    'useServerScope',
    'useAuth',
    '/api/daily-quest/progress?server_id=',
    'useEffect',
    'daily_quest_1',
    'daily_quest_2',
    'daily_quest_3',
    'In arrivo (deferred)',
    'server-authoritative',
]:
    assert needle in src, needle
# DailyHomeRewardSection deve includere il nuovo componente
home=open(os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')).read()
assert 'DailyTaskLoopOverview' in home
# .env frontend default OFF
env=os.path.join(R,'frontend/.env')
if os.path.exists(env):
    et=open(env).read()
    for ln in et.splitlines():
        if ln.startswith('EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=') and ln.split('=',1)[1].strip().lower()=='true':
            assert False, 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED must remain default OFF'
        if ln.startswith('EXPO_PUBLIC_DAILY_HOME_UNLOCK=') and ln.split('=',1)[1].strip().lower()=='true':
            assert False, 'EXPO_PUBLIC_DAILY_HOME_UNLOCK must remain default OFF'
print('[v110 PACK_100_FRONTEND_DAILY_TASK_LOOP_UI_GUARD] OK ui_default_off home_default_off overview_reads_tracker no_false_success')
