"""Pack 104 — Economy Strict Writes (shop buy / soul forge retire / equipment).

Endpoints registrati su prefix `/api/economy/strict`:

  * GET  /api/economy/strict/health
  * GET  /api/economy/strict/shop/catalog
  * POST /api/economy/strict/shop/buy?server_id=<sid>
  * POST /api/economy/strict/soul-forge/retire?server_id=<sid>
  * POST /api/economy/strict/equipment/equip?server_id=<sid>
  * POST /api/economy/strict/equipment/unequip?server_id=<sid>
  * POST /api/economy/strict/forge/preflight?server_id=<sid>         (deferred 503)

SAFETY Pack 104:
  * Triple kill switch AND su ogni endpoint mutating:
      - global ledger live (`REWARD_CLAIM_LEDGER_LIVE_ENABLED`)
      - economy writes strict (`ECONOMY_STRICT_WRITES_ENABLED`)
      - per-source (`SHOP_BUY_STRICT_ENABLED`, ecc.)
  * Solo test marker `pack_104_test_artifact` accettato (finche' runtime non e' live).
  * PSP obbligatorio. NO fallback `s1`.
  * idempotency_token mandatory (≥ 8 char).
  * Server-side claim_key deterministico, mai client-derived.
  * Reward FISSO server-side dal catalog/band. Payload client IGNORATO.
  * Solo PSP `soft_currencies` mutate. NO `users.gold/gems/experience` mutation.
  * NO `wallets`, `user_materials`, `user_fragments` (legacy account-wide).
  * NO premium/hard/gacha/IAP.
  * Audit ledger row su `reward_claim_ledger` per ogni mutating op.
  * Frontend guard `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED` default OFF.
"""
import hashlib
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Depends
from pydantic import BaseModel

from data.shop_strict_catalog_v1 import (
    CATALOG_VERSION as SHOP_CATALOG_VERSION,
    get_item as _shop_get_item,
    get_shop as _shop_get_shop,
    list_shops_summary as _shop_list_summary,
)
from data.forge_strict_catalog_v1 import (
    CATALOG_VERSION as FORGE_CATALOG_VERSION,
    ALLOWED_MATERIALS,
    MAX_EQUIPMENT_LEVEL_STRICT,
    MAX_EQUIPMENT_RARITY_STRICT,
    UPGRADE_STAT_BOOST_PER_LEVEL,
    get_upgrade_cost as _forge_get_upgrade_cost,
    get_recipe as _forge_get_recipe,
    list_recipes_summary as _forge_list_recipes,
    get_fusion_requirement as _forge_get_fusion_req,
)
from utils.reward_source_registry import (
    REWARD_SOURCE_REGISTRY,
    lookup_source,
    is_source_live,
    get_grant_fn,
    _PremiumGrantBlocked,
    _RewardTypeNotAllowed,
    ALLOWED_SOFT_CURRENCIES,
    FORBIDDEN_REWARD_TYPES,
)

PACK_104_USER_TEST_MARKER = "pack_104_test_artifact"
PACK_105_USER_TEST_MARKER = "pack_105_test_artifact"

# Kill switch env names (default OFF).
GLOBAL_LEDGER_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
ECONOMY_STRICT_KILL_SWITCH_ENV = "ECONOMY_STRICT_WRITES_ENABLED"
SHOP_BUY_KILL_SWITCH_ENV = "SHOP_BUY_STRICT_ENABLED"
SOUL_FORGE_KILL_SWITCH_ENV = "SOUL_FORGE_RETIRE_STRICT_ENABLED"
EQUIPMENT_KILL_SWITCH_ENV = "EQUIPMENT_STRICT_WRITES_ENABLED"
FORGE_KILL_SWITCH_ENV = "FORGE_STRICT_WRITES_ENABLED"
# Pack 105 per-source kill switches.
EQUIPMENT_UPGRADE_KILL_SWITCH_ENV = "EQUIPMENT_UPGRADE_STRICT_ENABLED"
FORGE_CRAFT_KILL_SWITCH_ENV = "FORGE_CRAFT_STRICT_ENABLED"
EQUIPMENT_FUSION_KILL_SWITCH_ENV = "EQUIPMENT_FUSION_STRICT_ENABLED"

# Source IDs.
SHOP_BUY_SOURCE = "shop_buy_strict_claim"
SOUL_FORGE_RETIRE_SOURCE = "soul_forge_retire_strict_claim"
EQUIPMENT_EQUIP_SOURCE = "equipment_equip_strict_claim"
EQUIPMENT_UNEQUIP_SOURCE = "equipment_unequip_strict_claim"
EQUIPMENT_UPGRADE_SOURCE = "equipment_upgrade_strict_claim"
FORGE_CRAFT_SOURCE = "forge_craft_strict_claim"
EQUIPMENT_FUSION_SOURCE = "equipment_fusion_strict_claim"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _global_ledger_on() -> bool:
    return _truthy(os.getenv(GLOBAL_LEDGER_KILL_SWITCH_ENV))


def _economy_strict_on() -> bool:
    return _truthy(os.getenv(ECONOMY_STRICT_KILL_SWITCH_ENV))


def _shop_buy_on() -> bool:
    return _truthy(os.getenv(SHOP_BUY_KILL_SWITCH_ENV))


def _soul_forge_on() -> bool:
    return _truthy(os.getenv(SOUL_FORGE_KILL_SWITCH_ENV))


def _equipment_on() -> bool:
    return _truthy(os.getenv(EQUIPMENT_KILL_SWITCH_ENV))


def _forge_on() -> bool:
    return _truthy(os.getenv(FORGE_KILL_SWITCH_ENV))


def _equipment_upgrade_on() -> bool:
    return _truthy(os.getenv(EQUIPMENT_UPGRADE_KILL_SWITCH_ENV))


