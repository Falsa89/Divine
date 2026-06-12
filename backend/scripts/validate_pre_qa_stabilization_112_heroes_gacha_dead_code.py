#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — heroes.py duplicated gacha dead-code validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
h = open(os.path.join(R, 'backend/routes/heroes.py')).read()
assert 'GACHA_DUPLICATE_DEAD_CODE_QUARANTINED' in h
assert h.count('GACHA_DUPLICATE_DEAD_CODE_QUARANTINED') >= 2, 'must quarantine both pull and pull10'
# Legacy mutation functions must be moved to dead-code helpers (NOT inline in route).
assert '_legacy_gacha_pull_dead_code' in h
assert '_legacy_gacha_pull_10_dead_code' in h
# Active route handlers must raise 423 immediately (no gems spend).
# Check that the literal '$inc' on gems appears ONLY in the dead-code helpers.
# Simple heuristic: route handlers should be tiny (start with raise HTTPException).
import re
m = re.search(r"@router\.post\(\"/gacha/pull\"\)\s+async def gacha_pull[^:]*:[^\n]*\n(.*?)(?=@router\.post|@router\.get|async def _legacy)", h, re.DOTALL)
assert m is not None, 'cannot locate gacha_pull handler body'
body = m.group(1)
assert 'GACHA_DUPLICATE_DEAD_CODE_QUARANTINED' in body, 'gacha_pull handler must raise 423'
assert '$inc' not in body, 'gacha_pull handler must NOT contain $inc (must be moved to dead-code)'
print('[v112 PRE_QA_112_HEROES_GACHA_DEAD_CODE] OK dead_code_helpers_only_quarantine_guard_active')
