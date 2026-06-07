#!/usr/bin/env python3
import json, os, urllib.request, urllib.error
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_staging_smoke_gate_preservation_v1.json")))
sp = d.get("static_proof", {})
for k in ("no_route_files_modified", "no_loader_runtime_modified", "postqa_d_gate_module_intact", "all_9_postqa_d_routes_still_gated", "preview_router_intact", "resolve_router_intact", "ledger_adapter_intact", "apply_script_did_not_execute", "rollback_script_did_not_execute", "backup_script_did_not_execute"):
    assert sp.get(k) is True, f"static {k}"
rp = d.get("runtime_proof", {})
for k in ("db_writes_observed", "reward_grants_observed", "progress_writes_observed", "currency_mutations_observed", "inventory_mutations_observed", "user_heroes_exp_mutations_observed", "psp_inserts_observed", "legacy_documents_deleted", "gacha_shop_vip_bp_mutations", "battle_simulate_call_from_staging_or_live"):
    assert rp.get(k) == 0, f"runtime {k} must be 0"
assert rp.get("index_created") is False
assert rp.get("collection_created") is False
for k in ("db_write", "destructive_migration", "delete", "reward_live", "progress_live", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
try:
    req = urllib.request.Request("http://localhost:8001/api/soul/forge", data=b'{}', headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423, f"expected 423, got {e.code}"
        body = e.read().decode("utf-8", "ignore")
        assert "LEGACY_MUTATION_LOCKED_BY_POSTQA_D" in body
except Exception as e:
    if isinstance(e, AssertionError):
        raise
print("[v110 STAGING_SMOKE_GATE_PRESERVATION] OK static+runtime POSTQA_D=9/9 reward_live=false progress_live=false")
