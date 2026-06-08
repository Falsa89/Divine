#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
pre = d.get('pre_write_snapshot', {})
assert pre.get('psp_total') == 1690
assert pre.get('direct_uuid_count') == 0
assert pre.get('objectid_compat_fallback_count') == 1690
assert pre.get('orphan_count') == 0
assert pre.get('duplicate_target_pairs') == 0
print(f"[v110 PACK_84_PRE_WRITE_SNAPSHOT] OK total={pre['psp_total']} direct=0 compat=1690 orphan=0")
