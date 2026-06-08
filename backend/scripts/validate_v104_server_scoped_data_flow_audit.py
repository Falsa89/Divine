#!/usr/bin/env python3
"""v104 — Server-scoped data flow audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_server_scoped_data_flow_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 audit json missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
surfaces = d.get('surfaces') or []
if len(surfaces) < 10: print(f'FAIL \u2014 surfaces audited < 10 (got {len(surfaces)})'); sys.exit(1)
required_fields = {'surface', 'reads_selected_server_id', 'sends_server_id_to_backend', 'backend_filters_by_server_id', 'fallback_declared', 'risk'}
allowed_risks = {'OK', 'PARTIAL', 'NOT_SERVER_SCOPED', 'BACKEND_PENDING', 'BUG'}
for s in surfaces:
    missing = required_fields - set(s.keys())
    if missing: print(f'FAIL \u2014 surface {s.get("surface")} missing fields: {missing}'); sys.exit(1)
    if s['risk'] not in allowed_risks: print(f'FAIL \u2014 surface {s["surface"]} invalid risk {s["risk"]}'); sys.exit(1)
ui = d.get('ui_obligation') or {}
# Pack 87 \u2014 stale token rebase: the legacy banner_text_required
# 'SERVER_DATA_ISOLATION_BACKEND_PENDING' was Pack 87 explicitly removed
# (Track H: server UI copy cleanup). The current config JSON may still
# carry the legacy token for historical reference; accept either legacy
# OR the new Pack 87 honest copy descriptor.
ACCEPTED_BANNER_TOKENS = {
    'SERVER_DATA_ISOLATION_BACKEND_PENDING',   # legacy pre-Pack-87
    'PACK_87_SERVER_SCOPED_UI_COPY_HONEST',    # rebased post-Pack-87 (optional)
}
banner_required = ui.get('banner_text_required')
if banner_required not in ACCEPTED_BANNER_TOKENS:
    print('FAIL \u2014 banner_text_required not in accepted token set'); sys.exit(1)
if not ui.get('banner_present_on_servers_screen', False): print('FAIL \u2014 banner_present_on_servers_screen must be true'); sys.exit(1)
if not ui.get('no_fake_per_server_data', False): print('FAIL \u2014 no_fake_per_server_data must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_different_server_data', 'fake_production_data', 'fake_PASS', 'validator_weakening', 'db_destructive_writes'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
# Verifica servers.tsx contiene un banner honest
srv_tsx = os.path.join(ROOT, 'frontend', 'app', 'servers.tsx')
if not os.path.isfile(srv_tsx): print('FAIL \u2014 servers.tsx missing'); sys.exit(1)
with open(srv_tsx, 'r', encoding='utf-8') as f: content = f.read()
# Pack 87: accept either legacy stale token (pre-cleanup) or new Pack 87
# honest descriptor copy.
HONEST_BANNER_FRAGMENTS = ['SERVER_DATA_ISOLATION_BACKEND_PENDING', 'Pack 85-87 attivi']
if not any(t in content for t in HONEST_BANNER_FRAGMENTS):
    print('FAIL \u2014 servers.tsx must contain either legacy stale token or Pack 87 honest banner descriptor'); sys.exit(1)
print(f"PASS \u2014 v104 server-scoped data flow audit ({len(surfaces)} surfaces, banner token present \u2014 Pack 87 cleanup accepted)")
sys.exit(0)
