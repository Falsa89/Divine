"""
Sanctuary regression + new behavior test (9-stage cap)
"""
import os
import sys
import json
import requests

BASE = "https://game-portal-327.preview.emergentagent.com/api"
EMAIL = "test@test.com"
PASSWORD = "password123"

results = []


def rec(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((status, name, detail))
    print(f"[{status}] {name}{' — ' + detail if detail else ''}")


def login():
    r = requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f"Login failed: {r.status_code} {r.text}")
    token = r.json().get("access_token") or r.json().get("token")
    return token


def main():
    token = login()
    h = {"Authorization": f"Bearer {token}"}

    # ---------- GET /api/sanctuary/{hero_id} (greek_hoplite) ----------
    r = requests.get(f"{BASE}/sanctuary/greek_hoplite", headers=h, timeout=30)
    rec("GET /api/sanctuary/greek_hoplite 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        print(r.text)
        dump()
        return
    data = r.json()
    cons = data.get("constellation", {})
    rec("constellation.total_stages == 9", cons.get("total_stages") == 9, f"got={cons.get('total_stages')}")
    rec("constellation.is_complete is boolean",
        isinstance(cons.get("is_complete"), bool), f"got={type(cons.get('is_complete')).__name__}")
    highest = cons.get("highest_stage", 0)
    expected_complete = highest >= 9
    rec("constellation.is_complete matches highest>=9",
        cons.get("is_complete") == expected_complete,
        f"highest={highest} is_complete={cons.get('is_complete')}")

    # ---------- GET /api/sanctuary/borea ----------
    r = requests.get(f"{BASE}/sanctuary/borea", headers=h, timeout=30)
    rec("GET /api/sanctuary/borea 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        bd = r.json()
        bc = bd.get("constellation", {})
        rec("borea total_stages==9", bc.get("total_stages") == 9)
        rec("borea is_complete is bool", isinstance(bc.get("is_complete"), bool))

    # ---------- Promote greek_hoplite to stage 9 ----------
    attempts_made = 0
    current_highest = highest
    # If greek_hoplite is NOT yet in today's heroes_attempted, attempting it consumes 1 slot.
    # Subsequent attempts on same hero are free. So we're safe to loop.
    promote_errors = []
    while current_highest < 9 and attempts_made < 15:
        next_stage = current_highest + 1
        rr = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                           json={"hero_id": "greek_hoplite", "stage": next_stage, "success": True},
                           timeout=30)
        attempts_made += 1
        if rr.status_code != 200:
            promote_errors.append(f"stage={next_stage} status={rr.status_code} body={rr.text[:200]}")
            break
        j = rr.json()
        current_highest = j.get("new_highest_stage", current_highest)

    rec(f"Promoted greek_hoplite to stage 9 (from {highest})",
        current_highest == 9,
        f"attempts_made={attempts_made} final={current_highest} errors={promote_errors}")

    # Normal flow: attempt stages 1..9 sequentially — verified by the loop above
    # since the loop only succeeds if each intermediate stage returns 200.
    rec("Normal flow: stages 1..9 attemptable sequentially",
        len(promote_errors) == 0 and current_highest == 9,
        f"errors={promote_errors}")

    # ---------- Assert GET sanctuary now returns is_complete=true ----------
    r = requests.get(f"{BASE}/sanctuary/greek_hoplite", headers=h, timeout=30)
    cons2 = r.json().get("constellation", {})
    rec("After reaching 9 -> is_complete == True",
        cons2.get("is_complete") is True and cons2.get("highest_stage") == 9,
        f"highest={cons2.get('highest_stage')} is_complete={cons2.get('is_complete')}")

    # ---------- Attempt stage=10 → expect 400 "La costellazione ha un massimo di 9 stage" ----------
    rr = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                       json={"hero_id": "greek_hoplite", "stage": 10, "success": True}, timeout=30)
    is_400 = rr.status_code == 400
    msg = ""
    try:
        msg = rr.json().get("detail", "")
    except Exception:
        msg = rr.text
    rec("Stage=10 returns 400", is_400, f"status={rr.status_code}")
    rec("Stage=10 message == 'La costellazione ha un massimo di 9 stage'",
        msg == "La costellazione ha un massimo di 9 stage",
        f"msg='{msg}'")

    # ---------- Attempt stage=9 with highest=9 → expect 400 "Costellazione già completata" (or >max) ----------
    rr = requests.post(f"{BASE}/sanctuary/constellation/attempt", headers=h,
                       json={"hero_id": "greek_hoplite", "stage": 9, "success": True}, timeout=30)
    try:
        msg2 = rr.json().get("detail", "")
    except Exception:
        msg2 = rr.text
    rec("Stage=9 when highest=9 returns 400", rr.status_code == 400, f"status={rr.status_code}")
    acceptable = msg2 in ("Costellazione già completata",
                           "La costellazione ha un massimo di 9 stage")
    rec("Stage=9 when highest=9 matches one of expected messages",
        acceptable, f"msg='{msg2}'")

    # ---------- affinity/gain on greek_hoplite ----------
    # read baseline
    r = requests.get(f"{BASE}/sanctuary/greek_hoplite", headers=h, timeout=30)
    aff_before = r.json().get("affinity", {})
    exp_before = aff_before.get("exp", 0)
    total_before = aff_before.get("total_exp", 0)

    rr = requests.post(f"{BASE}/sanctuary/affinity/gain", headers=h,
                       json={"hero_ids": ["greek_hoplite"]}, timeout=30)
    rec("POST /sanctuary/affinity/gain 200", rr.status_code == 200, f"status={rr.status_code}")
    if rr.status_code == 200:
        rj = rr.json()
        results_list = rj.get("results", [])
        found = [x for x in results_list if x.get("hero_id") == "greek_hoplite"]
        rec("affinity/gain returned greek_hoplite result", len(found) == 1,
            f"results={results_list}")
        if found:
            g = found[0]
            rec("affinity/gain gained==1", g.get("gained") == 1, f"gained={g.get('gained')}")
            # total_exp must have incremented by 1 (unless at max)
            tot_after = g.get("total_exp", 0)
            rec("affinity total_exp incremented by 1",
                tot_after == total_before + 1 or aff_before.get("level") == 10,
                f"before={total_before} after={tot_after}")

    # ---------- Regression ----------
    r = requests.get(f"{BASE}/sanctuary/home-hero", headers=h, timeout=30)
    rec("GET /api/sanctuary/home-hero 200", r.status_code == 200, f"status={r.status_code}")

    # Try to set home hero to an owned hero. Use current home_hero_id if set, else pick first owned.
    uh_r = requests.get(f"{BASE}/user/heroes", headers=h, timeout=30)
    owned_id = None
    if uh_r.status_code == 200:
        lst = uh_r.json()
        if isinstance(lst, list) and lst:
            owned_id = lst[0].get("hero_id") or lst[0].get("id")
    if not owned_id:
        # fallback from home-hero response
        hh = r.json()
        if hh.get("is_owned") and hh.get("hero", {}).get("id"):
            owned_id = hh["hero"]["id"]
    if owned_id:
        rr = requests.post(f"{BASE}/sanctuary/home-hero", headers=h,
                           json={"hero_id": owned_id}, timeout=30)
        rec(f"POST /api/sanctuary/home-hero owned={owned_id} 200",
            rr.status_code == 200, f"status={rr.status_code} body={rr.text[:200]}")
    else:
        rec("POST /api/sanctuary/home-hero owned hero", False, "No owned hero found")

    r = requests.get(f"{BASE}/sanctuary/greek_hoplite", headers=h, timeout=30)
    rec("GET /api/sanctuary/greek_hoplite 200 (regression)", r.status_code == 200, f"status={r.status_code}")

    r = requests.get(f"{BASE}/sanctuary/borea", headers=h, timeout=30)
    rec("GET /api/sanctuary/borea 200 (regression)", r.status_code == 200, f"status={r.status_code}")

    # public /api/heroes
    r = requests.get(f"{BASE}/heroes", timeout=30)
    rec("GET /api/heroes 200 (public, no auth)", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        heroes = r.json()
        n = len(heroes) if isinstance(heroes, list) else 0
        rec("GET /api/heroes returns >=32 heroes", n >= 32, f"count={n}")
        has_borea = any((x.get("id") == "borea") for x in heroes) if isinstance(heroes, list) else False
        rec("GET /api/heroes includes borea", has_borea, f"borea_found={has_borea}")

    r = requests.get(f"{BASE}/hero/encyclopedia/greek_hoplite", timeout=30)
    rec("GET /api/hero/encyclopedia/greek_hoplite 200", r.status_code == 200, f"status={r.status_code}")

    dump()


def dump():
    print("\n" + "=" * 60)
    passed = sum(1 for s, *_ in results if s == "PASS")
    failed = sum(1 for s, *_ in results if s == "FAIL")
    print(f"TOTAL: {passed} PASS / {failed} FAIL")
    if failed:
        print("\nFAILED:")
        for s, n, d in results:
            if s == "FAIL":
                print(f"  - {n}: {d}")


if __name__ == "__main__":
    main()
