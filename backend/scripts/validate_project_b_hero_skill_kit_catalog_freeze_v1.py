#!/usr/bin/env python3
"""
PROJECT_B Track C validator (read-only).

Verifica che:
- manifest JSON esiste con verdict atteso
- i 6 catalog baseline esistono ai paths dichiarati
- gli sha256 attuali matchano quelli registrati nel manifest (invariant)
- nessun runtime attachment / final balance numbers attivati

Exit 0 PASS / 1 FAIL.
"""
import hashlib
import json
import sys
from pathlib import Path

MANIFEST = Path("/app/data/design/hero_skill_kits/project_b_hero_skill_kit_catalog_freeze_manifest_v1.json")
CATALOG_DIR = Path("/app/data/design/hero_skill_kits")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MANIFEST.exists():
        fail(f"missing manifest: {MANIFEST}")
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_C_HERO_SKILL_KIT_CATALOG_FREEZE_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("catalog_content_modified") is not False:
        fail("catalog_content_modified must be False")

    catalogs = m.get("frozen_catalogs", [])
    if len(catalogs) < 6:
        fail(f"expected >=6 frozen catalogs, got {len(catalogs)}")

    canonical_active = [c for c in catalogs if c.get("freeze_status") == "CANONICAL_ACTIVE_BASELINE"]
    if len(canonical_active) != 1:
        fail(f"expected exactly 1 CANONICAL_ACTIVE_BASELINE catalog, got {len(canonical_active)}")
    if canonical_active[0].get("version_tag") != "rm134b_axispatch_v6":
        fail(f"canonical active baseline must be rm134b_axispatch_v6, got {canonical_active[0].get('version_tag')}")

    # Sha256 invariant check.
    for cat in catalogs:
        path = CATALOG_DIR / cat["name"]
        if not path.exists():
            fail(f"catalog file missing: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = cat.get("sha256")
        if actual != expected:
            fail(f"sha256 drift for {cat['name']}: expected {expected}, got {actual}")

    inv = m.get("invariants_to_validate", {})
    if inv.get("no_final_balance_numbers_live") is not True:
        fail("no_final_balance_numbers_live must be True")
    if inv.get("borea_activation") is not False:
        fail("borea_activation must be False")

    print(f"[PASS] PROJECT_B Track C catalog freeze OK: {len(catalogs)} catalogs frozen, sha256 invariant intact, canonical=rm134b_axispatch_v6")
    sys.exit(0)


if __name__ == "__main__":
    main()
