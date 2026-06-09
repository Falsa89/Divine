#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_inventory_route_schema_audit_v1.json')))
routes = d.get('inventory_routes', [])
assert any(r.get('path')=='GET /api/inventory' for r in routes)
sch = d.get('inventory_collection_schema', {})
assert sch.get('migration_needed_for_read_promotion') is False
assert d.get('read_promotion_safe_now') is True
print('[v110 PACK_89_INVENTORY_ROUTE_SCHEMA_AUDIT] OK GET_inventory_identified schema_already_server_scoped read_promotion_safe')
