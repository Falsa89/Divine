#!/usr/bin/env python3
"""
Pack 124 — Validator: report completeness.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs" / "divine"

REQUIRED_SECTIONS = [
    "Device QA 123 failures",
    "Root cause",
    "Real combat preview fix",
    "QA team seed",
    "Tower crash fix",
    "Training",
    "Arena/Boss back button",
    "Home hero trace",
    "Device QA Manifest V4",
    "Validators",
    "Regression",
    "No-touch confirmation",
    "Remaining blockers",
    "Next recommended step",
]


def main() -> int:
    errors: list[str] = []
    if not DOCS.exists():
        errors.append(f"missing docs dir: {DOCS}")
        return _emit(errors)
    candidates = sorted(DOCS.glob("*PRE_QA_PACK_124*.md"))
    if not candidates:
        errors.append("no pack 124 report .md found")
        return _emit(errors)
    report_path = candidates[-1]
    src = report_path.read_text(encoding="utf-8")
    print(f"OK    report file: {report_path.name}")
    for sec in REQUIRED_SECTIONS:
        # case-insensitive substring
        if sec.lower() not in src.lower():
            errors.append(f"missing section: `{sec}`")
        else:
            print(f"OK    section present: {sec}")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — report completeness")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_REPORT_COMPLETENESS",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_report_completeness_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  pack 124 report contains all required sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
