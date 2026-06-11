#!/usr/bin/env python3
"""Pack 104 — Cleanup / rollback procedure documented + script present."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cleanup = os.path.join(R, 'backend/scripts/cleanup_v110_pack_104_test_artifacts.py')
assert os.path.exists(cleanup), 'cleanup script missing'
src = open(cleanup).read()
assert '--apply' in src, 'cleanup must require --apply flag for destructive ops'
assert 'pack_104_test_artifact' in src
assert 'reward_claim_ledger' in src
assert 'player_server_profiles' in src
print('[v110 PACK_104_CLEANUP_ROLLBACK] OK script_present require_apply marker_filtered ledger_psp_targeted')
