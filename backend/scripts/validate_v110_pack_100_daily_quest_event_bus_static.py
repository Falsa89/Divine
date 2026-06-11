#!/usr/bin/env python3
"""Pack 100 — Daily Quest Event Bus / Bridge presence + safety."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend/utils/daily_quest_events.py')
assert os.path.exists(p)
src=open(p).read()
for needle in [
    'DAILY_QUEST_EVENT_ALLOWLIST',
    'DAILY_QUEST_EVENT_SOURCE_ALLOWLIST',
    'record_daily_quest_event',
    '"daily_login_claim_success": "daily_quest_1"',
    '"daily_login_claim_success": {"daily_login_claim"}',
    'EVENT_BRIDGE_MARKER = "_slc_pack_100_event_bridge"',
    'PLAYER_SERVER_PROFILE_REQUIRED',
    'EVENT_TYPE_NOT_ALLOWLISTED',
    'SOURCE_ROUTE_NOT_ALLOWLISTED',
    'TRACKER_KILL_SWITCH_OFF',
    'INVALID_SCOPE',
    '_slc_pack_100_completion_via_event_bridge',
    'list_event_mapping',
]:
    assert needle in src, needle

# Anti-leak: rimuovi commenti/docstring e poi controlla che nessun token reward
# compaia nel codice attivo.
def strip_comments_and_docstrings(s: str) -> str:
    # Rimuovi triple-quote docstrings
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    # Rimuovi commenti inline (#...)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(src)
for forbidden in [
    'reward_claim_ledger', 'soft_currencies', 'users.gold', 'users.gems',
    'mission_coins', 'honor', 'grant_fn', 'pulls', 'tickets',
]:
    assert forbidden not in code, f'bridge code leaked reward field: {forbidden}'

print('[v110 PACK_100_DAILY_QUEST_EVENT_BUS_STATIC] OK allowlist server_scoped no_reward_grant_in_bridge_code audit_marker')
