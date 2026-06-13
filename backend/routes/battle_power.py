"""Pre-QA Stabilization 116A — Battle Power summary route.

Endpoint:
  - `GET /api/battle-power/summary?server_id=<server_id>`

Contratto:
  - Auth required.
  - `server_id` REQUIRED (no silent s1 fallback).
  - Read-only: nessun `$set`, `$inc`, `insert_one`, `update_one`, `delete_one`.
  - Server-scoped: legge `player_server_profiles` + `user_heroes` filtrati
    su `(user_id, server_id)`. Mai fallback account-wide.
  - Se PSP mancante → blocker honest, NO falso power.
  - Se team mancante → `active_team_power=0` + `team_missing=true`.
  - Metadata sempre presenti: `formula_version`, `source=derived_read_only`,
    `runtime_attached=false`, `combat_authoritative=false`,
    `reward_authoritative=false`, `balance_final=false`,
    `excluded_power_sources=[...]`.

Vincoli statici (verificati dal validator 116A):
  - non importa `battle_engine`;
  - non chiama nessuna funzione mutante sul DB;
  - non legge `users` (account-wide) per costruire team/roster.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from utils.battle_power import (
    BATTLE_POWER_FORMULA_VERSION,
    build_battle_power_metadata,
    compute_hero_battle_power_v1,
)


def create_battle_power_router(db, get_current_user):
    """Crea il router `/api/battle-power/*` (read-only, server-scoped).

    Args:
        db: AsyncIOMotorDatabase (read-only access in questo modulo).
        get_current_user: dependency FastAPI per auth.
    """
    router = APIRouter(prefix="/api/battle-power", tags=["battle_power_116a"])

    @router.get("/summary")
    async def get_battle_power_summary(
        server_id: Optional[str] = Query(default=None),
        current_user: dict = Depends(get_current_user),
    ):
        # ---- 1) server_id REQUIRED (no silent s1 fallback) ----
        sid = (server_id or "").strip() if isinstance(server_id, str) else ""
        if not sid:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SERVER_ID_REQUIRED",
                    "message": (
                        "Battle Power 116A e' strictly server-scoped. "
                        "Fornire `server_id` esplicito; nessun silent s1 fallback."
                    ),
                    "no_silent_s1_fallback": True,
                    **build_battle_power_metadata(),
                },
            )

        uid = current_user.get("id")
        metadata = build_battle_power_metadata()
        # ---- 2) PSP server-scoped check (no account-wide fallback) ----
        psp = await db.player_server_profiles.find_one(
            {"user_id": uid, "server_id": sid}
        )
        if not psp:
            # Honest blocker: NO falso power, NO account-wide read.
            return {
                "status": "blocked_no_psp_for_server",
                "server_id": sid,
                **metadata,
                "psp_present_for_server": False,
                "active_team_power": 0,
                "team_missing": True,
                "team_slots": [],
                "owned_hero_count": 0,
                "max_owned_hero_power": 0,
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
            }

        # ---- 3) Server-scoped roster: read-only filter su (uid, sid) ----
        user_heroes_cursor = db.user_heroes.find({"user_id": uid, "server_id": sid})
        user_heroes = await user_heroes_cursor.to_list(500)

        # Pre-load hero catalog docs (batch). NB: read-only.
        hero_ids = [uh.get("hero_id") for uh in user_heroes if uh.get("hero_id")]
        hero_docs = []
        if hero_ids:
            hero_docs = await db.heroes.find({"id": {"$in": hero_ids}}).to_list(500)
        hero_by_id = {h["id"]: h for h in hero_docs}

        # Mappa user_hero per id e per hero_id (servono entrambi per il team
        # lookup: il team_formation puo' contenere uh.id o hero_id).
        uh_by_id = {uh.get("id"): uh for uh in user_heroes if uh.get("id")}
        uh_by_hero_id = {uh.get("hero_id"): uh for uh in user_heroes if uh.get("hero_id")}

        # ---- 4) Hero power derivato per ciascun owned hero ----
        owned_hero_powers = []
        for uh in user_heroes:
            hero = hero_by_id.get(uh.get("hero_id"))
            if not hero:
                continue
            p = compute_hero_battle_power_v1(hero, uh)
            owned_hero_powers.append({
                "user_hero_id": str(uh.get("id") or ""),
                "hero_id": str(uh.get("hero_id") or ""),
                "hero_name": hero.get("name"),
                "rarity": hero.get("rarity"),
                "level": uh.get("level"),
                "stars": uh.get("stars"),
                "power": p,
            })

        owned_hero_count = len(owned_hero_powers)
        max_owned_hero_power = max((h["power"] for h in owned_hero_powers), default=0)

        # ---- 5) Active team (PSP-scoped). NO account-wide fallback. ----
        psp_team = psp.get("team_formation") or []
        team_slots = []
        team_missing = True
        active_team_power = 0
        if isinstance(psp_team, list) and len(psp_team) > 0:
            team_missing = False
            for slot_idx, entry in enumerate(psp_team, start=1):
                # entry puo' essere user_hero_id, hero_id, o dict {"user_hero_id": ..., "hero_id": ...}
                user_hero_id = None
                hero_id = None
                if isinstance(entry, str):
                    if entry in uh_by_id:
                        user_hero_id = entry
                        hero_id = uh_by_id[entry].get("hero_id")
                    elif entry in uh_by_hero_id:
                        hero_id = entry
                        user_hero_id = uh_by_hero_id[entry].get("id")
                elif isinstance(entry, dict):
                    user_hero_id = entry.get("user_hero_id") or entry.get("id")
                    hero_id = entry.get("hero_id")
                    if not user_hero_id and hero_id and hero_id in uh_by_hero_id:
                        user_hero_id = uh_by_hero_id[hero_id].get("id")
                    if not hero_id and user_hero_id and user_hero_id in uh_by_id:
                        hero_id = uh_by_id[user_hero_id].get("hero_id")
                uh_doc = uh_by_id.get(user_hero_id) if user_hero_id else None
                hero_doc = hero_by_id.get(hero_id) if hero_id else None
                if uh_doc and hero_doc:
                    p = compute_hero_battle_power_v1(hero_doc, uh_doc)
                else:
                    p = 0
                team_slots.append({
                    "slot": slot_idx,
                    "user_hero_id": str(user_hero_id or ""),
                    "hero_id": str(hero_id or ""),
                    "power": p,
                })
                active_team_power += p

        return {
            "status": "ok",
            "server_id": sid,
            **metadata,
            "psp_present_for_server": True,
            "active_team_power": active_team_power,
            "team_missing": team_missing,
            "team_slots": team_slots,
            "owned_hero_count": owned_hero_count,
            "max_owned_hero_power": max_owned_hero_power,
            "owned_heroes_preview": owned_hero_powers[:10],
            "blocker": None,
        }

    @router.get("/metadata")
    async def get_battle_power_metadata():
        """Metadata read-only (no auth, no DB). Utile per UI introspection
        e per il validator statico 116A."""
        return {
            "status": "ok",
            **build_battle_power_metadata(),
        }

    # Sanity: il modulo dichiara la formula version come export per il
    # validator 116A.
    router.battle_power_formula_version = BATTLE_POWER_FORMULA_VERSION  # type: ignore[attr-defined]
    return router
