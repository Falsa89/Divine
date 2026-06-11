"""Pack 105 — Forge Strict Catalog v1 (server-side, deterministico).

Tre cataloghi:
  1. UPGRADE_COST_CATALOG_V1 — cost per livello equipment upgrade.
  2. FORGE_RECIPE_CATALOG_V1 — recipe forge craft (cost + grant).
  3. FUSION_REQUIREMENT_CATALOG_V1 — requisiti per rarity fusion (numero fodder, stat boost).

Tutte le `cost` keys sono server-side. Client cost/recipe payload IGNORATO.

Regole rigide:
  * Cost/grant soft_currencies ∈ ALLOWED_SOFT_CURRENCIES (no gems, no premium).
  * Cost materials: id ∈ ALLOWED_MATERIALS.
  * Grant equipment: solo rarity/slot/stats fissi server-side da template.
  * Max equipment level = 30 (cap conservativo Pack 105).
  * Max equipment rarity = 6.
"""
from typing import Any, Dict, List, Optional

CATALOG_VERSION = "forge_strict_catalog_v1.0.0-pack_105"

# Whitelist materiali server-scoped Pack 105.
# Stored in PSP.materials.{material_id} = int.
ALLOWED_MATERIALS = {
    "steel_ore",
    "magic_dust",
    "ancient_relic",
    "phoenix_feather",
    "crystal_shard",
}

# UPGRADE COST per livello target. Cap a 30.
UPGRADE_COST_CATALOG_V1: Dict[int, Dict[str, Dict[str, int]]] = {
    # target_level: {soft_currencies: {...}, materials: {...}}
    # Tier 1: lvl 1-9
    2:  {"soft_currencies": {"mission_coins": 5},   "materials": {"steel_ore": 2}},
    3:  {"soft_currencies": {"mission_coins": 8},   "materials": {"steel_ore": 3}},
    4:  {"soft_currencies": {"mission_coins": 12},  "materials": {"steel_ore": 4}},
    5:  {"soft_currencies": {"mission_coins": 18},  "materials": {"steel_ore": 5, "magic_dust": 1}},
    6:  {"soft_currencies": {"mission_coins": 25},  "materials": {"steel_ore": 7, "magic_dust": 2}},
    7:  {"soft_currencies": {"mission_coins": 35},  "materials": {"steel_ore": 9, "magic_dust": 3}},
    8:  {"soft_currencies": {"mission_coins": 50},  "materials": {"steel_ore": 12, "magic_dust": 4}},
    9:  {"soft_currencies": {"mission_coins": 70},  "materials": {"steel_ore": 15, "magic_dust": 6}},
    10: {"soft_currencies": {"mission_coins": 100, "honor": 25}, "materials": {"steel_ore": 20, "magic_dust": 8, "crystal_shard": 1}},
    # Tier 2: lvl 11-20 — qualunque target lvl > 10 usa la tier 10 cost (lookup get).
    # Per semplicita' Pack 105 esponiamo solo 1-10 esplicito. Lvl > 10 → cost = lvl 10 * 1.5 (calcolata).
}

# Forge craft recipes. Ogni recipe consuma materiali + soft currency e produce
# un nuovo user_equipment server-scoped da template fisso server-side.
FORGE_RECIPE_CATALOG_V1: Dict[str, Dict[str, Any]] = {
    "iron_sword_recipe": {
        "recipe_id": "iron_sword_recipe",
        "name": "Forgia Spada di Ferro",
        "cost": {
            "soft_currencies": {"mission_coins": 30},
            "materials": {"steel_ore": 5},
        },
        "grant_equipment_template": {
            "name": "Spada di Ferro Forgiata",
            "slot": "weapon",
            "rarity": 2,
            "level": 1,
            "stats": {"attack": 25, "defense": 5},
        },
    },
    "steel_armor_recipe": {
        "recipe_id": "steel_armor_recipe",
        "name": "Forgia Armatura d'Acciaio",
        "cost": {
            "soft_currencies": {"mission_coins": 40, "honor": 10},
            "materials": {"steel_ore": 8, "magic_dust": 2},
        },
        "grant_equipment_template": {
            "name": "Armatura d'Acciaio Forgiata",
            "slot": "armor",
            "rarity": 3,
            "level": 1,
            "stats": {"defense": 40, "hp": 100},
        },
    },
    "magic_amulet_recipe": {
        "recipe_id": "magic_amulet_recipe",
        "name": "Amuleto Mistico",
        "cost": {
            "soft_currencies": {"honor": 30},
            "materials": {"magic_dust": 5, "crystal_shard": 2},
        },
        "grant_equipment_template": {
            "name": "Amuleto Mistico",
            "slot": "accessory",
            "rarity": 3,
            "level": 1,
            "stats": {"magic": 30, "hp": 50},
        },
    },
}

# Fusion: per ogni rarity target richiede N fodder dello stesso slot e rarity-1.
FUSION_REQUIREMENT_CATALOG_V1: Dict[int, Dict[str, Any]] = {
    2: {"fodder_count": 2, "stat_boost_pct": 20, "cost_soft": {"mission_coins": 20}, "cost_materials": {"magic_dust": 1}},
    3: {"fodder_count": 2, "stat_boost_pct": 20, "cost_soft": {"mission_coins": 50},  "cost_materials": {"magic_dust": 2, "crystal_shard": 1}},
    4: {"fodder_count": 3, "stat_boost_pct": 25, "cost_soft": {"mission_coins": 100, "honor": 30}, "cost_materials": {"magic_dust": 4, "crystal_shard": 2}},
    5: {"fodder_count": 3, "stat_boost_pct": 30, "cost_soft": {"mission_coins": 200, "honor": 80}, "cost_materials": {"crystal_shard": 5, "ancient_relic": 1}},
    6: {"fodder_count": 4, "stat_boost_pct": 35, "cost_soft": {"mission_coins": 500, "honor": 200}, "cost_materials": {"ancient_relic": 3, "phoenix_feather": 1}},
}

