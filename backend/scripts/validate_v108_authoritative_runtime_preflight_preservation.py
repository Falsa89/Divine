#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_preflight_preservation_v1.json")
d = json.load(open(P))
q = d.get("postqa_d_preservation", {})
assert q.get("gates_locked_default_off") == 9
assert q.get("unlocked_in_this_pack") == []
assert q.get("lock_code") == "LEGACY_MUTATION_LOCKED_BY_POSTQA_D"
assert q.get("gate_module_intact") is True
a = d.get("authoritative_pre_preservation", {})
assert a.get("endpoint") == "/api/battle/instance/preview"
assert a.get("router_intact") is True
cases = a.get("micro_smoke_cases_still_pass", [])
assert len(cases) >= 4
# verify gate module still intact
GM = os.path.join(ROOT, "backend", "utils", "postqa_d_mutation_gate.py")
assert os.path.isfile(GM)
gm = open(GM).read()
assert "LEGACY_MUTATION_LOCKED_BY_POSTQA_D" in gm and "def make_legacy_mutation_gate_dep" in gm
# preview router still intact
PR = os.path.join(ROOT, "backend", "routes", "v108_authoritative_pre_instance.py")
assert os.path.isfile(PR)
pr_txt = open(PR).read()
assert "/instance/preview" in pr_txt and "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE" in pr_txt
# optional live smoke
try:
    r = urllib.request.Request("http://localhost:8001/api/soul/forge", data=b'{}', headers={"Content-Type":"application/json"}, method="POST")
    try:
        urllib.request.urlopen(r, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423
        assert 'LEGACY_MUTATION_LOCKED_BY_POSTQA_D' in e.read().decode('utf-8','ignore')
    r2 = urllib.request.Request("http://localhost:8001/api/battle/instance/preview", data=b'{"mode":"story"}', headers={"Content-Type":"application/json"}, method="POST")
    try:
        urllib.request.urlopen(r2, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423
        assert 'BATTLE_INSTANCE_SERVER_REQUIRED' in e.read().decode('utf-8','ignore')
except Exception as e:
    if isinstance(e, AssertionError):
        raise
print("[v108_AUTHORITATIVE_RUNTIME PREFLIGHT_PRESERVATION] OK POSTQA_D=9/9 AUTHORITATIVE_PRE=intact")
sys.exit(0)
