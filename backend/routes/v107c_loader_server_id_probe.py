"""v107C — Loader server_id acceptance probe router.

Mounts 5 probe endpoints that DEMONSTRATE acceptance of an optional `server_id`
query parameter without modifying existing loader endpoints. All endpoints are
read-only echoes; they NEVER touch the DB, NEVER mutate state, NEVER grant
rewards. When SERVER_SCOPED_RUNTIME_ENABLED=false (default), the server_id is
parsed, audited and reflected in the response with explicit `filter_applied:false`.
"""
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter

router = APIRouter(prefix="/api/v107c/loader-probe", tags=["loader_server_id_probe_v107c"])


def _flag(name: str) -> bool:
    return (os.getenv(name, "") or "").lower() == "true"


def _echo(endpoint: str, server_id: Optional[str]) -> Dict[str, Any]:
    flag_on = _flag("SERVER_SCOPED_RUNTIME_ENABLED")
    return {
        "endpoint_probed": endpoint,
        "server_id_received": server_id,
        "server_id_parsed": server_id is not None and len(server_id) > 0,
        "filter_applied": False,
        "feature_flag": {"SERVER_SCOPED_RUNTIME_ENABLED": flag_on},
        "status": "ACCEPTANCE_PROBE_NO_FILTER_APPLIED",
        "safety": {"db_writes_performed": 0, "reward_granted": False, "progress_written": False},
    }


@router.get("/user-heroes")
def probe_user_heroes(server_id: Optional[str] = None):
    return _echo("/api/user/heroes", server_id)


@router.get("/team-get-formation")
def probe_team_get_formation(server_id: Optional[str] = None):
    return _echo("/api/team/get-formation", server_id)


@router.get("/inventory")
def probe_inventory(server_id: Optional[str] = None):
    return _echo("/api/inventory", server_id)


@router.get("/currencies")
def probe_currencies(server_id: Optional[str] = None):
    return _echo("/api/currencies", server_id)


@router.get("/story-progress")
def probe_story_progress(server_id: Optional[str] = None):
    return _echo("/api/story/progress", server_id)
