#!/usr/bin/env python3
"""
Pack 124 — Validator: home hero trace JSON presence and shape.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACE = REPO_ROOT / "data" / "design" / "vertical_slice_qa" / "pack_124_home_hero_trace_v1.json"

REQUIRED_KEYS = [
    "schema_version", "pack", "track", "endpoint_used",
    "asset_fields_observed_in_code", "determinable_from_github_static_audit",
    "needs_updated_zip_or_device_screenshot", "investigative_steps_required",
    "no_touch_confirmation",
]


def main() -> int:
    errors: list[str] = []
    if not TRACE.exists():
        errors.append(f"missing: {TRACE}")
        return _emit(errors)
    data = json.loads(TRACE.read_text(encoding="utf-8"))
    for k in REQUIRED_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")
        else:
            print(f"OK    key present: {k}")
    nt = data.get("no_touch_confirmation", {})
    for nk in ("asset_files", "backend_routes", "character_bible", "heroes_master"):
        if nt.get(nk) is not False:
            errors.append(f"no_touch_confirmation.{nk} must be false (assets/back/CB/roster untouched)")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — home hero trace")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_HOME_HERO_TRACE",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_home_hero_trace_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  home hero trace JSON shape valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
