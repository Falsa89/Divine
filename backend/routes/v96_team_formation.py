"""
v96 — Team formation endpoints.

Chiude il blocker v95: /api/team/get-formation.

Pack 88 — STRICT SERVER-SCOPED:
  Quando server_id è fornito, la team_formation è ESCLUSIVAMENTE letta da
  player_server_profiles.team_formation (server-scoped). NESSUN fallback a
  users.team_formation account-wide. Se PSP non esiste → blocker
  PLAYER_SERVER_PROFILE_REQUIRED. Se PSP esiste ma team vuoto → blocker
  PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER + team_formation=[].

  Quando server_id NON è fornito, è la legacy/compat path account-wide
  esposta come deprecated, non player-facing.

Pack 125 — QA TEAM SAVE SERVER-SCOPED (POST /api/team/save-formation):
  Endpoint DEV/QA SOLO gated da `QA_TEAM_SAVE_ENABLED=true` env var +
  allowlist account via `QA_TEAM_SAVE_ALLOWLIST` (comma-separated user_ids
  oppure '*' per ambiente test). Quando gate fail-closed:
    - server_id obbligatorio (no account-wide write).
    - PSP deve esistere per (user_id, server_id).
    - Tutti gli hero_id devono essere in user_heroes con quel server_id.
    - Massimo 6 eroi per formazione.
    - Posizioni col 0..2 row 0..2 valide.
  Write SOLO su player_server_profiles.team_formation (no users update,
  no economy, no reward, no gacha, no shop, no VIP, no BP, no IAP).
  Idempotente: stesso payload → stesso risultato finale.

Invarianti garantiti:
- NO writes a users.team_formation nel flow server-scoped.
- NO fallback a user.team_formation account-wide quando server_id presente.
- NO fake team, NO global roster.
- NO copia S1→S2.
- Pack 87 starter team flow preservato (team init via starter claim).
- Pack 125: NO economy, NO reward, NO progress mutation.
"""
from typing import Optional, List, Any
import os
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

# HOTFIX E — contratto TeamFormation V1 centralizzato (read-only helper).
from helpers.team_formation_contract import (
    normalize_team_formation_to_v1,
    validate_v1_team_for_save,
    TEAM_FORMATION_V1_MAX_MEMBERS,
    TEAM_FORMATION_CONTRACT_VERSION,
    TEAM_FORMATION_V1_REQUIRED,
    TEAM_FORMATION_USER_HERO_ID_REQUIRED,
    TEAM_FORMATION_CANONICAL_ID_REQUIRED,
    TEAM_FORMATION_OWNED_HERO_NOT_FOUND,
    TEAM_FORMATION_SERVER_SCOPE_MISMATCH,
    TEAM_FORMATION_CANONICAL_MISMATCH,
    TEAM_FORMATION_DUPLICATE_USER_HERO,
    TEAM_FORMATION_DUPLICATE_CELL,
    TEAM_FORMATION_TOO_MANY_MEMBERS,
)

router = APIRouter(prefix="/api/team", tags=["v96_team_formation"])


SAFE_FALLBACK_LEGACY_NON_PLAYER_FACING = {
    "source": "safe_fallback_formation",
    "team_formation": [],
    "fallback_used": True,
    "reason": "no_saved_formation_for_account_legacy_non_player_facing",
}


