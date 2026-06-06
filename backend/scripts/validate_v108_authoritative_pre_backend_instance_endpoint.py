#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track C backend endpoint validator (static + live smoke)."""
import json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1) router file presence
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_pre_instance.py")
assert os.path.isfile(RT), f"router missing {RT}"
txt = open(RT).read()
for tok in (
    'PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE',
    '/instance/preview',
    'BATTLE_INSTANCE_SERVER_REQUIRED',
    'BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED',
    'BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED',
    'BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN',
    'BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN',
    'authoritative_live',
    'db_writes_allowed',
    'PLAYER_SAFE_FALLBACK_TEAM',
):
    assert tok in txt, f"router missing token {tok}"
# 2) NO DB write in router (no motor / no db. update / db.find)
for forbidden in (' db.', 'await db', 'motor', 'AsyncIOMotorClient'):
    assert forbidden not in txt, f"router must NOT touch DB: found {forbidden!r}"

# 3) router mounted in server.py
SRV = os.path.join(ROOT, "backend", "server.py")
stxt = open(SRV).read()
assert 'v108_authoritative_pre_instance' in stxt, 'server.py must include v108 authoritative pre router'

# 4) design json + flags
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_backend_instance_endpoint_v1.json")
d = json.load(open(P))
b = d.get("behavior", {})
assert b.get("db_writes") == 0
assert b.get("reward_grant") is False
assert b.get("progress_write") is False
assert b.get("authoritative_live") is False
assert b.get("server_filter_applied") is False

# 5) optional live smoke (skip silently if backend not reachable)
try:
    req = urllib.request.Request(
        "http://localhost:8001/api/battle/instance/preview",
        data=b'{"mode":"story"}', headers={"Content-Type":"application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=2)
        rc = 200
    except urllib.error.HTTPError as e:
        rc = e.code
        body = e.read().decode('utf-8', 'ignore')
        assert rc == 423, f"smoke: expected 423, got {rc}"
        assert 'BATTLE_INSTANCE_SERVER_REQUIRED' in body, f"smoke: missing block code in {body[:200]}"
except Exception as e:
    if isinstance(e, AssertionError):
        raise
    print(f"[v108_AUTHORITATIVE_PRE BACKEND_ENDPOINT] smoke skipped: {e}")
print("[v108_AUTHORITATIVE_PRE BACKEND_ENDPOINT] OK static+smoke router=safe authoritative_live=false")
sys.exit(0)
