#!/usr/bin/env python3
"""
PROJECT_B Track H validator (read-only).

Verifica:
- artifact_system_direction_v1.json integrity + hard rules
- artifact_bible_schema_v1.json present + canonical field set + hard_invariants
- artifact_bible_launch_candidates_v1.json: 5 candidates draft, hard rules rispettati per ognuno, value_pct <= 5.0
- Nessun artefatto e' marcato 'active'
- Nessun artefatto ha is_equipment=true / occupies_gear_slot=true / is_divine_weapon=true
- Nessun artefatto ha obtainment_source='hero_summon_banner'

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

DIRECTION = Path("/app/data/design/artifacts/artifact_system_direction_v1.json")
SCHEMA = Path("/app/data/design/artifacts/artifact_bible_schema_v1.json")
CANDIDATES = Path("/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    for p in (DIRECTION, SCHEMA, CANDIDATES):
        if not p.exists():
            fail(f"missing: {p}")
    d = json.loads(DIRECTION.read_text(encoding="utf-8"))
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    c = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    if d.get("verdict") != "TRACK_H_ARTIFACT_BIBLE_V1_SCHEMA_READY":
        fail(f"unexpected direction verdict: {d.get('verdict')}")
    hard_rules = d.get("hard_rules", [])
    required_phrases = ("NOT equipment", "NOT equipped on heroes", "NOT Divine Weapons",
                        "NOT unique 6-star weapons", "global roster/account bonuses")
    for phrase in required_phrases:
        if not any(phrase in r for r in hard_rules):
            fail(f"hard_rules missing canonical phrase: {phrase}")
    if d.get("v_b_lifecycle_status") != "design_only":
        fail("v_b_lifecycle_status must be 'design_only'")

    if s.get("schema_id") != "ARTIFACT_BIBLE_V1":
        fail("schema_id must be ARTIFACT_BIBLE_V1")
    for f in ("artifact_id", "rarity", "global_roster_account_bonus",
              "is_equipment", "occupies_gear_slot", "is_divine_weapon", "status"):
        if f not in s.get("fields", {}):
            fail(f"schema missing required field: {f}")
    for inv in ("is_equipment == false", "occupies_gear_slot == false",
                "is_divine_weapon == false", "obtainment_source != 'hero_summon_banner'"):
        if inv not in s.get("hard_invariants_per_artifact", []):
            fail(f"schema missing hard invariant: {inv}")

    candidates = c.get("candidates", [])
    if c.get("status") != "draft_candidates":
        fail("candidates status must be 'draft_candidates'")
    if len(candidates) < 5:
        fail(f"expected >=5 candidates, got {len(candidates)}")
    for cand in candidates:
        for hard in ("is_equipment", "occupies_gear_slot", "is_divine_weapon"):
            if cand.get(hard) is not False:
                fail(f"candidate {cand.get('artifact_id')} {hard} must be False")
        if cand.get("status") == "active":
            fail(f"candidate {cand.get('artifact_id')} status must NOT be 'active' in v1 design")
        if cand.get("obtainment_source") == "hero_summon_banner":
            fail(f"candidate {cand.get('artifact_id')} cannot use hero_summon_banner")
        bonus = cand.get("global_roster_account_bonus", {})
        if bonus.get("value_pct", 999) > 5.0:
            fail(f"candidate {cand.get('artifact_id')} bonus value_pct > 5.0 (anti-power-creep cap violated)")
        if not cand.get("anti_power_creep_caps_applied"):
            fail(f"candidate {cand.get('artifact_id')} must declare anti_power_creep_caps_applied=true")

    print(f"[PASS] PROJECT_B Track H Artifact Bible schema OK: direction + schema + {len(candidates)} draft candidates; hard invariants enforced")
    sys.exit(0)


if __name__ == "__main__":
    main()