def _forge_craft_on() -> bool:
    return _truthy(os.getenv(FORGE_CRAFT_KILL_SWITCH_ENV))


def _equipment_fusion_on() -> bool:
    return _truthy(os.getenv(EQUIPMENT_FUSION_KILL_SWITCH_ENV))


async def _require_pack_104_test_user(db, uid: str) -> None:
    """Test-only gate: solo utenti marcati `pack_104_test_artifact` possono eseguire."""
    user_doc = await db.users.find_one({"id": uid})
    if not user_doc or not user_doc.get(PACK_104_USER_TEST_MARKER):
        raise HTTPException(403, detail={
            "blocker": "ECONOMY_STRICT_ENDPOINT_TEST_ONLY",
            "marker_required": PACK_104_USER_TEST_MARKER,
        })


async def _require_pack_105_test_user(db, uid: str) -> None:
    """Test-only gate: solo utenti marcati `pack_105_test_artifact` possono eseguire i path Pack 105."""
    user_doc = await db.users.find_one({"id": uid})
    if not user_doc or not user_doc.get(PACK_105_USER_TEST_MARKER):
        raise HTTPException(403, detail={
            "blocker": "FORGE_STRICT_ENDPOINT_TEST_ONLY",
            "marker_required": PACK_105_USER_TEST_MARKER,
        })


async def _require_psp(db, uid: str, sid: str) -> Dict[str, Any]:
    psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
    if not psp:
        raise HTTPException(409, detail={
            "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
            "server_id": sid,
        })
    return psp


def _validate_idempotency_token(token: Optional[str]) -> None:
    if not token or not isinstance(token, str) or len(token) < 8:
        raise HTTPException(400, detail={"blocker": "IDEMPOTENCY_TOKEN_REQUIRED"})


def _validate_server_id(server_id: Optional[str]) -> str:
    if not server_id or not isinstance(server_id, str) or not server_id.strip():
        raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
    return server_id.strip()


def _gate_triple(per_source_check) -> None:
    """Triple kill switch AND: global ledger + economy strict + per-source."""
    if not _global_ledger_on():
        raise HTTPException(503, detail={
            "blocker": "REWARD_CLAIM_LEDGER_DISABLED",
            "kill_switch_env": GLOBAL_LEDGER_KILL_SWITCH_ENV,
        })
    if not _economy_strict_on():
        raise HTTPException(503, detail={
            "blocker": "ECONOMY_STRICT_WRITES_DISABLED",
            "kill_switch_env": ECONOMY_STRICT_KILL_SWITCH_ENV,
        })
    per_source_check()


# ====================================================================
# Pydantic request models
# ====================================================================


class ShopBuyRequest(BaseModel):
    shop_id: str
    item_id: str
    idempotency_token: str
    # NO price field — server-side catalog only.


class SoulForgeRetireRequest(BaseModel):
    user_hero_id: str
    idempotency_token: str


class EquipmentEquipRequest(BaseModel):
    equipment_id: str
    user_hero_id: str
    idempotency_token: str


class EquipmentUnequipRequest(BaseModel):
    equipment_id: str
    idempotency_token: str


# Pack 105 request models.


class EquipmentUpgradeRequest(BaseModel):
    equipment_id: str
    idempotency_token: str
    # NO cost/level fields — server-side catalog determines target_level = current+1 and cost.


class ForgeCraftRequest(BaseModel):
    recipe_id: str
    idempotency_token: str
    # NO cost/grant fields — server-side recipe catalog.


class EquipmentFusionRequest(BaseModel):
    base_equipment_id: str
    fodder_equipment_ids: list  # list of equipment_id to consume
    idempotency_token: str
    # NO cost/grant fields — server-side fusion requirement catalog.


# ====================================================================
# Registration
# ====================================================================


