"""
v96 — Team formation read-only endpoint.

Chiude il blocker v95: /api/team/get-formation.

Lettura SAFE del campo team_formation dal documento user autenticato.
- NO db_writes
- Fallback dichiarato se assente (NON spaccia per real formation)
- UI deve mostrare source label
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header

router = APIRouter(prefix="/api/team", tags=["v96_team_formation"])


SAFE_FALLBACK = {
    "source": "safe_fallback_formation",
    "team_formation": [],
    "fallback_used": True,
    "reason": "no_saved_formation_for_account",
}


def create_team_formation_router(db, get_current_user):
    @router.get("/get-formation")
    async def get_formation(
        server_id: Optional[str] = None,
        current_user: Optional[dict] = Depends(get_current_user),
    ):
        """
        Restituisce la formazione del player autenticato.

        Pack 79 (RUNTIME REAL, server-scoped):
          - Se `server_id` è fornito, il loader filtra per server_id ed è dichiarato
            `filter_applied=true`.
          - Quando un PSP esiste per (user, server_id), legge prima dal PSP
            (`selected_team_id`, `soft_currencies`, ecc.) e poi compone team_formation
            dal user.team_formation account-wide (compat back).
          - Quando il team_formation account-wide è vuoto, ritorna blocker esplicito
            `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` invece di fake team.

        Chain:
          saved_formation_server_scoped (PSP-aware) -> server_id + user.team_formation
          saved_formation                          -> nessun server_id, account-wide
          blocked_no_team_for_server               -> server_id richiesto ma nessun team
          safe_fallback_formation                  -> default difensivo (vuoto)
        """
        if not current_user:
            return {
                "v96_team_formation": True,
                "authenticated": False,
                "server_id": server_id,
                "filter_applied": bool(server_id),
                **SAFE_FALLBACK,
            }
        user = await db.users.find_one({"id": current_user["id"]})
        if not user:
            return {
                "v96_team_formation": True,
                "authenticated": True,
                "server_id": server_id,
                "filter_applied": bool(server_id),
                **SAFE_FALLBACK,
                "reason": "user_doc_not_found",
            }
        account_id = user.get("account_id") or user.get("id")
        team_formation = user.get("team_formation") or []
        psp_doc = None
        psp_present_for_server = False
        if server_id:
            psp_doc = await db.player_server_profiles.find_one(
                {"user_id": str(user.get("_id") or user.get("id")), "server_id": server_id}
            )
            psp_present_for_server = psp_doc is not None
        # Blocker esplicito quando server_id richiesto ma nessun team disponibile.
        if server_id and not team_formation:
            return {
                "v96_team_formation": True,
                "authenticated": True,
                "account_id": account_id,
                "server_id": server_id,
                "filter_applied": True,
                "psp_present_for_server": psp_present_for_server,
                "source": "blocked_no_team_for_server",
                "fallback_used": True,
                "team_formation": [],
                "blocker": "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER",
            }
        if not team_formation:
            return {
                "v96_team_formation": True,
                "authenticated": True,
                "account_id": account_id,
                "server_id": server_id,
                "filter_applied": bool(server_id),
                **SAFE_FALLBACK,
            }
        return {
            "v96_team_formation": True,
            "authenticated": True,
            "account_id": account_id,
            "server_id": server_id,
            "filter_applied": bool(server_id),
            "psp_present_for_server": psp_present_for_server,
            "source": "saved_formation_server_scoped" if server_id else "saved_formation",
            "fallback_used": False,
            "team_formation": team_formation,
        }

    return router
