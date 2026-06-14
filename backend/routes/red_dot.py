"""Pre-QA Stabilization 116C — Red Dot summary route (read-only)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from utils.red_dot_summary import build_red_dot_metadata, build_summary, RED_DOT_SUMMARY_VERSION


def create_red_dot_router(db, get_current_user):
    router = APIRouter(prefix="/api/red-dot", tags=["red_dot_116c"])

    @router.get("/summary")
    async def get_red_dot_summary(
        server_id: Optional[str] = Query(default=None),
        current_user: dict = Depends(get_current_user),
    ):
        # server_id REQUIRED — no silent s1 fallback.
        sid = (server_id or "").strip() if isinstance(server_id, str) else ""
        if not sid:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SERVER_ID_REQUIRED",
                    "message": "Red Dot summary e' server-scoped. Fornire server_id esplicito; nessun silent s1 fallback.",
                    "no_silent_s1_fallback": True,
                    **build_red_dot_metadata(),
                },
            )
        uid = current_user.get("id")
        # READ-ONLY: solo find_one su PSP (no writes, no mutation, no claim).
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        psp_present = psp is not None
        psp_team = (psp or {}).get("team_formation") or []
        team_missing = not (isinstance(psp_team, list) and len(psp_team) > 0)
        return build_summary(server_id=sid, psp_present=psp_present, team_missing=team_missing)

    @router.get("/metadata")
    async def get_red_dot_metadata():
        return {"status": "ok", **build_red_dot_metadata()}

    router.red_dot_summary_version = RED_DOT_SUMMARY_VERSION  # type: ignore[attr-defined]
    return router
