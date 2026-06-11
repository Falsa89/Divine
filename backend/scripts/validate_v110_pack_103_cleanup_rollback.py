#!/usr/bin/env python3
"""Pack 103 - Cleanup rollback."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend/scripts/cleanup_v110_pack_103_test_artifacts.py')
assert os.path.exists(p)
src=open(p).read()
for n in ['pack_103_test_artifact','--apply','REFUSED BY DEFAULT','TOWER_STRICT_EXECUTE_ENABLED','TOWER_FLOOR_CLAIM_ENABLED','reward_claim_ledger']:
    assert n in src, n
print('[v110 PACK_103_CLEANUP_ROLLBACK] OK')
