#!/usr/bin/env python3
"""
Pack 125 — Validator: report completeness.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs" / "divine"

REQUIRED_SECTIONS = [
    "Device QA 124",
    "File reali auditati",
    "Combat action loop",
    "Preview preload",
    "Home Borea",
    "QA seed",
    "server-scoped",
    "Validators",
    "No-live",
    "DB write QA authorization",
    "Device QA V5",
    "Remaining blockers",
    "Next step",
]


def main() -> int:
    errors: list[str] = []
    candidates = sorted(DOCS.glob("*PACK_125*.md"))
    if not candidates:
        errors.append("no pack 125 report .md found")
        return _emit(errors)
    report_path = candidates[-1]
    src = report_path.read_text(encoding="utf-8")
    print(f"OK    report file: {report_path.name}")
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in src.lower():
            errors.append(f"missing section: `{sec}`")
        else:
            print(f"OK    section: {sec}")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — report completeness")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_REPORT_COMPLETENESS",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_report_completeness_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  pack 125 report contains all required sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
