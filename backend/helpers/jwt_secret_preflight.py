"""SECURITY_HOTFIX_A — JWT_SECRET preflight (fail-closed).

Centralizza la risoluzione del JWT_SECRET con fail-closed contro il fallback
legacy hardcoded ``divine_waifus_secret_key_2025``.

Regole:
- se ``JWT_SECRET`` non e' impostato in env → fail-closed (RuntimeError);
- se ``JWT_SECRET`` == fallback legacy → fail-closed (RuntimeError);
- se ``ALLOW_INSECURE_DEV_JWT=true`` e ``ENV_PROFILE`` == ``local-dev`` → consenti
  un secret debole solo per dev locale isolato (mai per QA/staging/prod);
- non stampare mai il valore del secret nei log.
"""
from __future__ import annotations
import os

LEGACY_FALLBACK = "divine_waifus_secret_key_2025"
_PREFLIGHT_LOG_MSG = (
    "JWT_SECRET startup preflight failed: missing/default secret is not allowed "
    "in this environment."
)


def _is_local_dev_allowed() -> bool:
    if os.getenv("ALLOW_INSECURE_DEV_JWT", "").strip().lower() not in ("true", "1", "yes", "on"):
        return False
    profile = os.getenv("ENV_PROFILE", "").strip().lower()
    return profile in ("local-dev", "local", "dev")


def resolve_jwt_secret() -> str:
    """Ritorna JWT_SECRET valido o solleva RuntimeError fail-closed."""
    raw = os.getenv("JWT_SECRET")
    if raw is None or not raw.strip():
        if _is_local_dev_allowed():
            return "INSECURE_LOCAL_DEV_ONLY_PLACEHOLDER"
        raise RuntimeError(_PREFLIGHT_LOG_MSG)
    if raw.strip() == LEGACY_FALLBACK:
        if _is_local_dev_allowed():
            return raw
        raise RuntimeError(_PREFLIGHT_LOG_MSG)
    return raw
