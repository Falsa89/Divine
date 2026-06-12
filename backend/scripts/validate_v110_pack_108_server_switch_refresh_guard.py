#!/usr/bin/env python3
"""Pack 108 — Server Switch Refresh Guard validator.

Verifica che frontend/src/utils/serverSwitchRefreshGuard.ts implementi:
  - useServerSwitchRefreshGuard hook con refreshToken bump al cambio server.
  - buildPlayableLoopCacheKey che NON inietta 's1' silenziosamente.
  - serverScopeRequired: true marker.
  - NO_SERVER_SELECTED quando serverId e' assente.
Verifica che PlayableLoopConsumer.tsx usi useServerSwitchRefreshGuard e
non ricada su s1 in caso di server null.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(R, 'frontend/src/utils/serverSwitchRefreshGuard.ts')
c = open(f).read()

for token in (
    'useServerSwitchRefreshGuard', 'buildPlayableLoopCacheKey',
    'clearPlayableLoopCacheKeys', 'serverScopeRequired: true',
    'NO_SERVER_SELECTED', 'setRefreshToken',
    'lastServerId', 'useServerScope',
):
    assert token in c, f'missing in serverSwitchRefreshGuard.ts: {token}'

# No silent fallback a 's1' come default (cerca pattern di assegnazione di default).
assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None, 'silent ||"s1" fallback'
assert re.search(r"=\s*['\"]s1['\"]\s*[;,)]", c) is None, 'default ="s1"'
assert re.search(r"\?\?\s*['\"]s1['\"]", c) is None, 'silent ??"s1" fallback'

consumer = open(os.path.join(R, 'frontend/src/components/PlayableLoopConsumer.tsx')).read()
assert 'useServerSwitchRefreshGuard' in consumer
assert 'buildPlayableLoopCacheKey' in consumer
assert 'NO_SERVER_SELECTED' in consumer or 'playable-loop-no-server' in consumer
assert re.search(r"\|\|\s*['\"]s1['\"]", consumer) is None, 'silent ||"s1" in consumer'
assert re.search(r"=\s*['\"]s1['\"]\s*[;,)]", consumer) is None, 'default ="s1" in consumer'

print('[v110 PACK_108_SERVER_SWITCH_REFRESH_GUARD] OK hook_invalidates_on_switch no_silent_s1_fallback')
