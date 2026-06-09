#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_core_route_schema_audit_v1.json')))
assert len(d.get('backend_routes_audited', [])) >= 6
assert len(d.get('frontend_player_facing_callers_audited', [])) >= 9
ss = d.get('schema_status', {})
assert 'user_equipment' in ss and 'mixed' in ss['user_equipment'].lower()
assert isinstance(d.get('blocker_or_migration_needs'), list)
print('[v110 PACK_92_CORE_ROUTE_SCHEMA_AUDIT] OK backend_audited frontend_callers_audited schema_status migration_needs_documented')
