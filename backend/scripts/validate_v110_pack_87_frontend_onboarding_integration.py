#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_frontend_onboarding_integration_v1.json')))
assert d.get('frontend_file_modified') == 'frontend/app/servers.tsx'
assert d.get('bearer_required') is True
assert d.get('no_global_fallback_on_failure') is True
assert d.get('explicit_server_id') is True
assert d.get('idempotent_via_backend_marker') is True
seq = d.get('sequence', [])
assert any('/api/psp/ensure' in s for s in seq), 'sequence must include /api/psp/ensure'
assert any('/api/psp/starter/claim' in s for s in seq), 'sequence must include /api/psp/starter/claim'
assert any('router.replace' in s for s in seq)
# Static check sul file frontend
src = open(os.path.join(R, 'frontend/app/servers.tsx')).read()
assert '/api/psp/starter/claim' in src, 'servers.tsx must call /api/psp/starter/claim'
assert 'X-Pack-87-Frontend-Starter-Claim' in src, 'servers.tsx must mark Pack 87 frontend starter claim header'
assert 'pack87_starter_claim_last_mode' in src, 'servers.tsx must persist pack87_starter_claim_last_mode'
assert 'pack87_starter_user_hero_ids' in src, 'servers.tsx must persist pack87_starter_user_hero_ids'
# Ordine: ensure -> starter claim in onEnter
ensure_idx = src.find('/api/psp/ensure')
claim_idx = src.find('/api/psp/starter/claim')
assert ensure_idx > 0 and claim_idx > ensure_idx, 'starter claim must come AFTER ensure in onEnter'
print('[v110 PACK_87_FRONTEND_ONBOARDING_INTEGRATION] OK servers_tsx_calls_starter_claim_after_ensure bearer_required no_global_fallback persisted_async_storage_keys')
