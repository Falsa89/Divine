"""Test GET /api/hero/encyclopedia/{hero_id} (public endpoint) + regression."""
import requests
import json
import sys

BASE = "https://game-portal-327.preview.emergentagent.com/api"

MAX_STARS_BY_BASE = {1: 6, 2: 8, 3: 10, 4: 12, 5: 14, 6: 15}
STAR_LEVEL_CAPS = {
    1: 30, 2: 50, 3: 70, 4: 90, 5: 110,
    6: 130, 7: 150, 8: 170, 9: 190, 10: 210,
    11: 230, 12: 260, 13: 290, 14: 320, 15: 350,
}

results = {"passed": [], "failed": []}
hero_report = []


def record_pass(msg):
    results["passed"].append(msg)
    print(f"  OK   {msg}")


def record_fail(msg):
    results["failed"].append(msg)
    print(f"  FAIL {msg}")


def test_all_heroes_encyclopedia():
    print("\n=== 1) Encyclopedia for every hero ===")
    r = requests.get(f"{BASE}/heroes")
    assert r.status_code == 200, f"/api/heroes returned {r.status_code}"
    heroes = r.json()
    if isinstance(heroes, dict) and "heroes" in heroes:
        heroes = heroes["heroes"]
    print(f"Heroes count: {len(heroes)}")
    if len(heroes) != 31:
        record_fail(f"Expected 31 heroes, got {len(heroes)}")
    else:
        record_pass("31 heroes present")

    base_stars_ok = 0
    max_stars_ok = 0
    max_level_ok = 0
    hp_scaling_ok = 0
    base_active1_ok = 0
    ult_enhanced_ok = 0  # for rarity>=6
    star_bonus_ok = 0    # for rarity>=6
    total_rar6 = 0
    errors = []

    for hero in heroes:
        hid = hero.get("id")
        hname = hero.get("name")
        rarity = hero.get("rarity", 1)
        report = {"id": hid, "name": hname, "rarity": rarity, "errors": []}

        rr = requests.get(f"{BASE}/hero/encyclopedia/{hid}")
        if rr.status_code != 200:
            report["errors"].append(f"status {rr.status_code}")
            errors.append(f"{hname}({hid}): status {rr.status_code}")
            hero_report.append(report)
            continue
        data = rr.json()

        base = data.get("base", {})
        mx = data.get("max", {})

        # base.level == 1 and base.stars == rarity
        if base.get("level") != 1:
            report["errors"].append(f"base.level={base.get('level')}")
        if base.get("stars") != rarity:
            report["errors"].append(f"base.stars={base.get('stars')} vs rarity={rarity}")
        else:
            base_stars_ok += 1

        expected_max_stars = MAX_STARS_BY_BASE[rarity]
        if mx.get("stars") != expected_max_stars:
            report["errors"].append(f"max.stars={mx.get('stars')} expected {expected_max_stars}")
        else:
            max_stars_ok += 1

        expected_max_level = min(100, STAR_LEVEL_CAPS[expected_max_stars])
        if mx.get("level") != expected_max_level:
            report["errors"].append(f"max.level={mx.get('level')} expected {expected_max_level}")
        else:
            max_level_ok += 1

        b_hp = base.get("stats", {}).get("hp")
        m_hp = mx.get("stats", {}).get("hp")
        if b_hp is not None and m_hp is not None and m_hp > b_hp:
            hp_scaling_ok += 1
        else:
            report["errors"].append(f"HP scaling not valid (base={b_hp}, max={m_hp})")

        if base.get("skills", {}).get("active_1"):
            base_active1_ok += 1
        else:
            report["errors"].append("base.skills.active_1 missing")

        if rarity >= 6:
            total_rar6 += 1
            ult = mx.get("skills", {}).get("ultimate")
            if ult and "damage_mult" in ult and ult.get("enhanced") is True:
                ult_enhanced_ok += 1
            else:
                report["errors"].append(
                    f"max.skills.ultimate missing/not enhanced (got={ult})"
                )
            sb = mx.get("skills", {}).get("star_bonus")
            if sb and sb.get("name") == "Forma Trascendente":
                star_bonus_ok += 1
            else:
                report["errors"].append(
                    f"max.skills.star_bonus not Forma Trascendente (got={sb})"
                )

        hero_report.append(report)

    total = len(heroes)
    print("\n--- Per-hero summary ---")
    print(f"base.level==1 + base.stars==rarity : {base_stars_ok}/{total}")
    print(f"max.stars correct               : {max_stars_ok}/{total}")
    print(f"max.level correct               : {max_level_ok}/{total}")
    print(f"max.stats.hp > base.stats.hp    : {hp_scaling_ok}/{total}")
    print(f"base.skills.active_1 present    : {base_active1_ok}/{total}")
    print(f"[rarity>=6] max ultimate enh    : {ult_enhanced_ok}/{total_rar6}")
    print(f"[rarity>=6] star_bonus name OK  : {star_bonus_ok}/{total_rar6}")

    if base_stars_ok == total: record_pass(f"All {total} base.stars==rarity")
    else: record_fail(f"base.stars mismatch in {total - base_stars_ok} heroes")
    if max_stars_ok == total: record_pass("All max.stars match MAX_STARS_BY_BASE")
    else: record_fail(f"max.stars mismatch in {total - max_stars_ok} heroes")
    if max_level_ok == total: record_pass("All max.level == min(100, cap)")
    else: record_fail(f"max.level wrong in {total - max_level_ok} heroes")
    if hp_scaling_ok == total: record_pass("HP scaling > base for all heroes")
    else: record_fail(f"HP scaling wrong in {total - hp_scaling_ok} heroes")
    if base_active1_ok == total: record_pass("base.skills.active_1 present on all heroes")
    else: record_fail(f"base.active_1 missing in {total - base_active1_ok} heroes")
    if total_rar6 > 0:
        if ult_enhanced_ok == total_rar6: record_pass(f"Ultimate enhanced on all {total_rar6} rarity>=6 heroes")
        else: record_fail(f"Ultimate enhanced wrong in {total_rar6 - ult_enhanced_ok}/{total_rar6}")
        if star_bonus_ok == total_rar6: record_pass(f"Forma Trascendente set on all {total_rar6} rarity>=6 heroes")
        else: record_fail(f"star_bonus wrong in {total_rar6 - star_bonus_ok}/{total_rar6}")

    # Highlight problematic heroes
    problems = [h for h in hero_report if h["errors"]]
    if problems:
        print("\n--- Heroes with issues ---")
        for h in problems:
            print(f"  {h['name']} ({h['id']}) rarity={h['rarity']}: {h['errors']}")


