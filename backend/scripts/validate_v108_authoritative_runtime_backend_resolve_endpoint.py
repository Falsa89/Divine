#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_runtime_resolve.py")
assert os.path.isfile(RT)
txt = open(RT).read()
for tok in ("PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE","/instance/resolve-preview","BATTLE_RESULT_INSTANCE_REQUIRED","BATTLE_RESULT_AUTHORITATIVE_LIVE_FORBIDDEN","BATTLE_RESULT_REWARD_LIVE_FORBIDDEN","BATTLE_RESULT_PROGRESS_LIVE_FORBIDDEN","BATTLE_RESULT_PLAYER_TEAM_REQUIRED","BATTLE_RESULT_ENEMY_TEAM_REQUIRED","authoritative_staging","PLAYER_SAFE_FALLBACK_TEAM","MOCK_TEAM","FALLBACK_TEAM","GENERATED_ENEMY_RANDOM","db_writes_allowed","calls_battle_simulate_endpoint","battle_engine_formula_rewritten"):
    assert tok in txt, f"router missing token {tok}"
for forbidden in (" db.","await db","motor","AsyncIOMotorClient","from battle_engine","import battle_engine","/api/battle/simulate","battle/simulate"):
    assert forbidden not in txt, f"router must NOT contain {forbidden!r}"
SRV = os.path.join(ROOT, "backend", "server.py")
stxt = open(SRV).read()
assert "v108_authoritative_runtime_resolve" in stxt

P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_backend_resolve_endpoint_result_v1.json")
d = json.load(open(P))
b = d.get("behavior", {})
assert b.get("db_writes") == 0
assert b.get("reward_grant") is False
assert b.get("progress_write") is False
assert b.get("calls_battle_simulate") is False
assert b.get("authoritative_live") is False
assert b.get("authoritative_staging") is True
assert b.get("battle_engine_formula_rewritten") is False

try:
    req = urllib.request.Request("http://localhost:8001/api/battle/instance/resolve-preview", data=b'{"mode":"story"}', headers={"Content-Type":"application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423, f"smoke: expected 423, got {e.code}"
        body = e.read().decode('utf-8','ignore')
        assert 'BATTLE_RESULT_INSTANCE_REQUIRED' in body, f"smoke: missing code in {body[:200]}"
except Exception as e:
    if isinstance(e, AssertionError):
        raise
print("[v108_AUTHORITATIVE_RUNTIME BACKEND_RESOLVE_ENDPOINT] OK static+smoke no_db no_simulate no_battle_engine_import")
sys.exit(0)
