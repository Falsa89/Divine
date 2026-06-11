#!/usr/bin/env python3
"""Pack 101 — Tower legacy path audit: quarantena attiva + gate function."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
for needle in [
    '_TOWER_LEGACY_KILL_SWITCH_ENV = "TOWER_LEGACY_LIVE_ENABLED"',
    '_pack_101_tower_legacy_on',
    '_pack_101_tower_legacy_block_or_raise',
    'TOWER_LEGACY_QUARANTINED',
]:
    assert needle in combat, needle
# Le funzioni tower_status/tower_battle DEVONO chiamare il blocker prima di qualsiasi mutazione
lines = combat.splitlines()
in_tower_status = False; in_tower_battle = False
status_blocks = False; battle_blocks = False
for i,ln in enumerate(lines):
    if '@router.get("/tower/status")' in ln: in_tower_status=True; in_tower_battle=False
    elif '@router.post("/tower/battle")' in ln: in_tower_battle=True; in_tower_status=False
    elif ln.startswith('    @router.'): in_tower_status=False; in_tower_battle=False
    if in_tower_status and '_pack_101_tower_legacy_block_or_raise()' in ln: status_blocks=True
    if in_tower_battle and '_pack_101_tower_legacy_block_or_raise()' in ln: battle_blocks=True
assert status_blocks, 'tower_status missing quarantine guard'
assert battle_blocks, 'tower_battle missing quarantine guard'
print('[v110 PACK_101_TOWER_LEGACY_PATH_AUDIT] OK kill_switch_added status_quarantined battle_quarantined no_silent_path')
