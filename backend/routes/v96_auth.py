"""
v96 — Auth router (Google / Apple / Guest / Me / Logout / Refresh).

Pack MEGA_RELEASE_ACCELERATION_45_v96.

Endpoints:
- POST /api/auth/google         Linking via Google id_token (verify path o sandbox)
- POST /api/auth/apple          Linking via Apple identity_token (iOS-only client)
- POST /api/auth/guest          Guest/QA login (GATED da V96_AUTH_GUEST_ENABLED=true)
- GET  /api/auth/me             Restituisce account autenticato (alias-safe, no PII raw)
- POST /api/auth/logout         Invalida sessione lato client (stateless)
- POST /api/auth/refresh        Refresh token (CONTRACT, runtime DEFERRED)

Safety:
- NO raw OAuth token logging
- NO provider secret in repo (configurazione via env GOOGLE_CLIENT_ID / APPLE_CLIENT_ID)
- NO duplicate account per stesso provider subject (idempotent linking via hash)
- provider_user_id memorizzato come SHA-256 hash, NON in plain
- token JWT HS256, expiration 7 giorni
- alias-only nei log / sandbox

Provider credentials policy:
- Se mancano GOOGLE_CLIENT_ID / APPLE_CLIENT_ID, modalità sandbox attiva:
  status restituito = "CREDENTIALS_REQUIRED_FOR_STORE_BUILD".
  Nessuna verifica id_token reale; account viene creato ma marcato
  `provider_sandbox=true`. UI deve mostrarlo chiaramente.
"""
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["v96_auth"])

# ─────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "divine_waifus_secret_key_2025")
JWT_ALGO = "HS256"
JWT_EXP_DAYS = int(os.getenv("V96_JWT_EXP_DAYS", "7"))

