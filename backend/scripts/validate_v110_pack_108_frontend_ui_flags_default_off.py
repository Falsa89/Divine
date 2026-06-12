#!/usr/bin/env python3
"""Pack 108 — Frontend UI flags default OFF validator.

Verifica che frontend/.env contenga TUTTI i flag UI Pack 108 default OFF.
Verifica che frontend/src/utils/playableLoopFlags.ts esponga la mappa flag
e default a `false` per le surface sensibili.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(R, 'frontend/.env')
env = open(env_path).read()

for flag, expected_default in (
    ('EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_DAILY_HOME_UNLOCK', 'false'),
    ('EXPO_PUBLIC_LOBBY_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_FORGE_STRICT_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_GUILD_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_ARENA_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_PVP_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_EVENT_UI_ENABLED', 'false'),
    ('EXPO_PUBLIC_PLAYABLE_LOOP_MAP_UI_ENABLED', 'false'),
):
    m = re.search(rf'^{re.escape(flag)}=(\S+)$', env, re.MULTILINE)
    assert m, f'flag missing in frontend/.env: {flag}'
    assert m.group(1).strip().lower() == expected_default, f'flag {flag} expected {expected_default} got {m.group(1)}'

ts_path = os.path.join(R, 'frontend/src/utils/playableLoopFlags.ts')
ts = open(ts_path).read()
assert 'getPlayableLoopFlags' in ts
assert 'PLAYABLE_LOOP_STATUS_COPY' in ts
assert 'isFalseReadyClaim' in ts
for f in (
    'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED', 'EXPO_PUBLIC_DAILY_HOME_UNLOCK',
    'EXPO_PUBLIC_LOBBY_UI_ENABLED', 'EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED',
    'EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED', 'EXPO_PUBLIC_FORGE_STRICT_UI_ENABLED',
    'EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED', 'EXPO_PUBLIC_GUILD_UI_ENABLED',
    'EXPO_PUBLIC_ARENA_UI_ENABLED', 'EXPO_PUBLIC_PVP_UI_ENABLED',
    'EXPO_PUBLIC_EVENT_UI_ENABLED', 'EXPO_PUBLIC_PLAYABLE_LOOP_MAP_UI_ENABLED',
):
    assert f in ts, f'flag handler missing in playableLoopFlags.ts: {f}'

# Default false ovunque tranne il SERVER_SWITCH guard (default true).
assert "'EXPO_PUBLIC_SERVER_SWITCH_REFRESH_GUARD_ENABLED', true" in ts

print('[v110 PACK_108_FRONTEND_UI_FLAGS_DEFAULT_OFF] OK env_flags_default_off ts_handlers_present')
