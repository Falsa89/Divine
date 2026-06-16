#!/usr/bin/env python3
"""
Pack 125 — Validator: QA team seed applicato + server-scoped save endpoint safety.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / "backend" / "routes" / "v96_team_formation.py"
SEED = REPO_ROOT / "backend" / "scripts" / "qa_team_seed_canonical_heroes.py"
CLEAR = REPO_ROOT / "backend" / "scripts" / "qa_team_seed_clear.py"
REPORTS_DIR = REPO_ROOT / "backend" / "scripts" / "reports"


def main() -> int:
    errors: list[str] = []
    # 1. seed/clear scripts esistenti
    if not SEED.exists():
        errors.append("qa_team_seed_canonical_heroes.py missing")
    if not CLEAR.exists():
        errors.append("qa_team_seed_clear.py missing")
    # 2. Almeno un report seed deve esistere (evidence che e' stato applicato).
    # NB: escludiamo i report del validator (pattern *_safety_report.json).
    seed_reports = [p for p in REPORTS_DIR.glob("pack_124_qa_team_seed_*.json")
                    if "safety_report" not in p.name and "clear" not in p.name]
    seed_reports += [p for p in REPORTS_DIR.glob("pack_125_qa_team_seed_*.json")
                     if "safety_report" not in p.name and "clear" not in p.name]
    if not seed_reports:
        errors.append("no QA seed report found in backend/scripts/reports/ — seed not applied")
    else:
        print(f"OK    QA seed reports: {len(seed_reports)}")
        latest = sorted(seed_reports)[-1]
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            if data.get("status") != "PASS":
                errors.append(f"latest seed report status != PASS: {data.get('status')}")
            else:
                granted = data.get("granted", [])
                skipped = data.get("skipped", [])
                total = len(granted) + len(skipped)
                if total < 10:
                    errors.append(f"seed pool only {total} heroes (need >=10)")
                else:
                    print(f"OK    seed report: granted={len(granted)} skipped={len(skipped)} total={total}")
                if not data.get("account"):
                    errors.append("seed report missing account field")
                else:
                    print(f"OK    seed applied to account: {data['account']}")
        except Exception as e:
            errors.append(f"cannot parse seed report: {e}")
    # 3. v96 route deve avere save-formation endpoint con i guard.
    if not ROUTE.exists():
        errors.append("v96_team_formation.py missing")
        return _emit(errors)
    src = ROUTE.read_text(encoding="utf-8")
    required = [
        ("/save-formation", "save-formation endpoint route"),
        ("QA_TEAM_SAVE_ENABLED", "env gate"),
        ("QA_TEAM_SAVE_ALLOWLIST", "account allowlist gate"),
        ("PLAYER_SERVER_PROFILE_REQUIRED", "PSP required blocker"),
        ("OWNERSHIP_VALIDATION_FAILED", "ownership blocker"),
        ("DUPLICATE_POSITIONS", "position uniqueness blocker"),
        ("DUPLICATE_HEROES", "hero uniqueness blocker"),
        ("TEAM_TOO_LARGE", "max 6 blocker"),
        ("no_economy_mutation", "no economy mutation invariant"),
        ("no_reward", "no reward invariant"),
        ("no_progress", "no progress invariant"),
        ("no_gacha", "no gacha invariant"),
        ("no_account_wide_write", "no account-wide invariant"),
        ("player_server_profiles", "PSP write target"),
    ]
    for pat, desc in required:
        if pat not in src:
            errors.append(f"missing in route: `{pat}` ({desc})")
        else:
            print(f"OK    {desc}")
    # 4. NO write su `users` collection in save-formation branch.
    save_branch_start = src.find("async def save_formation")
    save_branch_end = src.find("return router", save_branch_start) if save_branch_start != -1 else -1
    if save_branch_start != -1 and save_branch_end != -1:
        branch = src[save_branch_start:save_branch_end]
        if "db.users.update" in branch or "db.users.insert" in branch or "db.users.replace" in branch:
            errors.append("save_formation writes to db.users (account-wide write FORBIDDEN)")
        else:
            print("OK    save_formation does NOT write to db.users")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — QA team seed + server-scoped save safety")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_TEAM_SEED_AND_SERVER_SCOPED_SAVE",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_team_seed_and_server_scoped_save_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  QA team seed applied + save-formation endpoint server-scoped safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
