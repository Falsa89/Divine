#!/usr/bin/env python3
"""v108_POSTQA_D - Track D frontend reachability blocker validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HELPER = os.path.join(ROOT, "frontend", "utils", "postqa_d_locked_endpoints.ts")
assert os.path.isfile(HELPER), f"missing helper {HELPER}"
ht = open(HELPER).read()
for token in (
    "POSTQA_D_PUBLIC_SYNC_TAG",
    "POSTQA_D_LOCK_CODE",
    "POSTQA_D_LOCKED_ENDPOINTS",
    "isLegacyMutationLocked",
    "POSTQA_D_LOCK_MESSAGE_TITLE",
    "POSTQA_D_LOCK_MESSAGE_BODY",
    "'/api/hero/gain-exp'",
    "'/api/fusion/star-up'",
    "'/api/soul/forge'",
    "'/api/gvg/end-war'",
    "'/api/equipment/equip'",
    "'/api/friends/gift'",
    "'/api/battlepass/buy-premium'",
    "'/api/vip/add-spend'",
    "'/api/hero/levelup'",
):
    assert token in ht, f"helper missing token {token}"

SURFACES = [
    ("frontend/app/hero-detail.tsx", "/api/hero/gain-exp"),
    ("frontend/app/hero-detail.tsx", "/api/fusion/star-up"),
    ("frontend/app/soul-forge.tsx", "/api/soul/forge"),
    ("frontend/app/gvg.tsx", "/api/gvg/end-war"),
    ("frontend/app/equipment.tsx", "/api/equipment/equip"),
    ("frontend/app/friends.tsx", "/api/friends/gift"),
    ("frontend/app/battlepass.tsx", "/api/battlepass/buy-premium"),
]
for rel, ep in SURFACES:
    full = os.path.join(ROOT, rel)
    assert os.path.isfile(full), f"missing {rel}"
    txt = open(full).read()
    assert "isLegacyMutationLocked" in txt, f"isLegacyMutationLocked missing in {rel}"
    assert (f"isLegacyMutationLocked('{ep}')" in txt), f"isLegacyMutationLocked('{ep}') missing in {rel}"
    assert "POSTQA_D_LOCK_MESSAGE_TITLE" in txt, f"lock title missing in {rel}"

P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_frontend_reachability_blockers_v1.json")
d = json.load(open(P))
assert d.get("ui_redesign") is False
assert len(d.get("surfaces", [])) == 7
print("[v108_POSTQA_D FRONTEND_BLOCKER] OK surfaces=7 helper_exports=6 ui_redesign=false")
sys.exit(0)
