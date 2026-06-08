"""
v96 — Team formation read-only endpoint.

Chiude il blocker v95: /api/team/get-formation.

Pack 88 — STRICT SERVER-SCOPED:
  Quando server_id è fornito, la team_formation è ESCLUSIVAMENTE letta da
  player_server_profiles.team_formation (server-scoped). NESSUN fallback a
  users.team_formation account-wide. Se PSP non esiste → blocker
  PLAYER_SERVER_PROFILE_REQUIRED. Se PSP esiste ma team vuoto → blocker
  PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER + team_formation=[].

  Quando server_id NON è fornito, è la legacy/compat path account-wide
  esposta come deprecated, non player-facing.

Invarianti garantiti:
- NO writes a users.team_formation nel flow server-scoped.
- NO fallback a user.team_formation account-wide quando server_id presente.
- NO fake team, NO global roster.
- NO copia S1→S2.
- Pack 87 starter team flow preservato (team init via starter claim).
"""
from typing import Optional
from fastapi import APIRouter, Depends, Header

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
                "team_formation": psp_team,
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

    return router
