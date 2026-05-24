"""PROJECT_F Track B — Housing Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

*** This route is gated behind HOUSING_PREVIEW_ENABLED. When the flag is unset
or not 'true' (case-insensitive), every request to `/api/housing/preview`
returns HTTP 503 with `{"status":"disabled", ...}` payload. ***

No DB writes. No live Housing bonus application. No combat/account stat
mutation. No external service calls. No frontend wiring. The route exists
only to publish the read-only preview contract shape that future packs can
activate explicitly.

With the flag ON (NOT the default), the route emits a deterministic, inert
read-only envelope that mirrors the upstream design `housing_bonus_resolver_stub`
design—still no live application.
"""
import os

from fastapi import APIRouter, HTTPException

FEATURE_FLAG = "HOUSING_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_f_track_b_housing_preview_v1"

router = APIRouter(prefix="/api/housing", tags=["housing"])


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "phase": "PROJECT_F_TRACK_B_HOUSING_PREVIEW_INERT_SKELETON",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/127B_HOUSING_PHASE3_INTEGRATION_DESIGN.md",
        "hint": (
            "Housing read-only preview is disabled by default. It will remain "
            "disabled until an explicit implementation pack enables HOUSING_PREVIEW_ENABLED."
        ),
        "live_bonus_applied": False,
        "db_writes": False,
        "combat_mutation": False,
    }


def _read_only_envelope(user_id: "str | None") -> dict:
    """Pure deterministic read-only envelope. Never mutates state, never
    returns live bonus values. Mirrors the upstream design stub shape."""
    return {
        "success": False,
        "phase": "PROJECT_F_TRACK_B_HOUSING_PREVIEW_READ_ONLY",
        "reason": "housing_preview_inert_envelope",
        "user_id": user_id,
        "preview": True,
        "dry_run": True,
        "live_bonus_applied": False,
        "db_writes": False,
        "combat_mutation": False,
        "rooms": [],
        "residents": [],
        "caps": {
            "hp_pct": {"min": 0.0, "max": 5.0},
            "atk_pct": {"min": 0.0, "max": 5.0},
            "def_pct": {"min": 0.0, "max": 5.0},
            "crit_pct": {"min": 0.0, "max": 2.0},
        },
        "envelope": {
            "hp_pct": 0.0,
            "atk_pct": 0.0,
            "def_pct": 0.0,
            "crit_pct": 0.0,
            "source": "housing_preview_zero_envelope_inert",
        },
        "contract_version": CONTRACT_VERSION,
    }


@router.get("/preview")
async def housing_preview_get() -> dict:
    """Read-only contract probe. Returns 503 when flag unset; with flag ON,
    returns a deterministic inert envelope (still no DB write)."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET"))
    return {
        "status": "flag_on_read_only_envelope",
        "runtime_enabled": True,
        "method": "GET",
        "phase": "PROJECT_F_TRACK_B_HOUSING_PREVIEW_READ_ONLY",
        "data": _read_only_envelope(None),
    }


__all__ = ["router", "FEATURE_FLAG", "CONTRACT_VERSION"]
