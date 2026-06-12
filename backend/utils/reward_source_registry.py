"""Pack 96 — Reward Source Registry (allowlist).

Centralizza la definizione delle source di reward claim attive in Pack 96.

Regole:
  - Ogni source DEVE essere allowlisted qui per essere accettata dall'endpoint
    `POST /api/rewards/claim`. Qualunque source non registrata viene rifiutata
    con il blocker `REWARD_SOURCE_NOT_ALLOWLISTED`.
  - Source `server_scoped=True` richiedono server_id + PSP.
  - `reward_types` definisce quali chiavi sono ammesse nel payload (whitelist).
  - `grant_fn` e' applicata SOLO se il source e' `live=True` e l'eseguito non e'
    un replay del ledger.
  - Premium / hard currency (`gems`) e' BANNATA in Pack 96 per qualunque source.
"""
from typing import Any, Dict, List, Optional

# Pack 96 forbidden reward types (premium / hard / cross-system)
FORBIDDEN_REWARD_TYPES = {
    "gems",                # premium currency
    "premium_pull",        # gacha
    "standard_pull",       # gacha
    "stamina",             # not server-scoped soft currency
    "experience",          # account-wide hero exp
}

# Allowlist of soft currencies (PSP.soft_currencies) for Pack 96 controlled sources
ALLOWED_SOFT_CURRENCIES = {
    "gold", "honor", "guild_points", "mission_coins",
    "dimension_frags", "prana", "soul_seals", "star_dust",
}


def _grant_soft_currency_to_psp(db, user_id: str, server_id: str,
                                payload: Dict[str, Any]) -> Dict[str, Any]:
    """Grant function: scrive SOLO `player_server_profiles.soft_currencies.*`.

    Ritorna l'oggetto granted per audit nel ledger.
    """
    inc: Dict[str, int] = {}
    for k, v in (payload or {}).items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        try:
            amount = int(v)
        except Exception:
            raise _RewardTypeNotAllowed(f"{k}:invalid_amount")
        if amount <= 0 or amount > 10000:
            # Pack 96: cap soft currency grant per call to a sane test bound.
            raise _RewardTypeNotAllowed(f"{k}:amount_out_of_bounds")
        inc[f"soft_currencies.{k}"] = amount
    return inc


def _grant_daily_quest_to_psp(db, user_id: str, server_id: str,
                              payload: Dict[str, Any]) -> Dict[str, Any]:
    """Grant per `daily_quest_completion_claim`. Reward fisso server-side.

    Pack 98: payload client viene IGNORATO. Reward: `{mission_coins: 15, honor: 8}`.
    Soft currency server-bound. NESSUN premium.
    """
    fixed_reward = {"mission_coins": 15, "honor": 8}
    inc: Dict[str, int] = {}
    for k, amount in fixed_reward.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        if amount <= 0 or amount > 100:
            raise _RewardTypeNotAllowed(f"{k}:daily_quest_amount_cap")
        inc[f"soft_currencies.{k}"] = amount
    return inc


def _grant_daily_login_to_psp(db, user_id: str, server_id: str,
                              payload: Dict[str, Any]) -> Dict[str, Any]:
    """Grant per `daily_login_claim`. Reward fisso piccolo, hard-coded server-side.

    Pack 97: payload viene IGNORATO e sostituito col reward definito qui
    (`mission_coins: 10, honor: 5`). Garantisce che nessun client possa influenzare
    il valore granted. Reward types interamente server-bound soft currency.
    """
    fixed_reward = {"mission_coins": 10, "honor": 5}
    inc: Dict[str, int] = {}
    for k, amount in fixed_reward.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        if amount <= 0 or amount > 100:
            raise _RewardTypeNotAllowed(f"{k}:daily_amount_cap")
        inc[f"soft_currencies.{k}"] = amount
    return inc


def _grant_noop(_db, _user_id: str, _server_id: str, _payload: Dict[str, Any]):
    """No-op grant: usato per source `story_progress_marker_claim`."""
    return {}


class _PremiumGrantBlocked(Exception):
    def __init__(self, reward_key: str):
        super().__init__(f"PREMIUM_GRANT_BLOCKED:{reward_key}")
        self.reward_key = reward_key


class _RewardTypeNotAllowed(Exception):
    def __init__(self, reward_key: str):
        super().__init__(f"REWARD_TYPE_NOT_ALLOWED:{reward_key}")
        self.reward_key = reward_key


