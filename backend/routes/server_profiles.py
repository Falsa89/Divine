"""
PROJECT_B Track A — server_profiles dual-route INERT SKELETON.

Questo modulo definisce 2 route skeleton flag-gated per la futura dual-route
SLC-H:
  - GET  /api/server-profiles/select  (read-only contract probe)
  - POST /api/server-profiles/select  (selection target; INERT)

Il runtime e' OFF di default. Quando il feature flag
SERVER_PROFILES_RUNTIME_ENABLED non e' impostato a "true", ogni route risponde
con HTTP 503 Service Unavailable e payload `{"status":"disabled", ...}`. Nessuna
logica di selezione, nessun DB write, nessuna scrittura su `server_profiles`.

Questo e' uno **skeleton di contratto**, non un'implementazione runtime. La
rimozione del legacy `/api/server/select` (V6 BLOCK_D Phase 3) **resta deferita**.

Nessun import da combat/account runtime; nessun side effect a load.
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


@router.get("/select")
async def server_profiles_select_probe() -> dict:
    """Read-only contract probe.

    Returns 503 when the feature flag is unset. When enabled in future, this
    will return the active server profile metadata for the calling user.
    """
    if not _runtime_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET"))
    # Inert future-implementation guard: even if the flag is enabled, this
    # skeleton refuses to expose behavior in PROJECT_B Track A. The actual
    # logic is deferred to the dedicated implementation pack.
    raise HTTPException(status_code=503, detail={
        **_disabled_payload("GET"),
        "status": "flag_on_but_implementation_deferred",
        "runtime_enabled": True,
    })


@router.post("/select")
async def server_profiles_select_target() -> dict:
    """Selection target route (INERT).

    No DB writes; no user state change. Returns 503 always in PROJECT_B Track A.
    """
    if not _runtime_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST"))
    raise HTTPException(status_code=503, detail={
        **_disabled_payload("POST"),
        "status": "flag_on_but_implementation_deferred",
        "runtime_enabled": True,
    })


__all__ = ["router", "FEATURE_FLAG"]