def register_economy_strict_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/economy/strict/health")
    async def economy_strict_health():
        return {
            "endpoint_group": "/api/economy/strict",
            "pack_origin": "pack_104+pack_105",
            "pack_104_test_marker": PACK_104_USER_TEST_MARKER,
            "pack_105_test_marker": PACK_105_USER_TEST_MARKER,
            "kill_switches": {
                GLOBAL_LEDGER_KILL_SWITCH_ENV: _global_ledger_on(),
                ECONOMY_STRICT_KILL_SWITCH_ENV: _economy_strict_on(),
                SHOP_BUY_KILL_SWITCH_ENV: _shop_buy_on(),
                SOUL_FORGE_KILL_SWITCH_ENV: _soul_forge_on(),
                EQUIPMENT_KILL_SWITCH_ENV: _equipment_on(),
                FORGE_KILL_SWITCH_ENV: _forge_on(),
                EQUIPMENT_UPGRADE_KILL_SWITCH_ENV: _equipment_upgrade_on(),
                FORGE_CRAFT_KILL_SWITCH_ENV: _forge_craft_on(),
                EQUIPMENT_FUSION_KILL_SWITCH_ENV: _equipment_fusion_on(),
            },
            "sources": {
                "shop_buy_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "soul_forge_retire_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "equipment_equip_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "equipment_unequip_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "equipment_upgrade_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "forge_craft_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
                "equipment_fusion_strict_claim": "READY_GATED_RUNTIME_REQUIRED",
            },
            "shop_catalog_version": SHOP_CATALOG_VERSION,
            "forge_catalog_version": FORGE_CATALOG_VERSION,
            "reward_live_general": False,
            "premium_grants": False,
            "release_readiness_claimed": False,
            "no_users_gold_gems_experience_mutation": True,
            "no_account_wide_writes": True,
            "no_cross_server": True,
            "no_iap_gacha_payment": True,
            "psp_material_storage_active": True,
            "_slc_pack_104_economy_strict_health": True,
            "_slc_pack_105_forge_strict_health": True,
        }

    @router.get("/economy/strict/shop/catalog")
    async def economy_strict_shop_catalog():
        """Catalog pubblico, read-only, identico cross-server."""
        return {
            "catalog_version": SHOP_CATALOG_VERSION,
            "shops": _shop_list_summary(),
            "content_identical_across_servers": True,
            "reward_live_general": False,
            "release_readiness_claimed": False,
            "_slc_pack_104_shop_catalog": True,
        }

    # ---------------- Shop Buy Strict ----------------

    @router.post("/economy/strict/shop/buy")
    async def shop_buy_strict(
        req: ShopBuyRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        # 1. Triple kill switch AND
        _gate_triple(lambda: (_shop_buy_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "SHOP_BUY_STRICT_DISABLED",
                "kill_switch_env": SHOP_BUY_KILL_SWITCH_ENV,
            })
        )))
        # 2. server_id + idempotency
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        # 3. Test marker
        await _require_pack_104_test_user(db, uid)
        # 4. PSP
        psp = await _require_psp(db, uid, sid)
        # 5. Server-side catalog lookup. NESSUN dato dal client per cost/grant.
        item = _shop_get_item(req.shop_id, req.item_id)
        if not item:
            raise HTTPException(404, detail={
                "blocker": "SHOP_ITEM_NOT_FOUND",
                "shop_id": req.shop_id,
                "item_id": req.item_id,
            })
        cost = item["cost"]
        grant = item["grant"]
        # 6. Anti-leak: forbid premium in cost/grant (catalog gia' validato, double-check).
        for k in list(cost.keys()) + list(grant.keys()):
            if k in FORBIDDEN_REWARD_TYPES:
                raise HTTPException(422, detail={
                    "blocker": "FORBIDDEN_CURRENCY",
                    "key": k,
                })
            if k not in ALLOWED_SOFT_CURRENCIES:
                raise HTTPException(422, detail={
                    "blocker": "CURRENCY_NOT_ALLOWED",
                    "key": k,
                })
        # 7. Server-side claim_key deterministico (Pack 104).
        claim_key = f"shop_buy_{sid}_{req.shop_id}_{req.item_id}_{req.idempotency_token}"
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        # 8. Idempotency PRE-check
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": SHOP_BUY_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "shop_id": req.shop_id,
                "item_id": req.item_id,
                "claim_source": SHOP_BUY_SOURCE,
                "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False,
                "premium_grant_blocked": True,
                "_slc_pack_104_shop_buy_idempotent": True,
            }
        # 9. Check soft currencies balance server-side.
        soft = (psp.get("soft_currencies") or {})
        for k, amt in cost.items():
            if int(soft.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_SOFT_CURRENCY",
                    "key": k,
                    "required": int(amt),
                    "available": int(soft.get(k, 0)),
                })
        # 10. Atomic: decrement cost + increment grant on PSP.soft_currencies.
        dec = {f"soft_currencies.{k}": -int(amt) for k, amt in cost.items()}
        inc_grant = {f"soft_currencies.{k}": int(amt) for k, amt in grant.items()}
        # Merge (Mongo $inc handles negatives)
        all_inc: Dict[str, int] = {}
        for d in (dec, inc_grant):
            for k, v in d.items():
                all_inc[k] = all_inc.get(k, 0) + v
        # 11. Grant via source registry (validates per-key cap).
        grant_fn = get_grant_fn(SHOP_BUY_SOURCE)
        assert grant_fn is not None
        try:
            grant_fn(db, uid, sid, {"_server_resolved_grant": grant})
        except _PremiumGrantBlocked as e:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED", "key": str(e)})
        except _RewardTypeNotAllowed as e:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED", "key": str(e)})
        # 12. Apply.
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": all_inc},
            upsert=False,
        )
        # 13. Ledger row.
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid,
            "server_id": sid,
            "claim_source": SHOP_BUY_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "shop_id": req.shop_id,
            "item_id": req.item_id,
            "rewards": {"server_scoped_grant": grant, "server_scoped_cost": cost},
            "applied_at": now,
            "created_at": now,
            "_slc_pack_104_shop_buy_strict": True,
            "_slc_pack_104_server_side_catalog": True,
            "_slc_pack_104_server_side_claim_key": True,
            "_slc_pack_96_controlled_claim": True,
            "_slc_pack_95_reward_claim_ledger": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            # Race: rollback inc, ritorna replay.
            rb = {k: -v for k, v in all_inc.items()}
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": rb},
            )
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": SHOP_BUY_SOURCE,
                "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "shop_id": req.shop_id, "item_id": req.item_id,
                    "claim_source": SHOP_BUY_SOURCE, "claim_key": claim_key,
                    "rewards": existing2.get("rewards"),
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False, "premium_grant_blocked": True,
                    "_slc_pack_104_shop_buy_idempotent_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "shop_id": req.shop_id,
            "item_id": req.item_id,
            "claim_source": SHOP_BUY_SOURCE,
            "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "reward_live_general": False,
            "premium_grant_blocked": True,
            "_slc_pack_104_shop_buy_strict": True,
        }

    # ---------------- Soul Forge Retire Strict ----------------

    @router.post("/economy/strict/soul-forge/retire")
    async def soul_forge_retire_strict(
        req: SoulForgeRetireRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_soul_forge_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "SOUL_FORGE_RETIRE_STRICT_DISABLED",
                "kill_switch_env": SOUL_FORGE_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_104_test_user(db, uid)
        await _require_psp(db, uid, sid)
        # claim_key deterministico server-side. Calcolato presto cosi' il
        # ledger PRE-check viene PRIMA del check ownership (replay-safe anche
        # dopo che l'hero e' gia' stato cancellato dal retire originale).
        claim_key = f"soul_forge_retire_{sid}_{req.user_hero_id}"
        server_idem_token = hashlib.sha1(f"{claim_key}|{req.idempotency_token}".encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": SOUL_FORGE_RETIRE_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "user_hero_id": req.user_hero_id,
                "claim_source": SOUL_FORGE_RETIRE_SOURCE,
                "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False,
                "premium_grant_blocked": True,
                "_slc_pack_104_soul_forge_retire_idempotent": True,
            }
        # Server-scoped hero ownership: (id, user_id, server_id). Solo dopo
        # il ledger PRE-check, cosi' un retire di hero gia' eliminato torna replay.
        uh = await db.user_heroes.find_one({
            "id": req.user_hero_id, "user_id": uid, "server_id": sid,
        })
        if not uh:
            raise HTTPException(404, detail={
                "blocker": "HERO_NOT_OWNED_ON_SERVER",
                "server_id": sid,
                "user_hero_id": req.user_hero_id,
            })
        # Hero non deve essere in active team server-scoped.
        team = await db.teams.find_one({"user_id": uid, "server_id": sid, "is_active": True})
        if team:
            in_team = any(p.get("user_hero_id") == req.user_hero_id for p in (team.get("formation") or []))
            if in_team:
                raise HTTPException(409, detail={
                    "blocker": "HERO_IN_ACTIVE_TEAM",
                    "user_hero_id": req.user_hero_id,
                })
        # Compute reward (stars band server-side).
        stars = int(uh.get("stars", 1))
        grant_fn = get_grant_fn(SOUL_FORGE_RETIRE_SOURCE)
        assert grant_fn is not None
        try:
            inc = grant_fn(db, uid, sid, {"_server_resolved_stars": stars})
        except _PremiumGrantBlocked as e:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED", "key": str(e)})
        except _RewardTypeNotAllowed as e:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED", "key": str(e)})
        # Apply grant first.
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": inc},
            upsert=False,
        )
        now = datetime.utcnow()
        rewards_summary = {k.replace("soft_currencies.", ""): v for k, v in inc.items()}
        ledger_row = {
            "user_id": uid,
            "server_id": sid,
            "claim_source": SOUL_FORGE_RETIRE_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "user_hero_id": req.user_hero_id,
            "stars": stars,
            "rewards": {"server_scoped_grant": rewards_summary, "retired_hero_stars": stars},
            "applied_at": now,
            "created_at": now,
            "_slc_pack_104_soul_forge_retire_strict": True,
            "_slc_pack_104_server_side_claim_key": True,
            "_slc_pack_104_no_cross_server_retire": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            rb = {k: -v for k, v in inc.items()}
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": rb},
            )
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": SOUL_FORGE_RETIRE_SOURCE,
                "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "user_hero_id": req.user_hero_id,
                    "claim_source": SOUL_FORGE_RETIRE_SOURCE, "claim_key": claim_key,
                    "rewards": existing2.get("rewards"),
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False, "premium_grant_blocked": True,
                    "_slc_pack_104_soul_forge_retire_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        # Delete hero server-scoped + remove from equipment (server-scoped).
        await db.user_heroes.delete_one({"id": req.user_hero_id, "user_id": uid, "server_id": sid})
        await db.user_equipment.update_many(
            {"user_id": uid, "server_id": sid, "equipped_to": req.user_hero_id},
            {"$unset": {"equipped_to": ""}},
        )
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "user_hero_id": req.user_hero_id,
            "claim_source": SOUL_FORGE_RETIRE_SOURCE,
            "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "stars": stars,
            "reward_live_general": False,
            "premium_grant_blocked": True,
            "_slc_pack_104_soul_forge_retire_strict": True,
        }

    # ---------------- Equipment Equip Strict ----------------

    @router.post("/economy/strict/equipment/equip")
    async def equipment_equip_strict(
        req: EquipmentEquipRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_equipment_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "EQUIPMENT_STRICT_WRITES_DISABLED",
                "kill_switch_env": EQUIPMENT_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_104_test_user(db, uid)
        await _require_psp(db, uid, sid)
        # Ownership server-scoped: equipment + hero must both match (user_id, server_id).
        equip = await db.user_equipment.find_one({
            "id": req.equipment_id, "user_id": uid, "server_id": sid,
        })
        if not equip:
            raise HTTPException(404, detail={
                "blocker": "EQUIPMENT_NOT_OWNED_ON_SERVER",
                "equipment_id": req.equipment_id,
                "server_id": sid,
            })
        hero = await db.user_heroes.find_one({
            "id": req.user_hero_id, "user_id": uid, "server_id": sid,
        })
        if not hero:
            raise HTTPException(404, detail={
                "blocker": "HERO_NOT_OWNED_ON_SERVER",
                "user_hero_id": req.user_hero_id,
                "server_id": sid,
            })
        slot = equip.get("slot", "weapon")
        claim_key = (
            f"equipment_equip_{sid}_{req.user_hero_id}_{slot}_{req.equipment_id}"
            f"_{req.idempotency_token}"
        )
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_EQUIP_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "equipment_id": req.equipment_id,
                "user_hero_id": req.user_hero_id,
                "slot": slot,
                "claim_source": EQUIPMENT_EQUIP_SOURCE,
                "claim_key": claim_key,
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False,
                "_slc_pack_104_equipment_equip_idempotent": True,
            }
        # Unequip current equipment in same slot, if any (server-scoped).
        prev_in_slot = await db.user_equipment.find_one({
            "user_id": uid, "server_id": sid,
            "equipped_to": req.user_hero_id,
            "slot": slot,
        })
        if prev_in_slot and prev_in_slot.get("id") != req.equipment_id:
            await db.user_equipment.update_one(
                {"id": prev_in_slot["id"], "user_id": uid, "server_id": sid},
                {"$unset": {"equipped_to": ""}, "$set": {"_slc_pack_104_equipment_strict_swap_off": True}},
            )
        # Equip target.
        await db.user_equipment.update_one(
            {"id": req.equipment_id, "user_id": uid, "server_id": sid},
            {"$set": {
                "equipped_to": req.user_hero_id,
                "_slc_pack_104_equipment_strict_equip": True,
            }},
        )
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid,
            "server_id": sid,
            "claim_source": EQUIPMENT_EQUIP_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "equipment_id": req.equipment_id,
            "user_hero_id": req.user_hero_id,
            "slot": slot,
            "rewards": {},
            "applied_at": now,
            "created_at": now,
            "_slc_pack_104_equipment_equip_strict": True,
            "_slc_pack_104_no_grant_currency": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            # Race: idempotent replay.
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": EQUIPMENT_EQUIP_SOURCE,
                "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "equipment_id": req.equipment_id, "user_hero_id": req.user_hero_id,
                    "slot": slot,
                    "claim_source": EQUIPMENT_EQUIP_SOURCE, "claim_key": claim_key,
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False,
                    "_slc_pack_104_equipment_equip_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "equipment_id": req.equipment_id,
            "user_hero_id": req.user_hero_id,
            "slot": slot,
            "claim_source": EQUIPMENT_EQUIP_SOURCE,
            "claim_key": claim_key,
            "applied_at": now.isoformat(),
            "reward_live_general": False,
            "_slc_pack_104_equipment_equip_strict": True,
        }

    # ---------------- Equipment Unequip Strict ----------------

    @router.post("/economy/strict/equipment/unequip")
    async def equipment_unequip_strict(
        req: EquipmentUnequipRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_equipment_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "EQUIPMENT_STRICT_WRITES_DISABLED",
                "kill_switch_env": EQUIPMENT_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_104_test_user(db, uid)
        await _require_psp(db, uid, sid)
        equip = await db.user_equipment.find_one({
            "id": req.equipment_id, "user_id": uid, "server_id": sid,
        })
        if not equip:
            raise HTTPException(404, detail={
                "blocker": "EQUIPMENT_NOT_OWNED_ON_SERVER",
                "equipment_id": req.equipment_id,
                "server_id": sid,
            })
        claim_key = f"equipment_unequip_{sid}_{req.equipment_id}_{req.idempotency_token}"
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_UNEQUIP_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "equipment_id": req.equipment_id,
                "claim_source": EQUIPMENT_UNEQUIP_SOURCE,
                "claim_key": claim_key,
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False,
                "_slc_pack_104_equipment_unequip_idempotent": True,
            }
        await db.user_equipment.update_one(
            {"id": req.equipment_id, "user_id": uid, "server_id": sid},
            {"$unset": {"equipped_to": ""}, "$set": {"_slc_pack_104_equipment_strict_unequip": True}},
        )
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid,
            "server_id": sid,
            "claim_source": EQUIPMENT_UNEQUIP_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "equipment_id": req.equipment_id,
            "rewards": {},
            "applied_at": now,
            "created_at": now,
            "_slc_pack_104_equipment_unequip_strict": True,
            "_slc_pack_104_no_grant_currency": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": EQUIPMENT_UNEQUIP_SOURCE,
                "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "equipment_id": req.equipment_id,
                    "claim_source": EQUIPMENT_UNEQUIP_SOURCE, "claim_key": claim_key,
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False,
                    "_slc_pack_104_equipment_unequip_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "equipment_id": req.equipment_id,
            "claim_source": EQUIPMENT_UNEQUIP_SOURCE,
            "claim_key": claim_key,
            "applied_at": now.isoformat(),
            "reward_live_general": False,
            "_slc_pack_104_equipment_unequip_strict": True,
        }

    # ---------------- Forge / Upgrade / Fusion (Pack 105 — READY_GATED) ----------------

    @router.post("/economy/strict/forge/preflight")
    async def forge_strict_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        """Pack 105 — Forge strict preflight + readiness.

        Restituisce lo stato dei 3 sotto-switch Pack 105:
          * EQUIPMENT_UPGRADE_STRICT_ENABLED
          * FORGE_CRAFT_STRICT_ENABLED
          * EQUIPMENT_FUSION_STRICT_ENABLED

        Pack 104 ritornava 503 DEFERRED. Pack 105 ora ritorna 200 OK con
        i sub-blockers risolti, conservando il triple kill switch AND default OFF.
        """
        return {
            "pack_origin": "pack_105",
            "kill_switches": {
                GLOBAL_LEDGER_KILL_SWITCH_ENV: _global_ledger_on(),
                ECONOMY_STRICT_KILL_SWITCH_ENV: _economy_strict_on(),
                FORGE_KILL_SWITCH_ENV: _forge_on(),
                EQUIPMENT_UPGRADE_KILL_SWITCH_ENV: _equipment_upgrade_on(),
                FORGE_CRAFT_KILL_SWITCH_ENV: _forge_craft_on(),
                EQUIPMENT_FUSION_KILL_SWITCH_ENV: _equipment_fusion_on(),
            },
            "sub_paths": {
                "equipment_upgrade_strict": "READY_GATED_RUNTIME_REQUIRED",
                "forge_craft_strict": "READY_GATED_RUNTIME_REQUIRED",
                "equipment_fusion_strict": "READY_GATED_RUNTIME_REQUIRED",
            },
            "forge_catalog_version": FORGE_CATALOG_VERSION,
            "max_equipment_level_strict": MAX_EQUIPMENT_LEVEL_STRICT,
            "max_equipment_rarity_strict": MAX_EQUIPMENT_RARITY_STRICT,
            "reward_live_general": False,
            "premium_grants": False,
            "release_readiness_claimed": False,
            "no_users_gold_gems_experience_mutation": True,
            "_slc_pack_105_forge_preflight": True,
        }

    # ---------------- Equipment Upgrade Strict (Pack 105) ----------------

    @router.post("/economy/strict/equipment/upgrade")
    async def equipment_upgrade_strict(
        req: EquipmentUpgradeRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_equipment_upgrade_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "EQUIPMENT_UPGRADE_STRICT_DISABLED",
                "kill_switch_env": EQUIPMENT_UPGRADE_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_105_test_user(db, uid)
        psp = await _require_psp(db, uid, sid)
        equip = await db.user_equipment.find_one({
            "id": req.equipment_id, "user_id": uid, "server_id": sid,
        })
        if not equip:
            raise HTTPException(404, detail={
                "blocker": "EQUIPMENT_NOT_OWNED_ON_SERVER",
                "equipment_id": req.equipment_id,
                "server_id": sid,
            })
        current_level = int(equip.get("level", 1))
        target_level = current_level + 1
        if target_level > MAX_EQUIPMENT_LEVEL_STRICT:
            raise HTTPException(409, detail={
                "blocker": "EQUIPMENT_MAX_LEVEL_REACHED",
                "current_level": current_level,
                "max_level": MAX_EQUIPMENT_LEVEL_STRICT,
            })
        # Cost server-side dal catalog.
        cost = _forge_get_upgrade_cost(target_level)
        if not cost:
            raise HTTPException(500, detail={"blocker": "UPGRADE_COST_LOOKUP_FAILED"})
        # claim_key server-side deterministico basato su idempotency_token
        # (cosi' replay dopo upgrade originale ritorna idempotent_replay anche
        # se current_level e' gia' avanzato).
        claim_key = f"equipment_upgrade_{sid}_{req.equipment_id}_{req.idempotency_token}"
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_UPGRADE_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "equipment_id": req.equipment_id,
                "target_level": target_level,
                "claim_source": EQUIPMENT_UPGRADE_SOURCE,
                "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False,
                "premium_grant_blocked": True,
                "_slc_pack_105_equipment_upgrade_idempotent": True,
            }
        # Check soft currencies balance.
        soft = (psp.get("soft_currencies") or {})
        for k, amt in cost["soft_currencies"].items():
            if int(soft.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_SOFT_CURRENCY",
                    "key": k, "required": int(amt), "available": int(soft.get(k, 0)),
                })
        # Check materials balance (PSP.materials).
        mat = (psp.get("materials") or {})
        for k, amt in cost["materials"].items():
            if int(mat.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_MATERIAL",
                    "key": k, "required": int(amt), "available": int(mat.get(k, 0)),
                })
        # Atomic spend: PSP soft + materials decrement.
        spend_inc: Dict[str, int] = {}
        for k, amt in cost["soft_currencies"].items():
            spend_inc[f"soft_currencies.{k}"] = -int(amt)
        for k, amt in cost["materials"].items():
            spend_inc[f"materials.{k}"] = -int(amt)
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": spend_inc},
            upsert=False,
        )
        # Apply upgrade on user_equipment server-scoped: level +1, stats +5% from current.
        base_stats = equip.get("base_stats") or equip.get("stats") or {}
        mult = 1 + (target_level - 1) * UPGRADE_STAT_BOOST_PER_LEVEL
        new_stats: Dict[str, Any] = {}
        for k, v in base_stats.items():
            if isinstance(v, int):
                new_stats[k] = int(v * mult)
            elif isinstance(v, float):
                new_stats[k] = round(v * mult, 3)
            else:
                new_stats[k] = v
        await db.user_equipment.update_one(
            {"id": req.equipment_id, "user_id": uid, "server_id": sid},
            {"$set": {
                "level": target_level,
                "stats": new_stats,
                "_slc_pack_105_equipment_upgrade_strict": True,
            }},
        )
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_UPGRADE_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "equipment_id": req.equipment_id,
            "target_level": target_level,
            "rewards": {
                "server_scoped_cost": cost,
                "new_level": target_level,
                "new_stats": new_stats,
            },
            "applied_at": now, "created_at": now,
            "_slc_pack_105_equipment_upgrade_strict": True,
            "_slc_pack_105_server_side_cost_catalog": True,
            "_slc_pack_105_psp_material_spend": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            # Rollback.
            rb = {k: -v for k, v in spend_inc.items()}
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid}, {"$inc": rb},
            )
            await db.user_equipment.update_one(
                {"id": req.equipment_id, "user_id": uid, "server_id": sid},
                {"$set": {"level": current_level, "stats": equip.get("stats") or {}}},
            )
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": EQUIPMENT_UPGRADE_SOURCE,
                "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True, "server_id": sid,
                    "equipment_id": req.equipment_id, "target_level": target_level,
                    "claim_source": EQUIPMENT_UPGRADE_SOURCE, "claim_key": claim_key,
                    "rewards": existing2.get("rewards"),
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False, "premium_grant_blocked": True,
                    "_slc_pack_105_equipment_upgrade_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "equipment_id": req.equipment_id,
            "target_level": target_level,
            "claim_source": EQUIPMENT_UPGRADE_SOURCE,
            "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "reward_live_general": False,
            "premium_grant_blocked": True,
            "_slc_pack_105_equipment_upgrade_strict": True,
        }

    # ---------------- Forge Craft Strict (Pack 105) ----------------

    @router.post("/economy/strict/forge/craft")
    async def forge_craft_strict(
        req: ForgeCraftRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_forge_craft_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "FORGE_CRAFT_STRICT_DISABLED",
                "kill_switch_env": FORGE_CRAFT_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_105_test_user(db, uid)
        psp = await _require_psp(db, uid, sid)
        recipe = _forge_get_recipe(req.recipe_id)
        if not recipe:
            raise HTTPException(404, detail={
                "blocker": "FORGE_RECIPE_NOT_FOUND",
                "recipe_id": req.recipe_id,
            })
        cost = recipe["cost"]
        tpl = recipe["grant_equipment_template"]
        claim_key = f"forge_craft_{sid}_{req.recipe_id}_{req.idempotency_token}"
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": FORGE_CRAFT_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True, "server_id": sid,
                "recipe_id": req.recipe_id,
                "claim_source": FORGE_CRAFT_SOURCE, "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False, "premium_grant_blocked": True,
                "_slc_pack_105_forge_craft_idempotent": True,
            }
        soft = (psp.get("soft_currencies") or {})
        for k, amt in cost["soft_currencies"].items():
            if int(soft.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_SOFT_CURRENCY",
                    "key": k, "required": int(amt), "available": int(soft.get(k, 0)),
                })
        mat = (psp.get("materials") or {})
        for k, amt in cost["materials"].items():
            if int(mat.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_MATERIAL",
                    "key": k, "required": int(amt), "available": int(mat.get(k, 0)),
                })
        spend_inc: Dict[str, int] = {}
        for k, amt in cost["soft_currencies"].items():
            spend_inc[f"soft_currencies.{k}"] = -int(amt)
        for k, amt in cost["materials"].items():
            spend_inc[f"materials.{k}"] = -int(amt)
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": spend_inc},
            upsert=False,
        )
        # Grant new user_equipment server-scoped from template (no client trust).
        new_eq_id = f"eq_forge_{uid}_{int(time.time() * 1000)}_{server_idem_token[:8]}"
        new_eq = {
            "id": new_eq_id,
            "user_id": uid,
            "server_id": sid,
            "template_id": req.recipe_id,
            "name": tpl["name"],
            "slot": tpl["slot"],
            "rarity": tpl["rarity"],
            "level": tpl["level"],
            "stats": dict(tpl["stats"]),
            "base_stats": dict(tpl["stats"]),
            "obtained_at": datetime.utcnow(),
            "_slc_pack_105_forge_craft_strict": True,
            "_slc_pack_105_server_side_recipe": True,
        }
        await db.user_equipment.insert_one(new_eq)
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid, "server_id": sid,
            "claim_source": FORGE_CRAFT_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "recipe_id": req.recipe_id,
            "rewards": {
                "server_scoped_cost": cost,
                "granted_equipment_id": new_eq_id,
                "granted_equipment_template": tpl,
            },
            "applied_at": now, "created_at": now,
            "_slc_pack_105_forge_craft_strict": True,
            "_slc_pack_105_server_side_recipe_catalog": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            # Rollback.
            rb = {k: -v for k, v in spend_inc.items()}
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid}, {"$inc": rb},
            )
            await db.user_equipment.delete_one({"id": new_eq_id, "user_id": uid, "server_id": sid})
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": FORGE_CRAFT_SOURCE, "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                return {
                    "idempotent_replay": True, "server_id": sid,
                    "recipe_id": req.recipe_id,
                    "claim_source": FORGE_CRAFT_SOURCE, "claim_key": claim_key,
                    "rewards": existing2.get("rewards"),
                    "applied_at": existing2.get("applied_at").isoformat() if hasattr(existing2.get("applied_at"), "isoformat") else existing2.get("applied_at"),
                    "reward_live_general": False, "premium_grant_blocked": True,
                    "_slc_pack_105_forge_craft_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False, "server_id": sid,
            "recipe_id": req.recipe_id,
            "claim_source": FORGE_CRAFT_SOURCE, "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "reward_live_general": False, "premium_grant_blocked": True,
            "_slc_pack_105_forge_craft_strict": True,
        }

    # ---------------- Equipment Fusion Strict (Pack 105) ----------------

    @router.post("/economy/strict/equipment/fusion")
    async def equipment_fusion_strict(
        req: EquipmentFusionRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _gate_triple(lambda: (_equipment_fusion_on() or (_ for _ in ()).throw(
            HTTPException(503, detail={
                "blocker": "EQUIPMENT_FUSION_STRICT_DISABLED",
                "kill_switch_env": EQUIPMENT_FUSION_KILL_SWITCH_ENV,
            })
        )))
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_105_test_user(db, uid)
        psp = await _require_psp(db, uid, sid)
        base = await db.user_equipment.find_one({
            "id": req.base_equipment_id, "user_id": uid, "server_id": sid,
        })
        if not base:
            raise HTTPException(404, detail={
                "blocker": "EQUIPMENT_NOT_OWNED_ON_SERVER",
                "equipment_id": req.base_equipment_id, "server_id": sid,
            })
        base_rarity = int(base.get("rarity", 1))
        if base_rarity >= MAX_EQUIPMENT_RARITY_STRICT:
            raise HTTPException(409, detail={
                "blocker": "EQUIPMENT_MAX_RARITY_REACHED",
                "current_rarity": base_rarity,
                "max_rarity": MAX_EQUIPMENT_RARITY_STRICT,
            })
        target_rarity = base_rarity + 1
        fusion_req = _forge_get_fusion_req(target_rarity)
        if not fusion_req:
            raise HTTPException(500, detail={"blocker": "FUSION_REQUIREMENT_LOOKUP_FAILED"})
        required_fodder_count = fusion_req["fodder_count"]
        if len(req.fodder_equipment_ids) != required_fodder_count:
            raise HTTPException(400, detail={
                "blocker": "FUSION_FODDER_COUNT_MISMATCH",
                "required": required_fodder_count,
                "provided": len(req.fodder_equipment_ids),
            })
        # Validate all fodders are server-scoped to (user_id, server_id), same slot, rarity == base_rarity.
        # base cannot be in fodder list.
        if req.base_equipment_id in req.fodder_equipment_ids:
            raise HTTPException(400, detail={"blocker": "BASE_EQUIPMENT_CANNOT_BE_FODDER"})
        # Idempotency PRE-check (precedes destructive ownership check).
        claim_key = f"equipment_fusion_{sid}_{req.base_equipment_id}_{req.idempotency_token}"
        server_idem_token = hashlib.sha1(claim_key.encode()).hexdigest()
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_FUSION_SOURCE,
            "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                existing["applied_at"] = applied_at.isoformat()
            return {
                "idempotent_replay": True, "server_id": sid,
                "base_equipment_id": req.base_equipment_id,
                "claim_source": EQUIPMENT_FUSION_SOURCE, "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at"),
                "reward_live_general": False, "premium_grant_blocked": True,
                "_slc_pack_105_equipment_fusion_idempotent": True,
            }
        base_slot = base.get("slot")
        fodder_docs = []
        for fid in req.fodder_equipment_ids:
            f = await db.user_equipment.find_one({"id": fid, "user_id": uid, "server_id": sid})
            if not f:
                raise HTTPException(404, detail={
                    "blocker": "FODDER_NOT_OWNED_ON_SERVER",
                    "fodder_id": fid, "server_id": sid,
                })
            if f.get("slot") != base_slot:
                raise HTTPException(400, detail={
                    "blocker": "FODDER_SLOT_MISMATCH",
                    "fodder_id": fid, "base_slot": base_slot, "fodder_slot": f.get("slot"),
                })
            if int(f.get("rarity", 0)) != base_rarity:
                raise HTTPException(400, detail={
                    "blocker": "FODDER_RARITY_MISMATCH",
                    "fodder_id": fid, "required_rarity": base_rarity, "fodder_rarity": f.get("rarity"),
                })
            fodder_docs.append(f)
        # Cost check.
        soft = (psp.get("soft_currencies") or {})
        for k, amt in fusion_req["cost_soft"].items():
            if int(soft.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_SOFT_CURRENCY",
                    "key": k, "required": int(amt), "available": int(soft.get(k, 0)),
                })
        mat = (psp.get("materials") or {})
        for k, amt in fusion_req["cost_materials"].items():
            if int(mat.get(k, 0)) < int(amt):
                raise HTTPException(402, detail={
                    "blocker": "INSUFFICIENT_MATERIAL",
                    "key": k, "required": int(amt), "available": int(mat.get(k, 0)),
                })
        # Spend.
        spend_inc: Dict[str, int] = {}
        for k, amt in fusion_req["cost_soft"].items():
            spend_inc[f"soft_currencies.{k}"] = -int(amt)
        for k, amt in fusion_req["cost_materials"].items():
            spend_inc[f"materials.{k}"] = -int(amt)
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": spend_inc}, upsert=False,
        )
        # Delete fodder server-scoped.
        for fid in req.fodder_equipment_ids:
            await db.user_equipment.delete_one({"id": fid, "user_id": uid, "server_id": sid})
        # Apply rarity +1 + stat boost % on base equipment.
        base_stats = base.get("base_stats") or base.get("stats") or {}
        boost = 1 + (fusion_req["stat_boost_pct"] / 100.0)
        new_base_stats: Dict[str, Any] = {}
        for k, v in base_stats.items():
            if isinstance(v, int):
                new_base_stats[k] = int(v * boost)
            elif isinstance(v, float):
                new_base_stats[k] = round(v * boost, 3)
            else:
                new_base_stats[k] = v
        # Apply level multiplier on top.
        level = int(base.get("level", 1))
        lvl_mult = 1 + (level - 1) * UPGRADE_STAT_BOOST_PER_LEVEL
        new_stats: Dict[str, Any] = {}
        for k, v in new_base_stats.items():
            if isinstance(v, int):
                new_stats[k] = int(v * lvl_mult)
            elif isinstance(v, float):
                new_stats[k] = round(v * lvl_mult, 3)
            else:
                new_stats[k] = v
        await db.user_equipment.update_one(
            {"id": req.base_equipment_id, "user_id": uid, "server_id": sid},
            {"$set": {
                "rarity": target_rarity,
                "base_stats": new_base_stats,
                "stats": new_stats,
                "_slc_pack_105_equipment_fusion_strict": True,
            }},
        )
        now = datetime.utcnow()
        ledger_row = {
            "user_id": uid, "server_id": sid,
            "claim_source": EQUIPMENT_FUSION_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(req.idempotency_token.encode()).hexdigest(),
            "base_equipment_id": req.base_equipment_id,
            "fodder_equipment_ids": req.fodder_equipment_ids,
            "rewards": {
                "server_scoped_cost": fusion_req,
                "new_rarity": target_rarity,
                "new_base_stats": new_base_stats,
                "new_stats": new_stats,
                "consumed_fodder_ids": req.fodder_equipment_ids,
            },
            "applied_at": now, "created_at": now,
            "_slc_pack_105_equipment_fusion_strict": True,
            "_slc_pack_105_server_side_fusion_catalog": True,
            "_slc_pack_105_no_cross_server_fusion": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False, "server_id": sid,
            "base_equipment_id": req.base_equipment_id,
            "claim_source": EQUIPMENT_FUSION_SOURCE, "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "reward_live_general": False, "premium_grant_blocked": True,
            "_slc_pack_105_equipment_fusion_strict": True,
        }

    # ---------------- Forge Catalog (Pack 105) ----------------

    @router.get("/economy/strict/forge/catalog")
    async def forge_strict_catalog():
        """Catalog pubblico Pack 105 — read-only, identico cross-server."""
        return {
            "catalog_version": FORGE_CATALOG_VERSION,
            "recipes": _forge_list_recipes(),
            "allowed_materials": sorted(ALLOWED_MATERIALS),
            "max_equipment_level_strict": MAX_EQUIPMENT_LEVEL_STRICT,
            "max_equipment_rarity_strict": MAX_EQUIPMENT_RARITY_STRICT,
            "upgrade_stat_boost_per_level": UPGRADE_STAT_BOOST_PER_LEVEL,
            "content_identical_across_servers": True,
            "reward_live_general": False,
            "release_readiness_claimed": False,
            "_slc_pack_105_forge_catalog": True,
        }
