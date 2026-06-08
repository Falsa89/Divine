#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
r = d.get('idempotency_rerun', {})
assert r.get('planned_writes_count') == 1690
assert r.get('actual_writes_count') == 0, f'idempotent rerun must write 0; got {r.get("actual_writes_count")}'
assert r.get('skipped_idempotent_count') == 1690
assert r.get('refused_no_match_count') == 0
assert r.get('verdict', '').startswith('IDEMPOTENT_RERUN')
print(f"[v110 PACK_84_IDEMPOTENCY_RERUN] OK actual=0 skipped=1690 verdict=IDEMPOTENT_RERUN_NO_WRITES")
