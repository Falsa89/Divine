#!/usr/bin/env python3
"""Pack 105 — Cleanup / rollback script presence."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cleanup = os.path.join(R, 'backend/scripts/cleanup_v110_pack_105_test_artifacts.py')
assert os.path.exists(cleanup), 'cleanup script missing'
src = open(cleanup).read()
assert '--apply' in src
assert 'pack_105_test_artifact' in src
assert 'reward_claim_ledger' in src
assert 'player_server_profiles' in src
assert 'user_equipment' in src
print('[v110 PACK_105_CLEANUP_ROLLBACK] OK script_present require_apply marker_filtered psp_ledger_equipment_targeted')
