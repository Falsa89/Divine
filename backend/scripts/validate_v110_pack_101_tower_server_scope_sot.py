#!/usr/bin/env python3
"""Pack 101 — Tower Server-Scope SOT presence + content."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'docs/divine/121_TOWER_SERVER_SCOPED_PROGRESS_SOT.md')
assert os.path.exists(p), 'Tower SOT missing'
src=open(p).read()
for needle in [
    'Tower Server-Scoped Progress SOT',
    'TOWER_LEGACY_LIVE_ENABLED',
    'TOWER_STRICT_PREFLIGHT_ENABLED',
    'player_server_profiles.tower_progress',
    'REWARD_QUARANTINED_PENDING_LEDGER',
    'TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY',
    'NO tower reward live grant',
    'NO `users.gold/users.gems/users.experience`',
    'NO destructive migration',
    'release readiness claim',
    'S1/S2 Isolation',
]:
    assert needle in src, needle
print('[v110 PACK_101_TOWER_SERVER_SCOPE_SOT] OK canon_psp tower_progress kill_switches_documented reward_quarantine_documented S1_S2_isolation_documented')
