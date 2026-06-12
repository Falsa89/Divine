#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — R-03 Pack 110 validators registered."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
suite = open(os.path.join(R, 'backend/scripts/run_hero_skill_kit_validator_suite.py')).read()
REQUIRED_PACK_110_TUPLES = (
    'PROJECT-PRE-QA-110-GACHA-QUARANTINE',
    'PROJECT-PRE-QA-110-TEAM-FORMATION-QUARANTINE',
    'PROJECT-PRE-QA-110-USE-SERVER-SCOPE-ALIAS',
    'PROJECT-PRE-QA-110-AUTH-TOKEN-BRIDGE',
    'PROJECT-PRE-QA-110-MENU-CLEANUP',
    'PROJECT-PRE-QA-110-ACHIEVEMENTS-QUARANTINE',
    'PROJECT-PRE-QA-110-MUTATING-ROUTE-ALLOWLIST',
    'PROJECT-PRE-QA-110-STATIC-ANTI-LEAK-GUARD',
    'PROJECT-PRE-QA-110-DATA-INVARIANTS',
    'PROJECT-PRE-QA-110-PACK-91-109-QA-KICKOFF-PRESERVATION',
    'PROJECT-PRE-QA-110-RUNTIME-SMOKE-E2E',
    'PROJECT-PRE-QA-110-FINAL-REPORT',
    'PRE-QA-STABILIZATION-110-ROLLUP',
    'PROJECT-PRE-QA-111-ROUTE-CLASSIFICATION',
)
for t in REQUIRED_PACK_110_TUPLES:
    assert t in suite, f'suite missing tuple: {t}'
# Verify no duplicate tuple entries.
for t in REQUIRED_PACK_110_TUPLES:
    assert suite.count(f"'{t}'") == 1, f'duplicate entry for {t}'
print('[v111 PRE_QA_111_VALIDATORS_REGISTERED] OK fourteen_pack_110_111_tuples_unique no_duplicates')
