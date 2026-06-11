"""Pack 104 — Shop Strict Catalog v1 (server-side, deterministico).

Catalog statico letto-solo per `/api/economy/strict/shop/buy`. Le entry
dichiarano `cost` (PSP soft currency consumata) e `grant` (PSP soft currency
ricevuta). NESSUNA entry può avere `cost` o `grant` su premium/hard currency.

Regole rigide:
  * Tutte le `cost` keys ∈ ALLOWED_SOFT_CURRENCIES.
  * Tutte le `grant` keys ∈ ALLOWED_SOFT_CURRENCIES.
  * `cost.amount` > 0 e ≤ 5000 (cap conservativo).
  * `grant.amount` > 0 e ≤ 1000 (cap conservativo).
  * Item id univoco. Shop id univoco. (shop_id, item_id) univoco.
  * Daily purchase limit ≥ 1 (per limitare abusi).

NON contiene:
  * Item premium (gems, premium_pull, ecc.) — vietati.
  * Item hero/equipment grant — Pack 104 non concede oggetti grant.
  * Pricing dinamico o client-controlled.
"""
from typing import Any, Dict, List, Optional

CATALOG_VERSION = "shop_strict_catalog_v1.0.0-pack_104"

# Lista deterministica di item shop server-side. Voci minime ma significative:
# 4 item che permettono scambio strict tra soft currencies PSP-scoped.
SHOP_STRICT_CATALOG_V1: Dict[str, Dict[str, Any]] = {
    "honor_exchange_shop": {
        "shop_id": "honor_exchange_shop",
        "name": "Mercato dell'Onore",
        "description": "Scambia Honor per altre soft currencies server-bound.",
        "items": [
            {
                "id": "honor_to_mission_coins_pack_small",
                "name": "Pacchetto Monete Missione (piccolo)",
                "cost": {"honor": 20},
                "grant": {"mission_coins": 30},
                "daily_purchase_limit": 5,
            },
            {
                "id": "honor_to_mission_coins_pack_large",
                "name": "Pacchetto Monete Missione (grande)",
                "cost": {"honor": 80},
                "grant": {"mission_coins": 150},
                "daily_purchase_limit": 2,
            },
        ],
    },
    "mission_coins_exchange_shop": {
        "shop_id": "mission_coins_exchange_shop",
        "name": "Bazar Mercenario",
        "description": "Scambia Monete Missione per Honor server-bound.",
        "items": [
            {
                "id": "mission_coins_to_honor_pack_small",
                "name": "Pacchetto Honor (piccolo)",
                "cost": {"mission_coins": 30},
                "grant": {"honor": 18},
                "daily_purchase_limit": 5,
            },
            {
                "id": "mission_coins_to_honor_pack_large",
                "name": "Pacchetto Honor (grande)",
                "cost": {"mission_coins": 120},
                "grant": {"honor": 80},
                "daily_purchase_limit": 2,
            },
        ],
    },
}


def get_shop(shop_id: str) -> Optional[Dict[str, Any]]:
    return SHOP_STRICT_CATALOG_V1.get(shop_id)


def get_item(shop_id: str, item_id: str) -> Optional[Dict[str, Any]]:
    shop = SHOP_STRICT_CATALOG_V1.get(shop_id)
    if not shop:
        return None
    for it in shop.get("items", []):
        if it.get("id") == item_id:
            # Restituisce una copia per safety (no mutation del catalog).
            return dict(it)
    return None


def list_shops_summary() -> List[Dict[str, Any]]:
    out = []
    for sid, shop in SHOP_STRICT_CATALOG_V1.items():
        out.append({
            "shop_id": sid,
            "name": shop["name"],
            "description": shop["description"],
            "items": [
                {
                    "id": it["id"],
                    "name": it["name"],
                    "cost": dict(it["cost"]),
                    "grant": dict(it["grant"]),
                    "daily_purchase_limit": it["daily_purchase_limit"],
                }
                for it in shop["items"]
            ],
        })
    return out


# Validation interna del catalog al load time. Aborta l'import se config invalida.
_ALLOWED = {
    "gold", "honor", "guild_points", "mission_coins",
    "dimension_frags", "prana", "soul_seals", "star_dust",
}
_FORBIDDEN = {"gems", "premium_pull", "standard_pull", "stamina", "experience"}


def _validate_catalog_on_import() -> None:
    seen_item_ids: set = set()
    for sid, shop in SHOP_STRICT_CATALOG_V1.items():
        assert sid == shop["shop_id"], f"shop_id mismatch: {sid}"
        for it in shop.get("items", []):
            iid = it["id"]
            assert iid not in seen_item_ids, f"duplicate item id: {iid}"
            seen_item_ids.add(iid)
            # cost validation
            for k, v in it["cost"].items():
                assert k in _ALLOWED and k not in _FORBIDDEN, f"forbidden cost key: {iid}.{k}"
                assert isinstance(v, int) and 0 < v <= 5000, f"cost out of range: {iid}.{k}={v}"
            # grant validation
            for k, v in it["grant"].items():
                assert k in _ALLOWED and k not in _FORBIDDEN, f"forbidden grant key: {iid}.{k}"
                assert isinstance(v, int) and 0 < v <= 1000, f"grant out of range: {iid}.{k}={v}"
            assert isinstance(it["daily_purchase_limit"], int) and it["daily_purchase_limit"] >= 1, \
                f"daily_purchase_limit invalid: {iid}"


_validate_catalog_on_import()


__all__ = [
    "SHOP_STRICT_CATALOG_V1", "CATALOG_VERSION",
    "get_shop", "get_item", "list_shops_summary",
]
