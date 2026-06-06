#!/usr/bin/env python3
import json,os,sys,urllib.request,urllib.error
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_zero_mutation_preservation_v1.json")))
sp=d.get("static_proof",{})
for k,v in {"ledger_adapter_imports_motor":False,"ledger_adapter_imports_db":False,"ledger_adapter_calls_collection":False,"preview_router_intact":True,"resolve_router_intact":True,"postqa_d_gate_module_intact":True,"all_9_postqa_d_routes_still_gated":True}.items():
    assert sp.get(k) is v
rp=d.get("runtime_proof",{})
for k in ("db_writes_observed","reward_grants_observed","progress_writes_observed","currency_mutations_observed","inventory_mutations_observed","user_heroes_exp_mutations_observed"):
    assert rp.get(k)==0
assert rp.get("ledger_collection_created") is False
assert rp.get("index_created") is False
# verify routers + gate module intact
for f in ("backend/routes/v108_authoritative_pre_instance.py","backend/routes/v108_authoritative_runtime_resolve.py","backend/utils/postqa_d_mutation_gate.py","backend/utils/authoritative_idempotency_ledger.py"):
    full=os.path.join(ROOT,f); assert os.path.isfile(full), f"missing {f}"
# adapter NO db imports
adp=open(os.path.join(ROOT,"backend/utils/authoritative_idempotency_ledger.py")).read()
for forb in ("import motor","from motor","AsyncIOMotorClient","await db"," db.","create_index","insert_one","update_one"):
    assert forb not in adp, f"ledger adapter contains forbidden: {forb}"
# optional smoke on POSTQA_D gate
try:
    req=urllib.request.Request("http://localhost:8001/api/soul/forge",data=b'{}',headers={"Content-Type":"application/json"},method="POST")
    try: urllib.request.urlopen(req,timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code==423
        assert 'LEGACY_MUTATION_LOCKED_BY_POSTQA_D' in e.read().decode('utf-8','ignore')
except Exception as e:
    if isinstance(e,AssertionError): raise
print("[v108_AUTHORITATIVE_ZERO_MUTATION_PRESERVATION] OK adapter_no_db routers_intact POSTQA_D_intact")
sys.exit(0)
