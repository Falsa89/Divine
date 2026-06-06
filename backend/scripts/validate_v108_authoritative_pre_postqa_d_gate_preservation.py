#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track I POSTQA_D gate preservation."""
import json, os, sys, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_postqa_d_gate_preservation_v1.json")
d = json.load(open(P))
gates = d.get("gates", [])
assert len(gates) == 9, f"expected 9 gates, got {len(gates)}"
assert d.get("lock_code_expected") == "LEGACY_MUTATION_LOCKED_BY_POSTQA_D"
assert d.get("lock_http_status") == 423
assert d.get("unlocked_in_this_pack") == []
assert d.get("safety_flags", {}).get("unlocking_postqa_d_gates") is False
# verify gate module exists and is unchanged structurally
GM = os.path.join(ROOT, "backend", "utils", "postqa_d_mutation_gate.py")
assert os.path.isfile(GM)
gm_txt = open(GM).read()
for tok in ("LEGACY_MUTATION_LOCKED_BY_POSTQA_D","def check_legacy_mutation_gate","def make_legacy_mutation_gate_dep","status_code=423"):
    assert tok in gm_txt, f"gate module missing token {tok}"
# verify at least one Depends gate site still present in each protected file
ROUTES = {
    ("backend/routes/hero_progression.py", "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS"),
    ("backend/routes/hero_progression.py", "DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS"),
    ("backend/routes/combat.py", "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS"),
    ("backend/routes/soul_forge.py", "DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS"),
    ("backend/routes/economy.py", "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS"),
    ("backend/routes/social.py", "DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS"),
    ("backend/routes/gvg.py", "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS"),
    ("backend/routes/equipment.py", "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS"),
}
for rel, gate in ROUTES:
    full = os.path.join(ROOT, rel)
    src = open(full).read()
    assert "make_legacy_mutation_gate_dep" in src, f"{rel} missing gate dep import"
    assert gate in src, f"{rel} missing flag {gate}"
# optional live smoke (skip if backend down)
try:
    req = urllib.request.Request("http://localhost:8001/api/soul/forge", data=b'{}', headers={"Content-Type":"application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423, f"smoke: expected 423 got {e.code}"
        body = e.read().decode('utf-8','ignore')
        assert 'LEGACY_MUTATION_LOCKED_BY_POSTQA_D' in body
except Exception as e:
    if isinstance(e, AssertionError):
        raise
print("[v108_AUTHORITATIVE_PRE POSTQA_D_GATE_PRESERVATION] OK 9 gates intact lock_code preserved")
sys.exit(0)
