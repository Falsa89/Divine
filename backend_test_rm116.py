"""
RM1.16 — Roster Phase 2 Backend Validation
Tests Borea correction (5→6★), Berserker seed (new), Hoplite canonical patch.
Validates: count = 33, no orphans, idempotency on /sanctuary/home-hero,
gacha/synergies/battle no regressions.
"""
import os
import sys
import json
import re
from typing import Tuple

import requests

BASE = "https://game-portal-327.preview.emergentagent.com/api"
EMAIL = "test@test.com"
PASSWORD = "password123"

PASS_COUNT = 0
FAIL_COUNT = 0
RESULTS = []


def record(name: str, ok: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if ok:
        PASS_COUNT += 1
        prefix = "PASS"
    else:
        FAIL_COUNT += 1
        prefix = "FAIL"
    RESULTS.append({"name": name, "ok": ok, "detail": detail})
    print(f"[{prefix}] {name} {('— ' + detail) if detail else ''}")


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def login_or_register() -> Tuple[str, dict]:
    # Try login first
    r = requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data["token"], data.get("user", {})
    # Else register
    r = requests.post(
        f"{BASE}/register",
        json={"username": "testuser", "email": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    if r.status_code == 200:
        data = r.json()
        return data["token"], data.get("user", {})
    raise RuntimeError(f"Login & Register failed: {r.status_code} {r.text}")


def main():
    print("=" * 80)
    print("RM1.16 ROSTER PHASE 2 BACKEND VALIDATION")
    print(f"Target: {BASE}")
    print("=" * 80)

    # 1) Health
    r = requests.get(f"{BASE}/health", timeout=15)
    record("1. GET /api/health 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        record("1b. /health body has 'status:ok'", r.json().get("status") == "ok")

    # 2) Auth
    try:
        token, user = login_or_register()
        record("2. Auth login/register", True, f"user_id={user.get('id')}")
    except Exception as e:
        record("2. Auth login/register", False, str(e))
        return
    H = auth_headers(token)

    # 3) GET /api/heroes — count must be 33
    r = requests.get(f"{BASE}/heroes", timeout=30)
    record("3a. GET /heroes 200", r.status_code == 200)
    heroes = r.json() if r.status_code == 200 else []
    record(
        "3b. /heroes total count == 33",
        len(heroes) == 33,
        f"got {len(heroes)} heroes (expected 33)",
    )

    by_id = {h["id"]: h for h in heroes}
    # Borea
    borea = by_id.get("borea")
    record("3c. Borea (id='borea') present in /heroes", borea is not None)
    if borea:
        record("3c.1 Borea rarity == 6", borea.get("rarity") == 6, f"rarity={borea.get('rarity')}")
        record(
            "3c.2 Borea canonical_id == 'greek_borea'",
            borea.get("canonical_id") == "greek_borea",
            f"canonical_id={borea.get('canonical_id')}",
        )
        record(
            "3c.3 Borea is_extra_premium == True",
            borea.get("is_extra_premium") is True,
            f"is_extra_premium={borea.get('is_extra_premium')}",
        )
        record(
            "3c.4 Borea max_stars == 15",
            borea.get("max_stars") == 15,
            f"max_stars={borea.get('max_stars')}",
        )
        record(
            "3c.5 Borea canonical_role == 'mage_aoe'",
            borea.get("canonical_role") == "mage_aoe",
        )
        record(
            "3c.6 Borea release_group == 'launch_extra_premium'",
            borea.get("release_group") == "launch_extra_premium",
        )
        record("3c.7 Borea is_official == True", borea.get("is_official") is True)
        record("3c.8 Borea origin_group == 'anemoi'", borea.get("origin_group") == "anemoi")
        record("3c.9 Borea category == 'deity'", borea.get("category") == "deity")
        # Backward compat
        record("3c.10 Borea hero_class == 'DPS' (runtime preserved)", borea.get("hero_class") == "DPS")
        record("3c.11 Borea element == 'wind'", borea.get("element") == "wind")
        record("3c.12 Borea faction == 'greek'", borea.get("faction") == "greek")

    # Berserker
    berserker = by_id.get("norse_berserker")
    record("3d. Berserker (id='norse_berserker') present", berserker is not None)
    if berserker:
        record("3d.1 Berserker rarity == 3", berserker.get("rarity") == 3)
        record("3d.2 Berserker faction == 'norse'", berserker.get("faction") == "norse")
        record("3d.3 Berserker element == 'fire'", berserker.get("element") == "fire")
        record("3d.4 Berserker hero_class == 'DPS'", berserker.get("hero_class") == "DPS")
        record(
            "3d.5 Berserker canonical_role == 'dps_melee'",
            berserker.get("canonical_role") == "dps_melee",
        )
        record(
            "3d.6 Berserker release_group == 'launch_base'",
            berserker.get("release_group") == "launch_base",
        )
        record("3d.7 Berserker is_official == True", berserker.get("is_official") is True)
        record("3d.8 Berserker max_stars == 8", berserker.get("max_stars") == 8)
        record(
            "3d.9 Berserker canonical_id == 'norse_berserker'",
            berserker.get("canonical_id") == "norse_berserker",
        )
        record(
            "3d.10 Berserker origin_group == 'berserkers'",
            berserker.get("origin_group") == "berserkers",
        )
        record(
            "3d.11 Berserker category == 'mythic_archetype'",
            berserker.get("category") == "mythic_archetype",
        )
        record("3d.12 Berserker is_extra_premium == False", berserker.get("is_extra_premium") is False)

    # Hoplite
    hop = by_id.get("greek_hoplite")
    record("3e. Hoplite (id='greek_hoplite') present", hop is not None)
    if hop:
        record(
            "3e.1 Hoplite rarity unchanged == 3", hop.get("rarity") == 3, f"rarity={hop.get('rarity')}"
        )
        record(
            "3e.2 Hoplite element unchanged == 'earth'",
            hop.get("element") == "earth",
            f"element={hop.get('element')}",
        )
        record(
            "3e.3 Hoplite faction unchanged == 'greek'",
            hop.get("faction") == "greek",
        )
        record(
            "3e.4 Hoplite canonical_role == 'tank'",
            hop.get("canonical_role") == "tank",
        )
        record(
            "3e.5 Hoplite release_group == 'launch_base'",
            hop.get("release_group") == "launch_base",
        )
        record("3e.6 Hoplite is_official == True", hop.get("is_official") is True)
        record("3e.7 Hoplite max_stars == 8", hop.get("max_stars") == 8)
        record(
            "3e.8 Hoplite origin_group == 'phalanx'",
            hop.get("origin_group") == "phalanx",
        )
        record(
            "3e.9 Hoplite category == 'mythic_archetype'",
            hop.get("category") == "mythic_archetype",
        )
        record(
            "3e.10 Hoplite canonical_id == 'greek_hoplite'",
            hop.get("canonical_id") == "greek_hoplite",
        )

    # 4) GET /api/heroes/{hero_id} for each
    for hid in ["borea", "norse_berserker", "greek_hoplite"]:
        r = requests.get(f"{BASE}/heroes/{hid}", timeout=15)
        record(f"4. GET /heroes/{hid} 200", r.status_code == 200, f"status={r.status_code}")
        if r.status_code == 200:
            d = r.json()
            record(
                f"4.{hid} has canonical_role+max_stars+is_official keys",
                all(k in d for k in ("canonical_role", "max_stars", "is_official")),
            )

    # 5) GET /api/user/heroes — must work, no orphans for borea/greek_hoplite
    r = requests.get(f"{BASE}/user/heroes", headers=H, timeout=30)
    record("5a. GET /user/heroes 200", r.status_code == 200)
    if r.status_code == 200:
        uh = r.json()
        record("5b. /user/heroes returns list", isinstance(uh, list), f"count={len(uh) if isinstance(uh, list) else '?'}")
        # Check no items have hero_name=None (orphan signal)
        if isinstance(uh, list):
            orphans = [x for x in uh if x.get("hero_name") is None]
            record(
                "5c. /user/heroes no orphans (hero_name None)",
                len(orphans) == 0,
                f"orphans={len(orphans)}",
            )
            # Check that user_heroes pointing to borea or greek_hoplite resolve
            borea_owns = [x for x in uh if x.get("hero_id") == "borea"]
            hop_owns = [x for x in uh if x.get("hero_id") == "greek_hoplite"]
            if borea_owns:
                record(
                    "5d. user_heroes 'borea' resolves to hero record",
                    all(x.get("hero_name") for x in borea_owns),
                    f"borea_owns={len(borea_owns)}",
                )
            if hop_owns:
                record(
                    "5e. user_heroes 'greek_hoplite' resolves",
                    all(x.get("hero_name") for x in hop_owns),
                    f"hop_owns={len(hop_owns)}",
                )

    # 6) /sanctuary/home-hero — call twice for idempotency
    r1 = requests.get(f"{BASE}/sanctuary/home-hero", headers=H, timeout=30)
    record("6a. GET /sanctuary/home-hero 200 (first call)", r1.status_code == 200)
    if r1.status_code == 200:
        d = r1.json()
        record("6b. /home-hero has hero+source+is_owned+in_tutorial keys", all(k in d for k in ("hero", "source", "is_owned", "in_tutorial")))

    r_count1 = requests.get(f"{BASE}/heroes", timeout=30)
    count1 = len(r_count1.json()) if r_count1.status_code == 200 else -1

    r2 = requests.get(f"{BASE}/sanctuary/home-hero", headers=H, timeout=30)
    record("6c. GET /sanctuary/home-hero 200 (second call)", r2.status_code == 200)

    r_count2 = requests.get(f"{BASE}/heroes", timeout=30)
    count2 = len(r_count2.json()) if r_count2.status_code == 200 else -1
    record(
        "6d. Heroes count stable after twice-call (33→33)",
        count1 == 33 and count2 == 33,
        f"count1={count1}, count2={count2}",
    )

    # 7) POST /api/battle/simulate
    r = requests.post(f"{BASE}/battle/simulate", headers=H, timeout=60)
    if r.status_code == 200:
        record("7. POST /battle/simulate 200", True)
        body = r.json()
        record("7b. battle result has team_a_final or victory key", any(k in body for k in ("team_a_final", "victory", "winner", "battle_log")))
    elif r.status_code == 400:
        # Possible reason: no team configured. Try setting up team.
        detail = r.json().get("detail", "")
        record(
            "7. POST /battle/simulate (400 — checking configurable)",
            False,
            f"400 detail={detail}",
        )
    else:
        record("7. POST /battle/simulate", False, f"status={r.status_code} body={r.text[:200]}")

    # 8) POST /api/gacha/pull — verify gacha works (Berserker is in the pool for rarity=3)
    # Read gems first
    rprof = requests.get(f"{BASE}/user/profile", headers=H, timeout=15)
    gems = rprof.json().get("gems", 0) if rprof.status_code == 200 else 0
    if gems >= 100:
        rg = requests.post(f"{BASE}/gacha/pull", headers=H, json={"banner": "standard"}, timeout=30)
        record("8a. POST /gacha/pull standard 200", rg.status_code == 200, f"status={rg.status_code} body={rg.text[:200]}")
        if rg.status_code == 200:
            d = rg.json()
            record("8b. gacha returned hero with id+rarity", "hero" in d and "rarity" in d)
    else:
        record("8a. POST /gacha/pull skipped (insufficient gems)", True, f"gems={gems}")

    # Verify Berserker is queryable as 3★ via /heroes filter (sanity for gacha pool)
    r3 = requests.get(f"{BASE}/heroes", timeout=15)
    if r3.status_code == 200:
        all_h = r3.json()
        rarity3 = [h for h in all_h if h.get("rarity") == 3]
        bers_in = any(h.get("id") == "norse_berserker" for h in rarity3)
        record(
            "8c. Berserker present in rarity=3 pool (gacha eligible)",
            bers_in,
            f"rarity3 count={len(rarity3)}",
        )

    # 9) Synergy endpoints
    r = requests.get(f"{BASE}/synergies/guide", timeout=15)
    record("9a. GET /synergies/guide 200", r.status_code == 200, f"status={r.status_code}")
    r = requests.get(f"{BASE}/synergies/team", headers=H, timeout=15)
    record("9b. GET /synergies/team 200", r.status_code == 200, f"status={r.status_code}")

    # Print summary
    print()
    print("=" * 80)
    print(f"TOTAL: {PASS_COUNT + FAIL_COUNT} | PASS: {PASS_COUNT} | FAIL: {FAIL_COUNT}")
    print("=" * 80)
    if FAIL_COUNT > 0:
        print("FAILED ASSERTIONS:")
        for r in RESULTS:
            if not r["ok"]:
                print(f"  - {r['name']}: {r['detail']}")
    return FAIL_COUNT == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
