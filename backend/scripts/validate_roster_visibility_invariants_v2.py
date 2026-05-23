#!/usr/bin/env python3
"""
V5 BLOCK_C roster visibility invariants v2 validator (extension of v1).

Read-only HTTP smoke against http://localhost:8001.
No DB writes. No runtime mutations.

Enforces 11 invariants (7 inherited from v1 + 5 new):
  - INV2_HEROES_COUNT, INV2_GAIA_404, INV2_BOREA_200_INERT, INV2_GREEK_BOREA_200_INERT,
    INV2_DRIFT_DOCS_KNOWN, INV2_CHARACTER_BIBLE_FILES_PRESENT (from v1)
  - INV2_BOREA_NOT_IN_BATTLE_PICKER (new)
  - INV2_BOREA_NOT_IN_GACHA_BANNER_POOL (new, heuristic)
  - INV2_LEGACY_PLACEHOLDERS_HIDDEN (new)
  - INV2_HERO_RARITY_DISTRIBUTION_SANE (new)
  - INV2_HERO_ELEMENT_DISTRIBUTION_SANE (new)

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://localhost:8001"
ROOT = Path("/app")
DRIFT_MARKER = ROOT / "data/design/system_safety/gacha_summon_drift_docs_housekeeping_v1.json"

errors: list[str] = []


def http_get(path: str, timeout: float = 5.0) -> tuple[int, str]:
    req = urllib.request.Request(BASE_URL + path)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        return e.code, body
    except Exception as exc:
        return -1, str(exc)


def _fetch_heroes() -> list[dict]:
    code, body = http_get("/api/heroes")
    if code != 200:
        errors.append(f"HEROES_FETCH: HTTP {code}")
        return []
    try:
        data = json.loads(body)
    except Exception as exc:
        errors.append(f"HEROES_FETCH: json decode {exc}")
        return []
    return data if isinstance(data, list) else []


def inv_heroes_count(heroes: list[dict]) -> None:
    if len(heroes) != 100:
        errors.append(f"INV2_HEROES_COUNT: expected 100, got {len(heroes)}")


def inv_gaia_404() -> None:
    code, _ = http_get("/api/heroes/primordial_gaia")
    if code != 404:
        errors.append(f"INV2_GAIA_404: expected 404, got {code}")


def _check_inert(slug: str, inv_id: str) -> None:
    code, body = http_get(f"/api/heroes/{slug}")
    if code != 200:
        errors.append(f"{inv_id}: expected 200, got {code}")
        return
    try:
        doc = json.loads(body)
    except Exception as exc:
        errors.append(f"{inv_id}: json decode {exc}")
        return
    if doc.get("is_obtainable") not in (False, 0, None):
        errors.append(f"{inv_id}: is_obtainable must be falsy")


def inv_borea_not_in_battle_picker(heroes: list[dict]) -> None:
    obtainable = [h for h in heroes if h.get("is_obtainable") is True]
    leaked = [h.get("id") for h in obtainable if h.get("id") in ("borea", "greek_borea")]
    if leaked:
        errors.append(f"INV2_BOREA_NOT_IN_BATTLE_PICKER: leaked {leaked}")


def inv_borea_not_in_gacha_pool(heroes: list[dict]) -> None:
    # Heuristic: any hero in the public roster with is_obtainable=True is in the gacha pool.
    # Borea/greek_borea must not appear there.
    inv_borea_not_in_battle_picker(heroes)  # subset check


def inv_legacy_placeholders_hidden(heroes: list[dict]) -> None:
    banned = ("PLACEHOLDER_", "TODO", "TEST_")
    leaks: list[str] = []
    for h in heroes:
        name = (h.get("name") or "").upper()
        for b in banned:
            if b in name:
                leaks.append(name)
                break
    if leaks:
        errors.append(f"INV2_LEGACY_PLACEHOLDERS_HIDDEN: leaked {leaks[:5]}")


def inv_rarity_distribution_sane(heroes: list[dict]) -> None:
    rarities = {h.get("rarity") for h in heroes if h.get("rarity") is not None}
    if len(rarities) < 4:
        errors.append(f"INV2_HERO_RARITY_DISTRIBUTION_SANE: only {len(rarities)} distinct rarity values")


def inv_element_distribution_sane(heroes: list[dict]) -> None:
    elements = {h.get("element") for h in heroes if h.get("element") is not None}
    if len(elements) < 4:
        errors.append(f"INV2_HERO_ELEMENT_DISTRIBUTION_SANE: only {len(elements)} distinct element values")


def inv_drift_marker() -> None:
    if not DRIFT_MARKER.exists():
        errors.append("INV2_DRIFT_DOCS_KNOWN: drift marker missing")
        return
    try:
        m = json.loads(DRIFT_MARKER.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"INV2_DRIFT_DOCS_KNOWN: malformed {exc}")
        return
    if m.get("housekeeping_canonical_rule", {}).get("rule_id") != "DRIFT_DOCS_GACHA_SUMMON_KNOWN_NONBLOCKING_V1":
        errors.append("INV2_DRIFT_DOCS_KNOWN: rule_id mismatch")


def inv_character_bible_files() -> None:
    for rel in ("backend/routes/sanctuary.py", "backend/routes/heroes.py"):
        if not (ROOT / rel).exists():
            errors.append(f"INV2_CHARACTER_BIBLE_FILES_PRESENT: missing {rel}")


def main() -> None:
    heroes = _fetch_heroes()
    inv_heroes_count(heroes)
    inv_gaia_404()
    _check_inert("borea", "INV2_BOREA_200_INERT")
    _check_inert("greek_borea", "INV2_GREEK_BOREA_200_INERT")
    inv_borea_not_in_battle_picker(heroes)
    inv_borea_not_in_gacha_pool(heroes)
    inv_legacy_placeholders_hidden(heroes)
    inv_rarity_distribution_sane(heroes)
    inv_element_distribution_sane(heroes)
    inv_drift_marker()
    inv_character_bible_files()

    if errors:
        print("[FAIL] V5 roster visibility invariants v2:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("[PASS] V5 roster visibility invariants v2: 11/11 holding")
    sys.exit(0)


if __name__ == "__main__":
    main()
