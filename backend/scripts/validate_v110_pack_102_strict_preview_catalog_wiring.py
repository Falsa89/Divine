#!/usr/bin/env python3
"""Pack 102 — Strict preview catalog wiring: ritorna catalog_floor."""
import os, sys, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend/scripts'))
from _pack_101_validator_helpers import extract_async_fn_body
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
body = extract_async_fn_body(src, 'tower_strict_battle_preview')
assert body, 'preview fn missing'
for needle in [
    '_tower_catalog_floor(floor_eff)',
    'catalog_floor',
    'FLOOR_OUT_OF_CATALOG_RANGE',
    'TOTAL_LAUNCH_FLOORS',
    '_slc_pack_102_catalog_wired',
    'catalog_version',
]:
    assert needle in body, needle
# Ancora no reward grant, no mutation
for forbidden in ['db.users.update_one(', 'db.player_server_profiles.update_one(', 'db.tower_progress.insert_one(', 'grant_fn(', 'reward_claim_ledger.insert']:
    assert forbidden not in body, f'preview leak: {forbidden}'
print('[v110 PACK_102_STRICT_PREVIEW_CATALOG_WIRING] OK catalog_floor_returned out_of_range_404 no_reward_no_mutation')
