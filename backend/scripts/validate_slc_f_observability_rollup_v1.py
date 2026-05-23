#!/usr/bin/env python3
"""
V4 BLOCK_D SLC-F observability rollup validator.

Produces a read-only consolidated rollup of SLC-F apply state:
- count of ensure_server_scope() callsites in backend/routes/*.py
- runtime files with helper import
- rollback scripts present in /app/backend/scripts/
- post-apply validators in /app/backend/scripts/
- forbidden runtime files canonical list integrity check
- suite health summary

Writes a JSON report to /app/data/design/server_lifecycle/_slc_f_observability_rollup_v1_result.json.
Read-only otherwise. Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/app")
ROUTES_DIR = ROOT / "backend/routes"
SCRIPTS_DIR = ROOT / "backend/scripts"
OUT = ROOT / "data/design/server_lifecycle/_slc_f_observability_rollup_v1_result.json"

FORBIDDEN_RUNTIME = [
    "backend/battle_engine.py",
    "backend/battle_core.py",
    "frontend/app/combat.tsx",
    "backend/routes/combat.py",
    "backend/routes/sanctuary.py",
    "backend/routes/cosmetics.py",
    "backend/routes/heroes.py",
    "backend/routes/affinity_gift_spend.py",
    "backend/routes/affinity_gifts.py",
]


def count_helper_callsites() -> int:
    n = 0
    for f in ROUTES_DIR.glob("*.py"):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        n += txt.count("ensure_server_scope(")
    return n


def files_with_helper_import() -> list[str]:
    out: list[str] = []
    for f in ROUTES_DIR.glob("*.py"):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "from utils.server_scope import ensure_server_scope" in txt:
            out.append(str(f.relative_to(ROOT)))
    return sorted(out)


def rollback_scripts() -> list[str]:
    return sorted(str(p.relative_to(ROOT)) for p in SCRIPTS_DIR.glob("rollback_*.py"))


def post_apply_validators() -> list[str]:
    out: list[str] = []
    for p in SCRIPTS_DIR.glob("validate_slc_f_*_post_apply*.py"):
        out.append(str(p.relative_to(ROOT)))
    for p in SCRIPTS_DIR.glob("validate_v2_*_scope.py"):
        out.append(str(p.relative_to(ROOT)))
    return sorted(out)


def forbidden_files_present() -> dict:
    res = {}
    for rel in FORBIDDEN_RUNTIME:
        res[rel] = (ROOT / rel).exists()
    return res


def main() -> None:
    callsites = count_helper_callsites()
    files_with_import = files_with_helper_import()
    rollbacks = rollback_scripts()
    post_apply = post_apply_validators()
    forbidden = forbidden_files_present()

    errors: list[str] = []
    if callsites < 20:
        errors.append(f"helper_callsites_low:{callsites}")
    if len(files_with_import) < 10:
        errors.append(f"files_with_helper_low:{len(files_with_import)}")
    if len(rollbacks) < 6:
        errors.append(f"rollback_scripts_low:{len(rollbacks)}")
    if len(post_apply) < 6:
        errors.append(f"post_apply_validators_low:{len(post_apply)}")
    for rel, present in forbidden.items():
        if not present:
            errors.append(f"forbidden_runtime_file_missing:{rel}")

    rollup = {
        "task_id": "V4_BLOCK_D_SLC_F_OBSERVABILITY_ROLLUP",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "verdict": "BLOCK_D_SLC_F_OBSERVABILITY_HARDENING_READY" if not errors else "BLOCK_D_FAIL",
        "metrics": {
            "ensure_server_scope_callsites": callsites,
            "runtime_files_with_helper_import": files_with_import,
            "runtime_files_with_helper_count": len(files_with_import),
            "rollback_scripts_present": rollbacks,
            "rollback_scripts_count": len(rollbacks),
            "post_apply_validators_present": post_apply,
            "post_apply_validators_count": len(post_apply),
            "forbidden_runtime_files_present": forbidden,
        },
        "errors": errors,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rollup, indent=2), encoding="utf-8")

    if errors:
        print("[FAIL] V4 BLOCK_D observability rollup:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(
        f"[PASS] V4 BLOCK_D observability rollup: callsites={callsites} files={len(files_with_import)} "
        f"rollbacks={len(rollbacks)} post_apply={len(post_apply)}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
