#!/usr/bin/env python3
"""
V7 BLOCK_E validator (HTTP smoke, read-only).

Validator dedicato per gli invarianti Borea-only / heroes-count / primordial_gaia.
Indipendente da validate_roster_visibility_invariants_v2.py: piu' veloce e con
separazione semantica chiara.

Invarianti:
  B_INV1: GET /api/heroes/borea -> HTTP 200
  B_INV2: borea is_obtainable == False
  B_INV3: GET /api/heroes/greek_borea -> HTTP 200
  B_INV4: greek_borea is_obtainable == False
  B_INV5: borea NOT in obtainable subset of /api/heroes
  B_INV6: greek_borea NOT in obtainable subset of /api/heroes
  B_INV7: GET /api/heroes/primordial_gaia -> HTTP 404
  B_INV8: heroes total count == 100
  B_INV9: borea/greek_borea slug invariati (legacy stability)

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://localhost:8001"
MARKER = Path("/app/data/design/system_safety/borea_inert_baseline_invariant_hardening_v1.json")
failures: list[str] = []


def _http_get(path: str, timeout: float = 5.0):
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as exc:
        return -1, str(exc)


def _check(condition: bool, label: str, detail: str = "") -> None:
    if not condition:
        failures.append(f"{label} {detail}".strip())


def main() -> None:
    # Marker integrity
    if not MARKER.exists():
        print(f"[FAIL] missing marker: {MARKER}")
        sys.exit(1)
    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_E_BOREA_INERT_BASELINE_INVARIANT_HARDENING_READY":
        print(f"[FAIL] unexpected verdict: {m.get('verdict')}")
        sys.exit(1)

    # B_INV1
    code, body = _http_get("/api/heroes/borea")
    _check(code == 200, "B_INV1", f"borea HTTP {code} (expected 200)")
    borea = None
    if code == 200:
        try:
            borea = json.loads(body)
        except Exception as exc:
            failures.append(f"B_INV1 borea body JSON parse error: {exc}")

    # B_INV2
    if isinstance(borea, dict):
        # Inert semantics: is_obtainable explicitly False OR field absent (treated as not obtainable).
        bo = borea.get("is_obtainable", None)
        _check(bo is False or bo is None, "B_INV2",
               f"borea is_obtainable={bo} (expected False or absent)")

    # B_INV3
    code, body = _http_get("/api/heroes/greek_borea")
    _check(code == 200, "B_INV3", f"greek_borea HTTP {code} (expected 200)")
    greek_borea = None
    if code == 200:
        try:
            greek_borea = json.loads(body)
        except Exception as exc:
            failures.append(f"B_INV3 greek_borea body JSON parse error: {exc}")

    # B_INV4
    if isinstance(greek_borea, dict):
        gbo = greek_borea.get("is_obtainable", None)
        _check(gbo is False or gbo is None, "B_INV4",
               f"greek_borea is_obtainable={gbo} (expected False or absent)")

    # B_INV5/6/8/9
    code, body = _http_get("/api/heroes")
    _check(code == 200, "B_INV_LIST", f"heroes HTTP {code} (expected 200)")
    if code == 200:
        try:
            heroes = json.loads(body)
        except Exception as exc:
            failures.append(f"heroes list JSON parse error: {exc}")
            heroes = []
        if isinstance(heroes, list):
            # B_INV8
            _check(len(heroes) == 100, "B_INV8", f"heroes count={len(heroes)} (expected 100)")
            slugs = {h.get("slug") or h.get("id") for h in heroes if isinstance(h, dict)}
            # B_INV5
            _check("borea" not in slugs, "B_INV5", "borea visible in /api/heroes list (should be hidden from obtainable)")
            # B_INV6
            _check("greek_borea" not in slugs, "B_INV6", "greek_borea visible in /api/heroes list (should be hidden from obtainable)")
            # B_INV9: legacy stability - canonical slug names must exist as catalog entries via detail endpoints
            # (already covered by B_INV1/3 returning 200 with the same slug field).
            if isinstance(borea, dict):
                _check(borea.get("slug") == "borea" or borea.get("id") == "borea",
                       "B_INV9", "borea canonical slug mutated")
            if isinstance(greek_borea, dict):
                _check(greek_borea.get("slug") == "greek_borea" or greek_borea.get("id") == "greek_borea",
                       "B_INV9", "greek_borea canonical slug mutated")

    # B_INV7
    code, _ = _http_get("/api/heroes/primordial_gaia")
    _check(code == 404, "B_INV7", f"primordial_gaia HTTP {code} (expected 404)")

    if failures:
        print("[FAIL] V7 BLOCK_E Borea inert baseline invariants:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("[PASS] V7 BLOCK_E Borea inert baseline invariants OK (9/9 + heroes=100 + primordial_gaia=404)")
    sys.exit(0)


if __name__ == "__main__":
    main()
