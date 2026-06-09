#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_route_guard_or_promotion_result_v1.json')))
assert d.get('action_taken') == 'PROMOTION_RUNTIME'
assert d.get('file_modified') == 'backend/routes/items.py'
assert d.get('route_modified') == 'GET /api/inventory'
inv = d.get('strict_invariants', {})
for k in ('server_id_optional_query_param','server_id_present_filters_strict','server_id_present_no_fallback_to_account_wide','server_id_absent_legacy_non_player_facing_path','no_db_writes','dual_read_uuid_objectid_compat','filter_applied_true_only_when_strict_path','legacy_account_inventory_used_false_in_strict_path'):
    assert inv.get(k) is True, f'invariant {k} must be true'
assert inv.get('server_id_present_psp_missing_blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert inv.get('server_id_blank_blocker') == 'SERVER_ID_REQUIRED'
# Static check sul route file
src = open(os.path.join(R, 'backend/routes/items.py')).read()
import re
# Estrai get_inventory body
m = re.search(r'async def get_inventory\([^)]*\)[^:]*:(.+?)(?=@router\.|\n    class |\n    async def )', src, re.DOTALL)
assert m, 'get_inventory not found'
body = m.group(1)
# Strict branch deve esistere e non leggere account-wide come fallback finale
assert 'if server_id:' in body
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in body
assert 'pack_89_inventory_strict_server_scope' in body
assert 'legacy_account_inventory_used' in body
assert 'inventory_source' in body
# Strict branch (server_id present): filtra per (user_id, server_id)
# Trovare la query strict
assert 'db.inventory.find' in body
assert '"user_id": user_id, "server_id":' in body or "'user_id': user_id, 'server_id':" in body
# Strict branch MUST not contain account-wide fallback (i.e., second find without server_id) — verifichiamo che dopo 'if server_id:' fino al return strict NON ci sia un fallback
# Trova split tra branch strict e legacy
strict_idx = body.find('if server_id:')
legacy_idx = body.find('# ---- Pack 89 LEGACY')
assert strict_idx > 0 and legacy_idx > strict_idx
strict_branch = body[strict_idx:legacy_idx]
# Nel branch strict, NO db.inventory.find query SENZA server_id
import re as _re
finds = _re.findall(r'db\.inventory\.find\((\{[^}]+\})', strict_branch)
for f in finds:
    assert 'server_id' in f, f'strict branch has db.inventory.find without server_id: {f}'
# NO writes (insert/update/delete) on inventory in get_inventory
for forbidden in ('db.inventory.insert','db.inventory.update','db.inventory.delete','db.inventory.replace'):
    assert forbidden not in body, f'forbidden inventory write in get_inventory: {forbidden}'
print('[v110 PACK_89_ROUTE_GUARD_OR_PROMOTION_RESULT] OK GET_inventory_strict_server_scoped no_account_wide_fallback_in_strict_branch no_db_writes_in_get_inventory')
