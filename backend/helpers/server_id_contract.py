"""Pack 5A-1 server id contract for PSP/server-scoped onboarding.

This helper is intentionally small and fail-closed. It validates only the
server ids that may create or consume PSP onboarding state.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Optional, Set, Tuple


ENV_ALLOWED_SERVER_IDS = "DIVINE_ALLOWED_SERVER_IDS"
DISALLOWED_SERVER_IDS = {
    "default",
    "s1",
    "preview_local",
    "local",
    "test",
    "unknown",
    "none",
    "null",
}

_SERVER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@dataclass(frozen=True)
class ServerIdValidation:
    ok: bool
    server_id: Optional[str]
    blocker: str
    http_status: int
    allowlist_source: str
    reason: str = ""


def _normalize_server_id(server_id: Any) -> Optional[str]:
    if server_id is None or not isinstance(server_id, str):
        return None
    sid = server_id.strip()
    if not sid or not _SERVER_ID_PATTERN.fullmatch(sid):
        return None
    return sid


def _is_forbidden_server_id(server_id: str) -> bool:
    return server_id.strip().lower() in DISALLOWED_SERVER_IDS


def _parse_allowed_server_ids(raw: str) -> Set[str]:
    allowed: Set[str] = set()
    for token in re.split(r"[\s,;]+", raw or ""):
        sid = _normalize_server_id(token)
        if sid and not _is_forbidden_server_id(sid):
            allowed.add(sid)
    return allowed


async def _allowed_from_server_profiles() -> Tuple[Set[str], str]:
    """Reads the existing read-only QA server profile source.

    The source route is read-only and returns the same IDs consumed by the
    server select UI. If it is unavailable or empty, callers fail closed.
    """
    try:
        from routes.v103_server_profiles import list_server_profiles

        payload = await list_server_profiles()
    except Exception:
        return set(), "v103_server_profiles_unavailable"

    allowed: Set[str] = set()
    for item in payload.get("servers") or []:
        if item.get("can_enter") is False:
            continue
        sid = _normalize_server_id(item.get("server_id"))
        if sid and not _is_forbidden_server_id(sid):
            allowed.add(sid)
    return allowed, "v103_server_profiles"


async def allowed_psp_server_ids() -> Tuple[Set[str], str]:
    env_allowed = _parse_allowed_server_ids(os.getenv(ENV_ALLOWED_SERVER_IDS, ""))
    if env_allowed:
        return env_allowed, ENV_ALLOWED_SERVER_IDS
    return await _allowed_from_server_profiles()


async def validate_psp_server_id(server_id: Any) -> ServerIdValidation:
    sid = _normalize_server_id(server_id)
    if sid is None:
        return ServerIdValidation(
            ok=False,
            server_id=None,
            blocker="SERVER_ID_REQUIRED",
            http_status=400,
            allowlist_source="none",
            reason="missing, empty, non-string, or invalid format",
        )
    if _is_forbidden_server_id(sid):
        return ServerIdValidation(
            ok=False,
            server_id=sid,
            blocker="SERVER_ID_FORBIDDEN",
            http_status=403,
            allowlist_source="reserved_id_blocklist",
            reason="reserved or non-runtime server id",
        )

    allowed, source = await allowed_psp_server_ids()
    if not allowed:
        return ServerIdValidation(
            ok=False,
            server_id=sid,
            blocker="SERVER_ID_ALLOWLIST_EMPTY",
            http_status=503,
            allowlist_source=source,
            reason="no allowed server ids configured or exposed",
        )
    if sid not in allowed:
        return ServerIdValidation(
            ok=False,
            server_id=sid,
            blocker="SERVER_ID_NOT_ALLOWLISTED",
            http_status=403,
            allowlist_source=source,
            reason="server id is not in the backend allowlist",
        )

    return ServerIdValidation(
        ok=True,
        server_id=sid,
        blocker="",
        http_status=200,
        allowlist_source=source,
    )
