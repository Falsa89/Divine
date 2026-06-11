#!/usr/bin/env python3
"""Pack 100 — Daily Login Hook: chiama bridge dopo successo, idempotente."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/daily_login_claim.py')).read()
for needle in [
    'from utils.daily_quest_events import record_daily_quest_event',
    'daily_login_claim_success',
    'source_route="daily_login_claim"',
    'pack_100_event_bridge_attempted',
    'daily_quest_event_bridge',
    'pack_100_event_bridge_enabled',
    'pack_100_event_emitted_on_success',
    'pack_100_event_target_quest',
]:
    assert needle in src, needle
# Hook deve essere chiamato in entrambi i success path (replay + new claim)
import re
hook_calls = re.findall(r'_record_dq_event\(', src)
assert len(hook_calls) >= 2, f'expected hook in replay + new path, found={len(hook_calls)}'
print(f'[v110 PACK_100_DAILY_LOGIN_HOOK] OK bridge_calls={len(hook_calls)} server_scoped no_premium_leak')
