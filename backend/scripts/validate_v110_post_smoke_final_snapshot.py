#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_post_smoke_final_snapshot_v1.json")
PRE = os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_pre_smoke_db_snapshot_v1.json")
assert os.path.isfile(P) and os.path.isfile(PRE)
d = json.load(open(P))
p = json.load(open(PRE))
assert d.get("snapshot_kind") == "post_smoke"
assert d.get("read_only") is True
assert d.get("db_writes") == 0
# Since no apply was executed, counts must match pre-snapshot exactly
for k, pre_v in p.get("counts", {}).items():
    post_v = d.get("counts", {}).get(k)
    if pre_v is None and post_v is None:
        continue
    assert pre_v == post_v, f"snapshot drift on {k}: pre={pre_v} post={post_v} (no apply executed; must match)"
print("[v110 POST_SMOKE_FINAL_SNAPSHOT] OK snapshot matches pre-snapshot (no apply executed)")
