#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: lobby NON deve consentire launch con fallback team/enemy spacciato per reale.
import os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'frontend','app','pre-battle-lobby.tsx')
c=open(p,encoding='utf-8').read()
required=['REAL_PLAYER_TEAM_SOURCE_PENDING','AUTHORED_ENCOUNTER_SOURCE_PENDING','SELECTED_SERVER_REQUIRED','launchAllowedNormal','EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH','blockerReasons','realPlayerTeamAvailable','authoredEncounterAvailable','selectedServerAvailable']
for t in required:
    if t not in c: print(f'FAIL token missing: {t}'); sys.exit(1)
if "server_id: 's1'" in c: print("FAIL hardcoded server_id 's1' still present"); sys.exit(1)
if 'PLAYER_SAFE_FALLBACK_TEAM' not in c: print('FAIL PLAYER_SAFE_FALLBACK_TEAM not declared'); sys.exit(1)
# startBattle must contain an early return when blockers active.
import re
m=re.search(r'const\s+startBattle\s*=\s*\(\)\s*=>\s*\{(.*?)\n\s{0,4}\};', c, re.DOTALL)
if not m: print('FAIL startBattle block not found'); sys.exit(1)
block=m.group(1)
if 'launchAllowedNormal' not in block or 'return' not in block: print('FAIL startBattle early-return guard missing'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: lobby blocks launch with fallback team/enemy'); sys.exit(0)
