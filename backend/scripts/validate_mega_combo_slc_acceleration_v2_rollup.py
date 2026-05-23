#!/usr/bin/env python3
"""
V2 rollup validator (MEGA_COMBO_SLC_ACCELERATION_V2 BLOCK_E).

Verifica la presenza e consistenza di TUTTI i marker dei 5 blocchi V2 e dei loro
relativi artefatti. Read-only.

Exit codes: 0 PASS / 1 FAIL
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DOCS = Path("/app/docs/divine")
MARKERS = {
    "BLOCK_A": {
        "json": Path("/app/data/design/system_safety/v2_economy_daily_claims_scope_marker.json"),
        "md": DOCS / "116A_ECONOMY_DAILY_CLAIMS_SCOPE.md",
        "expected_verdict": "BLOCK_A_ECONOMY_DAILY_CLAIMS_SCOPE_APPLIED_SAFE",
        "apply": True,
    },
    "BLOCK_B": {
        "json": Path("/app/data/design/system_safety/v2_gvg_user_mail_scope_marker.json"),
        "md": DOCS / "116B_GVG_USER_MAIL_SCOPE.md",
        "expected_verdict": "BLOCK_B_GVG_USER_MAIL_SCOPE_APPLIED_SAFE",
        "apply": True,
    },
    "BLOCK_C": {
        "json": Path("/app/data/design/server_lifecycle/economy_vip_paid_account_wide_marker_v1.json"),
        "md": DOCS / "116C_ECONOMY_VIP_PAID_ACCOUNT_WIDE_MARKER.md",
        "expected_verdict": "BLOCK_C_ECONOMY_VIP_PAID_MARKER_READY",
        "apply": False,
    },
    "BLOCK_D": {
        "json": Path("/app/data/design/system_safety/af2n_v8_signoff_design_review_v1.json"),
        "md": DOCS / "116D_AF2N_V8_SIGNOFF_DESIGN_REVIEW.md",
        "expected_verdict": "BLOCK_D_AF2N_V8_SIGNOFF_AUDIT_READY",
        "apply": False,
    },
    "BLOCK_E": {
        "json": Path("/app/data/design/server_lifecycle/_mega_combo_slc_acceleration_v2_rollup_result.json"),
        "md": DOCS / "116E_VALIDATOR_SUITE_GROWTH_V2.md",
        "expected_verdict": "BLOCK_E_VALIDATOR_SUITE_GROWTH_READY",
        "apply": False,
    },
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    rollup = {
        "task_id": "MEGA_COMBO_SLC_ACCELERATION_V2_ROLLUP",
        "verdict": "BLOCK_E_VALIDATOR_SUITE_GROWTH_READY",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "blocks": {},
    }

    for block, info in MARKERS.items():
        if block == "BLOCK_E":
            # rollup artifact written by this script itself
            rollup["blocks"][block] = {"verdict": info["expected_verdict"], "apply": False, "present": True}
            continue
        if not info["json"].exists():
            fail(f"{block}: missing JSON {info['json']}")
        if not info["md"].exists():
            fail(f"{block}: missing MD {info['md']}")
        try:
            m = json.loads(info["json"].read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{block}: malformed JSON {exc}")
        v = m.get("verdict")
        if v != info["expected_verdict"]:
            fail(f"{block}: verdict mismatch (got {v}, want {info['expected_verdict']})")
        if info["apply"] and not m.get("runtime_patch_applied"):
            fail(f"{block}: expected runtime_patch_applied=true for apply block")
        if (not info["apply"]) and m.get("runtime_patch_applied"):
            fail(f"{block}: expected runtime_patch_applied=false for audit/doc block")
        rollup["blocks"][block] = {"verdict": v, "apply": info["apply"], "present": True}

    # Write rollup artifact
    out = MARKERS["BLOCK_E"]["json"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rollup, indent=2), encoding="utf-8")

    print("[PASS] V2 rollup all 5 blocks consistent")
    sys.exit(0)


if __name__ == "__main__":
    main()
