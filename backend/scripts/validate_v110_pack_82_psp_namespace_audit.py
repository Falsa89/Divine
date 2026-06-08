#!/usr/bin/env python3
# Pack 82 - Track 4: PSP namespace audit (verifica gli artefatti dell'audit READ-ONLY).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
a = d.get('psp_namespace_audit_results', {})
assert a.get('audit_script_read_only') is True
assert a.get('audit_db_writes') == 0
assert a.get('psp_total', 0) > 0
assert a.get('orphan_count', -1) == 0, f'orphan PSPs found: {a.get("orphan_count")}'
# direct_uuid + objectid_compat == total (no orphan)
direct = a.get('direct_uuid_count', 0)
compat = a.get('objectid_compat_fallback_count', 0)
assert direct + compat == a.get('psp_total'), f'count mismatch: direct+compat != total ({direct}+{compat} != {a.get("psp_total")})'
print(f'[v110 PACK_82_PSP_NAMESPACE_AUDIT] OK total={a.get("psp_total")} direct={direct} compat={compat} orphan=0 read_only=true')
