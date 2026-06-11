#!/usr/bin/env python3
"""Pack 100 — First Real Daily Quest Event Mapping (rebased canonical post Pack 103).

CANONICAL BASELINE EVOLUTION:
  * Pack 100 baseline: SOLO daily_quest_1 attivo via daily_login_claim_success.
  * Pack 103 reconciled (approved): +daily_quest_2 attivo via tower_floor_clear_success
    (server-only, allowlist source `tower_strict_battle_execute`, no client free proof).
  * Pack 104: aggiunge la riga canonical che daily_quest_2 sia READY_VIA_TOWER_CLEAR
    (e non più COMPLETION_RUNTIME_DEFERRED).

Il check sull'origine server-side dell'evento (allowlist source route) RIMANE invariato.
"""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/utils/daily_quest_events.py')).read()
# daily_quest_1 mappato a daily_login_claim_success.
assert '"daily_login_claim_success": "daily_quest_1"' in src
# Pack 103 canonical: daily_quest_2 mappato a tower_floor_clear_success.
assert '"tower_floor_clear_success": "daily_quest_2"' in src

# Estrai il blocco DAILY_QUEST_EVENT_ALLOWLIST e verifica che daily_quest_3 NON sia ancora attivo.
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

# Sia daily_quest_1 sia daily_quest_2 devono comparire come value attivi (post Pack 103).
assert '"daily_quest_1"' in active, 'daily_quest_1 deve essere attivo'
assert '"daily_quest_2"' in active, 'daily_quest_2 deve essere attivo (Pack 103 canonical)'
# daily_quest_3 ancora NON attivo (deferred).
assert '"daily_quest_3"' not in active, f'daily_quest_3 NON deve essere attivo: {active}'

# Source allowlist: tower_floor_clear_success solo da tower_strict_battle_execute.
# Cerchiamo il blocco includendo l'intera definizione fino al primo } di chiusura.
src_allow = re.search(
    r'DAILY_QUEST_EVENT_SOURCE_ALLOWLIST[^=]*=\s*\{([\s\S]*?)^\}',
    src, re.M
)
assert src_allow, 'source allowlist dict missing'
src_block = src_allow.group(1)
assert '"tower_strict_battle_execute"' in src_block, \
    f'source allowlist must include tower_strict_battle_execute: {src_block[:200]}'
assert '"daily_login_claim"' in src_block, \
    f'source allowlist must include daily_login_claim: {src_block[:200]}'

# Health endpoint dice REAL_COMPLETION_EVENT_READY per daily_quest_1 e _2, deferred per _3.
claim = open(os.path.join(R, 'backend/routes/daily_quest_claim.py')).read()
assert '"daily_quest_1": "REAL_COMPLETION_EVENT_READY"' in claim
# Pack 103 canonical: daily_quest_2 ora REAL via tower clear.
assert ('"daily_quest_2": "REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR"' in claim
        or '"daily_quest_2": "REAL_COMPLETION_EVENT_READY"' in claim), \
    'daily_quest_2 deve essere READY via tower clear (Pack 103 canonical)'
assert '"daily_quest_3": "COMPLETION_RUNTIME_DEFERRED"' in claim

print('[v110 PACK_100_FIRST_DAILY_QUEST_EVENT_MAPPING] OK canonical_post_pack_103 quest_1_active quest_2_real_via_tower_clear quest_3_deferred source_allowlist_enforced')
