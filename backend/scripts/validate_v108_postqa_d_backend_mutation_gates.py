#!/usr/bin/env python3
"""v108_POSTQA_D - Track C backend mutation gates validator.
Controlla che:
- il modulo gate utility esista e definisca il LOCK_CODE atteso;
- ciascuno dei 9 endpoint chiami check_legacy_mutation_gate(...) nel file di rotta;
- nessun flag sia settato true di default in .env.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1) gate utility module
UTIL = os.path.join(ROOT, "backend", "utils", "postqa_d_mutation_gate.py")
assert os.path.isfile(UTIL), f"missing {UTIL}"
utxt = open(UTIL).read()
assert 'LEGACY_MUTATION_LOCKED_BY_POSTQA_D' in utxt
assert 'PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS' in utxt
assert 'def check_legacy_mutation_gate' in utxt
assert 'def make_legacy_mutation_gate_dep' in utxt
assert 'def _is_enabled' in utxt
assert 'status_code=423' in utxt

# 2) design json
P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_backend_mutation_gates_v1.json")
d = json.load(open(P))
assert d.get("http_status_when_locked") == 423
assert d.get("lock_code") == "LEGACY_MUTATION_LOCKED_BY_POSTQA_D"
applied = d.get("applied_endpoints", [])
assert len(applied) == 9, f"expected 9 applied endpoints, got {len(applied)}"

# 3) call sites in route files (via Depends factory nel decorator @router.post)
ROUTES = {
    ("/api/hero/gain-exp", "backend/routes/hero_progression.py", "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS"),
    ("/api/hero/levelup", "backend/routes/combat.py", "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS"),
    ("/api/fusion/star-up", "backend/routes/hero_progression.py", "DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS"),
    ("/api/soul/forge", "backend/routes/soul_forge.py", "DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS"),
    ("/api/vip/add-spend", "backend/routes/economy.py", "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS"),
    ("/api/battlepass/buy-premium", "backend/routes/economy.py", "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS"),
    ("/api/friends/gift", "backend/routes/social.py", "DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS"),
    ("/api/gvg/end-war", "backend/routes/gvg.py", "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS"),
    ("/api/equipment/equip", "backend/routes/equipment.py", "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS"),
}
for endpoint, rel, gate in ROUTES:
    full = os.path.join(ROOT, rel)
    assert os.path.isfile(full), f"missing route file {rel}"
    txt = open(full).read()
    assert 'from utils.postqa_d_mutation_gate import make_legacy_mutation_gate_dep' in txt, f"import missing in {rel}"
    pattern = re.compile(
        r'make_legacy_mutation_gate_dep\(\s*"' + re.escape(gate) + r'"\s*,\s*"' + re.escape(endpoint) + r'"\s*,?\s*\)',
        re.DOTALL,
    )
    assert pattern.search(txt), f"gate dep missing for {endpoint} in {rel}"

# 4) no flag enabled in .env
ENV = os.path.join(ROOT, "backend", ".env")
if os.path.isfile(ENV):
    et = open(ENV).read()
    for gate in (
        "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS",
    ):
        # se compare nel .env, deve essere false (vietato true di default)
        m = re.search(r'^' + re.escape(gate) + r'\s*=\s*(\S+)\s*$', et, re.MULTILINE)
        if m:
            assert m.group(1).strip().lower() not in ("true", "1", "yes", "on"), f"{gate} must not be enabled in .env"

print("[v108_POSTQA_D BACKEND_GATES] OK applied=9 default_off lock_code=LEGACY_MUTATION_LOCKED_BY_POSTQA_D")
sys.exit(0)