def create_team_formation_router(db, get_current_user):
    @router.get("/get-formation")
    async def get_formation(
        server_id: Optional[str] = None,
        current_user: Optional[dict] = Depends(get_current_user),
    ):
        """
        Restituisce la formazione del player autenticato.

        Pack 88 STRICT SERVER-SCOPED behavior:
          - server_id fornito:
              source = player_server_profiles.team_formation (server-scoped).
              NESSUN fallback a users.team_formation.
              PSP missing → blocker PLAYER_SERVER_PROFILE_REQUIRED.
              PSP exists, team empty → blocker PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER, team=[].
          - server_id assente:
              legacy/compat path account-wide non-player-facing.

        Response include:
          - team_source: "player_server_profile" (strict) | "legacy_account_wide_deprecated" | "none"
          - legacy_account_team_used: bool (true SOLO nel path account-wide non player-facing)
          - filter_applied: true SOLO se server_id presente E team da PSP
          - blocker: PLAYER_SERVER_PROFILE_REQUIRED | PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER | None
        """
        # Default response markers (Pack 88).
        base_response = {
            "v96_team_formation": True,
            "server_id": server_id,
            "pack_88_strict_server_scope": True,
        }
        if not current_user:
            return {
                **base_response,
                "authenticated": False,
                "filter_applied": False,
                "team_source": "none",
                "legacy_account_team_used": False,
                **SAFE_FALLBACK_LEGACY_NON_PLAYER_FACING,
            }
        uid_uuid = current_user.get("id")
        user = await db.users.find_one({"id": uid_uuid})
        if not user:
            return {
                **base_response,
                "authenticated": True,
                "filter_applied": False,
                "team_source": "none",
                "legacy_account_team_used": False,
                **SAFE_FALLBACK_LEGACY_NON_PLAYER_FACING,
                "reason": "user_doc_not_found",
            }
        account_id = user.get("account_id") or user.get("id")

        # =====================================================================
        # Pack 88 — STRICT SERVER-SCOPED PATH (server_id present)
        # =====================================================================
        if server_id:
            # Pack 82 dual-read compat + Pack 84 normalized PSP user_id (UUID):
            # lookup primary via UUID, fallback per PSP storici con _id-stringified.
            psp_doc = await db.player_server_profiles.find_one(
                {"user_id": uid_uuid, "server_id": server_id}
            )
            if not psp_doc:
                try:
                    psp_doc = await db.player_server_profiles.find_one(
                        {"user_id": str(user.get("_id") or user.get("id")), "server_id": server_id}
                    )
                except Exception:
                    psp_doc = None
            if not psp_doc:
                # NO fallback ad account-wide. Blocker onesto.
                return {
                    **base_response,
                    "authenticated": True,
                    "account_id": account_id,
                    "filter_applied": True,
                    "psp_present_for_server": False,
                    "profile_id": None,
                    "team_source": "none",
                    "legacy_account_team_used": False,
                    "source": "blocked_no_psp_for_server",
                    "fallback_used": False,
                    "team_formation": [],
                    "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                }
            profile_id = str(psp_doc.get("profile_id") or psp_doc.get("_id") or psp_doc.get("id") or "")
            psp_team = psp_doc.get("team_formation") or []
            psp_team_initialized_pack_87 = bool(psp_doc.get("_slc_pack_87_team_initialized_from_starter"))
            if not psp_team or (isinstance(psp_team, list) and len(psp_team) == 0):
                # PSP esiste ma team vuoto. Blocker onesto. NO fallback account-wide.
                return {
                    **base_response,
                    "authenticated": True,
                    "account_id": account_id,
                    "filter_applied": True,
                    "psp_present_for_server": True,
                    "profile_id": profile_id,
                    "team_source": "player_server_profile",
                    "legacy_account_team_used": False,
                    "source": "blocked_no_team_for_server",
                    "fallback_used": False,
                    "team_formation": [],
                    "psp_team_initialized_pack_87": psp_team_initialized_pack_87,
                    "blocker": "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER",
                }
            # Happy path: team_formation strict da PSP.
            # HOTFIX E — normalize-on-read a V1 senza DB writes.
            # Build lookup maps su user_heroes server-scoped per disambiguazione
            # legacy `hero_id` (potrebbe matchare user_heroes.id OR hero_id).
            uid_for_lookup = uid_uuid
            uh_docs = await db.user_heroes.find(
                {"user_id": uid_for_lookup, "server_id": server_id},
                projection={"id": 1, "user_hero_id": 1, "hero_id": 1, "server_id": 1, "_qa_seed": 1},
            ).to_list(length=200)
            owned_by_user_hero_id: dict = {}
            owned_by_canonical_id: dict = {}
            for d in uh_docs:
                owned_uh_id = d.get("user_hero_id") or d.get("id")
                if owned_uh_id:
                    owned_by_user_hero_id[str(owned_uh_id)] = d
                c = d.get("hero_id")
                if c:
                    owned_by_canonical_id.setdefault(str(c), []).append(d)
            v1_slots, v1_warnings = normalize_team_formation_to_v1(
                psp_team, owned_by_user_hero_id, owned_by_canonical_id
            )
            return {
                **base_response,
                "authenticated": True,
                "account_id": account_id,
                "filter_applied": True,
                "psp_present_for_server": True,
                "profile_id": profile_id,
                "team_source": "player_server_profile",
                "legacy_account_team_used": False,
                "source": "saved_formation_server_scoped",
                "fallback_used": False,
                # HOTFIX E — esposizione duale:
                #   - `team_formation`: forma canonica V1 normalizzata
                #     (consumata da frontend e snapshot Pack 130).
                #   - `team_formation_raw`: forma raw persistita (utile per QA
                #     per ispezionare drift legacy senza DB query).
                "team_formation": v1_slots,
                "team_formation_raw": psp_team,
                "team_formation_contract_version": TEAM_FORMATION_CONTRACT_VERSION,
                "team_formation_v1_warnings": v1_warnings,
                "psp_team_initialized_pack_87": psp_team_initialized_pack_87,
                "blocker": None,
            }

        # =====================================================================
        # Pack 88 — LEGACY/COMPAT PATH (no server_id, NON player-facing).
        # =====================================================================
        # Esiste solo per backward compat di tool/debug non player-facing.
        # NESSUNA promessa di server-scope; nessun filter_applied.
        legacy_team_formation = user.get("team_formation") or []
        if not legacy_team_formation:
            return {
                **base_response,
                "authenticated": True,
                "account_id": account_id,
                "filter_applied": False,
                "team_source": "none",
                "legacy_account_team_used": False,
                **SAFE_FALLBACK_LEGACY_NON_PLAYER_FACING,
            }
        return {
            **base_response,
            "authenticated": True,
            "account_id": account_id,
            "filter_applied": False,
            "team_source": "legacy_account_wide_deprecated",
            "legacy_account_team_used": True,
            "source": "saved_formation_legacy_account_wide_non_player_facing",
            "fallback_used": False,
            "team_formation": legacy_team_formation,
            "blocker": None,
            "_slc_pack_88_legacy_path_warning": "This path is non-player-facing. Use server_id for player-facing reads.",
        }

    # =========================================================================
    # Pack 125 / HOTFIX E — POST /api/team/save-formation (QA dev gated,
    # server-scoped, contratto TeamFormation V1).
    # =========================================================================
    class TeamSlotV1(BaseModel):
        """HOTFIX E — slot canonico V1.
        - user_hero_id: owned user_heroes.id (NON canonical/catalog id).
        - canonical_id: catalog hero id = user_heroes.hero_id.
        - col/row: 0..2 (3x3 visiva).
        """
        user_hero_id: str = Field(..., min_length=1, max_length=128)
        canonical_id: str = Field(..., min_length=1, max_length=128)
        col: int = Field(..., ge=0, le=2)
        row: int = Field(..., ge=0, le=2)

    class SaveFormationRequest(BaseModel):
        server_id: str = Field(..., min_length=1)
        team_formation: List[TeamSlotV1] = Field(default_factory=list)

    def _qa_save_gate_state() -> dict:
        """Stato del gate: enabled + allowlist. Read fresh ad ogni call."""
        enabled = os.environ.get("QA_TEAM_SAVE_ENABLED", "").strip().lower() == "true"
        allowlist_raw = os.environ.get("QA_TEAM_SAVE_ALLOWLIST", "").strip()
        return {
            "enabled": enabled,
            "allowlist_raw": allowlist_raw,
            "allowlist": [a.strip() for a in allowlist_raw.split(",") if a.strip()] if allowlist_raw else [],
            "wildcard": allowlist_raw == "*",
        }

    @router.post("/save-formation")
    async def save_formation(
        body: SaveFormationRequest,
        current_user: Optional[dict] = Depends(get_current_user),
    ):
        """
        Salva la team_formation server-scoped per il player autenticato.
        DEV/QA-only: gated da QA_TEAM_SAVE_ENABLED env var + allowlist.

        NO economy mutation, NO reward, NO progress, NO gacha, NO shop,
        NO VIP, NO BP, NO IAP. Write SOLO su
        player_server_profiles.team_formation.
        """
        gate = _qa_save_gate_state()
        if not gate["enabled"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "blocker": "QA_TEAM_SAVE_DISABLED",
                    "message": "Team save server-scoped e' un endpoint QA dev gated. Impostare QA_TEAM_SAVE_ENABLED=true per abilitarlo.",
                },
            )
        if not current_user:
            raise HTTPException(status_code=401, detail={"blocker": "AUTHENTICATION_REQUIRED"})
        uid_uuid = current_user.get("id")
        if not uid_uuid:
            raise HTTPException(status_code=401, detail={"blocker": "AUTHENTICATION_INVALID"})
        # Allowlist check (wildcard '*' consentito SOLO se env esplicito).
        if not gate["wildcard"]:
            if not gate["allowlist"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "blocker": "QA_TEAM_SAVE_ALLOWLIST_EMPTY",
                        "message": "QA_TEAM_SAVE_ALLOWLIST env var deve contenere user_id allowlisted (o '*').",
                    },
                )
            if uid_uuid not in gate["allowlist"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "blocker": "QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED",
                        "message": "Questo account non e' nell'allowlist QA team save.",
                    },
                )
        server_id = body.server_id
        # HOTFIX E — Cap dim dal contratto centralizzato (Pack 125 cap = 6).
        if len(body.team_formation) > TEAM_FORMATION_V1_MAX_MEMBERS:
            raise HTTPException(
                status_code=400,
                detail={
                    "blocker": TEAM_FORMATION_TOO_MANY_MEMBERS,
                    "max": TEAM_FORMATION_V1_MAX_MEMBERS,
                    "received": len(body.team_formation),
                },
            )
        # PSP fail-closed: deve esistere per (uid, server_id).
        psp_doc = await db.player_server_profiles.find_one(
            {"user_id": uid_uuid, "server_id": server_id}
        )
        if not psp_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                    "server_id": server_id,
                    "message": "PSP non trovato per questo (user_id, server_id). Crea il profilo server prima del save.",
                },
            )
        # HOTFIX E — Carica owned user_heroes per (uid, server_id) e costruisci
        # lookup `user_heroes.id → doc`. Le validazioni ownership + canonical
        # mismatch sono delegate a `validate_v1_team_for_save` (helper
        # centralizzato), refuse-by-default.
        uh_docs = await db.user_heroes.find(
            {"user_id": uid_uuid},
            projection={"id": 1, "user_hero_id": 1, "hero_id": 1, "server_id": 1, "_qa_seed": 1},
        ).to_list(length=500)
        owned_by_user_hero_id: dict = {}
        for d in uh_docs:
            owned_uh_id = d.get("user_hero_id") or d.get("id")
            if owned_uh_id:
                owned_by_user_hero_id[str(owned_uh_id)] = d
        slots_input = [
            {
                "user_hero_id": s.user_hero_id,
                "canonical_id": s.canonical_id,
                "col": s.col,
                "row": s.row,
            }
            for s in body.team_formation
        ]
        validated, err = validate_v1_team_for_save(
            slots_input, owned_by_user_hero_id, server_id
        )
        if err:
            # Mappiamo blocker → HTTP status code coerente con Hotfix B:
            # 400 default per validazione, 404 per owned-not-found,
            # 409 per server-scope mismatch.
            blocker_code = err.get("blocker", TEAM_FORMATION_V1_REQUIRED)
            if blocker_code == TEAM_FORMATION_OWNED_HERO_NOT_FOUND:
                http_status = 404
            elif blocker_code == TEAM_FORMATION_SERVER_SCOPE_MISMATCH:
                http_status = 409
            else:
                http_status = 400
            raise HTTPException(status_code=http_status, detail=err)
        # Save: SOLO player_server_profiles.team_formation. NO users update.
        # NO economy mutation. NO reward. NO progress.
        team_formation_payload: List[dict] = validated  # già forma V1
        await db.player_server_profiles.update_one(
            {"user_id": uid_uuid, "server_id": server_id},
            {
                "$set": {
                    "team_formation": team_formation_payload,
                    "_pack_125_qa_team_save_ts": __import__("time").time(),
                    "_pack_125_qa_team_save_source": "qa_dev_gated_endpoint",
                    "_hotfix_e_team_formation_contract_version": TEAM_FORMATION_CONTRACT_VERSION,
                }
            },
        )
        return {
            "v96_team_formation": True,
            "pack_125_qa_save": True,
            "hotfix_e_team_formation_v1": True,
            "team_formation_contract_version": TEAM_FORMATION_CONTRACT_VERSION,
            "status": "OK",
            "server_id": server_id,
            "team_formation": team_formation_payload,
            "team_size": len(team_formation_payload),
            "qa_gate": {
                "enabled": True,
                "wildcard": gate["wildcard"],
                "allowlist_size": len(gate["allowlist"]),
            },
            "invariants_respected": {
                "no_economy_mutation": True,
                "no_reward": True,
                "no_progress": True,
                "no_gacha": True,
                "no_shop": True,
                "no_vip": True,
                "no_battlepass": True,
                "no_iap": True,
                "no_account_wide_write": True,
                "scoped_to_player_server_profile": True,
            },
        }

    return router
