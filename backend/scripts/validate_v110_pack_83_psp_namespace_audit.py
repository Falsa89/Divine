#!/usr/bin/env python3
# Pack 83 - Track B: current PSP namespace audit.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
audit = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_namespace_audit_v1.json')))
assert audit.get('audit_read_only') is True
assert audit.get('audit_db_writes') == 0
assert audit.get('psp_total', 0) > 0
assert audit.get('orphan_count', -1) == 0, f'orphans found: {audit.get("orphan_count")}'
assert audit.get('duplicate_target_pairs_count', -1) == 0, f'duplicate target pairs: {audit.get("duplicate_target_pairs_count")}'
assert audit.get('missing_users_count', -1) == 0, f'missing users: {audit.get("missing_users_count")}'
total = audit.get('psp_total')
d = audit.get('direct_uuid_count', 0)
c = audit.get('objectid_compat_fallback_count', 0)
assert d + c == total, f'counts mismatch: direct+compat != total ({d}+{c} != {total})'
print(f'[v110 PACK_83_PSP_NAMESPACE_AUDIT] OK total={total} direct={d} compat={c} orphan=0 collisions=0')
