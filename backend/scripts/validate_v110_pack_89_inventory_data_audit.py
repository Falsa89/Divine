#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_inventory_data_audit_v1.json')))
assert d.get('read_only_audit') is True
assert d.get('no_db_writes_during_audit') is True
assert d.get('migration_needed_for_read_promotion') is False
assert d.get('docs_with_null_or_missing_server_id') == 0
print(f'[v110 PACK_89_INVENTORY_DATA_AUDIT] OK total_docs={d.get("total_inventory_docs")} all_with_server_id read_only no_migration_needed')
