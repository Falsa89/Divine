#!/usr/bin/env python3
"""
Pack 124 — Validator: tower device crash fix contract.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "frontend" / "app" / "tower-of-the-hells.tsx"

REQUIRED = [
    ("buildPreviewLobbyUrl", "import preview lobby builder"),
    ("if (disabled) return", "guard: locked floor non navigabile"),
    ("mode: 'tower'", "explicit mode tower"),
    ("floor_id: item.id", "floor_id propagato"),
    ("try {", "try/catch fail-closed"),
    ("__DEV__ && selectedFloor", "modal hidden in production (DEV-ONLY)"),
]


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append(f"missing: {TARGET}")
        return _emit(errors)
    src = TARGET.read_text(encoding="utf-8")
    for pat, desc in REQUIRED:
        if pat not in src:
            errors.append(f"missing `{pat}`: {desc}")
        else:
            print(f"OK    {desc}")
    # Test Clear button must NOT appear in production render path (only DEV-ONLY).
    # We check that the Modal containing 'Test Clear' is gated by __DEV__.
    if "Test Clear (TEST)" in src:
        # Acceptable only if inside __DEV__ gated Modal.
        m = re.search(r"visible=\{__DEV__\s*&&\s*selectedFloor", src)
        if not m:
            errors.append("'Test Clear (TEST)' button NOT gated behind __DEV__ Modal")
        else:
            print("OK    Test Clear button gated behind __DEV__ Modal")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — tower device crash fix contract")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_TOWER_DEVICE_CRASH_FIX",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_tower_device_crash_fix_contract_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  tower tap direct-to-lobby, modal DEV-ONLY, route safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
