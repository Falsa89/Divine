#!/usr/bin/env python3
"""Pack 105 — Endpoint signatures + safety."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()

for route in ('/economy/strict/equipment/upgrade','/economy/strict/forge/craft',
              '/economy/strict/equipment/fusion','/economy/strict/forge/catalog',
              '/economy/strict/forge/preflight'):
    assert route in src, f'route missing: {route}'

for ks in ('EQUIPMENT_UPGRADE_STRICT_ENABLED','FORGE_CRAFT_STRICT_ENABLED','EQUIPMENT_FUSION_STRICT_ENABLED'):
    assert ks in src, f'kill switch env missing: {ks}'

assert 'PACK_105_USER_TEST_MARKER' in src
assert 'pack_105_test_artifact' in src
assert '_require_pack_105_test_user' in src

for pyd_model in ('EquipmentUpgradeRequest','ForgeCraftRequest','EquipmentFusionRequest'):
    assert f'class {pyd_model}' in src

# Server-side claim_key deterministico.
assert 'equipment_upgrade_{sid}_' in src
assert 'forge_craft_{sid}_' in src
assert 'equipment_fusion_{sid}_' in src

# Client cost/recipe payload mai trustato (req.recipe_id e' OK; cost/grant/price sono forbidden)
assert 'req.cost' not in src, 'client cost never trusted'
assert 'req.grant' not in src, 'client grant never trusted'
assert 'req.price' not in src, 'client price never trusted'

# Forge preflight ora ritorna 200 (non piu' 503 DEFERRED).
assert 'FORGE_UPGRADE_STRICT_DEFERRED' not in src or '"forge_upgrade_strict": "FORGE_UPGRADE_STRICT_DEFERRED"' not in src
# Health source list contiene equipment_upgrade_strict_claim ecc.
for src_id in ('equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim'):
    assert src_id in src, f'health source missing: {src_id}'

print('[v110 PACK_105_FORGE_ENDPOINTS] OK all_routes_present kill_switches_named test_marker_required idempotency_required server_side_claim_keys preflight_ready no_client_trust')
