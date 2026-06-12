#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cleanup = os.path.join(R, 'backend/scripts/cleanup_v110_pack_107_test_artifacts.py')
assert os.path.exists(cleanup)
src = open(cleanup).read()
assert '--apply' in src and 'pack_107_test_artifact' in src
print('[v110 PACK_107_CLEANUP_ROLLBACK] OK script_present require_apply marker_filtered')
