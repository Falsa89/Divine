#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A=os.path.join(ROOT,"backend","utils","authoritative_idempotency_ledger.py")
assert os.path.isfile(A)
txt=open(A).read()
for tok in ("compute_request_hash","compute_result_hash","prepare_ledger_entry_dry_run","check_live_preconditions","battle_resolution_ledger","PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER","AUTHORITATIVE_LIVE_REWARD_PRECONDITIONS_NOT_MET","AUTHORITATIVE_LIVE_PROGRESS_PRECONDITIONS_NOT_MET","AUTHORITATIVE_LIVE_IDEMPOTENCY_REQUIRED","AUTHORITATIVE_LIVE_SERVER_FILTER_REQUIRED","AUTHORITATIVE_LIVE_ROLLBACK_REQUIRED"):
    assert tok in txt, f"missing token {tok}"
for forbidden in (" db.","await db","import motor","from motor","AsyncIOMotorClient","create_index","insert_one","insert_many","update_one","update_many"):
    assert forbidden not in txt, f"adapter must NOT contain {forbidden!r}"
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_idempotency_ledger_schema_v1.json")))
assert d.get("collection_created_in_this_pack") is False
assert d.get("index_created_in_this_pack") is False
assert d.get("db_writes_in_this_pack")==0
assert d.get("adapter_imports_motor") is False
# runtime dry-run smoke
import importlib.util
spec=importlib.util.spec_from_file_location("adp",A)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
entry=m.prepare_ledger_entry_dry_run(idempotency_key="k",account_id="a",server_id="s",battle_instance_id="b",mode="story",encounter_id="e",request_payload={"x":1},result_envelope={"winner":"player","turn_log":[1]})
assert entry["safety"]["dry_run"] is True and entry["safety"]["db_writes_performed"]==0
print("[v108_AUTHORITATIVE_IDEMPOTENCY_LEDGER_DRYRUN] OK adapter=safe no_db_imports schema_fields=16")
sys.exit(0)
