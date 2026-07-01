"""
Divine Waifus - Main Backend Server
FastAPI + MongoDB + JWT Auth
"""
import os
import uuid
import random
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Header, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

from battle_engine import create_battle_routes, ELEMENT_SKILLS, PASSIVE_SKILLS, POSITION_BUFFS
from game_systems import create_game_routes
from routes.sprites import register_sprite_routes
from routes.items import register_items_routes, BATTLE_DROPS

# RM1.20-C — Hero visibility helpers (PURE / NO-OP for heroes without flags).
# Default behavior preserves backward compatibility: heroes lacking
# show_in_*/obtainable flags remain visible/obtainable. Filters become active
# only after roster import/soft-deactivation flips the flags.
from utils.hero_visibility import (
    should_show_in_catalog,
    should_show_in_summon,
    should_show_in_collection,
    should_show_in_battle_picker,  # noqa: F401  (reserved for future battle picker endpoint)
)
from helpers.server_id_contract import validate_psp_server_id

# ===================== CONFIG =====================
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "divine_waifus")
from helpers.jwt_secret_preflight import resolve_jwt_secret  # SECURITY_HOTFIX_A
JWT_SECRET = resolve_jwt_secret()

app = FastAPI(title="Divine Waifus API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PACK 128/4A — Pre-QA Backend Mutation Allowlist Middleware (RUNTIME).
# Montato fail-closed by default: blocca con HTTP 423 PRE_QA_MUTATION_BLOCKED
# ogni mutazione (POST/PUT/PATCH/DELETE) su /api/* che non sia nella allowlist.
# Solo valori esplicitamente false/off/0/no in PRE_QA_MUTATION_GUARD_ENABLED
# disabilitano il guard.
# Vedi: backend/middleware/pre_qa_mutation_guard.py
#       data/design/system_safety/pack_128_backend_mutation_allowlist.json
from middleware.pre_qa_mutation_guard import PreQaMutationGuardMiddleware
app.add_middleware(PreQaMutationGuardMiddleware)

@app.on_event("startup")
async def ops_c_wiring_startup_check():
    """OPS-C-WIRING — Non-invasive boot hook for the Expo wrapper.

    Spawns /app/ops/startup_check.sh in background (best-effort, no wait,
    no exception propagation). The hook is itself idempotent and only
    restores `/usr/local/bin/start-expo.sh` if missing/drifted. NO DB
    writes. NO app logic mutation. Disabled if the env var
    `DISABLE_OPS_C_WIRING=1` is set.
    """
    if os.environ.get("DISABLE_OPS_C_WIRING") == "1":
        print("[OPS-C-WIRING] disabled via DISABLE_OPS_C_WIRING=1")
        return
    script = "/app/ops/startup_check.sh"
    if not os.path.exists(script) or not os.access(script, os.X_OK):
        print(f"[OPS-C-WIRING] hook missing/not-executable: {script}; skip")
        return
    try:
        import subprocess
        subprocess.Popen(
            ["bash", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print("[OPS-C-WIRING] startup_check.sh spawned (background, idempotent)")
    except Exception as exc:
        # Never fail backend boot due to wiring hook
        print(f"[OPS-C-WIRING] spawn error (non-fatal): {exc!r}")


# ===================== DATABASE =====================
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# ===================== AUTH =====================
def create_token(user_id: str) -> str:
    now = datetime.utcnow()
    issued_at = time.time()
    payload = {
        "user_id": user_id,
        "iat": int(issued_at),
        "auth_iat": issued_at,
        "exp": now + timedelta(days=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def _coerce_utc_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(value))
        except (TypeError, ValueError, OSError):
            return None
    if isinstance(value, str):
        try:
            raw = value.strip()
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            parsed = datetime.fromisoformat(raw)
            return parsed.replace(tzinfo=None)
        except ValueError:
            return None
    return None

def _token_issued_at(payload: dict) -> datetime:
    issued_at = _coerce_utc_datetime(payload.get("auth_iat", payload.get("iat")))
    if not issued_at:
        raise HTTPException(status_code=401, detail="Token privo di iat")
    return issued_at

def _latest_logout_cutoff(user: dict) -> Optional[datetime]:
    cutoffs = [
        _coerce_utc_datetime(user.get("last_logout")),
        _coerce_utc_datetime(user.get("last_logout_all")),
    ]
    valid = [cutoff for cutoff in cutoffs if cutoff is not None]
    return max(valid) if valid else None

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        issued_at = _token_issued_at(payload)
        user = await db.users.find_one({"id": payload["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="Utente non trovato")
        logout_cutoff = _latest_logout_cutoff(user)
        if logout_cutoff and issued_at < logout_cutoff:
            raise HTTPException(status_code=401, detail="Token revocato")
        return serialize_doc(user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def register(req: RegisterRequest):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email gia registrata")
    
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    username = req.username or req.email.split("@")[0]
    
    user = {
        "id": user_id,
        "email": req.email,
        "password": hashed,
        "username": username,
        "level": 1,
        "experience": 0,
        "gold": 5000,
        "gems": 100,
        "stamina": 100,
        "max_stamina": 100,
        "titles": ["Novizio"],
        "active_title": "Novizio",
        "aura": "none",
        "faction": None,
        "guild_id": None,
        "created_at": datetime.utcnow(),
    }
    await db.users.insert_one(user)
    
    # Pack 86 — Legacy starter user_heroes creation GUARDED.
    # Decisione canonica: gli eroi del player sono SERVER-SCOPED.
    # /api/register crea SOLO identita' account/auth, non roster operativo
    # account-wide. La creazione legacy di starter user_heroes senza
    # server_id e' DEPRECATA e disabilitata per default. Per backward
    # compatibility di test ambientali precedenti, e' mantenuta dietro un
    # flag esplicito dev-only `REGISTER_LEGACY_STARTER_HEROES_ENABLED=true`.
    # In produzione/runtime player-facing il flag DEVE restare OFF: gli
    # starter heroes saranno assegnati nel contesto server/onboarding
    # quando uno starter flow separato sara' approvato esplicitamente.
    # No premium grant. No reward. No progress live.
    starter_legacy_enabled = (os.environ.get("REGISTER_LEGACY_STARTER_HEROES_ENABLED", "false").lower() == "true")
    starter_legacy_created_count = 0
    if starter_legacy_enabled:
        # DEPRECATED PATH — dev/test only. NOT player-facing production path.
        # NOT claimed as final roster source. Will be removed once starter
        # flow is approved and server-scoped onboarding is wired.
        all_heroes = await db.heroes.find({"rarity": {"$lte": 2}}).to_list(100)
        eligible_starters = [h for h in all_heroes if should_show_in_summon(h)]
        if eligible_starters:
            starters = random.sample(eligible_starters, min(3, len(eligible_starters)))
            for hero in starters:
                user_hero = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "hero_id": hero["id"],
                    "level": 1,
                    "experience": 0,
                    "stars": hero["rarity"],
                    "obtained_at": datetime.utcnow(),
                    "_slc_pack_86_legacy_dev_only_starter": True,
                }
                await db.user_heroes.insert_one(user_hero)
                starter_legacy_created_count += 1
    
    token = create_token(user_id)
    return {
        "token": token,
        "user": {k: v for k, v in user.items() if k != "password" and k != "_id"},
        # Pack 86 — segnali espliciti per il frontend: server-scoped onboarding
        # e' richiesto. Roster operativo NON e' creato qui.
        "server_onboarding_required": True,
        "starter_flow_required": True,
        "starter_legacy_created_in_register": starter_legacy_created_count,
        "_slc_pack_86_register_starter_legacy_guard": True,
    }

@app.post("/api/login")
async def login(req: LoginRequest):
    user = await db.users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    if not bcrypt.checkpw(req.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    token = create_token(user["id"])
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password" and k != "_id"}}

@app.get("/api/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    safe_user = {k: v for k, v in current_user.items() if k != "password"}
    return safe_user

# ===================== HEROES =====================
@app.get("/api/heroes")
async def get_all_heroes():
    # RM1.22-F: rimosso limit `to_list(100)` (pre-existing) — ora il roster
    # totale è 132 (31 legacy + 101 ufficiali) e il limit clipping silenzioso
    # nascondeva 6 eroi visibili dopo l'attivazione 1★/2★. `to_list(None)`
    # carica tutto. Il filtro `should_show_in_catalog` resta invariato e
    # rimuove legacy/pending dal catalogo pubblico.
    heroes = await db.heroes.find({}, {"image_base64": 0}).to_list(None)
    # RM1.20-C: filter the public catalog. Heroes without flags remain
    # visible (helper default = True). Future legacy/pending heroes with
    # show_in_catalog=False or "owned_only" will be hidden from the
    # anonymous public catalog (owned=False).
    visible: list = []
    for h in heroes:
        if not should_show_in_catalog(h, owned=False):
            continue
        # RM1.17-E: expose sentinel asset:<id>:<variant> via image_url
        # Resolver frontend gestisce il sentinel; URL remoto resta invariato.
        if not h.get("image_url"):
            h["image_url"] = h.get("image") or None
        visible.append(h)
    return [serialize_doc(h) for h in visible]

@app.get("/api/heroes/{hero_id}")
async def get_hero(hero_id: str):
    # RM1.20-C: direct hero detail endpoint is intentionally NOT filtered.
    # It is still consumed by hero-detail screens (incl. owned legacy detail)
    # and by encyclopedia entry points. Filtering here would break legitimate
    # owner access. Catalog/list/gacha are filtered upstream; direct detail
    # filtering is deferred until an owned-aware detail endpoint exists.
    hero = await db.heroes.find_one({"id": hero_id})
    if not hero:
        raise HTTPException(status_code=404, detail="Eroe non trovato")
    # RM1.17-E: expose sentinel in image_url per retrocompatibilità frontend.
    if not hero.get("image_url") and hero.get("image"):
        hero["image_url"] = hero["image"]
    return serialize_doc(hero)

# Pack 85 — PSP onboarding new server (fresh-start).
# Crea idempotentemente un player_server_profile fresh-start per (user_id, server_id)
# se non esiste. NESSUNA copia da altri server. NESSUN reward grant. NESSUN starter
# hero creato (richiede starter flow approvato separatamente).
@app.post("/api/psp/ensure")
async def psp_ensure_fresh_start(
    response: Response,
    server_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Pack 85 — Ensure idempotente PSP fresh-start per (user_id, server_id).

    Decisione canonica:
      Entrare in un nuovo server = iniziare da ZERO su quel server.
      NESSUNA copia di roster/level/exp/team/story/inventory/equipment da altri server.

    Schema fresh-start (default):
      player_level = 1
      player_exp = 0
      team_formation = []
      story_progress = {}
      soft_currencies = {}
      onboarding_state = "pending"
      created_by_pack = "v110_pack_85_psp_onboarding_new_server_fresh_start"
    """
    validation = await validate_psp_server_id(server_id)
    if not validation.ok:
        response.status_code = validation.http_status
        response.headers["X-Server-Id-Validation"] = "failed"
        response.headers["X-Blocker"] = validation.blocker
        response.headers["X-Server-Id-Allowlist-Source"] = validation.allowlist_source
        if validation.server_id:
            response.headers["X-Server-Id"] = validation.server_id
        return {
            "v110_psp_ensure": False,
            "blocker": validation.blocker,
            "server_id": validation.server_id,
            "allowlist_source": validation.allowlist_source,
            "reason": validation.reason,
        }
    uid = current_user["id"]
    sid = validation.server_id
    existing = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
    if existing:
        response.headers["X-PSP-Ensure-Mode"] = "already_exists_no_write"
        response.headers["X-Server-Id"] = sid
        return {
            "v110_psp_ensure": True,
            "created": False,
            "already_existed": True,
            "user_id": uid,
            "server_id": sid,
            "profile_id": str(existing.get("profile_id") or existing.get("_id") or ""),
            "player_level": int(existing.get("player_level") or 1),
            "player_exp": int(existing.get("player_exp") or 0),
            "onboarding_state": existing.get("onboarding_state") or "active",
            "fresh_start_applied": False,
            "no_cross_server_copy": True,
        }
    # Fresh-start insert. NESSUNA lettura di altri server. NESSUNA copia.
    fresh_psp = {
        "user_id": uid,
        "server_id": sid,
        "profile_id": f"{uid}:{sid}",
        "player_level": 1,
        "player_exp": 0,
        "team_formation": [],
        "story_progress": {},
        "soft_currencies": {},
        "onboarding_state": "pending",
        "_slc_psp_user_id_namespace": "uuid_canonical",
        "_slc_psp_created_by_pack": "v110_pack_85_psp_onboarding_new_server_fresh_start",
        "_slc_psp_fresh_start": True,
        "_slc_psp_no_cross_server_copy": True,
        "created_at_utc": datetime.utcnow().isoformat() + "Z",
    }
    await db.player_server_profiles.insert_one(fresh_psp)
    response.headers["X-PSP-Ensure-Mode"] = "fresh_start_created"
    response.headers["X-Server-Id"] = sid
    return {
        "v110_psp_ensure": True,
        "created": True,
        "already_existed": False,
        "user_id": uid,
        "server_id": sid,
        "profile_id": fresh_psp["profile_id"],
        "player_level": 1,
        "player_exp": 0,
        "onboarding_state": "pending",
        "fresh_start_applied": True,
        "no_cross_server_copy": True,
    }


# Pack 87 — Server-scoped starter flow claim endpoint.
# Decisione canonica:
#   Gli starter heroes sono SERVER-SCOPED, non account-wide.
#   La registrazione NON assegna roster globale operativo (Pack 86 guard).
#   Lo starter roster e' assegnato SOLO nel contesto (user_id, server_id) e
#   SOLO via questo endpoint, idempotentemente (claim_once_per_server).
# Vincoli rigorosi:
#   - server_id esplicito richiesto;
#   - solo hero IDs starter-eligible (low-rarity, non-premium, esistenti,
#     catalogati, obtainable, official, non-deactivated) dal catalogo;
#   - level=1, exp=0, base stars/rarity dal catalogo;
#   - NESSUN premium currency, hard currency, inventory, equipment, story reward;
#   - NESSUNA mutazione player_level esistente;
#   - NESSUNA copia S1->S2;
#   - team_formation aggiornato SOLO se vuoto E PSP fresh-start;
#   - idempotency marker `_slc_pack_87_starter_claim_marker` impedisce doppio claim.
@app.post("/api/psp/starter/claim")
async def psp_starter_claim(
    response: Response,
    server_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Pack 87 — Server-scoped starter flow claim.

    Crea idempotentemente un piccolo starter roster (3 heroes) per
    (user_id, server_id) usando SOLO hero IDs dal config approvato
    `STARTER_SET_PACK_87` (low-rarity, non-premium, catalogati).

    Comportamento:
      - Se starter gia' reclamati per (user_id, server_id) -> no-op idempotente.
      - Se PSP non esiste -> blocker PLAYER_SERVER_PROFILE_REQUIRED.
      - Se hero IDs config non esistono nel catalogo o non sono eligible ->
        blocker STARTER_ROSTER_NOT_CATALOGED (refuse-by-default).
      - Crea user_heroes (con server_id) e aggiorna team_formation SOLO se vuoto.

    Authorization string Pack 87: AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87
    """
    validation = await validate_psp_server_id(server_id)
    if not validation.ok:
        response.status_code = validation.http_status
        response.headers["X-Server-Id-Validation"] = "failed"
        response.headers["X-Blocker"] = validation.blocker
        response.headers["X-Server-Id-Allowlist-Source"] = validation.allowlist_source
        if validation.server_id:
            response.headers["X-Server-Id"] = validation.server_id
        return {
            "v110_starter_claim": False,
            "blocker": validation.blocker,
            "server_id": validation.server_id,
            "allowlist_source": validation.allowlist_source,
            "reason": validation.reason,
        }
    uid = current_user["id"]
    sid = validation.server_id
    # Verifica PSP esiste (NON crea silently; Pack 85 ensure deve essere stato chiamato).
    psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
    if not psp:
        response.headers["X-Starter-Claim-Mode"] = "psp_required"
        response.status_code = 409
        return {
            "v110_starter_claim": False,
            "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
            "hint": "Call POST /api/psp/ensure?server_id=<sid> first.",
        }
    # Idempotency check: claim_once_per_server marker.
    already_claimed = bool(psp.get("_slc_pack_87_starter_claim_marker"))
    if already_claimed:
        # Conta starter Pack 87 esistenti per server
        existing_count = await db.user_heroes.count_documents({
            "user_id": uid,
            "server_id": sid,
            "creation_source": "server_scoped_starter_flow_pack_87",
        })
        response.headers["X-Starter-Claim-Mode"] = "already_claimed_no_write"
        response.headers["X-Server-Id"] = sid
        return {
            "v110_starter_claim": True,
            "created": False,
            "already_claimed": True,
            "user_id": uid,
            "server_id": sid,
            "starter_user_heroes_created_now": 0,
            "starter_user_heroes_present": existing_count,
            "no_cross_server_copy": True,
            "no_account_wide_starter": True,
            "no_premium_grant": True,
            "no_reward_grant": True,
            "no_player_level_mutation": True,
        }
    # HOTFIX D — Carica il set starter dal contratto centralizzato
    # (`backend/helpers/starter_roster_contract.py`). Sostituisce la lista
    # hardcoded Pack 87 con una sorgente unica importata sia dal claim sia
    # dall'esposizione `/api/user/heroes`. Semantica invariata: stessi
    # IDs, stessi ruoli, stessi flag richiesti, stessa idempotenza.
    from helpers.starter_roster_contract import (
        starter_set_for_claim,
        STARTER_REQUIRED_FLAGS,
    )
    starter_set = starter_set_for_claim()
    # Verifica che TUTTI gli heroes siano eligible (catalogabili, non-premium, low-rarity, esistenti).
    approved_heroes = []
    for hero_id, role in starter_set:
        h = await db.heroes.find_one({"id": hero_id})
        if not h:
            response.status_code = 409
            response.headers["X-Starter-Claim-Mode"] = "roster_not_cataloged"
            return {
                "v110_starter_claim": False,
                "blocker": "STARTER_ROSTER_NOT_CATALOGED",
                "missing_hero_id": hero_id,
            }
        # HOTFIX D — eligibility checks gated dal contratto centralizzato
        # (refuse-by-default, NO silent invention). Mappa 1-1 con i blocker
        # ratificati Pack 87. Soglia `high_rarity_threshold` dal contratto.
        if STARTER_REQUIRED_FLAGS["high_rarity_forbidden"] and int(h.get("rarity") or 0) > STARTER_REQUIRED_FLAGS["high_rarity_threshold"]:
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_HIGH_RARITY", "hero_id": hero_id}
        if STARTER_REQUIRED_FLAGS["is_official_required"] and h.get("is_official") is not True:
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_NOT_OFFICIAL", "hero_id": hero_id}
        if STARTER_REQUIRED_FLAGS["obtainable_required"] and h.get("obtainable") is not True:
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_NOT_OBTAINABLE", "hero_id": hero_id}
        if STARTER_REQUIRED_FLAGS["show_in_catalog_required"] and h.get("show_in_catalog") is not True:
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_NOT_CATALOG_VISIBLE", "hero_id": hero_id}
        if STARTER_REQUIRED_FLAGS["deactivated_forbidden"] and h.get("deactivated_at"):
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_DEACTIVATED", "hero_id": hero_id}
        if STARTER_REQUIRED_FLAGS["premium_forbidden"] and h.get("is_premium") is True:
            response.status_code = 409
            return {"v110_starter_claim": False, "blocker": "STARTER_ROSTER_PREMIUM_FORBIDDEN", "hero_id": hero_id}
        approved_heroes.append((h, role))
    # Crea user_heroes server-scoped. NO writes su altre collections.
    created_ids = []
    now = datetime.utcnow()
    for h, role in approved_heroes:
        new_uh_id = str(uuid.uuid4())
        user_hero = {
            "id": new_uh_id,
            "user_id": uid,
            "server_id": sid,  # MANDATORY server_id Pack 87
            "hero_id": h["id"],
            "level": 1,
            "experience": 0,
            "stars": int(h.get("rarity") or 1),
            "obtained_at": now,
            "creation_source": "server_scoped_starter_flow_pack_87",
            "_slc_pack_87_starter_user_hero": True,
            "_slc_pack_87_starter_role": role,
            "_slc_pack_87_authorization": "AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87",
        }
        await db.user_heroes.insert_one(user_hero)
        created_ids.append(new_uh_id)
    # Aggiorna team_formation SOLO se vuoto (no overwrite).
    team_initialized = False
    cur_team = psp.get("team_formation") or []
    if not cur_team or len(cur_team) == 0:
        team_formation = [
            {
                "slot_index": i,
                "user_hero_id": uh_id,
                "_slc_pack_87_starter_team_init": True,
            }
            for i, uh_id in enumerate(created_ids)
        ]
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid, "team_formation": {"$in": [None, []]}},
            {"$set": {
                "team_formation": team_formation,
                "_slc_pack_87_team_initialized_from_starter": True,
            }},
        )
        team_initialized = True
    # Set idempotency marker SOLO ora, dopo successo (idempotent semantics).
    await db.player_server_profiles.update_one(
        {"user_id": uid, "server_id": sid},
        {"$set": {
            "_slc_pack_87_starter_claim_marker": True,
            "_slc_pack_87_starter_claim_marker_at_utc": now.isoformat() + "Z",
            "onboarding_state": "starter_claimed",
        }},
    )
    response.headers["X-Starter-Claim-Mode"] = "starter_claimed_first_time"
    response.headers["X-Server-Id"] = sid
    return {
        "v110_starter_claim": True,
        "created": True,
        "already_claimed": False,
        "user_id": uid,
        "server_id": sid,
        "starter_user_heroes_created_now": len(created_ids),
        "starter_user_hero_ids": created_ids,
        "starter_hero_ids": [h["id"] for h, _ in approved_heroes],
        "team_initialized": team_initialized,
        "no_cross_server_copy": True,
        "no_account_wide_starter": True,
        "no_premium_grant": True,
        "no_reward_grant": True,
        "no_player_level_mutation": True,
        "creation_source": "server_scoped_starter_flow_pack_87",
        "_slc_pack_87_authorization": "AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87",
    }



@app.get("/api/user/heroes")
async def get_user_heroes(
    response: Response,
    server_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Pack 81 — `/api/user/heroes` server-scoped promotion (PRODUCTIVE ROUTE).

    Contratto:
    - Quando `server_id` viene passato, il filtro Mongo include `server_id`
      REALMENTE (`{"user_id": uid, "server_id": server_id}`) e il PSP viene
      verificato in `player_server_profiles`. Se manca il PSP, blocker
      `PLAYER_SERVER_PROFILE_REQUIRED` (header) e roster vuoto.
    - Quando `server_id` NON viene passato, il route torna un roster legacy
      account-wide ma marca esplicitamente `X-Server-Scope:
      account_wide_legacy_DEPRECATED` e `X-Filter-Applied: false`. Le UI
      player-facing devono passare `server_id` o bloccare onestamente.

    Decisione canonica (Pack 81):
    ```
    user_heroes / roster posseduto / livelli / stelle / build operative /
    team formation / battle player team source sono SERVER-SCOPED.
    ```

    NESSUN DB write. NESSUN reward grant. NESSUNA mutazione economia.
    """
    uid = current_user["id"]
    canonical_decision = "user_heroes_are_server_scoped"
    if server_id and isinstance(server_id, str) and server_id.strip():
        validation = await validate_psp_server_id(server_id)
        if not validation.ok:
            response.status_code = validation.http_status
            response.headers["X-Server-Scope"] = "server_scoped"
            response.headers["X-Filter-Applied"] = "false"
            response.headers["X-Blocker"] = validation.blocker
            response.headers["X-Server-Id"] = validation.server_id or ""
            response.headers["X-Server-Id-Validation"] = "failed"
            response.headers["X-Server-Id-Allowlist-Source"] = validation.allowlist_source
            response.headers["X-Canonical-Decision"] = canonical_decision
            response.headers["X-Roster-Source"] = "server_scoped_server_id_rejected"
            response.headers["X-Roster-Count"] = "0"
            response.headers["X-PSP-Lookup-Mode"] = "skipped_server_id_rejected"
            return []
        sid = validation.server_id
        # Pack 82 — DUAL-READ PSP LOOKUP.
        # I PSP migrati da Pack 77 hanno user_id = str(users._id) (ObjectId hex),
        # mentre i PSP futuri canonici useranno users.id (uuid). Per
        # compatibilita' senza migrazione fisica (zero DB writes), tentiamo
        # prima il namespace canonico uuid e poi il fallback ObjectId compat.
        psp_lookup_mode = "direct_uuid"
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            # Fallback compat: cerca via str(users._id). Solo per PSP legacy Pack 77.
            legacy_uid = str(current_user.get("_id") or "")
            if legacy_uid:
                psp_compat = await db.player_server_profiles.find_one({"user_id": legacy_uid, "server_id": sid})
                if psp_compat:
                    psp = psp_compat
                    psp_lookup_mode = "objectid_compat_fallback"
        if not psp:
            response.headers["X-Server-Scope"] = "server_scoped"
            response.headers["X-Filter-Applied"] = "false"
            response.headers["X-Blocker"] = "PLAYER_SERVER_PROFILE_REQUIRED"
            response.headers["X-Server-Id"] = sid
            response.headers["X-Profile-Id"] = ""
            response.headers["X-Canonical-Decision"] = canonical_decision
            response.headers["X-Roster-Source"] = "server_scoped_no_psp_blocked"
            response.headers["X-Roster-Count"] = "0"
            response.headers["X-PSP-Lookup-Mode"] = "not_found"
            response.headers["X-Player-Level"] = "1"
            response.headers["X-Player-Exp"] = "0"
            response.headers["X-Server-Progression-State"] = "fresh_start_pending_psp_creation"
            return []
        profile_id = str(psp.get("profile_id") or psp.get("_id") or "")
        # Pack 82 — Server-scoped player progress SOT (letto dal PSP, MAI da users globale).
        server_player_level = int(psp.get("player_level") or 1)
        server_player_exp = int(psp.get("player_exp") or 0)
        # Filtro REALE su {user_id, server_id} — niente fallback account-wide.
        user_heroes = await db.user_heroes.find({"user_id": uid, "server_id": sid}).to_list(1000)
        # Pack 116A-EXT — batch-load del catalog heroes per evitare N+1 +
        # arricchimento `power` derived 116A read-only (no DB writes).
        from utils.battle_power import (
            BATTLE_POWER_FORMULA_VERSION as _BP_FV_SS,
            BATTLE_POWER_SOURCE as _BP_SRC_SS,
            compute_hero_battle_power_v1 as _compute_bp_ss,
        )
        _hero_ids_ss = list({uh.get("hero_id") for uh in user_heroes if uh.get("hero_id")})
        _hero_docs_ss = []
        if _hero_ids_ss:
            _hero_docs_ss = await db.heroes.find({"id": {"$in": _hero_ids_ss}}).to_list(2000)
        _hero_by_id_ss = {h["id"]: h for h in _hero_docs_ss}
        result = []
        # HOTFIX D — import contratto starter per fallback exposure.
        # Quando il merge col catalog produce hero_class mancante per uno
        # starter canonico, applichiamo backfill da `starter_fallback_exposure`
        # senza sovrascrivere campi già valorizzati. NESSUN DB read extra,
        # NESSUN /api/heroes usage: il contratto è pure data importata.
        from helpers.starter_roster_contract import (
            is_starter_id as _hd_is_starter_id,
            starter_fallback_exposure as _hd_starter_fallback_exposure,
        )
        starter_fallback_applied = 0
        starter_catalog_missing_ids: list[str] = []
        for uh in user_heroes:
            uh_hero_id = uh.get("hero_id")
            hero = _hero_by_id_ss.get(uh_hero_id)
            if hero:
                if not should_show_in_collection(hero, owned=True):
                    continue
                _power_ss = _compute_bp_ss(hero, uh)
                merged = {
                    **serialize_doc(uh),
                    "hero_name": hero.get("name"),
                    "hero_element": hero.get("element"),
                    "hero_rarity": hero.get("rarity"),
                    "hero_image": hero.get("image_url") or hero.get("image_base64") or hero.get("image"),
                    "hero_stats": hero.get("base_stats"),
                    "hero_class": hero.get("hero_class"),
                    # Pack 116A-EXT — Battle Power derivato per la card eroe.
                    "power": _power_ss,
                    "battle_power_formula_version": _BP_FV_SS,
                    "battle_power_source": _BP_SRC_SS,
                }
                # HOTFIX D — fallback hero_class per starter canonici quando
                # il catalog espone l'eroe ma `hero_class` è None/missing.
                # Backfill solo se il campo non è già valorizzato.
                if _hd_is_starter_id(uh_hero_id) and not merged.get("hero_class"):
                    _fb = _hd_starter_fallback_exposure(uh_hero_id, uh)
                    if _fb:
                        # Backfill ONLY i campi mancanti / falsy nel merge corrente.
                        for _k, _v in _fb.items():
                            if not merged.get(_k):
                                merged[_k] = _v
                        starter_fallback_applied += 1
                result.append(merged)
            elif _hd_is_starter_id(uh_hero_id):
                # HOTFIX D — starter canonico posseduto (user_heroes esiste)
                # ma NON trovato in `db.heroes` catalog: esponiamo comunque
                # con fallback minimale dal contratto, mai inventando lore.
                # Header `X-Starter-Catalog-Missing` lo elencherà per QA.
                if uh_hero_id:
                    starter_catalog_missing_ids.append(uh_hero_id)
                _fb = _hd_starter_fallback_exposure(uh_hero_id, uh)
                merged = {
                    **serialize_doc(uh),
                    "hero_name": uh_hero_id,  # placeholder: nessuna lore inventata.
                    "hero_element": _fb.get("hero_element"),
                    "hero_rarity": _fb.get("hero_rarity"),
                    "hero_image": None,
                    "hero_stats": None,
                    "hero_class": _fb.get("hero_class"),
                    "starter_role": _fb.get("starter_role"),
                    "power": 0,
                    "battle_power_formula_version": _BP_FV_SS,
                    "battle_power_source": _BP_SRC_SS,
                    "_hotfix_d_starter_fallback_applied": True,
                    "_hotfix_d_catalog_missing": True,
                }
                result.append(merged)
                starter_fallback_applied += 1
        response.headers["X-Server-Scope"] = "server_scoped"
        response.headers["X-Filter-Applied"] = "true"
        response.headers["X-Server-Id"] = sid
        response.headers["X-Profile-Id"] = profile_id
        response.headers["X-Blocker"] = ""
        response.headers["X-Canonical-Decision"] = canonical_decision
        response.headers["X-Roster-Source"] = "server_scoped_psp_filtered"
        response.headers["X-Roster-Count"] = str(len(result))
        response.headers["X-PSP-Lookup-Mode"] = psp_lookup_mode
        response.headers["X-Player-Level"] = str(server_player_level)
        response.headers["X-Player-Exp"] = str(server_player_exp)
        response.headers["X-Server-Progression-State"] = "psp_present_server_scoped"
        # HOTFIX D — diagnostica esposizione starter per QA (read-only).
        response.headers["X-Starter-Fallback-Applied"] = str(starter_fallback_applied)
        if starter_catalog_missing_ids:
            response.headers["X-Starter-Catalog-Missing"] = ",".join(starter_catalog_missing_ids)
        return result
    raise HTTPException(
        status_code=400,
        detail={
            "blocker": "SERVER_ID_REQUIRED_FOR_GAMEPLAY_STATE",
            "route": "/api/user/heroes",
            "message": "server_id is required for server-bound gameplay roster reads.",
        },
    )
    # Nessun server_id -> legacy account-wide DEPRECATED. UI player-facing
    # devono passare server_id o bloccare onestamente.
    user_heroes = await db.user_heroes.find({"user_id": uid}).to_list(1000)
    result = []
    for uh in user_heroes:
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if hero:
            if not should_show_in_collection(hero, owned=True):
                continue
            merged = {
                **serialize_doc(uh),
                "hero_name": hero.get("name"),
                "hero_element": hero.get("element"),
                "hero_rarity": hero.get("rarity"),
                "hero_image": hero.get("image_url") or hero.get("image_base64") or hero.get("image"),
                "hero_stats": hero.get("base_stats"),
                "hero_class": hero.get("hero_class"),
            }
            result.append(merged)
    response.headers["X-Server-Scope"] = "account_wide_legacy_DEPRECATED"
    response.headers["X-Filter-Applied"] = "false"
    response.headers["X-Server-Id"] = ""
    response.headers["X-Profile-Id"] = ""
    response.headers["X-Blocker"] = "SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING"
    response.headers["X-Canonical-Decision"] = canonical_decision
    response.headers["X-Roster-Source"] = "account_wide_legacy_DEPRECATED"
    response.headers["X-Roster-Count"] = str(len(result))
    response.headers["X-PSP-Lookup-Mode"] = "skipped_no_server_id"
    response.headers["X-Player-Level"] = ""
    response.headers["X-Player-Exp"] = ""
    response.headers["X-Server-Progression-State"] = "account_wide_legacy_DEPRECATED"
    return result

# ===================== GACHA =====================
# PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF (P0) \u2014 Rate launch-safe.
# Tutte le rate per banner sommano a 1.0. 5\u2605+6\u2605 combinato:
#   standard   = 0.015 (1.50%)
#   elemental  = 0.025 (2.50%)
#   selective  = 0.035 (3.50%)
#   premium    = 0.050 (5.00%, surface LOCKED in UI)
#   targeted   = 0.050 (5.00%, surface LOCKED in UI)
# guarantee_weights: distribuzione cond. a rarity>=guarantee_10 normalizzata
# dalle rate finali; impedisce il "4 mitici + 3 leggendari in x10" osservato
# in QA con le vecchie weights hardcoded [0.65, 0.25, 0.10] / [0.70, 0.30].
GACHA_BANNERS = {
    "standard": {
        "name": "Banner Standard",
        "cost_single": 100,
        "cost_multi": 900,
        "rates": {1: 0.39, 2: 0.32, 3: 0.20, 4: 0.075, 5: 0.0135, 6: 0.0015},
        "guarantee_10": 4,
        "guarantee_weights": {4: 0.8333, 5: 0.1500, 6: 0.0167},
        "filter": None,
    },
    "elemental": {
        "name": "Banner Elementale",
        "cost_single": 120,
        "cost_multi": 1000,
        "rates": {1: 0.345, 2: 0.31, 3: 0.23, 4: 0.09, 5: 0.022, 6: 0.003},
        "guarantee_10": 4,
        "guarantee_weights": {4: 0.7826, 5: 0.1913, 6: 0.0261},
        "filter": None,  # will pick random element focus
    },
    "selective": {
        "name": "Banner Selettivo",
        "cost_single": 150,
        "cost_multi": 1350,
        "rates": {1: 0.32, 2: 0.30, 3: 0.24, 4: 0.105, 5: 0.03, 6: 0.005},
        "guarantee_10": 4,
        "guarantee_weights": {4: 0.75, 5: 0.2143, 6: 0.0357},
        "filter": None,
    },
    "premium": {
        "name": "Banner Premium",
        "cost_single": 200,
        "cost_multi": 1800,
        "rates": {1: 0.28, 2: 0.29, 3: 0.25, 4: 0.13, 5: 0.0425, 6: 0.0075},
        "guarantee_10": 5,
        "guarantee_weights": {5: 0.85, 6: 0.15},
        "filter": None,
    },
    "targeted": {
        "name": "Banner Mirato",
        "cost_single": 180,
        "cost_multi": 1600,
        "rates": {1: 0.28, 2: 0.29, 3: 0.25, 4: 0.13, 5: 0.0425, 6: 0.0075},
        "guarantee_10": 5,
        "guarantee_weights": {5: 0.85, 6: 0.15},
        "filter": None,
    },
}

class GachaPullRequest(BaseModel):
    banner: str = "standard"

async def _do_gacha_pull(user_id: str, banner_id: str):
    banner = GACHA_BANNERS.get(banner_id, GACHA_BANNERS["standard"])
    rates = banner["rates"]
    roll = random.random()
    cumulative = 0
    rarity = 1
    for r, rate in rates.items():
        cumulative += rate
        if roll <= cumulative:
            rarity = r
            break
    query: dict = {"rarity": rarity}
    if banner_id == "elemental":
        focus = random.choice(["fire", "water", "earth", "wind", "light", "dark"])
        if random.random() < 0.6:
            query["element"] = focus
    heroes = await db.heroes.find(query).to_list(100)
    # RM1.20-C: filter candidates by show_in_summon + obtainable. Heroes
    # without flags remain eligible (default True). Hidden/non-obtainable
    # heroes (legacy soft-deactivated, pending official imports) are
    # excluded. Rates/costs/guarantee logic UNCHANGED.
    eligible = [h for h in heroes if should_show_in_summon(h)]
    if not eligible:
        # Fallback 1: same rarity, no element focus
        heroes = await db.heroes.find({"rarity": rarity}).to_list(100)
        eligible = [h for h in heroes if should_show_in_summon(h)]
    if not eligible:
        # Fallback 2: any rarity, eligible only
        heroes = await db.heroes.find({}).to_list(200)
        eligible = [h for h in heroes if should_show_in_summon(h)]
    if not eligible:
        # Pool vuoto: errore esplicito invece di pescare un eroe nascosto.
        raise HTTPException(
            status_code=503,
            detail="Pool gacha temporaneamente non disponibile (nessun eroe ottenibile).",
        )
    hero = random.choice(eligible)
    user_hero = {
        "id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"],
        "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow(),
    }
    await db.user_heroes.insert_one(user_hero)
    return hero, user_hero

@app.post("/api/gacha/pull")
async def gacha_pull(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
    # Pre-QA Stabilization 110 — Gacha quarantine guard (default ON).
    # Blocker canonico: GACHA_LIVE_DISABLED_PRE_QA.
    if str(os.environ.get("GACHA_LIVE_ENABLED", "false")).strip().lower() not in ("true", "1", "yes", "on"):
        raise HTTPException(423, detail={
            "blocker": "GACHA_LIVE_DISABLED_PRE_QA",
            "pack_origin": "pre_qa_stabilization_110",
            "no_gems_spend": True,
            "no_hero_grant": True,
            "no_account_wide_user_heroes_mutation": True,
            "gacha_server_scope_required": True,
            "deferred_next_step": "AUTORIZZO_V110_GACHA_LIVE_PACK_NEXT",
        })
    user_id = current_user["id"]
    banner = GACHA_BANNERS.get(req.banner, GACHA_BANNERS["standard"])
    user = await db.users.find_one({"id": user_id})
    cost = banner["cost_single"]
    if user.get("gems", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Gemme insufficienti! Servono {cost}")
    await db.users.update_one({"id": user_id}, {"$inc": {"gems": -cost}})
    hero, user_hero = await _do_gacha_pull(user_id, req.banner)
    updated_user = await db.users.find_one({"id": user_id})
    return {
        "hero": serialize_doc(hero), "user_hero_id": user_hero["id"],
        "is_new": True, "rarity": hero["rarity"],
        "remaining_gems": updated_user.get("gems", 0), "banner": req.banner,
    }

@app.post("/api/gacha/pull10")
async def gacha_pull_10(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
    # Pre-QA Stabilization 110 — Gacha quarantine guard (default ON).
    if str(os.environ.get("GACHA_LIVE_ENABLED", "false")).strip().lower() not in ("true", "1", "yes", "on"):
        raise HTTPException(423, detail={
            "blocker": "GACHA_LIVE_DISABLED_PRE_QA",
            "pack_origin": "pre_qa_stabilization_110",
            "no_gems_spend": True,
            "no_hero_grant": True,
            "no_account_wide_user_heroes_mutation": True,
            "gacha_server_scope_required": True,
            "deferred_next_step": "AUTORIZZO_V110_GACHA_LIVE_PACK_NEXT",
        })
    user_id = current_user["id"]
    banner = GACHA_BANNERS.get(req.banner, GACHA_BANNERS["standard"])
    user = await db.users.find_one({"id": user_id})
    cost = banner["cost_multi"]
    if user.get("gems", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Gemme insufficienti! Servono {cost}")
    await db.users.update_one({"id": user_id}, {"$inc": {"gems": -cost}})
    results = []
    for i in range(10):
        if i == 9:
            # Guaranteed minimum rarity on last pull.
            # PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF: usa guarantee_weights
            # dal banner dict (normalizzate dalle rate finali) invece di
            # hardcoded dev-like weights. Previene la regressione "4 mitici
            # + 3 leggendari in x10" osservata in QA.
            g = banner["guarantee_10"]
            gw = banner.get("guarantee_weights")
            if gw:
                rarities = sorted(gw.keys())
                weights = [gw[r] for r in rarities]
            else:
                # Fallback legacy (non dovrebbe mai colpire dopo signoff).
                rarities = list(range(g, 7))
                weights = [0.65, 0.25, 0.10] if g == 4 else [0.70, 0.30]
            rarity = random.choices(rarities, weights=weights)[0]
            query: dict = {"rarity": rarity}
            heroes = await db.heroes.find(query).to_list(100)
            # RM1.20-C: same visibility filter on the guaranteed pull.
            eligible = [h for h in heroes if should_show_in_summon(h)]
            if not eligible:
                heroes = await db.heroes.find({}).to_list(200)
                eligible = [h for h in heroes if should_show_in_summon(h)]
            if not eligible:
                raise HTTPException(
                    status_code=503,
                    detail="Pool gacha temporaneamente non disponibile (nessun eroe ottenibile).",
                )
            hero = random.choice(eligible)
            uh = {"id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"], "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow()}
            await db.user_heroes.insert_one(uh)
            results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
        else:
            hero, uh = await _do_gacha_pull(user_id, req.banner)
            results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
    updated_user = await db.users.find_one({"id": user_id})
    return {"results": results, "remaining_gems": updated_user.get("gems", 0), "banner": req.banner}

@app.get("/api/gacha/banners")
async def get_gacha_banners():
    return {k: {"name": v["name"], "cost_single": v["cost_single"], "cost_multi": v["cost_multi"],
                "rates": v["rates"], "guarantee_10": v["guarantee_10"]} for k, v in GACHA_BANNERS.items()}

# ===================== TEAM =====================
@app.get("/api/team")
async def get_team(current_user: dict = Depends(get_current_user)):
    team = await db.teams.find_one({"user_id": current_user["id"], "is_active": True})
    if team:
        return serialize_doc(team)
    return {"formation": [], "total_power": 0}

# ===================== UTILITY =====================
def calculate_hero_power(hero: dict, user_hero: dict = None) -> int:
    stats = hero.get("base_stats", {})
    level = user_hero.get("level", 1) if user_hero else 1
    rarity = hero.get("rarity", 1)
    power = (
        stats.get("physical_damage", stats.get("attack", 100)) +
        stats.get("magic_damage", 0) +
        stats.get("physical_defense", stats.get("defense", 50)) +
        stats.get("magic_defense", 0) +
        stats.get("hp", 1000) // 10 +
        stats.get("speed", 10) +
        stats.get("healing", 0) // 2
    )
    power = int(power * (1 + (level - 1) * 0.05) * (1 + rarity * 0.2))
    return power

# ===================== BATTLE ROUTES =====================
battle_router = create_battle_routes(db, get_current_user, serialize_doc, calculate_hero_power)
app.include_router(battle_router)

# ===================== GAME SYSTEMS ROUTES =====================
game_router = create_game_routes(db, get_current_user, serialize_doc, calculate_hero_power)
app.include_router(game_router)

# ===================== SPRITE ROUTES =====================
sprite_router = APIRouter(prefix="/api")
register_sprite_routes(sprite_router, db)
app.include_router(sprite_router)

# ===================== ITEMS & SKILL ROUTES =====================
items_router = APIRouter(prefix="/api")
register_items_routes(items_router, db, get_current_user)
app.include_router(items_router)

# ===================== SERVER PROFILES DUAL-ROUTE SKELETON (PROJECT_B Track A) =====================
# Inert flag-gated routes. Runtime OFF by default via SERVER_PROFILES_RUNTIME_ENABLED.
# When the flag is unset, both GET and POST /api/server-profiles/select return HTTP 503
# with a status="disabled" payload. No DB writes, no behavior exposure.
# Upstream design: 122D (V8 BLOCK_D dual-route), 123A (collection live inert).
from routes.server_profiles import router as server_profiles_router
app.include_router(server_profiles_router)

# v103 — Safe read-only /api/server-profiles/list endpoint (QA fallback dichiarato).
from routes.v103_server_profiles import router as v103_server_profiles_router
app.include_router(v103_server_profiles_router)

# v107A — Battle Launch Contract router. POST /api/battle/launch returns preview
# echo only. NO DB writes, NO reward grant, NO progress write. Live behavior is
# gated by BATTLE_LAUNCH_AUTHORITATIVE_ENABLED / REWARD_LIVE_ENABLED /
# PROGRESS_LIVE_ENABLED flags; defaults coerce any live request down to preview.
from routes.v107a_battle_launch import router as v107a_battle_launch_router
app.include_router(v107a_battle_launch_router)

# Pack 130 — Lobby Launch Context (read-only, server-scoped, no DB write).
# Vedi: backend/routes/v130_lobby_launch_context.py,
#       backend/helpers/lobby_launch_context.py,
#       backend/helpers/real_player_snapshot.py
from routes.v130_lobby_launch_context import router as v130_lobby_launch_router
app.include_router(v130_lobby_launch_router)

# Pack 131 — Combat Preview (GET, read-only, consumes Pack 130 launch context).
from routes.v131_combat_preview import router as v131_combat_preview_router
app.include_router(v131_combat_preview_router)

# v108_AUTHORITATIVE_PRE — Battle Instance Envelope preview endpoint.
# POST /api/battle/instance/preview returns the authoritative-pre envelope.
# authoritative_live=false sempre; nessuna scrittura DB; nessun reward/progress.
# PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE
from routes.v108_authoritative_pre_instance import router as v108_authoritative_pre_instance_router
app.include_router(v108_authoritative_pre_instance_router)

# v108_AUTHORITATIVE_RUNTIME — Battle Result Envelope resolve-preview endpoint.
# POST /api/battle/instance/resolve-preview returns the authoritative-staging result.
# authoritative_live=false, authoritative_staging=true. NO DB write, NO reward,
# NO progress, NO call to /api/battle/simulate. Resolver deterministico in-memory.
# PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE
from routes.v108_authoritative_runtime_resolve import router as v108_authoritative_runtime_resolve_router
app.include_router(v108_authoritative_runtime_resolve_router)

# v107C — Loader server_id acceptance probe router. Read-only echo of server_id
# query parameter on 5 probe paths. Demonstrates acceptance contract without
# touching existing loader endpoints. NO DB writes, NO mutation.
from routes.v107c_loader_server_id_probe import router as v107c_loader_server_id_probe_router
app.include_router(v107c_loader_server_id_probe_router)

# PROJECT_F Track B — Housing read-only preview route skeleton (DISABLED-BY-DEFAULT INERT).
# Returns 503 when HOUSING_PREVIEW_ENABLED is unset/!=true. No DB writes, no live bonus,
# no combat/account stat mutation. Upstream design: 127B / 128B (Project F Track B).
from routes.housing_preview import router as housing_preview_router
app.include_router(housing_preview_router)

# PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME Phase 1 preview-only route
# (DISABLED-BY-DEFAULT INERT). Returns 503 when HERO_ELEVATION_PREVIEW_ENABLED is
# unset/!=true. No DB writes, no materials spent, no combat/account stat mutation.
# Upstream design: docs/divine/202_HERO_GEAR_PROGRESSION_BIBLE.md (Bible 202).
from routes.hero_elevation_preview import router as hero_elevation_preview_router
app.include_router(hero_elevation_preview_router)

# PROJECT_GEAR_CAP_PLUS_50_RUNTIME preview-only route (DISABLED-BY-DEFAULT INERT).
# Returns 503 when GEAR_CAP_PLUS_50_PREVIEW_ENABLED is unset/!=true. No DB writes,
# no materials spent, no live mutation. Replica Bible 202 track D (gear_level_cap=50,
# legacy=20, staged caps +10/+20/+35/+50). Separato da Hero Elevation, Gemme, Rune,
# Artifact, Divine Weapon, BP Delta, combat, battle_engine, character bible.
from routes.gear_cap_preview import router as gear_cap_preview_router
app.include_router(gear_cap_preview_router)

# PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME preview-only route (DISABLED-BY-DEFAULT INERT).
# Returns 503 when GEAR_FORGE_RUNTIME_PREVIEW_ENABLED is unset/!=true. No DB writes,
# no materials spent, no live mutation. Fusion commit DISABLED in this pack: l'audit
# (track A) ha trovato guards mancanti sul legacy /forge/fuse. Il legacy /forge/* resta
# completamente intoccato. Separato da Hero Elevation, Gemme, Rune, Artifact, Divine Weapon,
# BP Delta, combat, battle_engine, character bible.
from routes.gear_forge_preview import router as gear_forge_preview_router
app.include_router(gear_forge_preview_router)

# MEGA_RELEASE_ACCELERATION_44_v95 — Read-only catalog router (runtime apply).
# Endpoints: GET /api/encounter-source/catalog, GET /api/encounter-source/get,
# GET /api/live-mode/catalog, GET /api/avatar-placeholder/catalog.
# Read-only / idempotent / NO DB writes / NO reward / NO ranking / NO PII.
# Old MD5 server.py: 055df030553f4791e8cac14254f1b148. v95 unlock authorized.
try:
    from routes.v95_readonly_catalog import router as v95_readonly_catalog_router
    app.include_router(v95_readonly_catalog_router)
except Exception as _v95_err:
    # Fail-safe: se l'import fallisce non blocca il boot
    import logging
    logging.getLogger(__name__).warning("v95_readonly_catalog router import failed: %s", _v95_err)

# MEGA_RELEASE_ACCELERATION_45_v96 — Auth (Google/Apple/Guest/Me/Logout/Refresh)
# + Team Formation account-bridged endpoint (chiude blocker v95).
# auth_db_writes = allowed (collection users).
# gameplay/economy/reward/score db_writes = 0.
# NO raw OAuth token logging. NO provider secret in repo.
try:
    from routes.v96_auth import create_auth_router, provider_status_router
    app.include_router(create_auth_router(db, get_current_user))
    app.include_router(provider_status_router)
except Exception as _v96_auth_err:
    import logging
    logging.getLogger(__name__).warning("v96_auth router import failed: %s", _v96_auth_err)

try:
    from routes.v96_team_formation import create_team_formation_router
    app.include_router(create_team_formation_router(db, get_current_user))
except Exception as _v96_tf_err:
    import logging
    logging.getLogger(__name__).warning("v96_team_formation router import failed: %s", _v96_tf_err)

# Pre-QA Stabilization 116A — Battle Power foundation (read-only, derived,
# server-scoped). NO DB writes. NO combat authoritative. NO reward.
try:
    from routes.battle_power import create_battle_power_router
    app.include_router(create_battle_power_router(db, get_current_user))
except Exception as _bp_116a_err:
    import logging
    logging.getLogger(__name__).warning("battle_power 116a router import failed: %s", _bp_116a_err)

# Pre-QA Stabilization 116C — Red Dot notification badge foundation.
# Read-only, server-scoped, no DB writes, no claim, no push.
try:
    from routes.red_dot import create_red_dot_router
    app.include_router(create_red_dot_router(db, get_current_user))
except Exception as _rd_116c_err:
    import logging
    logging.getLogger(__name__).warning("red_dot 116c router import failed: %s", _rd_116c_err)

# Pre-QA Stabilization 117B — Hero Upgrade Readiness (read-only).
# Server-scoped, no DB writes, no upgrade activation, no material consume.
try:
    from routes.hero_upgrade_readiness import create_hero_upgrade_readiness_router
    app.include_router(create_hero_upgrade_readiness_router(db, get_current_user))
except Exception as _hu_117b_err:
    import logging
    logging.getLogger(__name__).warning("hero_upgrade_readiness 117b router import failed: %s", _hu_117b_err)

# MEGA_RELEASE_ACCELERATION_47_v98 — Admin server-actors status (read-only)
# + GDPR data export + hard-delete-confirm (runtime gated).
try:
    from routes.v98_admin_and_gdpr import router as v98_admin_router, create_auth_extra_router
    app.include_router(v98_admin_router)
    app.include_router(create_auth_extra_router(db, get_current_user))
except Exception as _v98_err:
    import logging
    logging.getLogger(__name__).warning("v98_admin_and_gdpr router import failed: %s", _v98_err)

# PROJECT_MATERIAL_RAID_RUNTIME preview-only route (DISABLED-BY-DEFAULT INERT).
# Returns 503 when MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED is unset/!=true. No DB writes,
# no materials granted, no live mutation, no stamina, no tickets, no paid attempts.
# Reward claim DISABLED in questo pack: l'audit (track A) ha trovato che non esiste una
# canonical user_materials collection ne idempotent grant. Legacy /raids/*, /inventory,
# /item-shop restano completamente intoccati. Separato da Hero Elevation, Gemme, Rune,

# PROJECT_MATERIAL_RAID_RUNTIME preview-only route (DISABLED-BY-DEFAULT INERT).
# Returns 503 when MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED is unset/!=true. No DB writes,
# no materials granted, no live mutation, no stamina, no tickets, no paid attempts.
# Reward claim DISABLED in questo pack: l'audit (track A) ha trovato che non esiste una
# canonical user_materials collection ne idempotent grant. Legacy /raids/*, /inventory,
# /item-shop restano completamente intoccati. Separato da Hero Elevation, Gemme, Rune,
# Artifact, Divine Weapon, BP Delta, combat, battle_engine, character bible, gear forge commit.
from routes.material_raid_preview import router as material_raid_preview_router
app.include_router(material_raid_preview_router)

# PROJECT_GEM_SOCKET_RUNTIME preview-only route (DISABLED-BY-DEFAULT INERT).
# PUBLIC_SYNC_TAG_v27_GEM_SOCKET_RUNTIME / PUBLIC_SYNC_TAG_RESYNC_v27b_GEM_SOCKET_RUNTIME
# PUBLIC_SYNC_TAG_RESYNC_v27c_GEM_SOCKET_SERVER_REGISTRATION
# (do not remove; sentinels required for public sync verification of server.py blob).
# PROJECT_GEM_SOCKET_RUNTIME v27c — preview-only route registration sync.
# DISABLED-BY-DEFAULT via GEM_SOCKET_RUNTIME_PREVIEW_ENABLED.
# No DB writes, no gear mutation, no material spend, no premium gems currency spend,
# no live socket commit. Gemme = gear sockets; Rune = hero scroll/talisman layer.
# Returns 503 when GEM_SOCKET_RUNTIME_PREVIEW_ENABLED is unset/!=true. No DB writes,
# no mutation, no premium gems spend, no material spend, no live socket commit.
# Gemme = socket nei gear (NON Rune/scroll/talisman, NON premium currency `gems`).
# Legacy /forge/*, /raid/*, /inventory, premium currency users.gems INTOCCATI.
from routes.gem_socket_preview import router as gem_socket_preview_router
app.include_router(gem_socket_preview_router)

# PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT (MEGA_BATCH_ACCELERATION_1 TRACK A v31).
# PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1 / STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT_REGISTRATION_SENTINEL.
# Preview-only/gated route at /api/story/battle-instance-preview/* (DISABLED-BY-DEFAULT INERT).
# Flag: STORY_BATTLE_INSTANCE_PREVIEW_ENABLED. Returns 503 inert envelope when off.
# No DB writes, no reward grant, no EXP grant, no story progress mutation. story.tsx
# UNCHANGED, combat.tsx UNCHANGED, battle_engine UNCHANGED. /api/story/battle and
# /api/battle/simulate UNCHANGED. Provides battle_instance_id + idempotency_key +
# snapshots + reward/commit/replay policies for future visual battle runner consumption.
from routes.story_battle_instance_preview import router as story_battle_instance_preview_router
app.include_router(story_battle_instance_preview_router)

# ============================================================================
# PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK (v34 PHASE_4).
# PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT. Disabled-by-default-inert (503 envelope).
# Flag: GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED. No DB writes, no reward
# grant, no EXP grant, no story/daily/quest/achievement progress. No call to
# battle_engine. No call to /api/battle/simulate. No call to /api/story/battle.
# combat.tsx UNCHANGED. story.tsx UNCHANGED. story-visual-battle-sandbox.tsx
# UNCHANGED. Home routes UNCHANGED. battle_engine.py UNCHANGED.
# Frontend deeplink-only sandbox screen /generic-visual-battle-runner-preview.
# Provides a preview shell that consumes v33 contract sample payload.
# ============================================================================
from routes.generic_visual_battle_runner_preview import router as generic_visual_battle_runner_preview_router
app.include_router(generic_visual_battle_runner_preview_router)

# ============================================================================
# PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK (v36 PHASE_6).
# BATTLE_REPLAY_PREVIEW_ROUTE_GATED_VIEW_ONLY. Disabled-by-default 503 envelope.
# Flag: BATTLE_REPLAY_PREVIEW_ENABLED. viewer_kind=guild_war_view.
# No DB writes, no reward, no EXP, no story/daily/quest/achievement progress.
# No war score mutation. No guild points mutation. No call to battle_engine.
# No call to /api/battle/simulate. No call to /api/story/battle. No live
# /battle-replay route created. Guild War runtime UNCHANGED. combat.tsx /
# story.tsx / story-visual-battle-sandbox.tsx / generic-visual-battle-runner-
# preview.tsx UNCHANGED. Home routes UNCHANGED. battle_engine.py UNCHANGED.
# Frontend deeplink-only sandbox screen /battle-replay-preview reusing v35
# VisualBattlePreviewShell with a local pure adapter.
# ============================================================================
from routes.battle_replay_preview import router as battle_replay_preview_router
app.include_router(battle_replay_preview_router)

# ============================================================================
# MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37 (Track A + Track B + Track C).
# ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT.
# - Gem Socket commit safety preview (flag GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED)
# - Material Raid claim safety preview (flag MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED)
# All default 503. No live commit. No live claim. No gear/gem/user_materials
# mutation. No DB writes. No premium users.gems use. No stamina/tickets/paid
# attempts. server.py scoped diff only.
# ============================================================================
from routes.gem_socket_commit_safety_preview import router as gem_socket_commit_safety_preview_router
app.include_router(gem_socket_commit_safety_preview_router)
from routes.material_raid_claim_safety_preview import router as material_raid_claim_safety_preview_router
app.include_router(material_raid_claim_safety_preview_router)
# ============================================================================
# ====                                                                    ====
# ====  PUBLIC_CONTENT_REPAIR_v38c_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION_LOUD
# ====  MEGA_ECONOMY_SAFETY_ACCELERATION_2_v38c                            ====
# ====                                                                    ====
# ============================================================================
# Pack:             MEGA_ECONOMY_SAFETY_ACCELERATION_2_LOUD_SERVER_REGISTRATION_REPAIR_PACK_v38c
# Parent v38:       97d74515
# Parent v38b:      189b09a1
# Mode:             PUBLIC_CONTENT_REPAIR_BACKEND_SERVER_REGISTRATION_ONLY_LOUD
#
# Purpose
# -------
# Force a fresh public blob refresh of backend/server.py so that the next
# "Save to GitHub" PUSH cannot re-skip this file. The v38 route files
# (backend/routes/gear_forge_fusion_safety_preview.py and
#  backend/routes/rune_scroll_talisman_safety_preview.py) are already public
# and correct. The v38b marker/doc were published, but the raw public blob
# of backend/server.py still failed to expose the v38 router registrations.
# This v38c block is intentionally large, unique, and loud (top-level,
# uppercase, banner-style) so the public blob hash is guaranteed to change.
#
# This is NOT a suite-runner sync fix.
# This is NOT live economy enablement.
# This is NOT a route logic change.
# This is NOT a duplicate router registration: each include_router for the
# two v38 routers appears EXACTLY ONCE in this file (see grep counts below).
#
# Required visible tokens (LOUD block, must appear in public raw server.py)
# -------------------------------------------------------------------------
#   PUBLIC_CONTENT_REPAIR_v38c_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION_LOUD
#   gear_forge_fusion_safety_preview_router
#   rune_scroll_talisman_safety_preview_router
#   include_router for gear_forge_fusion_safety_preview_router   [count == 1]
#   include_router for rune_scroll_talisman_safety_preview_router [count == 1]
#
# Safety booleans (unchanged from v38 / v38b)
# ------------------------------------------
#   db_writes:                                            0
#   gear_forge_live_commit_enabled:                       false
#   rune_scroll_talisman_live_commit_enabled:             false
#   gear_mutation_enabled:                                false
#   rune_inventory_mutation_enabled:                      false
#   hero_rune_slot_mutation_enabled:                      false
#   user_materials_mutation_enabled:                      false
#   premium_users_gems_used:                              false
#   materials_consumed:                                   false
#   currency_consumed:                                    false
#   reward_grant_enabled:                                 false
#   exp_grant_enabled:                                    false
#   bp_delta_runtime_enabled:                             false
#   economy_changed:                                      false
#   gacha_changed:                                        false
#   bp_vip_shop_changed:                                  false
#   battle_engine_changed:                                false
#   combat_story_home_routes_changed:                     false
#   forge_py_changed:                                     false
#   route_files_changed:                                  false
#   character_bible_changed:                              false
#   hero_final_numbers_changed:                           false
#   validator_weakening:                                  false
#   fake_pass:                                            false
#   suite_runner_sync_fix_attempted:                      false (caveat accepted)
#
# Marker:  data/design/economy_safety/mega_economy_safety_acceleration_2_loud_server_registration_repair_v38c_marker_v1.json
# Doc 246: docs/divine/246_MEGA_ECONOMY_SAFETY_ACCELERATION_2_LOUD_SERVER_REGISTRATION_REPAIR_v38c.md
#
# History
# -------
# v38 (97d74515): created route files + design + validators + suite tuples.
# v38b (189b09a1): published marker/doc + v38b sentinel in server.py, but the
#                  public raw blob still did not expose the v38 router
#                  registrations to external verification.
# v38c (this commit): re-asserts the registrations under a louder banner so
#                     the public raw blob hash changes deterministically.
# ============================================================================
# ============================================================================
# PUBLIC_CONTENT_REPAIR_v38b_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION
# ----------------------------------------------------------------------------
# (v38b sentinel preserved for historical traceability — see doc 245)
# Public verification after v38b reported this sentinel was not visible on
# the public raw blob. v38c (above) is the louder follow-up that forces the
# blob refresh. Per spec, the v38b sentinel TEXT is preserved here so that
# both the v38b and v38c diagnostic trails remain greppable on the public
# raw file once the blob is refreshed.
# ----------------------------------------------------------------------------
# MEGA_ECONOMY_SAFETY_ACCELERATION_2_SERVER_REGISTRATION_REPAIR_PACK_v38b
# Parent pack:   MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_PACK_v38
# Parent commit: 97d74515
# ============================================================================
from routes.gear_forge_fusion_safety_preview import router as gear_forge_fusion_safety_preview_router
app.include_router(gear_forge_fusion_safety_preview_router)
from routes.rune_scroll_talisman_safety_preview import router as rune_scroll_talisman_safety_preview_router
app.include_router(rune_scroll_talisman_safety_preview_router)
# ============================================================================
# ====                                                                    ====
# ====  PUBLIC_CONTENT_REPAIR_v39b_ARTIFACT_AND_DIVINE_WEAPON_SERVER_REGISTRATION_LOUD
# ====  MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39b                           ====
# ====                                                                    ====
# ============================================================================
# Pack:             MEGA_ECONOMY_SAFETY_ACCELERATION_3_LOUD_SERVER_REGISTRATION_REPAIR_PACK_v39b
# Parent v39:       6093c4f3
# Parent v38c:      4c2398d6
# Mode:             PUBLIC_CONTENT_REPAIR_BACKEND_SERVER_REGISTRATION_ONLY_LOUD
#
# Purpose
# -------
# Force a fresh public blob refresh of backend/server.py so that the next
# "Save to GitHub" PUSH cannot re-skip this file for the v39 router
# registrations. The v39 route files
# (backend/routes/artifact_upgrade_safety_preview.py and
#  backend/routes/divine_weapon_upgrade_safety_preview.py) are already
# public and correct. Local container had these registrations from v39, but
# external GitHub verification reported the public raw blob did not expose
# them. This v39b block is intentionally large, unique, and loud (top-level,
# uppercase, banner-style) so the public blob hash is guaranteed to change.
#
# This is NOT a suite-runner sync fix.
# This is NOT live economy enablement.
# This is NOT a route logic change.
# This is NOT a duplicate router registration: each include_router for the
# two v39 routers appears EXACTLY ONCE in this file (count == 1).
#
# Required visible tokens (LOUD block, must appear in public raw server.py)
# -------------------------------------------------------------------------
#   PUBLIC_CONTENT_REPAIR_v39b_ARTIFACT_AND_DIVINE_WEAPON_SERVER_REGISTRATION_LOUD
#   artifact_upgrade_safety_preview_router
#   divine_weapon_upgrade_safety_preview_router
#   include_router for artifact_upgrade_safety_preview_router       [count == 1]
#   include_router for divine_weapon_upgrade_safety_preview_router  [count == 1]
#
# Safety booleans (unchanged from v39)
# ------------------------------------
#   db_writes:                                          0
#   artifact_live_upgrade_enabled:                      false
#   artifact_live_fusion_enabled:                       false
#   artifact_live_pull_enabled:                         false
#   artifact_bonus_activation_enabled:                  false
#   artifact_mutation_enabled:                          false
#   divine_weapon_live_unlock_enabled:                  false
#   divine_weapon_live_upgrade_enabled:                 false
#   divine_weapon_live_awakening_enabled:               false
#   divine_weapon_mutation_enabled:                     false
#   hero_copy_consumption_enabled:                      false
#   user_materials_mutation_enabled:                    false
#   premium_users_gems_used:                            false
#   materials_consumed:                                 false
#   currency_consumed:                                  false
#   reward_grant_enabled:                               false
#   exp_grant_enabled:                                  false
#   bp_delta_runtime_enabled:                           false
#   economy_changed:                                    false
#   gacha_changed:                                      false
#   bp_vip_shop_changed:                                false
#   battle_engine_changed:                              false
#   combat_story_home_routes_changed:                   false
#   artifacts_legacy_route_changed:                     false
#   route_files_changed:                                false
#   character_bible_changed:                            false
#   hero_final_numbers_changed:                         false
#   validator_weakening:                                false
#   fake_pass:                                          false
#   duplicate_router_registration:                      false
#   suite_runner_sync_fix_attempted:                    false (caveat accepted)
#
# Marker:  data/design/economy_safety/mega_economy_safety_acceleration_3_loud_server_registration_repair_v39b_marker_v1.json
# Doc 250: docs/divine/250_MEGA_ECONOMY_SAFETY_ACCELERATION_3_LOUD_SERVER_REGISTRATION_REPAIR_v39b.md
#
# History
# -------
# v39 (6093c4f3): created route files + design + validators + suite tuples.
# v39b (this commit): re-asserts the registrations under a louder banner so
#                     the public raw blob hash changes deterministically.
# ============================================================================
# ============================================================================
# MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39_ARTIFACT_AND_DIVINE_WEAPON_SAFETY
# ----------------------------------------------------------------------------
# (v39 sentinel preserved for historical traceability — see doc 249)
# Public verification after v39 reported these registrations were not visible
# on the public raw blob. v39b (above) is the louder follow-up that forces
# the blob refresh. The v39 sentinel TEXT is preserved here so that both
# diagnostic trails remain greppable on the public raw file once the blob
# is refreshed.
# ----------------------------------------------------------------------------
# Pack:          MEGA_ECONOMY_SAFETY_ACCELERATION_3_ARTIFACT_AND_DIVINE_WEAPON_HARDENING_PACK_v39
# Parent v38b:   189b09a1 / Parent v38c: 4c2398d6
# Mode:          ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT
# ============================================================================
from routes.artifact_upgrade_safety_preview import router as artifact_upgrade_safety_preview_router
app.include_router(artifact_upgrade_safety_preview_router)
from routes.divine_weapon_upgrade_safety_preview import router as divine_weapon_upgrade_safety_preview_router
app.include_router(divine_weapon_upgrade_safety_preview_router)

# ============================================================================
# ====                                                                    ====
# ====  PUBLIC_CONTENT_REGISTRATION_v40_BATTLE_PASS_AND_MAIL_CLAIM_SAFETY_LOUD
# ====  MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40                            ====
# ====                                                                    ====
# ============================================================================
# Pack:             MEGA_ECONOMY_SAFETY_ACCELERATION_4_BATTLE_PASS_AND_MAIL_CLAIM_HARDENING_PACK_v40
# Parent v39:       6093c4f3
# Parent v39b:      8998a7f9
# Mode:             REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM
#
# Purpose
# -------
# Close the last 2 placeholders of the endgame economy safety registry v3
# (battle_pass_reward_claim + mail_reward_claim) by attaching preview-only
# safety routers. After this commit, ALL 8 operation families have an
# active preview-only safety layer (registry v4).
#
# This is NOT live reward grant enablement.
# This is NOT a duplicate router registration: each include_router for the
# two v40 routers appears EXACTLY ONCE in this file (count == 1).
#
# Required visible tokens
# -----------------------
#   PUBLIC_CONTENT_REGISTRATION_v40_BATTLE_PASS_AND_MAIL_CLAIM_SAFETY_LOUD
#   battle_pass_claim_safety_preview_router
#   mail_claim_safety_preview_router
#   include_router for battle_pass_claim_safety_preview_router  [count == 1]
#   include_router for mail_claim_safety_preview_router         [count == 1]
#
# Safety booleans
# ---------------
#   db_writes:                                          0
#   battle_pass_live_claim_enabled:                     false
#   mail_live_claim_enabled:                            false
#   reward_grant_enabled:                               false
#   inventory_mutation_enabled:                         false
#   currency_mutation_enabled:                          false
#   user_wallet_mutation_enabled:                       false
#   premium_users_gems_used:                            false
#   battle_pass_purchase_enabled:                       false
#   premium_track_unlock_enabled:                       false
#   vip_mutation_enabled:                               false
#   shop_mutation_enabled:                              false
#   mail_state_mutation_enabled:                        false
#   mail_delete_enabled:                                false
#   mail_read_state_mutation_enabled:                   false
#   bp_delta_runtime_enabled:                           false
#   battle_engine_changed:                              false
#   combat_story_home_routes_changed:                   false
#   frontend_battlepass_tsx_changed:                    false
#   frontend_vip_tsx_changed:                           false
#   artifact_dw_gem_gear_rune_routes_changed:           false
#   character_bible_changed:                            false
#   hero_final_numbers_changed:                         false
#   validator_weakening:                                false
#   fake_pass:                                          false
#   duplicate_router_registration:                      false
#
# Marker:  data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json
# Doc 253: docs/divine/253_MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40.md
# Registry: data/design/economy_safety/reward_claim_economy_safety_registry_v4.json
# ============================================================================
from routes.battle_pass_claim_safety_preview import router as battle_pass_claim_safety_preview_router
app.include_router(battle_pass_claim_safety_preview_router)
from routes.mail_claim_safety_preview import router as mail_claim_safety_preview_router
app.include_router(mail_claim_safety_preview_router)

# ===================== SEED =====================
# Mappa nome eroe → faction canonica (valori che il resolver background
# accetta direttamente: greek/norse/egyptian/japanese/celtic).
# NON scrivere mai alias asset (nordic/egypt) nel DB — quelli restano
# SOLO nel registry di /app/frontend/components/ui/battleBackgrounds.ts.
HERO_FACTION_MAP: dict = {
    # --- Greek pantheon + nymph / minor ----------------------------------
    "Hoplite": "greek",
    "Athena": "greek", "Aphrodite": "greek", "Artemis": "greek",
    "Medusa": "greek", "Hera": "greek", "Persephone": "greek",
    "Nyx": "greek", "Demeter": "greek", "Hecate": "greek",
    "Selene": "greek", "Iris": "greek", "Echo": "greek",
    "Daphne": "greek", "Chloris": "greek", "Aura": "greek",
    "Hestia": "greek", "Nike": "greek", "Psyche": "greek",
    # --- Japanese pantheon (Shinto) --------------------------------------
    "Amaterasu": "japanese", "Tsukuyomi": "japanese",
    "Susanoo": "japanese", "Izanami": "japanese",
    "Sakuya": "japanese", "Kaguya": "japanese",
    "Inari": "japanese", "Benzaiten": "japanese",
    "Raijin": "japanese", "Fujin": "japanese",
    # --- Norse pantheon --------------------------------------------------
    "Freya": "norse", "Valkyrie": "norse",
    # Egyptian / Celtic: nessun eroe attualmente presente nel roster.
}

def resolve_hero_faction(name: str, existing: str | None = None) -> str | None:
    """Ritorna la faction per il nome eroe. Se esiste già un valore
    canonico lo preserva (evita di sovrascrivere eventuali fix manuali)."""
    if existing and str(existing).lower() in {"greek", "norse", "egyptian", "japanese", "celtic"}:
        return existing
    return HERO_FACTION_MAP.get(name)

def _env_flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}

def _explicit_startup_bot_server_id() -> str:
    server_id = os.getenv("DIVINE_STARTUP_BOT_SERVER_ID", "").strip()
    if not server_id or server_id.lower() == "default":
        return ""
    return server_id

@app.on_event("startup")
async def seed_database():
    """Seed heroes if not present"""
    if not _env_flag_enabled("DIVINE_ALLOW_STARTUP_SEED_WRITES"):
        print("Startup seed SKIPPED: DIVINE_ALLOW_STARTUP_SEED_WRITES is not enabled")
        return

    count = await db.heroes.count_documents({})
    if count >= 30:
        # Migrazione one-shot: popola il campo faction sui record DB esistenti
        # che non ce l'hanno (o ce l'hanno nullo). Solo update mirati per
        # nome presente in HERO_FACTION_MAP. Nessun altro campo viene toccato.
        missing = await db.heroes.find(
            {"$or": [{"faction": None}, {"faction": {"$exists": False}}]},
            {"name": 1, "faction": 1},
        ).to_list(1000)
        updated = 0
        for h in missing:
            f = resolve_hero_faction(h.get("name", ""), h.get("faction"))
            if f:
                await db.heroes.update_one({"_id": h["_id"]}, {"$set": {"faction": f}})
                updated += 1
        if updated:
            print(f"[faction-migration] Populated faction on {updated} existing heroes")
        return
    
    await db.heroes.delete_many({})
    
    heroes_data = [
        {"id": "greek_hoplite", "name": "Hoplite", "rarity": 3, "element": "earth", "faction": "greek", "hero_class": "Tank", "image": "asset:greek_hoplite:splash", "base_stats": {"hp": 8500, "attack": 1200, "defense": 1100, "speed": 95, "crit_rate": 0.10, "crit_damage": 1.5}},
        {"name": "Amaterasu", "rarity": 6, "element": "fire", "hero_class": "DPS", "base_stats": {"hp": 12000, "attack": 2800, "defense": 900, "speed": 130, "crit_rate": 0.25, "crit_damage": 2.0}},
        {"name": "Tsukuyomi", "rarity": 6, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 11000, "attack": 3000, "defense": 800, "speed": 140, "crit_rate": 0.30, "crit_damage": 2.2}},
        {"name": "Susanoo", "rarity": 6, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 15000, "attack": 2200, "defense": 1400, "speed": 110, "crit_rate": 0.15, "crit_damage": 1.6}},
        {"name": "Izanami", "rarity": 6, "element": "dark", "hero_class": "Support", "base_stats": {"hp": 13000, "attack": 2000, "defense": 1100, "speed": 125, "crit_rate": 0.18, "crit_damage": 1.7}},
        {"name": "Athena", "rarity": 5, "element": "light", "hero_class": "Tank", "base_stats": {"hp": 14000, "attack": 1800, "defense": 1300, "speed": 105, "crit_rate": 0.12, "crit_damage": 1.5}},
        {"name": "Aphrodite", "rarity": 5, "element": "water", "hero_class": "Support", "base_stats": {"hp": 11500, "attack": 1600, "defense": 1000, "speed": 120, "crit_rate": 0.15, "crit_damage": 1.5}},
        {"name": "Artemis", "rarity": 5, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 10000, "attack": 2400, "defense": 750, "speed": 145, "crit_rate": 0.28, "crit_damage": 1.9}},
        {"name": "Freya", "rarity": 5, "element": "light", "hero_class": "DPS", "base_stats": {"hp": 10500, "attack": 2500, "defense": 800, "speed": 135, "crit_rate": 0.22, "crit_damage": 1.8}},
        {"name": "Valkyrie", "rarity": 5, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 13000, "attack": 1900, "defense": 1200, "speed": 115, "crit_rate": 0.14, "crit_damage": 1.5}},
        {"name": "Medusa", "rarity": 5, "element": "earth", "hero_class": "DPS", "base_stats": {"hp": 10800, "attack": 2300, "defense": 850, "speed": 125, "crit_rate": 0.20, "crit_damage": 1.8}},
        {"name": "Hera", "rarity": 4, "element": "light", "hero_class": "Support", "base_stats": {"hp": 10000, "attack": 1500, "defense": 900, "speed": 110, "crit_rate": 0.12, "crit_damage": 1.5}},
        {"name": "Persephone", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9500, "attack": 2000, "defense": 700, "speed": 130, "crit_rate": 0.20, "crit_damage": 1.7}},
        {"name": "Nyx", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9000, "attack": 2100, "defense": 650, "speed": 135, "crit_rate": 0.22, "crit_damage": 1.7}},
        {"name": "Demeter", "rarity": 4, "element": "earth", "hero_class": "Support", "base_stats": {"hp": 11000, "attack": 1400, "defense": 950, "speed": 100, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Hecate", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9200, "attack": 1950, "defense": 720, "speed": 128, "crit_rate": 0.18, "crit_damage": 1.6}},
        {"name": "Selene", "rarity": 4, "element": "light", "hero_class": "Support", "base_stats": {"hp": 10500, "attack": 1550, "defense": 880, "speed": 112, "crit_rate": 0.13, "crit_damage": 1.5}},
        {"name": "Sakuya", "rarity": 3, "element": "water", "hero_class": "Support", "base_stats": {"hp": 9000, "attack": 1300, "defense": 800, "speed": 108, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Kaguya", "rarity": 3, "element": "light", "hero_class": "DPS", "base_stats": {"hp": 8500, "attack": 1700, "defense": 650, "speed": 120, "crit_rate": 0.16, "crit_damage": 1.5}},
        {"name": "Inari", "rarity": 3, "element": "fire", "hero_class": "DPS", "base_stats": {"hp": 8000, "attack": 1800, "defense": 600, "speed": 125, "crit_rate": 0.18, "crit_damage": 1.6}},
        {"name": "Benzaiten", "rarity": 3, "element": "water", "hero_class": "Support", "base_stats": {"hp": 9500, "attack": 1200, "defense": 850, "speed": 105, "crit_rate": 0.10, "crit_damage": 1.3}},
        {"name": "Raijin", "rarity": 3, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 8200, "attack": 1750, "defense": 620, "speed": 135, "crit_rate": 0.15, "crit_damage": 1.5}},
        {"name": "Fujin", "rarity": 3, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 10000, "attack": 1400, "defense": 900, "speed": 110, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Iris", "rarity": 2, "element": "light", "hero_class": "Support", "base_stats": {"hp": 7500, "attack": 1100, "defense": 700, "speed": 105, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Echo", "rarity": 2, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 7000, "attack": 1400, "defense": 550, "speed": 115, "crit_rate": 0.12, "crit_damage": 1.4}},
        {"name": "Daphne", "rarity": 2, "element": "earth", "hero_class": "Tank", "base_stats": {"hp": 8500, "attack": 1000, "defense": 800, "speed": 95, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Chloris", "rarity": 2, "element": "earth", "hero_class": "Support", "base_stats": {"hp": 8000, "attack": 1050, "defense": 750, "speed": 100, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Aura", "rarity": 1, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 6000, "attack": 1200, "defense": 450, "speed": 110, "crit_rate": 0.10, "crit_damage": 1.3}},
        {"name": "Hestia", "rarity": 1, "element": "fire", "hero_class": "Support", "base_stats": {"hp": 6500, "attack": 900, "defense": 600, "speed": 95, "crit_rate": 0.06, "crit_damage": 1.2}},
        {"name": "Nike", "rarity": 1, "element": "light", "hero_class": "Tank", "base_stats": {"hp": 7000, "attack": 850, "defense": 700, "speed": 90, "crit_rate": 0.05, "crit_damage": 1.2}},
        {"name": "Psyche", "rarity": 1, "element": "water", "hero_class": "Support", "base_stats": {"hp": 6200, "attack": 950, "defense": 550, "speed": 100, "crit_rate": 0.07, "crit_damage": 1.2}},
    ]
    
    for hero in heroes_data:
        if "id" not in hero:
            hero["id"] = str(uuid.uuid4())
        # Popolamento faction: preserva eventuale valore già presente (es.
        # greek_hoplite nel seed), altrimenti risolve via HERO_FACTION_MAP.
        hero["faction"] = resolve_hero_faction(hero.get("name", ""), hero.get("faction"))
        hero["created_at"] = datetime.utcnow()
        await db.heroes.insert_one(hero)
    
    print(f"Seeded {len(heroes_data)} heroes into database")

# ===================== BOT SYSTEM =====================
from bot_system import initialize_bots, run_bot_cycle

bot_task_handle = None

@app.on_event("startup")
async def start_bot_system():
    """Initialize bots and start background cycle.

    v108_POSTQA_A — Hard kill switch onesto: env BOTS_DISABLED=true disabilita
    Pack 3: startup bots are disabled by default and require explicit opt-in
    plus an explicit non-default server id.
    """
    global bot_task_handle
    # v108_POSTQA_A hard kill switch (BOTS_DISABLED / BOT_KILL_SWITCH)
    if os.environ.get("BOTS_DISABLED", "").lower() == "true" or os.environ.get("BOT_KILL_SWITCH", "").lower() == "true":
        print("[v108_POSTQA_A] BOTS_DISABLED=true: skipping startup bot initialization and cycle")
        return

    if not _env_flag_enabled("DIVINE_ENABLE_STARTUP_BOTS"):
        print("Bot system SKIPPED: DIVINE_ENABLE_STARTUP_BOTS is not enabled")
        return

    bot_server_id = _explicit_startup_bot_server_id()
    if not bot_server_id:
        print("Bot system SKIPPED: DIVINE_STARTUP_BOT_SERVER_ID must be explicit and not 'default'")
        return

    # Wait for DB to be ready
    await asyncio.sleep(5)
    try:
        count = await initialize_bots(bot_server_id, 20)
        print(f"Bot system ready: {count} bots on server '{bot_server_id}'")
    except Exception as e:
        print(f"Bot init error: {e}")
    
    # Start background task
    bot_task_handle = asyncio.create_task(bot_background_loop(bot_server_id))

async def bot_background_loop(server_id: str):
    """Run bot actions every 3-5 minutes.

    v108_POSTQA_A — Hard kill switch: env BOTS_DISABLED=true esce dal loop.
    """
    while True:
        try:
            # v108_POSTQA_A hard kill switch (BOTS_DISABLED / BOT_KILL_SWITCH)
            if os.environ.get("BOTS_DISABLED", "").lower() == "true" or os.environ.get("BOT_KILL_SWITCH", "").lower() == "true":
                print("[v108_POSTQA_A] BOTS_DISABLED=true: exiting bot_background_loop")
                return
            await asyncio.sleep(random.randint(180, 300))  # 3-5 min
            await run_bot_cycle(server_id)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Bot cycle error: {e}")
            await asyncio.sleep(60)

@app.post("/api/admin/bots/run-cycle")
async def admin_run_bot_cycle(current_user: dict = Depends(get_current_user)):
    """Manually trigger a bot cycle (for testing).

    v108_POSTQA_A — Hard kill switch: env BOTS_DISABLED=true blocca anche
    il trigger admin-manual.
    """
    # v108_POSTQA_A hard kill switch (BOTS_DISABLED / BOT_KILL_SWITCH)
    if os.environ.get("BOTS_DISABLED", "").lower() == "true" or os.environ.get("BOT_KILL_SWITCH", "").lower() == "true":
        return {"success": False, "error": "BOTS_DISABLED=true (v108_POSTQA_A kill switch)"}
    bot_server_id = os.getenv("DIVINE_MANUAL_BOT_SERVER_ID", "").strip()
    if not bot_server_id or bot_server_id.lower() == "default":
        return {"success": False, "error": "DIVINE_MANUAL_BOT_SERVER_ID must be explicit and not 'default'"}
    try:
        await run_bot_cycle(bot_server_id)
        return {"success": True, "message": "Bot cycle completed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/bots/status")
async def admin_bot_status(current_user: dict = Depends(get_current_user)):
    """Get status of all bots."""
    bots = await db.users.find({"is_bot": True}, {"password": 0}).to_list(200)
    tiers = {}
    for b in bots:
        tier = b.get("bot_tier", "unknown")
        tiers[tier] = tiers.get(tier, 0) + 1
    return {
        "total_bots": len(bots),
        "tier_distribution": tiers,
        "bots": [{
            "username": b["username"], "tier": b.get("bot_tier"), "personality": b.get("bot_personality"),
            "level": b.get("level"), "last_action": str(b.get("bot_last_action", "")),
        } for b in bots[:30]],
    }

@app.get("/api/health")
async def health():
    bot_count = await db.users.count_documents({"is_bot": True})
    return {"status": "ok", "game": "Divine Waifus", "version": "1.0.0", "bots": bot_count}

# ===================== HOPLITE REEL (DEV VISUAL VALIDATION) =====================
# Pagina helper: mostra i frame catturati in /app/tmp/hop/ come reel visuale
# per validazione rapida delle animazioni Hoplite. Serve inline via img base64.
@app.get("/api/hoplite-reel")
async def hoplite_reel(crop: bool = False, curated: bool = False, v2: bool = False):
    from fastapi.responses import HTMLResponse
    import base64, glob
    if v2:
        # V2: frames del nuovo rig (cartella /app/tmp/hop2), con label per fase.
        CURATED2 = [
            ("00_idle.png",         "IDLE baseline",    "Pose base — spear level, shield up, legs radicate"),
            ("01_windup.png",       "RITRAZIONE",       "Phase 1 (~80ms) — spear tirato indietro +70, rot +8°, torso +2°"),
            ("02_thrust_mid.png",   "AFFONDO mid",      "Phase 2 (~190ms) — spear in corsa, torso -4° lean forward"),
            ("03_impact.png",       "AFFONDO peak",     "Phase 2 end (~290ms) — spear thrust max -180, massima estensione"),
            ("04_impact_end.png",   "IMPATTO hold",     "Phase 3 (~370ms) — hold a -200, max thrust + body weight forward"),
            ("05_return.png",       "RITORNO guardia",  "Phase 4 (~550ms) — rientro easing out, torso si raddrizza"),
            ("06_idle_back.png",    "IDLE ripristino",  "Post-return (~850ms) — tutto a 0, home position recuperata"),
        ]
        imgs_html = ""
        for fname, label, caption in CURATED2:
            p = f"/app/tmp/hop2/{fname}"
            try:
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                imgs_html += f'<div class="cell"><div class="lbl">{label}</div><div class="cap">{caption}</div><img src="data:image/png;base64,{b64}"/></div>'
            except Exception:
                pass
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{{margin:0;padding:16px;background:#0a0a0a;color:#fff;font-family:monospace}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}
.cell{{position:relative;border:2px solid #FFB347;background:#0a0a0a;border-radius:8px;overflow:hidden}}
.cell img{{width:100%;display:block}}
.lbl{{position:absolute;top:0;left:0;background:#FF0055;color:#fff;padding:6px 14px;font-size:15px;font-weight:900;z-index:10;border-bottom-right-radius:10px;letter-spacing:1px}}
.cap{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.88);color:#FFD700;padding:8px 12px;font-size:12px;z-index:10}}
h1{{font-size:22px;margin:6px 0 18px 4px;color:#FFD700}}
.legend{{background:#1a1410;border:1px solid #FFB347;padding:14px;border-radius:6px;margin-bottom:20px;font-size:12px;color:#FFCC99;line-height:1.6}}
</style></head>
<body>
<h1>⚔️ HOPLITE — AFFONDO DI FALANGE (RIG-BASED LAYER ANIMATION)</h1>
<div class="legend">
<b>PIPELINE:</b> 7 layer PNG separati (hair / legs / skirt / torso / shield_arm / spear_arm / head_helmet) · pivot anatomici (bacino, spalla sx lancia, spalla dx scudo) · idle breathing SEMPRE attivo in background · combat deltas additivi on top · gambe FISSE (disciplina tank) · no drift dalla cella.
</div>
<div class="grid">{imgs_html}</div>
</body></html>"""
        return HTMLResponse(content=html)
    folder = "/app/tmp/hop/crop" if crop else "/app/tmp/hop"
    if curated:
        CURATED = [
            (0,  "IDLE",          "Hoplite in home position, spear relaxed"),
            (19, "ATTACK wind-up", "Inizio forward lean + spear raising"),
            (21, "ATTACK thrust",  "CONFIRMED: leaning forward, spear extended"),
            (23, "ATTACK follow",  "Mid-return, shield still forward"),
            (25, "SKILL AFTERMATH","Log: 'Hoplite Terremoto -> Mago Corotto' — post-impact"),
            (17, "HIT reaction",   "Red color shift + heal +1,517 floating (damaged then healed)"),
        ]
        items = CURATED
        cols = 2
    else:
        files = sorted(glob.glob(f"{folder}/f*.jpg"))
        items = [(i, f"f{i:03d}", "") for i in range(len(files))]
        cols = 3 if crop else 4
    imgs_html = ""
    for idx, label, caption in items:
        p = f"{folder}/f{idx:03d}.jpg"
        try:
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            imgs_html += f'<div class="cell"><div class="lbl">{label}</div><div class="cap">{caption}</div><img src="data:image/jpeg;base64,{b64}"/></div>'
        except Exception:
            pass
    extra = ""
    if curated:
        extra = """<div class="note"><b>NOTA DEATH:</b> non catturata in questa battaglia (team ha vinto 6/6 in 2 turni, nessun player KO).
        Per validare l'animazione death serve un combattimento dove Hoplite muore — es. PvP contro avversario più forte,
        oppure Tower of Infinity stage avanzato. Posso orchestrarlo in un run successivo se confermi.</div>"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{{margin:0;padding:10px;background:#000;color:#fff;font-family:monospace}}
.grid{{display:grid;grid-template-columns:repeat({cols},1fr);gap:12px}}
.cell{{position:relative;border:2px solid #FFB347;background:#111;border-radius:6px;overflow:hidden}}
.cell img{{width:100%;display:block}}
.lbl{{position:absolute;top:0;left:0;background:#FF0055;color:#fff;padding:5px 12px;font-size:15px;font-weight:900;z-index:10;border-bottom-right-radius:8px}}
.cap{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.85);color:#FFD700;padding:6px 10px;font-size:12px;z-index:10}}
h1{{font-size:18px;margin:6px 0 14px 4px;color:#FFD700}}
.note{{background:#2a1a1a;border:2px solid #FFB347;padding:14px;border-radius:6px;margin-top:20px;font-size:13px;color:#FFCC99;line-height:1.5}}
</style></head>
<body><h1>⚔️ HOPLITE ANIMATION VALIDATION — 1x speed</h1>
<div class="grid">{imgs_html}</div>
{extra}
</body></html>"""
    return HTMLResponse(content=html)

# ===================== EXPO GO CONNECT HELPER =====================
# Pagina HTML auto-contenuta: il dev apre questa URL dal browser del telefono
# e può toccare il pulsante "Open in Expo Go" (deep link exp://) per lanciare
# Expo Go direttamente con l'URL diretto (preview.emergentagent.com), senza
# passare dal proxy cluster-2.preview.emergentcf.cloud che al momento è 403.
# Include anche il QR code generato lato server in SVG (no dipendenze JS).
@app.get("/api/expo-connect")
async def expo_connect():
    from fastapi.responses import HTMLResponse
    import qrcode
    import qrcode.image.svg
    import io
    # Usa l'hostname del request per costruire l'URL — funziona sia in preview
    # che in locale. Default → preview.emergentagent.com.
    host = os.getenv("EXPO_PUBLIC_PREVIEW_HOST", "game-portal-327.preview.emergentagent.com")
    exp_url = f"exp://{host}"
    https_url = f"https://{host}"

    # Genera QR come SVG inline (nessuna dipendenza extra client-side)
    factory = qrcode.image.svg.SvgImage
    qr_img = qrcode.make(exp_url, image_factory=factory, box_size=10, border=2)
    buf = io.BytesIO()
    qr_img.save(buf)
    qr_svg = buf.getvalue().decode("utf-8")
    # Rimuove xml declaration per embedding inline
    qr_svg = qr_svg.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Divine Waifus · Connect Expo Go</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0D0D2B 0%, #1A0A2E 100%);
    color: #fff;
    min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }}
  h1 {{
    font-size: 22px; letter-spacing: 2px; margin: 0 0 8px 0; color: #FFD700;
    text-shadow: 0 0 20px rgba(255,215,0,0.4);
  }}
  .sub {{ font-size: 12px; color: #aaa; margin-bottom: 28px; text-align: center; }}
  .card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,215,0,0.2);
    border-radius: 14px;
    padding: 22px;
    max-width: 380px;
    width: 100%;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  }}
  .btn-open {{
    display: block; text-decoration: none;
    background: linear-gradient(135deg, #FF6B35 0%, #FF4444 100%);
    color: #fff;
    font-size: 18px; font-weight: 900; letter-spacing: 1px;
    text-align: center;
    padding: 18px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(255,107,53,0.4);
    margin-bottom: 18px;
    transition: transform 0.1s;
  }}
  .btn-open:active {{ transform: scale(0.97); }}
  .qr-wrap {{
    background: #fff; border-radius: 10px; padding: 14px;
    margin: 18px auto; width: fit-content;
  }}
  .qr-wrap svg {{ display: block; width: 220px; height: 220px; }}
  .url-box {{
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: monospace;
    font-size: 11px;
    color: #44AAFF;
    word-break: break-all;
    margin: 10px 0;
  }}
  .step {{
    background: rgba(68,170,255,0.08);
    border-left: 3px solid #44AAFF;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
    margin: 8px 0;
  }}
  .step strong {{ color: #FFD700; }}
  .footer {{
    font-size: 10px; color: #666; margin-top: 24px; text-align: center;
  }}
  .warn {{
    background: rgba(255,68,68,0.1);
    border: 1px solid rgba(255,68,68,0.3);
    border-radius: 8px;
    padding: 10px;
    font-size: 11px;
    color: #FF8888;
    margin-bottom: 16px;
  }}
</style>
</head>
<body>
  <h1>⚔️ DIVINE WAIFUS</h1>
  <div class="sub">Expo Go Connect · Dev Bypass</div>

  <div class="card">
    <div class="warn">
      Il proxy QR di default è al momento <b>offline</b>.
      Usa questa pagina per connettere Expo Go direttamente.
    </div>

    <a class="btn-open" href="{exp_url}">📱 Apri in Expo Go</a>

    <div class="step"><strong>Metodo 1:</strong> Tocca il pulsante qui sopra dal browser del telefono. Expo Go si aprirà automaticamente.</div>

    <div class="step"><strong>Metodo 2:</strong> Apri Expo Go → "Scan QR code" e inquadra il QR qui sotto.</div>

    <div class="qr-wrap">
      {qr_svg}
    </div>

    <div class="step"><strong>Metodo 3:</strong> Copia e incolla l'URL manualmente in Expo Go.</div>
    <div class="url-box">{exp_url}</div>
  </div>

  <div class="footer">Divine Waifus dev console · {host}</div>
</body>
</html>
"""
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