def test_404():
    print("\n=== 2) 404 for nonexistent id ===")
    r = requests.get(f"{BASE}/hero/encyclopedia/nonexistent-id")
    if r.status_code != 404:
        record_fail(f"Expected 404, got {r.status_code}")
        return
    try:
        detail = r.json().get("detail")
    except Exception:
        detail = None
    if detail == "Eroe non trovato":
        record_pass("404 with detail 'Eroe non trovato'")
    else:
        record_fail(f"Detail mismatch: {detail}")


def test_public_no_auth():
    print("\n=== 3) Public endpoint (no auth) ===")
    r = requests.get(f"{BASE}/heroes")
    heroes = r.json()
    if isinstance(heroes, dict) and "heroes" in heroes:
        heroes = heroes["heroes"]
    hid = heroes[0]["id"]
    # Explicitly no Authorization header
    r2 = requests.get(f"{BASE}/hero/encyclopedia/{hid}", headers={})
    if r2.status_code == 200:
        record_pass("GET /hero/encyclopedia/{id} returns 200 without Authorization header")
    else:
        record_fail(f"Public access returned {r2.status_code}")


def test_hoplite_focus():
    print("\n=== 4) Focus on greek_hoplite ===")
    r = requests.get(f"{BASE}/hero/encyclopedia/greek_hoplite")
    if r.status_code != 200:
        record_fail(f"greek_hoplite status {r.status_code}")
        return
    data = r.json()
    base = data.get("base", {})
    mx = data.get("max", {})
    bs = base.get("skills", {})
    ms = mx.get("skills", {})

    checks = [
        (data.get("rarity") == 3, f"rarity == 3 (got {data.get('rarity')})"),
        (base.get("stars") == 3, f"base.stars == 3 (got {base.get('stars')})"),
        (mx.get("stars") == 10, f"max.stars == 10 (got {mx.get('stars')})"),
        (mx.get("level") == 100, f"max.level == 100 (got {mx.get('level')})"),
        (mx.get("level_cap") == 210, f"max.level_cap == 210 (got {mx.get('level_cap')})"),
        (bs.get("active_1") is not None, f"base.active_1 exists (got {bs.get('active_1')})"),
        (bs.get("active_1", {}).get("name") == "Pugno di Terra",
         f"base.active_1.name == 'Pugno di Terra' (got {bs.get('active_1', {}).get('name')})"),
        (bs.get("active_2") is None, f"base.active_2 is None (got {bs.get('active_2')})"),
        (ms.get("active_2") is not None, f"max.active_2 exists (got {ms.get('active_2')})"),
        (ms.get("active_2", {}).get("name") == "Terremoto",
         f"max.active_2.name == 'Terremoto' (got {ms.get('active_2', {}).get('name')})"),
        (ms.get("active_1", {}).get("enhanced") is True,
         f"max.active_1.enhanced == True (got {ms.get('active_1', {}).get('enhanced')})"),
        (ms.get("passive_3") is not None and ms.get("passive_3", {}).get("name") == "Aura Trascendente",
         f"max.passive_3 is Aura Trascendente (got {ms.get('passive_3')})"),
        (ms.get("ultimate") is not None,
         f"max.ultimate exists since rarity param=max_stars=10>=6 (got {ms.get('ultimate')})"),
    ]

    if ms.get("ultimate"):
        print(f"  Hoplite max ult name: {ms['ultimate'].get('name')} mult={ms['ultimate'].get('damage_mult')}")

    for ok, msg in checks:
        if ok:
            record_pass(f"[hoplite] {msg}")
        else:
            record_fail(f"[hoplite] {msg}")