def _grant_tower_floor_to_psp(db, user_id: str, server_id: str,
                              payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 103 — Grant per `tower_floor_completion_claim`.

    Reward FISSO server-side per band di floor. Payload client IGNORATO.
    Solo soft_currencies PSP-scoped (mission_coins, honor). NO premium.
    """
    floor = int((payload or {}).get("_server_resolved_floor", 0))
    if floor < 1 or floor > 100:
        raise _RewardTypeNotAllowed(f"tower_floor_out_of_band:{floor}")
    if floor == 100:
        fixed_reward = {"mission_coins": 100, "honor": 50}
    elif floor == 50:
        fixed_reward = {"mission_coins": 50, "honor": 25}
    elif floor >= 51:
        fixed_reward = {"mission_coins": 18, "honor": 9}
    elif floor >= 10:
        fixed_reward = {"mission_coins": 12, "honor": 6}
    else:
        fixed_reward = {"mission_coins": 5, "honor": 3}
    inc: Dict[str, int] = {}
    for k, amount in fixed_reward.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        if amount <= 0 or amount > 200:
            raise _RewardTypeNotAllowed(f"{k}:tower_floor_amount_cap")
        inc[f"soft_currencies.{k}"] = amount
    return inc



def _grant_shop_buy_strict_to_psp(db, user_id: str, server_id: str,
                                   payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 104 — Grant per `shop_buy_strict_claim`.

    Reward FISSO server-side basato sul catalog `shop_strict_catalog_v1` lookup
    (catalog_item.grant). Payload client IGNORATO (solo `_server_resolved_grant`
    e' accettato — viene scritto dal route dopo lookup catalog server-side).

    Solo PSP soft_currencies. NO premium. NO hard. NO inventory grant in Pack 104.
    """
    fixed_grant = (payload or {}).get("_server_resolved_grant") or {}
    if not isinstance(fixed_grant, dict) or not fixed_grant:
        raise _RewardTypeNotAllowed("shop_buy_grant_missing_server_resolved")
    inc: Dict[str, int] = {}
    for k, amount in fixed_grant.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        try:
            amt = int(amount)
        except Exception:
            raise _RewardTypeNotAllowed(f"{k}:invalid_amount")
        # Cap conservativo per shop buy strict Pack 104.
        if amt <= 0 or amt > 1000:
            raise _RewardTypeNotAllowed(f"{k}:shop_buy_amount_cap")
        inc[f"soft_currencies.{k}"] = amt
    return inc


def _grant_soul_forge_retire_strict_to_psp(db, user_id: str, server_id: str,
                                            payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 104 — Grant per `soul_forge_retire_strict_claim`.

    Reward FISSO server-side per band di stelle. Payload client IGNORATO eccetto
    `_server_resolved_stars` (calcolato dal route dopo lookup user_heroes server-scoped).

    Solo PSP soft_currencies. NO prana/soul_seals/star_dust legacy wallet (account-wide).
    Solo `mission_coins` + `honor` (PSP-scoped).
    """
    stars = int((payload or {}).get("_server_resolved_stars", 0))
    if stars < 1 or stars > 15:
        raise _RewardTypeNotAllowed(f"soul_forge_stars_out_of_band:{stars}")
    # Band: 1-2 stars: 5/3; 3-4: 10/5; 5: 20/10; 6+: 40/20.
    if stars >= 6:
        fixed_reward = {"mission_coins": 40, "honor": 20}
    elif stars == 5:
        fixed_reward = {"mission_coins": 20, "honor": 10}
    elif stars >= 3:
        fixed_reward = {"mission_coins": 10, "honor": 5}
    else:
        fixed_reward = {"mission_coins": 5, "honor": 3}
    inc: Dict[str, int] = {}
    for k, amount in fixed_reward.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        if amount <= 0 or amount > 100:
            raise _RewardTypeNotAllowed(f"{k}:soul_forge_amount_cap")
        inc[f"soft_currencies.{k}"] = amount
    return inc


def _grant_equipment_strict_noop(_db, _user_id: str, _server_id: str,
                                  _payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 104 — equipment_equip/unequip_strict_claim NON dà reward.

    Solo audit row ledger (mutation pura di stato `equipped_to`). Ritorna dict vuoto.
    Nessun $inc su PSP. Nessuna mutation users.*.
    """
    return {}


def _grant_forge_strict_pack_105(_db, _user_id: str, _server_id: str,
                                  _payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 105 — Grant fn placeholder per upgrade/forge/fusion strict.

    Le mutazioni effettive (PSP.materials, PSP.soft_currencies, user_equipment)
    avvengono direttamente nell'handler per atomicita`. Questo grant_fn ritorna
    sempre dict vuoto: la sua presenza serve solo per soddisfare il registry
    contract (`grant_fn_name`). Eventuali grant currency vengono validati
    server-side dall'handler stesso (cap, whitelist, no premium).

    Ritorna dict vuoto. Audit ledger row contiene il dettaglio reale.
    """
    return {}


def _grant_controlled_reward_pack_106(_db, _user_id: str, _server_id: str,
                                       payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pack 106 — Grant fn per mail/achievement/daily_weekly controlled.

    Payload deve includere `_server_resolved_reward` (dict con `soft_currencies` e
    `materials`), settato dall'handler dopo lookup catalog server-side. Payload
    client IGNORATO.

    Ritorna `$inc` dict per PSP.soft_currencies.<k> + PSP.materials.<k>.
    """
    fixed = (payload or {}).get("_server_resolved_reward") or {}
    if not isinstance(fixed, dict):
        raise _RewardTypeNotAllowed("server_resolved_reward_missing")
    inc: Dict[str, int] = {}
    soft = fixed.get("soft_currencies") or {}
    mats = fixed.get("materials") or {}
    for k, amount in soft.items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(f"soft:{k}")
        try:
            amt = int(amount)
        except Exception:
            raise _RewardTypeNotAllowed(f"{k}:invalid_amount")
        if amt <= 0 or amt > 500:
            raise _RewardTypeNotAllowed(f"{k}:pack_106_amount_cap")
        inc[f"soft_currencies.{k}"] = amt
    # Whitelist materials Pack 106 (5 items)
    ALLOWED_MAT = {"steel_ore", "magic_dust", "ancient_relic", "phoenix_feather", "crystal_shard"}
    for k, amount in mats.items():
        if k not in ALLOWED_MAT:
            raise _RewardTypeNotAllowed(f"material:{k}")
        try:
            amt = int(amount)
        except Exception:
            raise _RewardTypeNotAllowed(f"{k}:invalid_amount")
        if amt <= 0 or amt > 50:
            raise _RewardTypeNotAllowed(f"{k}:pack_106_material_cap")
        inc[f"materials.{k}"] = amt
    return inc


REWARD_SOURCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "qa_controlled_soft_currency_claim": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_soft_currency_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_96",
        "description": "Test/QA controlled soft currency claim. Server-scoped, non-premium. Payload e' un dict di soft currency increments capped a 10000 per chiave.",
    },
    "story_progress_marker_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_noop",
        "idempotency": "mandatory",
        "pack_origin": "pack_96",
        "description": "Marker-only claim per story progress milestones. NESSUN reward grant, scrive solo ledger row + opzionalmente PSP.story_progress (futuro pack).",
    },
    "daily_login_claim": {
        "server_scoped": True,
        "reward_types": ["mission_coins", "honor"],
        "live": True,
        "grant_fn_name": "grant_daily_login_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_97",
        "per_source_kill_switch_env": "DAILY_LOGIN_CLAIM_ENABLED",
        "per_source_kill_switch_default": False,
        "fixed_reward": {"mission_coins": 10, "honor": 5},
        "amount_cap_per_key": 100,
        "daily_idempotency_strategy": "server_side_claim_key_daily_login_<server_id>_<YYYY-MM-DD UTC>",
        "description": "Pack 97 first real player-facing claim source. Daily login reward server-scoped, soft currency only. Server-side claim_key deterministic. Per-source kill switch default OFF.",
    },
    "daily_quest_completion_claim": {
        "server_scoped": True,
        "reward_types": ["mission_coins", "honor"],
        "live": True,
        "grant_fn_name": "grant_daily_quest_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_98",
        "per_source_kill_switch_env": "DAILY_QUEST_CLAIM_ENABLED",
        "per_source_kill_switch_default": False,
        "fixed_reward": {"mission_coins": 15, "honor": 8},
        "amount_cap_per_key": 100,
        "quest_id_whitelist": ["daily_quest_1", "daily_quest_2", "daily_quest_3"],
        "completion_proof_required": True,
        "completion_proof_test_only_via_marker": "pack_98_test_artifact",
        "daily_idempotency_strategy": "server_side_claim_key_daily_quest_<server_id>_<quest_id>_<YYYY-MM-DD UTC>",
        "ready_status": "READY_GATED_COMPLETION_REQUIRED",
        "description": "Pack 98 second real player-facing claim source. Daily quest completion. Server-side claim_key + completion proof required (test-only via marker until real quest runtime exists).",
    },
    "tower_floor_completion_claim": {
        "server_scoped": True,
        "reward_types": ["mission_coins", "honor"],
        "live": True,
        "grant_fn_name": "grant_tower_floor_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_103",
        "per_source_kill_switch_env": "TOWER_FLOOR_CLAIM_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 200,
        "floor_band_rewards": {
            "1-9": {"mission_coins": 5, "honor": 3},
            "10-49": {"mission_coins": 12, "honor": 6},
            "50": {"mission_coins": 50, "honor": 25},
            "51-99": {"mission_coins": 18, "honor": 9},
            "100": {"mission_coins": 100, "honor": 50},
        },
        "execution_proof_required": True,
        "claim_key_strategy": "server_side_claim_key_tower_floor_<server_id>_<floor>",
        "ready_status": "READY_GATED_EXECUTION_REQUIRED",
        "description": "Pack 103 third real player-facing claim source. Tower floor completion. Server-side claim_key + execution proof via PSP.tower_progress advance. Per-source kill switch default OFF. Reward fisso server-side per floor band, solo PSP soft currencies.",
    },
    "shop_buy_strict_claim": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_shop_buy_strict_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_104",
        "per_source_kill_switch_env": "SHOP_BUY_STRICT_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 1000,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "claim_key_strategy": "server_side_claim_key_shop_buy_<server_id>_<shop_id>_<item_id>_<purchase_key>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 104 shop buy strict claim. Server-side catalog/price/grant. Payload client IGNORATO. Solo soft currencies PSP-scoped. NO premium. NO IAP. NO gacha.",
    },
    "soul_forge_retire_strict_claim": {
        "server_scoped": True,
        "reward_types": ["mission_coins", "honor"],
        "live": True,
        "grant_fn_name": "grant_soul_forge_retire_strict_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_104",
        "per_source_kill_switch_env": "SOUL_FORGE_RETIRE_STRICT_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 100,
        "stars_band_rewards": {
            "1-2": {"mission_coins": 5, "honor": 3},
            "3-4": {"mission_coins": 10, "honor": 5},
            "5": {"mission_coins": 20, "honor": 10},
            "6-15": {"mission_coins": 40, "honor": 20},
        },
        "claim_key_strategy": "server_side_claim_key_soul_forge_retire_<server_id>_<hero_instance_id>",
        "client_payload_ignored": True,
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 104 soul forge retire strict claim. Cross-server retire vietato. Reward fisso server-side per band stelle, solo PSP soft currencies. NO premium. NO wallet legacy account-wide grants.",
    },
    "equipment_equip_strict_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_equipment_strict_noop",
        "idempotency": "mandatory",
        "pack_origin": "pack_104",
        "per_source_kill_switch_env": "EQUIPMENT_STRICT_WRITES_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 0,
        "client_payload_ignored": True,
        "claim_key_strategy": "server_side_claim_key_equipment_equip_<server_id>_<hero_instance_id>_<slot>_<purchase_key>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 104 equipment equip strict claim (no reward grant). Solo audit ledger row + mutation server-scoped di equipped_to. NO grant currency. NO premium. NO cross-server.",
    },
    "equipment_unequip_strict_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_equipment_strict_noop",
        "idempotency": "mandatory",
        "pack_origin": "pack_104",
        "per_source_kill_switch_env": "EQUIPMENT_STRICT_WRITES_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 0,
        "client_payload_ignored": True,
        "claim_key_strategy": "server_side_claim_key_equipment_unequip_<server_id>_<equipment_instance_id>_<purchase_key>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 104 equipment unequip strict claim (no reward grant). Solo audit ledger row + mutation server-scoped di $unset equipped_to. NO grant currency. NO premium. NO cross-server.",
    },
    "equipment_upgrade_strict_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_forge_strict_pack_105",
        "idempotency": "mandatory",
        "pack_origin": "pack_105",
        "per_source_kill_switch_env": "EQUIPMENT_UPGRADE_STRICT_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 0,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "claim_key_strategy": "server_side_claim_key_equipment_upgrade_<server_id>_<equipment_instance_id>_<target_level>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 105 equipment upgrade strict claim. Consume PSP materials + soft_currencies server-side. Stat boost +5% per livello. Max level 30. Ledger idempotent. No premium. No users.* mutation.",
    },
    "forge_craft_strict_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_forge_strict_pack_105",
        "idempotency": "mandatory",
        "pack_origin": "pack_105",
        "per_source_kill_switch_env": "FORGE_CRAFT_STRICT_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 0,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "claim_key_strategy": "server_side_claim_key_forge_craft_<server_id>_<recipe_id>_<idempotency_token>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 105 forge craft strict claim. Consume PSP materials + soft + grant nuovo user_equipment server-scoped da template fisso. Ledger idempotent. No premium. No users.* mutation.",
    },
    "equipment_fusion_strict_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_forge_strict_pack_105",
        "idempotency": "mandatory",
        "pack_origin": "pack_105",
        "per_source_kill_switch_env": "EQUIPMENT_FUSION_STRICT_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 0,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "claim_key_strategy": "server_side_claim_key_equipment_fusion_<server_id>_<base_equipment_id>_<idempotency_token>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 105 equipment fusion strict claim. Consume fodder server-scoped (stesso slot, rarity-1) + PSP materials + soft. Rarity +1 + stat boost. Ledger idempotent. No cross-server consume. No premium.",
    },
    "mail_claim_controlled": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_controlled_reward_pack_106",
        "idempotency": "mandatory",
        "pack_origin": "pack_106",
        "per_source_kill_switch_env": "MAIL_CLAIM_CONTROLLED_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 500,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "claim_key_strategy": "server_side_claim_key_mail_<server_id>_<mail_id>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 106 mail controlled claim. Server-side catalog reward. PSP soft+materials only. No premium. No cross-server. Ledger idempotent.",
    },
    "achievement_claim_controlled": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_controlled_reward_pack_106",
        "idempotency": "mandatory",
        "pack_origin": "pack_106",
        "per_source_kill_switch_env": "ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 500,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "completion_proof_required": True,
        "claim_key_strategy": "server_side_claim_key_achievement_<server_id>_<achievement_id>",
        "ready_status": "READY_GATED_COMPLETION_REQUIRED",
        "description": "Pack 106 achievement controlled claim. Server-side catalog reward. Completion proof required (test-only marker). One claim per user/server/achievement_id. PSP soft+materials only.",
    },
    "daily_weekly_reward_claim": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_controlled_reward_pack_106",
        "idempotency": "mandatory",
        "pack_origin": "pack_106",
        "per_source_kill_switch_env": "DAILY_WEEKLY_REWARD_CLAIM_ENABLED",
        "per_source_kill_switch_default": False,
        "amount_cap_per_key": 500,
        "client_payload_ignored": True,
        "server_side_catalog_required": True,
        "period_keying": "UTC_day_or_iso_week",
        "claim_key_strategy": "server_side_claim_key_dwr_<server_id>_<task_id>_<period_key>",
        "ready_status": "READY_GATED_RUNTIME_REQUIRED",
        "description": "Pack 106 daily/weekly reward claim. Server-side task catalog. Daily=UTC day, Weekly=UTC ISO week. One claim per user/server/task/period. PSP soft+materials only.",
    },
}


