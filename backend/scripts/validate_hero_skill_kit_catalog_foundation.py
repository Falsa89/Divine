#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path("/app")
if not ROOT.exists():
    # allow local validation from extracted pack root
    ROOT = Path.cwd()

BASE = ROOT / "data" / "design" / "hero_skill_kits"

REQ = BASE / "hero_skill_kit_catalog_requirements_v1.json"
SCHEMA = BASE / "hero_skill_kit_schema_v1.json"
FIVE = BASE / "hero_skill_kits_5star_manifest_v1.json"
SIX = BASE / "hero_skill_kits_6star_borea_v1.json"

def load(path):
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def assert_false(obj, key, context):
    if obj.get(key) is not False:
        raise AssertionError(f"{context}: expected {key}=false")

def validate_unique(entries, label):
    ids = [e.get("hero_id") for e in entries]
    if any(not x for x in ids):
        raise AssertionError(f"{label}: missing hero_id")
    if len(ids) != len(set(ids)):
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        raise AssertionError(f"{label}: duplicate hero_id {dupes}")
    return ids

def main():
    req = load(REQ)
    schema = load(SCHEMA)
    five = load(FIVE)
    six = load(SIX)

    for name, obj in [("schema", schema), ("5star", five), ("6star", six)]:
        assert_false(obj, "runtime_attached", name)
        assert_false(obj, "balance_values_finalized", name)

    expected_prog = {
        "1": ["basic"],
        "2": ["basic", "passive_base"],
        "3": ["basic", "passive_base", "skill_1"],
        "4": ["basic", "passive_base", "skill_1", "passive_advanced"],
        "5": ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2"],
        "6": ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2", "ultimate"],
    }
    if schema.get("skill_slot_progression") != expected_prog:
        raise AssertionError("schema skill_slot_progression mismatch")
    if req.get("skill_slot_progression_required") != expected_prog:
        raise AssertionError("requirements skill_slot_progression_required mismatch")

    five_entries = five.get("entries", [])
    six_entries = six.get("entries", [])
    if len(five_entries) != 20:
        raise AssertionError(f"expected 20 5★ entries, got {len(five_entries)}")
    if len(six_entries) != 13:
        raise AssertionError(f"expected 13 6★ entries, got {len(six_entries)}")

    validate_unique(five_entries, "5star entries")
    six_ids = validate_unique(six_entries, "6star entries")

    if "greek_borea" not in six_ids:
        raise AssertionError("missing greek_borea in 6star catalog")

    allowed_elements = set(schema.get("allowed_elements", []))
    if allowed_elements != {"water", "fire", "earth", "wind", "lightning", "light", "dark"}:
        raise AssertionError("allowed_elements mismatch")

    for e in five_entries:
        if e.get("native_rarity") != 5:
            raise AssertionError(f"{e.get('hero_id')}: expected native_rarity 5")
        if e.get("release_group") != "launch_base":
            raise AssertionError(f"{e.get('hero_id')}: 5★ release_group must be launch_base")
        assert_false(e, "runtime_attached", e.get("hero_id"))
        assert_false(e, "balance_values_finalized", e.get("hero_id"))
        if e.get("expected_slots") != expected_prog["5"]:
            raise AssertionError(f"{e.get('hero_id')}: wrong expected_slots")
        if set(e.get("skill_package", {}).keys()) != set(expected_prog["5"]):
            raise AssertionError(f"{e.get('hero_id')}: 5★ skill_package slots mismatch")
        if e.get("element") not in allowed_elements:
            raise AssertionError(f"{e.get('hero_id')}: invalid element {e.get('element')}")

    launch_base_count = 0
    extra_count = 0
    for e in six_entries:
        hid = e.get("hero_id")
        if e.get("native_rarity") != 6:
            raise AssertionError(f"{hid}: expected native_rarity 6")
        assert_false(e, "runtime_attached", hid)
        assert_false(e, "balance_values_finalized", hid)
        if e.get("expected_slots") != expected_prog["6"]:
            raise AssertionError(f"{hid}: wrong expected_slots")
        if set(e.get("skill_package", {}).keys()) != set(expected_prog["6"]):
            raise AssertionError(f"{hid}: 6★ skill_package slots mismatch")
        if not e.get("divine_weapon_id") or not e.get("divine_weapon_name"):
            raise AssertionError(f"{hid}: missing divine weapon")
        if e.get("element") not in allowed_elements:
            raise AssertionError(f"{hid}: invalid element {e.get('element')}")
        if hid == "greek_borea":
            if e.get("release_group") != "launch_extra_premium":
                raise AssertionError("greek_borea must be launch_extra_premium")
            extra_count += 1
        else:
            if e.get("release_group") != "launch_base":
                raise AssertionError(f"{hid}: 6★ non-Borea must be launch_base")
            launch_base_count += 1
        for slot, sk in e.get("skill_package", {}).items():
            if sk.get("slot") != slot:
                raise AssertionError(f"{hid}/{slot}: slot field mismatch")
            if sk.get("design_status") != "approved_direction":
                raise AssertionError(f"{hid}/{slot}: design_status must be approved_direction")
            # Pack 115G — Skill foundation semantic truth:
            # `final_numbers` puo' essere non-null SOLO se chiaramente marcato
            # come foundation_draft preview-only e NON runtime-ready/live/final.
            fn = sk.get("final_numbers")
            if fn is not None:
                if not isinstance(fn, dict):
                    raise AssertionError(
                        f"{hid}/{slot}: final_numbers must be null or a dict envelope, "
                        f"not {type(fn).__name__}"
                    )
                status_val = fn.get("status")
                if status_val != "foundation_draft":
                    raise AssertionError(
                        f"{hid}/{slot}: final_numbers.status must be 'foundation_draft', "
                        f"got {status_val!r}"
                    )
                if fn.get("runtime_ready") is not False:
                    raise AssertionError(
                        f"{hid}/{slot}: final_numbers.runtime_ready must be explicitly False, "
                        f"got {fn.get('runtime_ready')!r}"
                    )
                # Vietato qualunque flag che dichiari runtime/live/final/finalized.
                forbidden_live_flags = (
                    "runtime",
                    "runtime_attached",
                    "battle_runtime_attached",
                    "live",
                    "is_live",
                    "final",
                    "is_final",
                    "finalized",
                    "balance_finalized",
                    "balance_values_finalized",
                )
                for flag in forbidden_live_flags:
                    if fn.get(flag) is True:
                        raise AssertionError(
                            f"{hid}/{slot}: final_numbers must not declare {flag}=True"
                        )
                # Anche string-valued flags devono non dichiarare semantica live.
                status_forbidden = {"runtime", "live", "final", "finalized", "ready"}
                if isinstance(status_val, str) and status_val.lower() in status_forbidden:
                    raise AssertionError(
                        f"{hid}/{slot}: final_numbers.status non puo' essere "
                        f"{status_val!r} in fase foundation"
                    )

    if launch_base_count != 12:
        raise AssertionError(f"expected 12 launch_base 6★ entries, got {launch_base_count}")
    if extra_count != 1:
        raise AssertionError(f"expected 1 extra premium 6★ entry, got {extra_count}")

    print("PASS: RM1.26-A hero skill kit catalog foundation validated")
    print(f"- 5★ launch_base entries: {len(five_entries)}")
    print(f"- 6★ launch_base entries: {launch_base_count}")
    print(f"- 6★ extra premium entries: {extra_count}")
    print(f"- total 6★ catalog entries: {len(six_entries)}")
    print(f"- skill slot progression: ok")
    print(f"- runtime_attached: false")
    print(f"- balance_values_finalized: false")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
