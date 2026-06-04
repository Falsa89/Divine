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
        current_user: Optional[dict] = Depends(get_current_user),
    ):
        """
        Restituisce la formazione del player autenticato.

        Chain:
          saved_formation     -> user.team_formation popolato e valido
          local_cached_formation -> gestito client-side
          safe_fallback_formation -> nessuna formation, UI lo deve dichiarare
        """
        if not current_user:
            # difensivo (get_current_user di solito raise 401 ma manteniamo idempotenza)
            return {
                "v96_team_formation": True,
                "authenticated": False,
                **SAFE_FALLBACK,
            }
        # Re-fetch per dati freschi (read-only, no write)
        user = await db.users.find_one({"id": current_user["id"]})
        if not user:
            return {
                "v96_team_formation": True,
                "authenticated": True,
                **SAFE_FALLBACK,
                "reason": "user_doc_not_found",
            }
        team_formation = user.get("team_formation") or []
        if not team_formation:
            return {
                "v96_team_formation": True,
                "authenticated": True,
                "account_id": user.get("account_id") or user.get("id"),
                **SAFE_FALLBACK,
            }
        # Real formation
        return {
            "v96_team_formation": True,
            "authenticated": True,
            "account_id": user.get("account_id") or user.get("id"),
            "source": "saved_formation",
            "fallback_used": False,
            "team_formation": team_formation,
        }

    return router
