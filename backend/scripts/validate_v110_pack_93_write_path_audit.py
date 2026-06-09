#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_write_path_audit_v1.json')))
assert len(d.get('write_endpoints_audited', [])) >= 14
assert len(d.get('reward_claim_path_audited', [])) >= 6
print('[v110 PACK_93_WRITE_PATH_AUDIT] OK endpoints_audited reward_paths_audited')