MAX_EQUIPMENT_LEVEL_STRICT = 30
MAX_EQUIPMENT_RARITY_STRICT = 6
UPGRADE_STAT_BOOST_PER_LEVEL = 0.05  # +5% per livello


def get_upgrade_cost(target_level: int) -> Optional[Dict[str, Dict[str, int]]]:
    """Cost per upgrade al `target_level`. Lvl > 10: cost = lvl 10 * 1.5 (round)."""
    if target_level < 2 or target_level > MAX_EQUIPMENT_LEVEL_STRICT:
        return None
    if target_level in UPGRADE_COST_CATALOG_V1:
        # Deep copy
        c = UPGRADE_COST_CATALOG_V1[target_level]
        return {
            "soft_currencies": dict(c["soft_currencies"]),
            "materials": dict(c["materials"]),
        }
    # Tier 11-30: lvl 10 * 1.5
    base = UPGRADE_COST_CATALOG_V1[10]
    multiplier = 1.5 + (target_level - 11) * 0.1  # cresce di 0.1 per livello
    return {
        "soft_currencies": {k: int(round(v * multiplier)) for k, v in base["soft_currencies"].items()},
        "materials": {k: int(round(v * multiplier)) for k, v in base["materials"].items()},
    }


def get_recipe(recipe_id: str) -> Optional[Dict[str, Any]]:
    r = FORGE_RECIPE_CATALOG_V1.get(recipe_id)
    if not r:
        return None
    # Deep copy
    return {
        "recipe_id": r["recipe_id"],
        "name": r["name"],
        "cost": {
            "soft_currencies": dict(r["cost"]["soft_currencies"]),
            "materials": dict(r["cost"]["materials"]),
        },
        "grant_equipment_template": dict(r["grant_equipment_template"]),
    }


def list_recipes_summary() -> List[Dict[str, Any]]:
    return [get_recipe(rid) for rid in FORGE_RECIPE_CATALOG_V1.keys()]


def get_fusion_requirement(target_rarity: int) -> Optional[Dict[str, Any]]:
    if target_rarity < 2 or target_rarity > MAX_EQUIPMENT_RARITY_STRICT:
        return None
    req = FUSION_REQUIREMENT_CATALOG_V1.get(target_rarity)
    if not req:
        return None
    return {
        "fodder_count": req["fodder_count"],
        "stat_boost_pct": req["stat_boost_pct"],
        "cost_soft": dict(req["cost_soft"]),
        "cost_materials": dict(req["cost_materials"]),
    }


def _validate_catalog_on_import() -> None:
    _ALLOWED_SOFT = {
        "gold", "honor", "guild_points", "mission_coins",
        "dimension_frags", "prana", "soul_seals", "star_dust",
    }
    _FORBIDDEN = {"gems", "premium_pull", "standard_pull", "stamina", "experience"}

    # Upgrade catalog validation
    for lvl, c in UPGRADE_COST_CATALOG_V1.items():
        assert 2 <= lvl <= MAX_EQUIPMENT_LEVEL_STRICT
        for k, v in c["soft_currencies"].items():
            assert k in _ALLOWED_SOFT and k not in _FORBIDDEN, f"upgrade soft forbidden: {lvl}.{k}"
            assert isinstance(v, int) and 0 < v <= 10000
        for k, v in c["materials"].items():
            assert k in ALLOWED_MATERIALS, f"upgrade material forbidden: {lvl}.{k}"
            assert isinstance(v, int) and 0 < v <= 100

    # Recipe catalog validation
    for rid, r in FORGE_RECIPE_CATALOG_V1.items():
        assert rid == r["recipe_id"]
        for k, v in r["cost"]["soft_currencies"].items():
            assert k in _ALLOWED_SOFT and k not in _FORBIDDEN, f"recipe soft forbidden: {rid}.{k}"
        for k, v in r["cost"]["materials"].items():
            assert k in ALLOWED_MATERIALS, f"recipe material forbidden: {rid}.{k}"
        tpl = r["grant_equipment_template"]
        assert tpl["slot"] in {"weapon", "armor", "accessory", "helmet", "gloves", "boots"}
        assert 1 <= tpl["rarity"] <= MAX_EQUIPMENT_RARITY_STRICT
        assert tpl["level"] == 1

    # Fusion requirement validation
    for rar, req in FUSION_REQUIREMENT_CATALOG_V1.items():
        assert 2 <= rar <= MAX_EQUIPMENT_RARITY_STRICT
        assert req["fodder_count"] >= 1
        for k, v in req["cost_soft"].items():
            assert k in _ALLOWED_SOFT and k not in _FORBIDDEN, f"fusion soft forbidden: {rar}.{k}"
        for k, v in req["cost_materials"].items():
            assert k in ALLOWED_MATERIALS, f"fusion material forbidden: {rar}.{k}"


_validate_catalog_on_import()


__all__ = [
    "UPGRADE_COST_CATALOG_V1",
    "FORGE_RECIPE_CATALOG_V1",
    "FUSION_REQUIREMENT_CATALOG_V1",
    "CATALOG_VERSION",
    "ALLOWED_MATERIALS",
    "MAX_EQUIPMENT_LEVEL_STRICT",
    "MAX_EQUIPMENT_RARITY_STRICT",
    "UPGRADE_STAT_BOOST_PER_LEVEL",
    "get_upgrade_cost",
    "get_recipe",
    "list_recipes_summary",
    "get_fusion_requirement",
]