def test_regression():
    print("\n=== 5) Regression on /heroes, /user/heroes, /hero/full-detail ===")
    r = requests.get(f"{BASE}/heroes")
    if r.status_code == 200:
        record_pass("/api/heroes returns 200")
    else:
        record_fail(f"/api/heroes returned {r.status_code}")

    # login
    login = requests.post(f"{BASE}/login", json={"email": "test@test.com", "password": "password123"})
    if login.status_code != 200:
        record_fail(f"login failed status={login.status_code} body={login.text[:200]}")
        return
    token = login.json().get("token") or login.json().get("access_token")
    if not token:
        record_fail(f"login response missing token: {login.json()}")
        return
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{BASE}/user/heroes", headers=headers)
    if r.status_code == 200:
        uhs = r.json()
        if isinstance(uhs, dict) and "heroes" in uhs:
            uhs = uhs["heroes"]
        record_pass(f"/api/user/heroes returns 200 with {len(uhs)} user_heroes")
    else:
        record_fail(f"/api/user/heroes returned {r.status_code}")
        return

    if uhs:
        uhid = uhs[0].get("id") or uhs[0].get("user_hero_id")
        r = requests.get(f"{BASE}/hero/full-detail/{uhid}", headers=headers)
        if r.status_code == 200:
            detail = r.json()
            req_keys = {"hero_id", "user_hero_id", "name", "stars", "level", "skills"}
            missing = req_keys - set(detail.keys())
            if not missing:
                record_pass("/api/hero/full-detail returns 200 with expected keys")
            else:
                record_fail(f"/api/hero/full-detail missing keys: {missing}")
        else:
            record_fail(f"/api/hero/full-detail returned {r.status_code}")


if __name__ == "__main__":
    try:
        test_all_heroes_encyclopedia()
        test_404()
        test_public_no_auth()
        test_hoplite_focus()
        test_regression()
    except Exception as e:
        print(f"\nFATAL: {e}")
        import traceback
        traceback.print_exc()

    print("\n\n============ FINAL SUMMARY ============")
    print(f"PASSED: {len(results['passed'])}")
    for p in results["passed"]:
        print(f"  + {p}")
    print(f"FAILED: {len(results['failed'])}")
    for f in results["failed"]:
        print(f"  - {f}")
    sys.exit(0 if not results["failed"] else 1)
