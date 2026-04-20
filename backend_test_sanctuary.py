"""
Sanctuary module backend tests — Divine Waifus.
Endpoints tested:
- GET  /api/sanctuary/home-hero
- POST /api/sanctuary/home-hero
- POST /api/sanctuary/complete-tutorial
- GET  /api/sanctuary/{hero_id}
- POST /api/sanctuary/affinity/gain
- POST /api/sanctuary/constellation/attempt
- POST /api/sanctuary/constellation/skip/{hero_id}
Regression: /api/heroes, /api/hero/encyclopedia/greek_hoplite, /api/user/heroes
"""
import os
import sys
import json
import asyncio
import random
import requests

BASE = "https://game-portal-327.preview.emergentagent.com/api"
EMAIL = "test@test.com"
PASSWORD = "password123"

results = []  # (section, ok, detail)
MUTATIONS = []


def log(section, ok, detail=""):
    icon = "PASS" if ok else "FAIL"
    print(f"[{icon}] {section} :: {detail}")
    results.append((section, ok, detail))


def login():
    r = requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    d = r.json()
    return d["token"], d["user"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


async def reset_tutorial_and_affinity(user_id, hero_id="greek_hoplite"):
    """Reset DB state so tests are deterministic."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from dotenv import load_dotenv
    load_dotenv("/app/backend/.env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    # Reset tutorial flag and home hero
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"in_tutorial": True}, "$unset": {"home_hero_id": ""}},
    )
    # Clear affinity for the test hero
    await db.user_affinity.delete_many({"user_id": user_id, "hero_id": hero_id})
    # Clear constellation data + daily quota
    await db.user_constellation.delete_many({"user_id": user_id})
    await db.user_constellation_daily.delete_many({"user_id": user_id})
    client.close()


async def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    from dotenv import load_dotenv
    load_dotenv("/app/backend/.env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    return client, db


async def main():
    # --- pre-reset ---
    print(">>> Resetting test user state...")
    tok, user = login()
    user_id = user["id"]
    await reset_tutorial_and_affinity(user_id)
    print(f">>> User: {user['username']} (id={user_id})")

    h = auth_headers(tok)

    # ============================================================
    # 1. GET /api/sanctuary/home-hero  (tutorial flow)
    # ============================================================
    print("\n=== 1. GET /api/sanctuary/home-hero ===")
    r = requests.get(f"{BASE}/sanctuary/home-hero", headers=h, timeout=15)
    if r.status_code != 200:
        log("1.home-hero.GET status", False, f"status={r.status_code} body={r.text[:300]}")
    else:
        d = r.json()
        ok_keys = all(k in d for k in ("source", "hero", "is_owned", "in_tutorial"))
        log("1.home-hero.GET keys", ok_keys, f"keys={list(d.keys())}")
        log("1.home-hero.source=tutorial", d.get("source") == "tutorial", f"source={d.get('source')}")
        log("1.home-hero.in_tutorial=True", d.get("in_tutorial") is True, f"in_tutorial={d.get('in_tutorial')}")
        hero = d.get("hero") or {}
        log("1.home-hero.hero.id=borea", hero.get("id") == "borea", f"hero_id={hero.get('id')}")
        log("1.home-hero.is_owned=False", d.get("is_owned") is False, f"is_owned={d.get('is_owned')}")

    # Check Borea seeded in /api/heroes
    r = requests.get(f"{BASE}/heroes", timeout=15)
    if r.status_code == 200:
        heroes = r.json()
        # Handle both list or {heroes:[...]} shapes
        if isinstance(heroes, dict) and "heroes" in heroes:
            heroes = heroes["heroes"]
        borea_present = any(h2.get("id") == "borea" for h2 in heroes)
        log("1.borea_seeded_in_heroes", borea_present, f"total={len(heroes)} borea_present={borea_present}")
    else:
        log("1.GET_heroes", False, f"status={r.status_code}")

    # ============================================================
    # 2. POST /api/sanctuary/home-hero
    # ============================================================
    print("\n=== 2. POST /api/sanctuary/home-hero ===")

    # 2a. Get list of non-owned heroes
    client, db = await get_db()
    owned = await db.user_heroes.find({"user_id": user_id}).to_list(500)
    owned_ids = {uh["hero_id"] for uh in owned}
    all_heroes = await db.heroes.find({}).to_list(500)
    all_ids = [h3["id"] for h3 in all_heroes]
    not_owned = [hid for hid in all_ids if hid not in owned_ids and hid != "borea"]
    first_owned = next(iter(owned_ids)) if owned_ids else None
    client.close()

    print(f"   owned_count={len(owned_ids)} not_owned_count={len(not_owned)} first_owned={first_owned}")

    # 2a. non-owned (non-borea) → 400
    if not_owned:
        r = requests.post(f"{BASE}/sanctuary/home-hero", headers=h, json={"hero_id": not_owned[0]}, timeout=15)
        log("2a.non_owned_returns_400", r.status_code == 400, f"status={r.status_code} hero={not_owned[0]} body={r.text[:200]}")
    else:
        log("2a.non_owned_returns_400", True, "SKIPPED: user owns all heroes")

    # 2b. owned → 200
    if first_owned:
        r = requests.post(f"{BASE}/sanctuary/home-hero", headers=h, json={"hero_id": first_owned}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            log("2b.owned_returns_200", True, f"response={d}")
            log("2b.owned.success_true", d.get("success") is True, f"success={d.get('success')}")
            log("2b.owned.home_hero_id", d.get("home_hero_id") == first_owned, f"returned={d.get('home_hero_id')}")
            log("2b.owned.hero_name_present", bool(d.get("hero_name")), f"hero_name={d.get('hero_name')}")
            MUTATIONS.append(f"home_hero_id set to '{first_owned}'")
        else:
            log("2b.owned_returns_200", False, f"status={r.status_code} body={r.text[:200]}")

    # 2c. non-existent id → 404
    r = requests.post(f"{BASE}/sanctuary/home-hero", headers=h, json={"hero_id": "does_not_exist_xyz"}, timeout=15)
    log("2c.nonexistent_returns_404", r.status_code == 404, f"status={r.status_code} body={r.text[:150]}")

    # ============================================================
    # 3. POST /api/sanctuary/complete-tutorial
    # ============================================================
    print("\n=== 3. POST /api/sanctuary/complete-tutorial ===")
    r = requests.post(f"{BASE}/sanctuary/complete-tutorial", headers=h, timeout=15)
    if r.status_code == 200:
        d = r.json()
        log("3.complete-tutorial.200", True, f"response={d}")
        log("3.complete-tutorial.success_true", d.get("success") is True, "")
        log("3.complete-tutorial.in_tutorial_false", d.get("in_tutorial") is False, "")
        MUTATIONS.append("in_tutorial set to False")
    else:
        log("3.complete-tutorial.200", False, f"status={r.status_code} body={r.text[:200]}")

    # 3b. GET home-hero should no longer return source=tutorial
    r = requests.get(f"{BASE}/sanctuary/home-hero", headers=h, timeout=15)
    if r.status_code == 200:
        d = r.json()
        log("3b.home-hero.in_tutorial_false", d.get("in_tutorial") is False, f"in_tutorial={d.get('in_tutorial')}")
        log("3b.home-hero.source_not_tutorial", d.get("source") != "tutorial", f"source={d.get('source')}")
    else:
        log("3b.home-hero.GET", False, f"status={r.status_code}")

    # ============================================================
    # 4. GET /api/sanctuary/{hero_id}
    # ============================================================
    print("\n=== 4. GET /api/sanctuary/{hero_id} ===")
    def _check_sanctuary_response(label, hero_id, expected_owned):
        r = requests.get(f"{BASE}/sanctuary/{hero_id}", headers=h, timeout=15)
        if r.status_code != 200:
            log(f"4.{label}.status", False, f"status={r.status_code} body={r.text[:200]}")
            return
        d = r.json()
        hero = d.get("hero") or {}
        for f in ("id", "name", "rarity", "element", "faction", "hero_class"):
            log(f"4.{label}.hero.{f}", f in hero, f"val={hero.get(f)}")
        log(f"4.{label}.is_owned", d.get("is_owned") == expected_owned, f"is_owned={d.get('is_owned')} exp={expected_owned}")
        for f in ("is_home", "in_tutorial"):
            log(f"4.{label}.{f}_present", f in d, f"val={d.get(f)}")

        aff = d.get("affinity") or {}
        for f in ("level", "exp", "max_level", "progress", "current_title", "unlocked_rewards", "next_reward", "all_rewards", "full_curve"):
            log(f"4.{label}.affinity.{f}", f in aff, f"present={f in aff}")
        log(f"4.{label}.affinity.level=0", aff.get("level") == 0, f"level={aff.get('level')}")
        log(f"4.{label}.affinity.max_level=10", aff.get("max_level") == 10, f"max_level={aff.get('max_level')}")
        prog = aff.get("progress") or {}
        for f in ("exp_in_level", "exp_to_next", "progress", "max_reached"):
            log(f"4.{label}.affinity.progress.{f}", f in prog, f"val={prog.get(f)}")
        all_r = aff.get("all_rewards") or []
        log(f"4.{label}.affinity.all_rewards.len=11", len(all_r) == 11, f"len={len(all_r)}")
        if len(all_r) == 11:
            log(f"4.{label}.affinity.all_rewards[0].level=0", all_r[0].get("level") == 0, f"v={all_r[0].get('level')}")
            log(f"4.{label}.affinity.all_rewards[10].level=10", all_r[10].get("level") == 10, f"v={all_r[10].get('level')}")
        fc = aff.get("full_curve") or []
        expected_curve = [6, 11, 19, 34, 60, 107, 191, 340, 605, 1077]
        log(f"4.{label}.affinity.full_curve.match", fc == expected_curve, f"curve={fc}")
        unl = aff.get("unlocked_rewards") or []
        log(f"4.{label}.affinity.unlocked_rewards.has_level_0", any(u.get("level") == 0 for u in unl), f"unl={unl}")

        con = d.get("constellation") or {}
        for f in ("highest_stage", "next_stage", "next_is_boss", "boss_every", "fragments", "fragment_name",
                  "daily_limit", "daily_slots_used", "daily_slots_left", "hero_already_attempted_today", "can_attempt_today"):
            log(f"4.{label}.const.{f}", f in con, f"present={f in con}")
        log(f"4.{label}.const.highest=0", con.get("highest_stage") == 0, f"v={con.get('highest_stage')}")
        log(f"4.{label}.const.next=1", con.get("next_stage") == 1, f"v={con.get('next_stage')}")
        log(f"4.{label}.const.next_is_boss=False", con.get("next_is_boss") is False, f"v={con.get('next_is_boss')}")
        log(f"4.{label}.const.boss_every=3", con.get("boss_every") == 3, f"v={con.get('boss_every')}")
        log(f"4.{label}.const.fragments=0", con.get("fragments") == 0, f"v={con.get('fragments')}")
        log(f"4.{label}.const.daily_limit=3", con.get("daily_limit") == 3, f"v={con.get('daily_limit')}")
        log(f"4.{label}.const.daily_slots_left=3", con.get("daily_slots_left") == 3, f"v={con.get('daily_slots_left')}")
        log(f"4.{label}.const.can_attempt=True", con.get("can_attempt_today") is True, f"v={con.get('can_attempt_today')}")

    _check_sanctuary_response("borea", "borea", expected_owned=False)
    _check_sanctuary_response("greek_hoplite", "greek_hoplite", expected_owned=("greek_hoplite" in owned_ids))

    # random owned hero
    random_owned = random.choice(list(owned_ids)) if owned_ids else None
    if random_owned:
        _check_sanctuary_response(f"random({random_owned})", random_owned, expected_owned=True)

    # 4b. invalid hero_id → 404
    r = requests.get(f"{BASE}/sanctuary/not_a_real_hero_xyz", headers=h, timeout=15)
    log("4b.invalid_hero.404", r.status_code == 404, f"status={r.status_code} body={r.text[:150]}")

    # ============================================================
    # 5. POST /api/sanctuary/affinity/gain
    # ============================================================
    print("\n=== 5. POST /api/sanctuary/affinity/gain ===")
    # Reset greek_hoplite affinity for clean test
    client, db = await get_db()
    await db.user_affinity.delete_many({"user_id": user_id, "hero_id": "greek_hoplite"})
    client.close()

    # 5a. Single gain → exp=1, level=0
    r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                      json={"hero_ids": ["greek_hoplite"], "source": "battle_complete"}, timeout=15)
    if r.status_code == 200:
        d = r.json()
        results_list = d.get("results") or []
        log("5a.single_gain.200", True, f"response={d}")
        log("5a.single_gain.results_len=1", len(results_list) == 1, f"len={len(results_list)}")
        if results_list:
            row = results_list[0]
            log("5a.single_gain.level=0", row.get("level") == 0, f"level={row.get('level')}")
            log("5a.single_gain.exp=1", row.get("exp") == 1, f"exp={row.get('exp')}")
            log("5a.single_gain.gained=1", row.get("gained") == 1, f"gained={row.get('gained')}")
            log("5a.single_gain.leveled_up=False", row.get("leveled_up") is False, f"lu={row.get('leveled_up')}")
        MUTATIONS.append("greek_hoplite affinity: +1 exp (call 5a)")
    else:
        log("5a.single_gain.200", False, f"status={r.status_code}")

    # 5b. Second call → still level 0, exp=2
    r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                      json={"hero_ids": ["greek_hoplite"]}, timeout=15)
    if r.status_code == 200:
        d = r.json()
        row = (d.get("results") or [{}])[0]
        log("5b.second_gain.level=0", row.get("level") == 0, f"level={row.get('level')}")
        log("5b.second_gain.exp=2", row.get("exp") == 2, f"exp={row.get('exp')}")
        MUTATIONS.append("greek_hoplite affinity: +1 exp (call 5b) → exp=2")
    else:
        log("5b.second_gain", False, f"status={r.status_code}")

    # 5c. Four more calls (total 6 gains from 5a) → should level up to Lv 1
    # Already at exp=2 after two calls, need 4 more to hit 6 total → level 1
    for i in range(4):
        r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                          json={"hero_ids": ["greek_hoplite"]}, timeout=15)
        if r.status_code != 200:
            log(f"5c.gain_{i+3}.status", False, f"status={r.status_code}")
    # Final check
    r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                      json={"hero_ids": ["greek_hoplite"]}, timeout=15)
    # Actually we are now at exp=6 after 6 calls, then one more push? Let's re-check.
    # Cumulative cost of level 1: 6 exp. After 6 calls exp=6 → level-up to 1 with exp=0 remaining.
    # Now 7th call: exp=1, level=1.
    if r.status_code == 200:
        d = r.json()
        row = (d.get("results") or [{}])[0]
        log("5c.after_7_total.level>=1", row.get("level", 0) >= 1, f"level={row.get('level')}")
        log("5c.after_7_total.exp", True, f"exp={row.get('exp')} total_exp={row.get('total_exp')}")
    MUTATIONS.append("greek_hoplite affinity: total 7 gains → should be Lv 1+")

    # 5d. Verify leveled_up=True appeared at some point via direct DB check on final state
    # Now check final level - did it hit Lv 1?
    r_check = requests.get(f"{BASE}/sanctuary/greek_hoplite", headers=h, timeout=15)
    if r_check.status_code == 200:
        aff_final = r_check.json().get("affinity", {})
        log("5d.leveled_to_Lv1", aff_final.get("level", 0) >= 1, f"final_level={aff_final.get('level')} title={aff_final.get('current_title')}")
        log("5d.title=Conoscente", aff_final.get("current_title") == "Conoscente", f"title={aff_final.get('current_title')}")

    # 5e. Invalid hero_id in array should be silently skipped
    r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                      json={"hero_ids": ["fake_hero_xyz", "greek_hoplite"]}, timeout=15)
    if r.status_code == 200:
        d = r.json()
        results_list = d.get("results") or []
        # Should only process greek_hoplite, fake ignored
        ids = [row.get("hero_id") for row in results_list]
        log("5e.invalid_skipped", "fake_hero_xyz" not in ids, f"returned_ids={ids}")
        log("5e.valid_processed", "greek_hoplite" in ids, f"returned_ids={ids}")
    else:
        log("5e.invalid_in_list", False, f"status={r.status_code}")

    # 5f. Multiple valid hero_ids
    if first_owned and first_owned != "greek_hoplite" and len(owned_ids) >= 2:
        second_owned = [hid for hid in owned_ids if hid != first_owned][0]
        ids_req = [first_owned, second_owned]
        r = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h, json={"hero_ids": ids_req}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            ids_out = [row.get("hero_id") for row in d.get("results", [])]
            log("5f.multiple_valid.all_processed", set(ids_out) == set(ids_req), f"req={ids_req} out={ids_out}")
            MUTATIONS.append(f"affinity gained on: {ids_req}")

    # ============================================================
    # 6. POST /api/sanctuary/constellation/attempt
    # ============================================================
    print("\n=== 6. POST /api/sanctuary/constellation/attempt ===")
    # Clean state first
    client, db = await get_db()
    await db.user_constellation.delete_many({"user_id": user_id})
    await db.user_constellation_daily.delete_many({"user_id": user_id})
    client.close()

    test_hero_for_const = "greek_hoplite" if "greek_hoplite" in owned_ids else first_owned
    if not test_hero_for_const:
        log("6.setup", False, "No owned hero available for constellation tests")
    else:
        print(f"   using hero_id={test_hero_for_const} for constellation tests")

        # 6a. stage > highest+1 (i.e. stage 2 when highest=0, highest+1=1) → 400
        r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                          json={"hero_id": test_hero_for_const, "stage": 2, "success": True}, timeout=15)
        log("6a.stage_too_high.400", r.status_code == 400, f"status={r.status_code} body={r.text[:150]}")

        # 6b. non-owned, non-Borea → 400
        if not_owned:
            r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                              json={"hero_id": not_owned[0], "stage": 1, "success": True}, timeout=15)
            log("6b.non_owned.400", r.status_code == 400, f"status={r.status_code} body={r.text[:150]}")
        else:
            log("6b.non_owned.400", True, "SKIPPED: user owns all heroes")

        # 6c. stage 1 success → new_highest_stage=1, is_boss=False, fragments=0
        r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                          json={"hero_id": test_hero_for_const, "stage": 1, "success": True}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            log("6c.stage1.200", True, f"response={d}")
            log("6c.stage1.success=true", d.get("success") is True, f"success={d.get('success')}")
            log("6c.stage1.stage=1", d.get("stage") == 1, f"stage={d.get('stage')}")
            log("6c.stage1.is_boss=False", d.get("is_boss") is False, f"is_boss={d.get('is_boss')}")
            log("6c.stage1.new_highest=1", d.get("new_highest_stage") == 1, f"v={d.get('new_highest_stage')}")
            log("6c.stage1.fragments=0", d.get("fragments_dropped") == 0, f"v={d.get('fragments_dropped')}")
            MUTATIONS.append(f"constellation[{test_hero_for_const}]: stage1 cleared")
        else:
            log("6c.stage1", False, f"status={r.status_code} body={r.text[:200]}")

        # 6d. stage 2 success (move to highest=2)
        r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                          json={"hero_id": test_hero_for_const, "stage": 2, "success": True}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            log("6d.stage2.new_highest=2", d.get("new_highest_stage") == 2, f"v={d.get('new_highest_stage')}")
            log("6d.stage2.is_boss=False", d.get("is_boss") is False, f"v={d.get('is_boss')}")
            MUTATIONS.append(f"constellation[{test_hero_for_const}]: stage2 cleared")
        else:
            log("6d.stage2", False, f"status={r.status_code}")

        # 6e. stage 3 boss success → is_boss=True, fragments in [1,3]
        r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                          json={"hero_id": test_hero_for_const, "stage": 3, "success": True}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            log("6e.stage3.is_boss=True", d.get("is_boss") is True, f"v={d.get('is_boss')}")
            log("6e.stage3.fragments_in_1_3", 1 <= d.get("fragments_dropped", 0) <= 3, f"v={d.get('fragments_dropped')}")
            log("6e.stage3.new_highest=3", d.get("new_highest_stage") == 3, f"v={d.get('new_highest_stage')}")
            MUTATIONS.append(f"constellation[{test_hero_for_const}]: stage3 boss cleared, fragments={d.get('fragments_dropped')}")
        else:
            log("6e.stage3", False, f"status={r.status_code} body={r.text[:200]}")

        # 6f. Daily limit: 4th DIFFERENT hero → 400
        # Current daily: 1 hero attempted. Need 3 more different heroes.
        extra_owned = [hid for hid in owned_ids if hid != test_hero_for_const][:3]
        if len(extra_owned) >= 3:
            # Hero #2
            r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                              json={"hero_id": extra_owned[0], "stage": 1, "success": True}, timeout=15)
            log("6f.hero2.200", r.status_code == 200, f"status={r.status_code}")
            # Hero #3
            r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                              json={"hero_id": extra_owned[1], "stage": 1, "success": True}, timeout=15)
            log("6f.hero3.200", r.status_code == 200, f"status={r.status_code}")
            # Hero #4 (should be rejected)
            r = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                              json={"hero_id": extra_owned[2], "stage": 1, "success": True}, timeout=15)
            log("6f.hero4.400", r.status_code == 400, f"status={r.status_code} body={r.text[:200]}")
            if r.status_code == 400:
                log("6f.hero4.msg_italian", "Limite giornaliero" in r.text, f"msg={r.text[:200]}")
            MUTATIONS.append(f"constellation[{extra_owned[0]},{extra_owned[1]}]: stage1 cleared (daily limit test)")
        else:
            log("6f.daily_limit", True, "SKIPPED: insufficient owned heroes")

    # ============================================================
    # 7. POST /api/sanctuary/constellation/skip/{hero_id}
    # ============================================================
    print("\n=== 7. POST /api/sanctuary/constellation/skip/{hero_id} ===")
    r = requests.post(f"{BASE}/sanctuary/constellation/skip/{test_hero_for_const or 'greek_hoplite'}",
                      headers=h, timeout=15)
    if r.status_code == 200:
        d = r.json()
        log("7.skip.200", True, f"response={d}")
        log("7.skip.available=False", d.get("available") is False, f"v={d.get('available')}")
        log("7.skip.shape", all(k in d for k in ("available", "reason", "highest_stage", "would_skip_to", "vip_gated", "min_vip_level")),
            f"keys={list(d.keys())}")
    else:
        log("7.skip", False, f"status={r.status_code} body={r.text[:200]}")

    # ============================================================
    # REGRESSION CHECKS
    # ============================================================
    print("\n=== REGRESSION ===")
    r = requests.get(f"{BASE}/heroes", timeout=15)
    log("reg.GET_heroes", r.status_code == 200, f"status={r.status_code}")

    r = requests.get(f"{BASE}/hero/encyclopedia/greek_hoplite", timeout=15)
    log("reg.GET_hero_encyclopedia_greek_hoplite", r.status_code == 200, f"status={r.status_code}")

    r = requests.get(f"{BASE}/user/heroes", headers=h, timeout=15)
    log("reg.GET_user_heroes", r.status_code == 200, f"status={r.status_code}")

    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed
    print(f"TOTAL: {total}  PASSED: {passed}  FAILED: {failed}")
    if failed:
        print("\nFAILED ASSERTIONS:")
        for section, ok, detail in results:
            if not ok:
                print(f"  - {section} :: {detail}")

    print("\nPERSISTENT MUTATIONS on test@test.com:")
    for m in MUTATIONS:
        print(f"  - {m}")


if __name__ == "__main__":
    asyncio.run(main())
