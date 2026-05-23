"""
SLC-F BATCH-0 — Server/Account scope helpers (gated route patch apply).

This module provides PASSIVE helpers used by Batch-1 server_bound low-risk
routes to stamp the SLC-G default legacy server_id and account_id on
documents being written, with strict set-only-if-missing semantics.

Strict design:
- No second server opened: `resolve_server_id()` always returns 's1' until
  `SECOND_SERVER_OPENING_ENABLED` is explicitly set (separate gated task).
- `resolve_account_id(user_id)` returns the SLC-G migration convention:
  account_id == user_id (verbatim).
- `ensure_server_scope(doc, user_id)` MUTATES the dict by ADDING
  `server_id` and `account_id` ONLY when those keys are absent.
  Never overwrites existing values. Idempotent at runtime.

This module is design-additive: importing it has no runtime side effect
on routes that do not call its functions. AF2-N, combat, gacha and
catalog code paths do not import this module and are NOT touched.
"""
from __future__ import annotations

import os
from typing import Any, MutableMapping, Optional

# SLC-G default legacy server (must remain 's1' until a second server opens
# via the SECOND_SERVER_OPENING_ENABLED feature flag in a future gated task).
LEGACY_DEFAULT_SERVER_ID: str = "s1"


def second_server_opening_enabled() -> bool:
    """Returns True only if SECOND_SERVER_OPENING_ENABLED env is explicitly 'true'."""
    return os.environ.get("SECOND_SERVER_OPENING_ENABLED", "").lower() == "true"


def server_profiles_runtime_enabled() -> bool:
    """Returns True only if SERVER_PROFILES_RUNTIME_ENABLED env is explicitly 'true'."""
    return os.environ.get("SERVER_PROFILES_RUNTIME_ENABLED", "").lower() == "true"


def resolve_server_id(_request: Any = None) -> str:
    """
    Resolve the active server_id for the current request context.

    Until a second server is officially opened, this MUST always return
    the legacy default 's1'. This guarantees back-compat with SLC-G
    migration and prevents accidental cross-server resource leakage.
    """
    if not second_server_opening_enabled():
        return LEGACY_DEFAULT_SERVER_ID
    # Placeholder: when second-server selection comes online in a future
    # gated task (SLC-H live wiring), this function will be extended to
    # read the active server from the request/session. Until then,
    # second-server selection is intentionally NOT honored.
    return LEGACY_DEFAULT_SERVER_ID


def resolve_account_id(user_id: Optional[str]) -> Optional[str]:
    """
    Resolve account_id for a given user_id.

    Per the SLC-G migration contract, account_id == user_id verbatim
    for legacy single-shard accounts. This will remain the canonical
    derivation until an account/profile split is introduced via a
    separate gated task.
    """
    if user_id is None:
        return None
    return user_id


def ensure_server_scope(
    doc: MutableMapping[str, Any],
    user_id: Optional[str] = None,
    request: Any = None,
) -> MutableMapping[str, Any]:
    """
    Stamp `server_id` and `account_id` on the document **only if missing**.

    Behaviour:
    - Never overwrites pre-existing values.
    - Never changes `user_id`, `id`, `_id`, or any other field.
    - Returns the same dict (mutated in place) for ergonomic chaining.
    - Safe to call multiple times on the same dict (idempotent).

    Args:
        doc: the document about to be inserted (mutated in place).
        user_id: source of truth for account_id derivation.
        request: optional request object for future server selection.

    Returns:
        The same `doc` reference, with `server_id`/`account_id` stamped.
    """
    if doc is None:
        return doc
    # If a doc carries its own user_id we may use it as a fallback.
    effective_uid = user_id if user_id is not None else doc.get("user_id")
    if "server_id" not in doc:
        doc["server_id"] = resolve_server_id(request)
    if "account_id" not in doc:
        derived = resolve_account_id(effective_uid)
        if derived is not None:
            doc["account_id"] = derived
    return doc


__all__ = [
    "LEGACY_DEFAULT_SERVER_ID",
    "second_server_opening_enabled",
    "server_profiles_runtime_enabled",
    "resolve_server_id",
    "resolve_account_id",
    "ensure_server_scope",
]
