"""
PROJECT_B Track A + PROJECT_C Track A — server_profiles dual-route.

Skeleton flag-gated routes:
  - GET  /api/server-profiles/select  (read-only contract probe)
  - POST /api/server-profiles/select  (selection target; INERT)

Runtime is OFF by default. When SERVER_PROFILES_RUNTIME_ENABLED != "true",
every route responds with HTTP 503 + payload `{"status":"disabled", ...}`.

PROJECT_C Track A adds a **behavior layer** behind the skeleton: pure helpers
that compute a deterministic read-only response shape from the (currently
empty) `server_profiles` collection. These helpers are NEVER called when the
flag is unset (the route returns 503 first). With flag ON, they emit a
non-mutating envelope; **no DB write**, **no users.server mutation**, **no
active server switching**, **no dual-write DB behavior**.

No import from combat/account runtime; no load-time side effects.
"""
import os

from fastapi import APIRouter, HTTPException

# Feature flag canonical name (must match V8 BLOCK_D dual-route design doc).
FEATURE_FLAG = "SERVER_PROFILES_RUNTIME_ENABLED"

router = APIRouter(prefix="/api/server-profiles", tags=["server-profiles"])


def _runtime_enabled() -> bool:
    """Return True only if the feature flag is explicitly enabled."""
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "phase": "PROJECT_B_TRACK_A_INERT_SKELETON",
        "contract_version": "v1",
        "upstream_design_doc": "/app/docs/divine/122D_LEGACY_SERVER_SELECT_DUAL_ROUTE_DESIGN.md",
        "hint": (
            "This is a contract probe. The SLC-H dual-route runtime is OFF "
            "by default and will remain disabled until the implementation pack "
            "explicitly enables it."
        ),
    }


# ===================== PROJECT_C TRACK A — BEHAVIOR LAYER (FLAG-GATED, OFF BY DEFAULT) =====================
# Pure helpers that compute the read-only response shape. They are NEVER called when the
# feature flag is unset (the route returns 503 first). With flag ON, the helpers compute a
# response from the existing `server_profiles` collection (0 docs in current state). No DB
# write, no users.server mutation, no active server switching, no dual-write. The helpers
# are deterministic, side-effect free, and unit-testable.


def _read_only_select_response_for_user(user_id: "str | None") -> dict:
    """Compute a deterministic read-only response shape from the (currently empty)
    server_profiles collection. **No DB write**. Returns an envelope that mirrors
    the legacy /api/server/select shape with an additive optional extension.
    """
    payload = {
        "success": False,
        "phase": "PROJECT_C_TRACK_A_BEHAVIOR_LAYER_READ_ONLY",
        "reason": "no_active_server_profile_for_user",
        "server_profile_id": None,
        "is_archived": False,
        "fallback_used": True,
        "fallback_target": "users.server (legacy; NOT mutated here)",
    }
    try:
        # Lazy import to avoid load-time side effects.
        from server import db  # type: ignore
        if user_id:
            doc = db.server_profiles.find_one({"user_id": user_id, "is_archived": False})
            if doc:
                payload.update({
                    "success": True,
                    "server_profile_id": str(doc.get("_id")),
                    "is_archived": False,
                    "fallback_used": False,
                    "fallback_target": None,
                    "reason": "server_profile_active_read_only",
                })
    except Exception:
        # Any error keeps the inert envelope; never raise.
        payload["reason"] = "server_profile_lookup_error_fallback_inert"
    return payload


@router.get("/select")
async def server_profiles_select_probe() -> dict:
    """Read-only contract probe.

    Returns 503 when the feature flag is unset. With flag set, returns a
    deterministic read-only envelope (still inert: no DB write).
    """
    if not _runtime_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET"))
    # PROJECT_C Track A: behavior layer activates only when flag ON.
    # No authentication wired here (deferred); user_id stays None → fallback envelope.
    return {
        "status": "flag_on_behavior_layer_read_only",
        "runtime_enabled": True,
        "method": "GET",
        "phase": "PROJECT_C_TRACK_A_BEHAVIOR_LAYER",
        "data": _read_only_select_response_for_user(None),
    }


@router.post("/select")
async def server_profiles_select_target() -> dict:
    """Selection target route (INERT).

    No DB writes; no user state change. Returns 503 when flag unset; with flag
    ON, returns the same read-only envelope (no mutation).
    """
    if not _runtime_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST"))
    # PROJECT_C Track A: POST behavior layer is also inert (read-only envelope).
    # No DB write, no active-server switch, no dual-write.
    return {
        "status": "flag_on_behavior_layer_read_only",
        "runtime_enabled": True,
        "method": "POST",
        "phase": "PROJECT_C_TRACK_A_BEHAVIOR_LAYER",
        "data": _read_only_select_response_for_user(None),
        "mutation_executed": False,
        "active_server_switched": False,
        "dual_write_executed": False,
    }


# ===================== PROJECT_D TRACK A — FLAGGED PREVIEW BEHAVIOR (DOUBLE-FLAG-GATED, INERT) =====================
# Pure helper that computes a deterministic **preview/dry-run** envelope. Requires BOTH
#   SERVER_PROFILES_RUNTIME_ENABLED=true  AND  SERVER_PROFILES_PREVIEW_ENABLED=true
# to be considered "preview-eligible". The default routes above DO NOT call this helper.
# Whatever the value of SERVER_PROFILES_PREVIEW_ENABLED, the default GET/POST routes
# return 503 when SERVER_PROFILES_RUNTIME_ENABLED is unset (verified by validator).
# **No DB write, no active server switching, no second server, no DB mutation.**

PREVIEW_FEATURE_FLAG = "SERVER_PROFILES_PREVIEW_ENABLED"


def _preview_runtime_enabled() -> bool:
    """Return True only if BOTH the runtime flag AND the preview sub-flag are ON.

    This double-gate is a safety net: even if RUNTIME_ENABLED is ever flipped, the
    preview envelope remains inert until PREVIEW_ENABLED is also explicitly enabled.
    """
    if not _runtime_enabled():
        return False
    return os.environ.get(PREVIEW_FEATURE_FLAG, "").strip().lower() == "true"


def _preview_dry_run_envelope(user_id: "str | None") -> dict:
    """Compute a deterministic **preview/dry-run** envelope. Pure, no DB writes.

    The envelope mirrors the read-only select shape with explicit `preview=True`
    metadata so consumers can detect the dry-run nature. The function NEVER mutates
    DB state, NEVER switches active server, NEVER creates a profile.

    NOTE: the default route handlers above DO NOT call this helper. It exists for
    future flag-gated wiring and is unit-testable in isolation.
    """
    base = _read_only_select_response_for_user(user_id)
    base["phase"] = "PROJECT_D_TRACK_A_FLAGGED_PREVIEW_DRY_RUN_READ_ONLY"
    base["preview"] = True
    base["dry_run"] = True
    base["mutation_executed"] = False
    base["active_server_switched"] = False
    base["dual_write_executed"] = False
    base["second_server_opened"] = False
    base["preview_feature_flag"] = PREVIEW_FEATURE_FLAG
    base["preview_runtime_enabled"] = _preview_runtime_enabled()
    return base


__all__ = ["router", "FEATURE_FLAG", "PREVIEW_FEATURE_FLAG"]