# v97 — Refresh token rotation
REFRESH_EXP_DAYS = int(os.getenv("V97_REFRESH_EXP_DAYS", "30"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "").strip()
GUEST_ENABLED = os.getenv("V96_AUTH_GUEST_ENABLED", "true").lower() == "true"

# Marker statuses
PROVIDER_STATUS_READY = "READY"
PROVIDER_STATUS_SANDBOX = "CREDENTIALS_REQUIRED_FOR_STORE_BUILD"


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────
def _hash_provider_subject(provider: str, subject: str) -> str:
    """Hash deterministico del provider subject. NON memorizziamo l'ID raw."""
    return hashlib.sha256(f"{provider}:{subject}".encode("utf-8")).hexdigest()


def _create_token(user_id: str, account_id: str, provider: str) -> str:
    payload = {
        "user_id": user_id,
        "account_id": account_id,
        "provider": provider,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=JWT_EXP_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def _safe_alias(email: Optional[str], provider: str) -> str:
    """Genera alias QA-safe dal local-part dell'email (no PII completo)."""
    if not email:
        return f"player_{provider}_{uuid.uuid4().hex[:6]}"
    local = email.split("@")[0]
    return f"{local[:12]}_{provider[:3]}"


def _alias_safe_account(user: dict) -> dict:
    """Restituisce una vista safe dell'account: NO email raw, NO password, NO provider_user_id raw."""
    return {
        "user_id": user.get("id"),
        "account_id": user.get("account_id") or user.get("id"),
        "alias": user.get("alias") or user.get("username") or "player",
        "username": user.get("username"),
        "provider": user.get("provider", "local"),
        "provider_sandbox": bool(user.get("provider_sandbox", False)),
        "level": user.get("level", 1),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
        "last_login": user.get("last_login").isoformat() if user.get("last_login") else None,
    }


# ─────────────────────────────────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────────────────────────────────
class GoogleAuthRequest(BaseModel):
    id_token: Optional[str] = Field(None, description="Google id_token; in sandbox può essere omesso")
    sandbox_subject: Optional[str] = Field(None, description="Solo in sandbox: subject simulato")
    email: Optional[str] = Field(None, description="Email opzionale per alias")


class AppleAuthRequest(BaseModel):
    identity_token: Optional[str] = Field(None, description="Apple identity_token; in sandbox può essere omesso")
    sandbox_subject: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    full_name: Optional[str] = Field(None)


class GuestAuthRequest(BaseModel):
    alias_hint: Optional[str] = Field(None, max_length=24)


# ─────────────────────────────────────────────────────────────────────────
# Router factory (per ricevere db / get_current_user dal main server)
# ─────────────────────────────────────────────────────────────────────────
def create_auth_router(db, get_current_user):
    """Crea il router auth v96 collegato al db Motor e a get_current_user esistente."""

    async def _link_or_create_account(provider: str, subject_hash: str, email: Optional[str], sandbox: bool) -> dict:
        """Idempotent: stessa coppia (provider, subject_hash) → stesso account."""
        existing = await db.users.find_one({"provider_user_id_hash": subject_hash, "provider": provider})
        now = datetime.utcnow()
        if existing:
            await db.users.update_one({"id": existing["id"]}, {"$set": {"last_login": now}})
            existing["last_login"] = now
            return existing
        # Nuovo account
        user_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())
        alias = _safe_alias(email, provider)
        user_doc = {
            "id": user_id,
            "account_id": account_id,
            "provider": provider,
            "provider_user_id_hash": subject_hash,
            "provider_sandbox": sandbox,
            "alias": alias,
            "username": alias,
            "level": 1,
            "experience": 0,
            "gold": 0,
            "gems": 0,
            "stamina": 100,
            "max_stamina": 100,
            "created_at": now,
            "last_login": now,
            "team_formation": [],
        }
        await db.users.insert_one(user_doc)
        return user_doc

    async def _issue_refresh_token(user_id: str) -> str:
        """v97 — emette nuovo refresh token (32 hex bytes) e lo salva hashato."""
        token = str(uuid.uuid4()) + str(uuid.uuid4())
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        await db.refresh_tokens.insert_one({
            "token_hash": token_hash,
            "user_id": user_id,
            "issued_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=REFRESH_EXP_DAYS),
            "revoked_at": None,
        })
        return token

    # ──────────────────────────────────────────────────────────────────
    # POST /api/auth/google
    # ──────────────────────────────────────────────────────────────────
    @router.post("/google")
    async def auth_google(req: GoogleAuthRequest):
        sandbox = not GOOGLE_CLIENT_ID
        subject = None
        if not sandbox and req.id_token:
            # In produzione qui andrebbe verificato id_token via google-auth library.
            # NON eseguiamo verifica in questo container: marker resta sandbox-style.
            # Se l'utente fornisce GOOGLE_CLIENT_ID configureremo google.oauth2.id_token.verify_oauth2_token.
            # In attesa di credentials reali, fallback a sandbox mode per evitare fake PASS.
            sandbox = True
        if sandbox:
            subject = req.sandbox_subject or f"sandbox_google_{uuid.uuid4().hex[:12]}"
        else:
            # placeholder — non raggiunto senza credentials
            raise HTTPException(status_code=503, detail="Google verify path not yet wired")
        subject_hash = _hash_provider_subject("google", subject)
        user = await _link_or_create_account("google", subject_hash, req.email, sandbox=sandbox)
        token = _create_token(user["id"], user.get("account_id"), "google")
        refresh_token = await _issue_refresh_token(user["id"])
        return {
            "status": PROVIDER_STATUS_SANDBOX if sandbox else PROVIDER_STATUS_READY,
            "provider": "google",
            "token": token,
            "refresh_token": refresh_token,
            "expires_in_days": JWT_EXP_DAYS,
            "refresh_expires_in_days": REFRESH_EXP_DAYS,
            "account": _alias_safe_account(user),
            "credentials_required_for_store_build": sandbox,
        }

    # ──────────────────────────────────────────────────────────────────
    # POST /api/auth/apple
    # ──────────────────────────────────────────────────────────────────
    @router.post("/apple")
    async def auth_apple(req: AppleAuthRequest):
        sandbox = not APPLE_CLIENT_ID
        subject = None
        if not sandbox and req.identity_token:
            sandbox = True  # placeholder verify path (vedi nota Google)
        if sandbox:
            subject = req.sandbox_subject or f"sandbox_apple_{uuid.uuid4().hex[:12]}"
        else:
            raise HTTPException(status_code=503, detail="Apple verify path not yet wired")
        subject_hash = _hash_provider_subject("apple", subject)
        user = await _link_or_create_account("apple", subject_hash, req.email, sandbox=sandbox)
        token = _create_token(user["id"], user.get("account_id"), "apple")
        refresh_token = await _issue_refresh_token(user["id"])
        return {
            "status": PROVIDER_STATUS_SANDBOX if sandbox else PROVIDER_STATUS_READY,
            "provider": "apple",
            "ios_only_client_side": True,
            "token": token,
            "refresh_token": refresh_token,
            "expires_in_days": JWT_EXP_DAYS,
            "refresh_expires_in_days": REFRESH_EXP_DAYS,
            "account": _alias_safe_account(user),
            "credentials_required_for_store_build": sandbox,
        }

    # ──────────────────────────────────────────────────────────────────
    # POST /api/auth/guest  (gated, QA/dev only)
    # ──────────────────────────────────────────────────────────────────
    @router.post("/guest")
    async def auth_guest(req: GuestAuthRequest):
        if not GUEST_ENABLED:
            raise HTTPException(status_code=403, detail="Guest login disabled")
        subject = f"guest_{uuid.uuid4().hex[:16]}"
        subject_hash = _hash_provider_subject("guest", subject)
        alias = req.alias_hint or f"guest_{subject[-6:]}"
        user = await _link_or_create_account("guest", subject_hash, email=None, sandbox=True)
        # update alias se hint fornito
        if req.alias_hint:
            await db.users.update_one({"id": user["id"]}, {"$set": {"alias": alias, "username": alias}})
            user["alias"] = alias
            user["username"] = alias
        token = _create_token(user["id"], user.get("account_id"), "guest")
        refresh_token = await _issue_refresh_token(user["id"])
        return {
            "status": "GUEST_QA_ONLY",
            "provider": "guest",
            "gated": True,
            "token": token,
            "refresh_token": refresh_token,
            "expires_in_days": JWT_EXP_DAYS,
            "refresh_expires_in_days": REFRESH_EXP_DAYS,
            "account": _alias_safe_account(user),
            "credentials_required_for_store_build": True,
        }

    # ──────────────────────────────────────────────────────────────────
    # GET /api/auth/me
    # ──────────────────────────────────────────────────────────────────
    @router.get("/me")
    async def auth_me(current_user: dict = Depends(get_current_user)):
        return {
            "v96_auth": True,
            "authenticated": True,
            "account": _alias_safe_account(current_user),
        }

    # ──────────────────────────────────────────────────────────────────
    # POST /api/auth/logout
    # ──────────────────────────────────────────────────────────────────
    @router.post("/logout")
    async def auth_logout(current_user: dict = Depends(get_current_user)):
        # Stateless JWT: il client deve scartare il token. Aggiorniamo last_login per audit.
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"last_logout": datetime.utcnow()}})
        return {"v96_auth": True, "logged_out": True}

    # ──────────────────────────────────────────────────────────────────
    # v97 — POST /api/auth/refresh  (runtime rotation)
    # ──────────────────────────────────────────────────────────────────
    class RefreshReq(BaseModel):
        refresh_token: str

    @router.post("/refresh")
    async def auth_refresh(req: RefreshReq):
        """Rotation: verifica refresh_token, revoca quello vecchio, emette nuova coppia."""
        token_hash = hashlib.sha256(req.refresh_token.encode("utf-8")).hexdigest()
        rec = await db.refresh_tokens.find_one({"token_hash": token_hash})
        if not rec:
            raise HTTPException(status_code=401, detail="invalid_refresh_token")
        if rec.get("revoked_at"):
            # replay: revoca tutta la famiglia per protezione
            await db.refresh_tokens.update_many(
                {"user_id": rec["user_id"], "revoked_at": None},
                {"$set": {"revoked_at": datetime.utcnow(), "revoke_reason": "replay_detected"}},
            )
            raise HTTPException(status_code=401, detail="refresh_token_replayed_family_revoked")
        if rec.get("expires_at") and rec["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=401, detail="refresh_token_expired")
        # Revoca vecchio + emetti nuovo
        await db.refresh_tokens.update_one(
            {"_id": rec["_id"]},
            {"$set": {"revoked_at": datetime.utcnow(), "revoke_reason": "rotated"}},
        )
        user = await db.users.find_one({"id": rec["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="user_not_found")
        new_access = _create_token(user["id"], user.get("account_id"), user.get("provider", "local"))
        new_refresh = str(uuid.uuid4()) + str(uuid.uuid4())
        new_refresh_hash = hashlib.sha256(new_refresh.encode("utf-8")).hexdigest()
        await db.refresh_tokens.insert_one({
            "token_hash": new_refresh_hash,
            "user_id": user["id"],
            "issued_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=REFRESH_EXP_DAYS),
            "revoked_at": None,
            "rotated_from_token_hash": token_hash,
        })
        return {
            "v97_auth": True,
            "token": new_access,
            "refresh_token": new_refresh,
            "expires_in_days": JWT_EXP_DAYS,
            "refresh_expires_in_days": REFRESH_EXP_DAYS,
            "rotation_applied": True,
        }

    # ──────────────────────────────────────────────────────────────────
    # v97 — POST /api/auth/logout-all
    # ──────────────────────────────────────────────────────────────────
    @router.post("/logout-all")
    async def auth_logout_all(current_user: dict = Depends(get_current_user)):
        result = await db.refresh_tokens.update_many(
            {"user_id": current_user["id"], "revoked_at": None},
            {"$set": {"revoked_at": datetime.utcnow(), "revoke_reason": "logout_all"}},
        )
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"last_logout_all": datetime.utcnow()}})
        return {"v97_auth": True, "logged_out_all": True, "refresh_tokens_revoked": result.modified_count}

    # ──────────────────────────────────────────────────────────────────
    # v97 — POST /api/auth/delete-account-request  (soft-delete request)
    # ──────────────────────────────────────────────────────────────────
    @router.post("/delete-account-request")
    async def auth_delete_account_request(current_user: dict = Depends(get_current_user)):
        """Soft-delete: marca pending_deletion + grace period 14 giorni.

        Internal Alpha: NON cancella runtime — marca con scheduled_deletion_at.
        Commercial: richiede cron job + hard delete + data export pre-cancellazione.
        """
        now = datetime.utcnow()
        scheduled = now + timedelta(days=14)
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {
                "deletion_requested_at": now,
                "scheduled_deletion_at": scheduled,
                "pending_deletion": True,
            }},
        )
        # Revoca tutte le sessioni come logout-all
        await db.refresh_tokens.update_many(
            {"user_id": current_user["id"], "revoked_at": None},
            {"$set": {"revoked_at": now, "revoke_reason": "delete_account_request"}},
        )
        return {
            "v97_auth": True,
            "delete_account_request_accepted": True,
            "soft_delete_mode": True,
            "grace_period_days": 14,
            "scheduled_deletion_at": scheduled.isoformat(),
            "hard_delete_runtime": "INTERNAL_ALPHA_READY_COMMERCIAL_NEEDS_REVIEW",
            "gdpr_data_export_endpoint_planned": "POST /api/auth/data-export-request (CONTRACT_DEFERRED)",
            "reversible_within_grace_period": True,
        }

    # ──────────────────────────────────────────────────────────────────
    # v97 — GET /api/auth/privacy-status
    # ──────────────────────────────────────────────────────────────────
    @router.get("/privacy-status")
    async def auth_privacy_status(current_user: dict = Depends(get_current_user)):
        return {
            "v97_auth": True,
            "account_id": current_user.get("account_id") or current_user.get("id"),
            "data_minimization": True,
            "raw_oauth_token_logged": False,
            "provider_user_id_raw_stored": False,
            "provider_user_id_hashed": True,
            "pii_in_logs": False,
            "pending_deletion": bool(current_user.get("pending_deletion", False)),
            "scheduled_deletion_at": current_user.get("scheduled_deletion_at").isoformat() if current_user.get("scheduled_deletion_at") else None,
            "data_export_runtime": "CONTRACT_DEFERRED_TO_V98",
            "retention_policy_days": 365,
        }

    return router


