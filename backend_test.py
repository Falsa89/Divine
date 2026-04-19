#!/usr/bin/env python3
"""Smoke test for Divine Waifus backend after P0 dependency/mongod restore."""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def log(status, name, detail=""):
    marker = "OK " if status else "FAIL"
    print(f"[{marker}] {name}" + (f" -- {detail}" if detail else ""))

def main():
    results = []
    token = None

    # 1. GET /docs
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=10)
        ok = r.status_code == 200
        results.append(("GET /docs", ok, f"status={r.status_code}"))
        log(ok, "GET /docs", f"status={r.status_code}")
    except Exception as e:
        results.append(("GET /docs", False, str(e)))
        log(False, "GET /docs", str(e))

    # 2. POST /api/login
    try:
        r = requests.post(f"{BASE_URL}/api/login",
                          json={"email": "test@test.com", "password": "password123"},
                          timeout=10)
        payload = r.json() if r.status_code == 200 else {}
        token = payload.get("token")
        user_id = payload.get("user", {}).get("id") if "user" in payload else None
        ok = r.status_code == 200 and bool(token) and bool(user_id)
        detail = f"status={r.status_code} token={'yes' if token else 'no'} user.id={user_id}"
        results.append(("POST /api/login", ok, detail))
        log(ok, "POST /api/login", detail)
        if not ok:
            print("Response body:", r.text[:500])
    except Exception as e:
        results.append(("POST /api/login", False, str(e)))
        log(False, "POST /api/login", str(e))

    if not token:
        print("\nCRITICAL: no token obtained. Aborting rest of smoke.")
        return results

    headers = {"Authorization": f"Bearer {token}"}

    smoke_tests = [
        ("GET /api/user/profile", "/api/user/profile", (200,),
         lambda j: (j.get("user", {}) or j).get("level", 0) >= 1 or j.get("level", 0) >= 1),
        ("GET /api/user/heroes", "/api/user/heroes", (200,),
         lambda j: isinstance(j, list) or isinstance(j.get("heroes"), list) or isinstance(j, dict)),
        ("GET /api/heroes", "/api/heroes", (200,),
         lambda j: isinstance(j, list) and len(j) > 0),
        ("GET /api/gacha/banners", "/api/gacha/banners", (200,), None),
        ("GET /api/team", "/api/team", (200,), None),
        ("GET /api/battle/skills", "/api/battle/skills", (200,), None),
        ("GET /api/tower/status", "/api/tower/status", (200,), None),
        ("GET /api/pvp/status", "/api/pvp/status", (200,), None),
        ("GET /api/events/daily", "/api/events/daily", (200,), None),
        ("GET /api/guild/info", "/api/guild/info", (200, 404), None),
        ("GET /api/story/chapters", "/api/story/chapters", (200,), None),
        ("GET /api/titles", "/api/titles", (200,), None),
    ]

    for name, path, accept_codes, validator in smoke_tests:
        try:
            r = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=15)
            ok_status = r.status_code in accept_codes
            extra = ""
            validator_ok = True
            if ok_status and r.status_code == 200 and validator is not None:
                try:
                    j = r.json()
                    validator_ok = bool(validator(j))
                    if not validator_ok:
                        extra = f" validator_failed; sample={json.dumps(j)[:200]}"
                except Exception as ve:
                    validator_ok = False
                    extra = f" json_parse_failed: {ve}"
            ok = ok_status and validator_ok
            detail = f"status={r.status_code}{extra}"
            if ok and path == "/api/heroes":
                try:
                    j = r.json()
                    names = {h.get("name") for h in j if isinstance(h, dict)}
                    want = {"Hoplite", "Athena", "Amaterasu"}
                    present = want & names
                    detail += f" count={len(j)} matched={sorted(present)}"
                    if present != want:
                        missing = want - names
                        detail += f" MISSING={sorted(missing)}"
                except Exception:
                    pass
            if ok and path == "/api/user/profile":
                try:
                    j = r.json()
                    u = j.get("user", j)
                    detail += f" user.level={u.get('level')} user.id={u.get('id')}"
                except Exception:
                    pass
            results.append((name, ok, detail))
            log(ok, name, detail)
            if not ok and r.status_code >= 500:
                print(f"   500-series body: {r.text[:500]}")
            elif not ok:
                print(f"   body: {r.text[:300]}")
        except Exception as e:
            results.append((name, False, str(e)))
            log(False, name, str(e))

    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"TOTAL: {passed}/{total} passed")
    failed = [(n, d) for n, ok, d in results if not ok]
    if failed:
        print("\nFAILED:")
        for n, d in failed:
            print(f"  - {n}: {d}")
    else:
        print("ALL PASSED -- backend ripristinato, zero regressioni")
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)
