"""HOTFIX D — Starter Roster Contract centralizzato.

Modulo READ-ONLY che centralizza:

  1. la lista canonica dei tre starter (IDs immutabili);
  2. le proprietà attese (role, hero_class, rarity, element);
  3. i flag di catalog-eligibility che il backend `/api/psp/starter/claim`
     deve verificare prima di creare `user_heroes` starter;
  4. un fallback minimale di esposizione per `GET /api/user/heroes` quando
     il catalog `db.heroes` espone uno starter con `hero_class` mancante
     o non lo espone affatto (lo user_hero esiste ma il merge col catalog
     fallisce). Il fallback NON inventa lore/personaggi/rarità nuove: usa
     solo metadati derivati dai dati canonici già storicamente presenti
     in `STARTER_SET_PACK_87` (Pack 87, ratificati).

ZERO DB writes. ZERO chiamate runtime esterne. Pure data + helper di
lookup. Importato sia da `backend/server.py` (claim + exposure) sia dai
validator HOTFIX D.

Reference Pack 87:
  Authorization: AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87
  Tre starter canonici, low-rarity, non-premium, official, obtainable,
  show_in_catalog, non-deactivated, non-high-rarity (rarity <= 2).
"""

from __future__ import annotations

from typing import Optional, TypedDict


# ── Authorization string (Pack 87 ratificata) ──────────────────────────────
STARTER_ROSTER_CONTRACT_VERSION = "hotfix_d_starter_roster_contract_v1"
STARTER_ROSTER_AUTHORIZATION = "AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87"


class StarterRequiredFlags(TypedDict):
    """Flag richiesti sul documento `db.heroes.<hero_id>` perché lo starter
    sia eligibile al claim. Aderiscono al contratto refuse-by-default già
    presente in `backend/server.py` (Pack 87)."""
    is_official_required: bool
    obtainable_required: bool
    show_in_catalog_required: bool
    premium_forbidden: bool
    deactivated_forbidden: bool
    high_rarity_forbidden: bool
    high_rarity_threshold: int  # rarity > soglia ⇒ STARTER_ROSTER_HIGH_RARITY


# Flag richiesti dal contratto: identici alla logica server.py Pack 87.
STARTER_REQUIRED_FLAGS: StarterRequiredFlags = {
    "is_official_required": True,
    "obtainable_required": True,
    "show_in_catalog_required": True,
    "premium_forbidden": True,
    "deactivated_forbidden": True,
    "high_rarity_forbidden": True,
    "high_rarity_threshold": 2,
}


class StarterEntry(TypedDict):
    """Una entry del contratto starter — sufficiente sia per il claim
    server-side sia per il fallback di esposizione su `/api/user/heroes`."""
    starter_id: str
    expected_role: str          # "tank" | "dps" | "support"
    expected_hero_class: str    # "Tank" | "DPS" | "Support" — case PascalCase per coerenza UI
    expected_rarity: int        # 1 o 2 (low-rarity)
    expected_element: str       # "earth" | "wind" | "light" — derivato da Pack 87 catalog


# ── Lista canonica (immutabile) ────────────────────────────────────────────
# IDs e ruoli identici a `starter_set` storicamente presente in
# `backend/server.py` (linee 431-436 al baseline HOTFIX C `9593a7c5b`).
# Element / hero_class / rarity sono i valori canonici Pack 87 ratificati.
STARTER_ROSTER_CONTRACT: list[StarterEntry] = [
    {
        "starter_id": "greek_phalanx_recruit",
        "expected_role": "tank",
        "expected_hero_class": "Tank",
        "expected_rarity": 1,
        "expected_element": "earth",
    },
    {
        "starter_id": "celtic_forest_archer",
        "expected_role": "dps",
        "expected_hero_class": "DPS",
        "expected_rarity": 1,
        "expected_element": "wind",
    },
    {
        "starter_id": "angelic_sanctuary_acolyte",
        "expected_role": "support",
        "expected_hero_class": "Support",
        "expected_rarity": 1,
        "expected_element": "light",
    },
]

# ── Indici di lookup ────────────────────────────────────────────────────────
STARTER_IDS: list[str] = [e["starter_id"] for e in STARTER_ROSTER_CONTRACT]
STARTER_ID_SET: set[str] = set(STARTER_IDS)


def is_starter_id(hero_id: Optional[str]) -> bool:
    """True se l'hero_id appartiene al contratto starter canonico."""
    return bool(hero_id) and hero_id in STARTER_ID_SET


def get_starter_entry(hero_id: Optional[str]) -> Optional[StarterEntry]:
    """Ritorna la entry contratto per uno starter_id, o None se non starter."""
    if not hero_id:
        return None
    for entry in STARTER_ROSTER_CONTRACT:
        if entry["starter_id"] == hero_id:
            return entry
    return None


# ── Helper per `/api/psp/starter/claim` ────────────────────────────────────
def starter_set_for_claim() -> list[tuple[str, str]]:
    """Forma legacy `[(hero_id, role), ...]` consumata dal route
    `POST /api/psp/starter/claim` (Pack 87). Non muta i campi storici."""
    return [(e["starter_id"], e["expected_role"]) for e in STARTER_ROSTER_CONTRACT]


# ── Helper per `GET /api/user/heroes` (HOTFIX D) ───────────────────────────
def starter_fallback_exposure(hero_id: str, base_uh: dict) -> dict:
    """Costruisce un payload di esposizione fallback per uno starter canonico
    quando il merge con `db.heroes` produce campi mancanti (es. hero_class
    None). NON sovrascrive valori già presenti nel merge corrente: agisce
    solo come backfill per garantire visibilità coerente a heroes.tsx /
    battle.tsx (Hotfix B/C downstream).

    Non legge mai `db.heroes` qui. È pure data dal contratto.
    """
    entry = get_starter_entry(hero_id)
    if not entry:
        return {}
    return {
        "hero_id": hero_id,
        "hero_class": entry["expected_hero_class"],
        "hero_element": entry["expected_element"],
        "hero_rarity": entry["expected_rarity"],
        "starter_role": entry["expected_role"],
        "_hotfix_d_starter_fallback_applied": True,
    }


__all__ = [
    "STARTER_ROSTER_CONTRACT_VERSION",
    "STARTER_ROSTER_AUTHORIZATION",
    "STARTER_REQUIRED_FLAGS",
    "STARTER_ROSTER_CONTRACT",
    "STARTER_IDS",
    "STARTER_ID_SET",
    "is_starter_id",
    "get_starter_entry",
    "starter_set_for_claim",
    "starter_fallback_exposure",
]