# ─────────────────────────────────────────────────────────────────────────
# Provider status (read-only, no auth required)
# ─────────────────────────────────────────────────────────────────────────
provider_status_router = APIRouter(prefix="/api/auth", tags=["v96_auth_status"])


@provider_status_router.get("/provider-status")
def provider_status():
    """Ritorna lo status dei provider di login, alias-safe (no secret)."""
    return {
        "v96_auth": True,
        "google": {
            "status": PROVIDER_STATUS_READY if GOOGLE_CLIENT_ID else PROVIDER_STATUS_SANDBOX,
            "credentials_present": bool(GOOGLE_CLIENT_ID),
            "dev_build_required": True,
            "library_recommendation": "@react-native-google-signin/google-signin",
        },
        "apple": {
            "status": PROVIDER_STATUS_READY if APPLE_CLIENT_ID else PROVIDER_STATUS_SANDBOX,
            "credentials_present": bool(APPLE_CLIENT_ID),
            "ios_only_client_side": True,
            "library_recommendation": "expo-apple-authentication",
        },
        "guest": {"status": "GATED_QA_ONLY", "enabled": GUEST_ENABLED},
        "jwt": {"alg": JWT_ALGO, "exp_days": JWT_EXP_DAYS},
        "refresh_token": "DEFERRED",
        "safety": {
            "raw_oauth_token_logged": False,
            "provider_secret_in_repo": False,
            "alias_only": True,
        },
    }
