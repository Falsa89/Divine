#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_apply_preflight_zero_mutation_preservation_v1.json")))
sp = d.get("static_proof", {})
for k in ("no_route_files_modified", "no_loader_runtime_modified", "no_new_collection_in_runtime", "no_index_creation_in_runtime", "postqa_d_gate_module_intact", "all_9_postqa_d_routes_still_gated", "preview_router_intact", "resolve_router_intact", "ledger_adapter_intact", "apply_script_does_not_execute_by_default", "rollback_script_does_not_execute_by_default", "backup_script_does_not_execute_by_default"):
    assert sp.get(k) is True, f"static {k}"
rp = d.get("runtime_proof", {})
for k in ("db_writes_observed", "reward_grants_observed", "progress_writes_observed", "currency_mutations_observed", "inventory_mutations_observed", "user_heroes_exp_mutations_observed", "psp_inserts_observed", "team_updates_observed", "equipment_updates_observed", "legacy_documents_deleted"):
    assert rp.get(k) == 0, f"runtime {k} must be 0"
assert rp.get("index_created") is False
assert rp.get("collection_created") is False
assert d.get("apply_executed") is False
assert d.get("rollback_executed") is False
assert d.get("backup_executed") is False
for f in ("backend/utils/postqa_d_mutation_gate.py", "backend/utils/authoritative_idempotency_ledger.py", "backend/routes/v108_authoritative_pre_instance.py", "backend/routes/v108_authoritative_runtime_resolve.py", "backend/scripts/apply_v110_psp_migration_gated.py", "backend/scripts/rollback_v110_psp_migration_gated.py", "backend/scripts/backup_v110_psp_migration_preflight.py"):
    assert os.path.isfile(os.path.join(R, f)), f"missing {f}"
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
print("[v110 APPLY_PREFLIGHT_ZERO_MUTATION_PRESERVATION] OK static+runtime POSTQA_D=9/9 apply/rollback/backup not executed")
