#!/usr/bin/env python3
"""Pack 104 — Economy strict endpoints: presence + signature + safety."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()

# Endpoint registrati.
for route in ('/economy/strict/health','/economy/strict/shop/catalog','/economy/strict/shop/buy','/economy/strict/soul-forge/retire','/economy/strict/equipment/equip','/economy/strict/equipment/unequip','/economy/strict/forge/preflight'):
    assert route in src, f'route missing: {route}'

# Kill switch env names.
for ks in ('REWARD_CLAIM_LEDGER_LIVE_ENABLED','ECONOMY_STRICT_WRITES_ENABLED','SHOP_BUY_STRICT_ENABLED','SOUL_FORGE_RETIRE_STRICT_ENABLED','EQUIPMENT_STRICT_WRITES_ENABLED','FORGE_STRICT_WRITES_ENABLED'):
    assert ks in src, f'kill switch env missing: {ks}'

# Pack 104 test marker mandatory.
assert 'PACK_104_USER_TEST_MARKER' in src
assert 'pack_104_test_artifact' in src

# Idempotency token mandatory check.
assert '_validate_idempotency_token' in src
assert 'IDEMPOTENCY_TOKEN_REQUIRED' in src

# Server-side claim_key deterministico (no client trust).
assert 'shop_buy_{sid}_' in src
assert 'soul_forge_retire_{sid}_' in src
assert 'equipment_equip_{sid}_' in src
assert 'equipment_unequip_{sid}_' in src

# Forge DEFERRED (Pack 104 canonical) ovvero READY (Pack 105 canonical, dopo riconciliazione).
# Almeno uno dei due deve essere riconoscibile: o entrambi i marker DEFERRED Pack 104,
# oppure tutti i sub-path READY Pack 105.
_forge_deferred_pack_104 = ('FORGE_UPGRADE_STRICT_DEFERRED' in src
                             and 'EQUIPMENT_FUSION_STRICT_DEFERRED' in src)
_forge_ready_pack_105 = ('equipment_upgrade_strict' in src
                          and 'forge_craft_strict' in src
                          and 'equipment_fusion_strict' in src
                          and 'EQUIPMENT_UPGRADE_STRICT_ENABLED' in src)
assert _forge_deferred_pack_104 or _forge_ready_pack_105, \
    'forge strict status must be either Pack 104 DEFERRED or Pack 105 READY'

# No client price/payload trust nei BaseModel (no `price`, no `cost`, no `grant` keys).
for pyd_model in ('ShopBuyRequest','SoulForgeRetireRequest','EquipmentEquipRequest','EquipmentUnequipRequest'):
    assert f'class {pyd_model}' in src
# E nessuna chiamata a payload['price'] o payload['cost']/grant lato server (catalog server-side).
assert 'req.price' not in src, 'client price never trusted'
assert 'req.cost' not in src, 'client cost never trusted'
assert 'req.grant' not in src, 'client grant never trusted'

# Triple gate AND helper.
assert '_gate_triple(' in src

print('[v110 PACK_104_ECONOMY_ENDPOINTS] OK all_routes_present kill_switches_named test_marker_required idempotency_required server_side_claim_keys forge_deferred no_client_price_trust')
