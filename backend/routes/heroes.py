"""
Divine Waifus - Heroes, Gacha & Team Routes
"""
import random
import uuid
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Depends, Response
from pydantic import BaseModel


GACHA_BANNERS = {
    "standard": {
        "name": "Banner Standard",
        "cost_single": 100,
        "cost_multi": 900,
        "rates": {1: 0.30, 2: 0.30, 3: 0.20, 4: 0.12, 5: 0.06, 6: 0.02},
        "guarantee_10": 4,
        "filter": None,
    },
    "elemental": {
        "name": "Banner Elementale",
        "cost_single": 120,
        "cost_multi": 1000,
        "rates": {1: 0.15, 2: 0.25, 3: 0.28, 4: 0.18, 5: 0.10, 6: 0.04},
        "guarantee_10": 4,
        "filter": None,
    },
    "premium": {
        "name": "Banner Premium",
        "cost_single": 200,
        "cost_multi": 1800,
        "rates": {1: 0.05, 2: 0.15, 3: 0.25, 4: 0.25, 5: 0.20, 6: 0.10},
        "guarantee_10": 5,
        "filter": None,
    },
}


def register_heroes_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== HEROES ====================
    @router.get("/heroes")
    async def get_all_heroes():
        heroes = await db.heroes.find({}, {"image_base64": 0}).to_list(100)
        for h in heroes:
            if not h.get("image_url"):
                h["image_url"] = None
        return [serialize_doc(h) for h in heroes]

    @router.get("/heroes/{hero_id}")
    async def get_hero(hero_id: str):
        hero = await db.heroes.find_one({"id": hero_id})
        if not hero:
            raise HTTPException(status_code=404, detail="Eroe non trovato")
        return serialize_doc(hero)

    @router.get("/user/heroes")
    async def get_user_heroes(
        response: Response,
        server_id: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
    ):
        """
        Pack 81 — `/api/user/heroes` server-scoped promotion.

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
            sid = server_id.strip()
            # PSP-aware: il roster server-scoped richiede un PSP esistente
            # per la coppia (uid, sid). Senza PSP -> blocker onesto, NESSUN
            # fallback legacy account-wide.
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            if not psp:
                response.headers["X-Server-Scope"] = "server_scoped"
                response.headers["X-Filter-Applied"] = "false"
                response.headers["X-Blocker"] = "PLAYER_SERVER_PROFILE_REQUIRED"
                response.headers["X-Server-Id"] = sid
                response.headers["X-Profile-Id"] = ""
                response.headers["X-Canonical-Decision"] = canonical_decision
                response.headers["X-Roster-Source"] = "server_scoped_no_psp_blocked"
                return []
            profile_id = str(psp.get("profile_id") or psp.get("_id") or "")
            # Filtro REALE su {user_id, server_id} — niente fallback account-wide.
            user_heroes = await db.user_heroes.find({"user_id": uid, "server_id": sid}).to_list(500)
            result = []
            for uh in user_heroes:
                hero = await db.heroes.find_one({"id": uh["hero_id"]})
                if hero:
                    merged = {
                        **serialize_doc(uh),
                        "hero_name": hero.get("name"),
                        "hero_element": hero.get("element"),
                        "hero_rarity": hero.get("rarity"),
                        "hero_image": hero.get("image_url") or hero.get("image_base64"),
                        "hero_stats": hero.get("base_stats"),
                        "hero_class": hero.get("hero_class"),
                    }
                    result.append(merged)
            response.headers["X-Server-Scope"] = "server_scoped"
            response.headers["X-Filter-Applied"] = "true"
            response.headers["X-Server-Id"] = sid
            response.headers["X-Profile-Id"] = profile_id
            response.headers["X-Blocker"] = ""
            response.headers["X-Canonical-Decision"] = canonical_decision
            response.headers["X-Roster-Source"] = "server_scoped_psp_filtered"
            response.headers["X-Roster-Count"] = str(len(result))
            return result
        # Nessun server_id -> legacy account-wide DEPRECATED. Le UI player-facing
        # devono passare server_id o bloccare onestamente. Restituiamo l'array
        # legacy ma marchiamo esplicitamente il deprecation via headers.
        user_heroes = await db.user_heroes.find({"user_id": uid}).to_list(500)
        result = []
        for uh in user_heroes:
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            if hero:
                merged = {
                    **serialize_doc(uh),
                    "hero_name": hero.get("name"),
                    "hero_element": hero.get("element"),
                    "hero_rarity": hero.get("rarity"),
                    "hero_image": hero.get("image_url") or hero.get("image_base64"),
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
        return result

    # ==================== GACHA ====================
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
        if not heroes:
            heroes = await db.heroes.find({"rarity": rarity}).to_list(100)
        if not heroes:
            heroes = await db.heroes.find({}).to_list(100)
        hero = random.choice(heroes)
        user_hero = {
            "id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"],
            "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow(),
        }
        await db.user_heroes.insert_one(user_hero)
        return hero, user_hero

    @router.post("/gacha/pull")
    async def gacha_pull(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
        # Pre-QA Stabilization 112 — DEAD-CODE QUARANTINE.
        # Questo endpoint duplica /api/gacha/pull in server.py (gia' quarantineato Pack 110).
        # Anche se non registrato attivamente, lo blindiamo per anti-regression.
        raise HTTPException(423, detail={
            "blocker": "GACHA_DUPLICATE_DEAD_CODE_QUARANTINED",
            "pack_origin": "pre_qa_stabilization_112",
            "canonical_path": "see /api/gacha/pull in backend/server.py (quarantined by Pack 110)",
            "no_gems_spend": True, "no_hero_grant": True,
        })

    @router.post("/gacha/pull10")
    async def gacha_pull_10(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
        # Pre-QA Stabilization 112 — DEAD-CODE QUARANTINE.
        raise HTTPException(423, detail={
            "blocker": "GACHA_DUPLICATE_DEAD_CODE_QUARANTINED",
            "pack_origin": "pre_qa_stabilization_112",
            "canonical_path": "see /api/gacha/pull10 in backend/server.py (quarantined by Pack 110)",
            "no_gems_spend": True, "no_hero_grant": True,
        })

    # ORIGINAL legacy implementations preserved as dead code below (unreachable):
    async def _legacy_gacha_pull_dead_code(req: GachaPullRequest, current_user: dict):
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

    async def _legacy_gacha_pull_10_dead_code(req: GachaPullRequest, current_user: dict):
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
                g = banner["guarantee_10"]
                rarity = random.choices(list(range(g, 7)), weights=[0.65, 0.25, 0.10] if g == 4 else [0.70, 0.30])[0]
                query: dict = {"rarity": rarity}
                heroes = await db.heroes.find(query).to_list(100)
                if not heroes:
                    heroes = await db.heroes.find({}).to_list(100)
                hero = random.choice(heroes)
                uh = {"id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"], "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow()}
                await db.user_heroes.insert_one(uh)
                results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
            else:
                hero, uh = await _do_gacha_pull(user_id, req.banner)
                results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
        updated_user = await db.users.find_one({"id": user_id})
        return {"results": results, "remaining_gems": updated_user.get("gems", 0), "banner": req.banner}

    @router.get("/gacha/banners")
    async def get_gacha_banners():
        return {k: {"name": v["name"], "cost_single": v["cost_single"], "cost_multi": v["cost_multi"],
                    "rates": v["rates"], "guarantee_10": v["guarantee_10"]} for k, v in GACHA_BANNERS.items()}

    # ==================== TEAM ====================
    @router.get("/team")
    async def get_team(current_user: dict = Depends(get_current_user)):
        team = await db.teams.find_one({"user_id": current_user["id"], "is_active": True})
        if team:
            return serialize_doc(team)
        return {"formation": [], "total_power": 0}

    # ==================== USER PROFILE ====================
    @router.get("/user/profile")
    async def get_profile(current_user: dict = Depends(get_current_user)):
        safe_user = {k: v for k, v in current_user.items() if k != "password"}
        return safe_user