_GRANT_FN_MAP = {
    "grant_soft_currency_to_psp": _grant_soft_currency_to_psp,
    "grant_noop": _grant_noop,
    "grant_daily_login_to_psp": _grant_daily_login_to_psp,
    "grant_daily_quest_to_psp": _grant_daily_quest_to_psp,
    "grant_tower_floor_to_psp": _grant_tower_floor_to_psp,
    "grant_shop_buy_strict_to_psp": _grant_shop_buy_strict_to_psp,
    "grant_soul_forge_retire_strict_to_psp": _grant_soul_forge_retire_strict_to_psp,
    "grant_equipment_strict_noop": _grant_equipment_strict_noop,
    "grant_forge_strict_pack_105": _grant_forge_strict_pack_105,
    "grant_controlled_reward_pack_106": _grant_controlled_reward_pack_106,
}


def lookup_source(source_id: str) -> Optional[Dict[str, Any]]:
    return REWARD_SOURCE_REGISTRY.get(source_id)


def is_source_live(source_id: str) -> bool:
    src = REWARD_SOURCE_REGISTRY.get(source_id)
    return bool(src and src.get("live"))


def get_grant_fn(source_id: str):
    src = REWARD_SOURCE_REGISTRY.get(source_id) or {}
    return _GRANT_FN_MAP.get(src.get("grant_fn_name") or "")


def list_allowlisted_sources() -> List[str]:
    return [k for k, v in REWARD_SOURCE_REGISTRY.items() if v.get("live")]


__all__ = [
    "REWARD_SOURCE_REGISTRY", "FORBIDDEN_REWARD_TYPES", "ALLOWED_SOFT_CURRENCIES",
    "lookup_source", "is_source_live", "get_grant_fn", "list_allowlisted_sources",
    "_PremiumGrantBlocked", "_RewardTypeNotAllowed",
]
