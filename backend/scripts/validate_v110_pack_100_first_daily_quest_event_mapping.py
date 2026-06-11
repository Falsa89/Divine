#!/usr/bin/env python3
"""Pack 100 — First Real Daily Quest Event Mapping (daily_quest_1 ready, _2/_3 deferred)."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/utils/daily_quest_events.py')).read()
# daily_quest_1 mappato a daily_login_claim_success
assert '"daily_login_claim_success": "daily_quest_1"' in src

# Estrai SOLO il blocco DAILY_QUEST_EVENT_ALLOWLIST e poi rimuovi i commenti
m = re.search(r'DAILY_QUEST_EVENT_ALLOWLIST:\s*Dict\[str, str\]\s*=\s*\{(.*?)\}', src, re.S)
assert m, 'allowlist dict missing'
block = m.group(1)
# Rimuovi commenti (#...) dentro il blocco prima del check
active_lines = []
for ln in block.splitlines():
    s = ln.split('#', 1)[0]
    if s.strip():
        active_lines.append(s)
active = '\n'.join(active_lines)

# Solo daily_quest_1 deve comparire come value attivo
assert '"daily_quest_2"' not in active, f'daily_quest_2 NON deve essere attivo: {active}'
assert '"daily_quest_3"' not in active, f'daily_quest_3 NON deve essere attivo: {active}'
assert '"daily_quest_1"' in active, 'daily_quest_1 deve essere attivo'

# Health endpoint dice REAL_COMPLETION_EVENT_READY per daily_quest_1
claim = open(os.path.join(R, 'backend/routes/daily_quest_claim.py')).read()
assert '"daily_quest_1": "REAL_COMPLETION_EVENT_READY"' in claim
assert '"daily_quest_2": "COMPLETION_RUNTIME_DEFERRED"' in claim
assert '"daily_quest_3": "COMPLETION_RUNTIME_DEFERRED"' in claim

print('[v110 PACK_100_FIRST_DAILY_QUEST_EVENT_MAPPING] OK quest_1_active quest_2_3_deferred only_daily_login_claim_success_active')
