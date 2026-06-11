"""Pack 102 — Tower Floor Catalog (100 launch floors, deterministic enemy teams).

CONTRATTO:
  * Import-safe. NO DB writes. NO mutations su users.* o PSP.
  * Tutti gli enemy hero_id sono presi STRETTAMENTE da
    `data.character_bible.LAUNCH_BASE_HERO_IDS` (100 launch heroes ufficiali).
  * Borea (`launch_extra_premium`) NON e\u0300 usato in tower (premium/restricted).
  * Composizione deterministica: stesso output ad ogni esecuzione.
  * 6 unita\u0300 per piano, nessun duplicate hero_id nello stesso team.
  * Boss team ogni 10 piani; major boss su piano 50 e 100; mini-spike ogni 5 piani non multipli di 10.
  * NO boss mostri singoli. Tutti i boss sono team 6v6 con `boss_leader_slot=0`.

CATALOG VERSION: v1 (launch base 100 piani).
EXPANSION POLICY: documentata nel SOT, +20/+30 piani per patch (non aggiunti live in Pack 102).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from data.character_bible import (
    CHARACTER_BIBLE,
    CHARACTER_BIBLE_BY_ID,
    LAUNCH_BASE_HERO_IDS,
)

CATALOG_VERSION = "tower_v1_100_launch"
CATALOG_PACK_ORIGIN = "pack_102"
TOTAL_LAUNCH_FLOORS = 100
TEAM_SIZE = 6

# Tipi di piano canonici
FLOOR_TYPE_NORMAL = "normal"
FLOOR_TYPE_MINI_SPIKE = "mini_spike"
FLOOR_TYPE_BOSS_TEAM = "boss_team"
FLOOR_TYPE_MAJOR_BOSS_TEAM = "major_boss_team"

# Ordine slot canonico (deterministico) per garantire team composition coerente
SLOT_ROLE_ORDER: Tuple[str, ...] = (
    "tank",          # slot 0 (boss leader slot quando boss_team)
    "dps_melee",     # slot 1
    "dps_ranged",    # slot 2
    "mage_aoe",      # slot 3
    "support_buffer",# slot 4
    "healer",        # slot 5
)

# Mini-spike: sostituisce healer con assassin_burst (piu\u0300 pressure)
SLOT_ROLE_ORDER_MINI: Tuple[str, ...] = (
    "tank", "dps_melee", "dps_ranged", "mage_aoe", "support_buffer", "assassin_burst",
)

# Boss team: leader tank/dps_melee piu\u0300 alto rarity, 5 supporting roles
SLOT_ROLE_ORDER_BOSS: Tuple[str, ...] = (
    "tank", "dps_melee", "dps_ranged", "mage_aoe", "control_debuff", "healer",
)


# Indice heroes per (rarity, role) -> sorted list of hero_ids
def _build_role_rarity_index() -> Dict[Tuple[int, str], List[str]]:
    idx: Dict[Tuple[int, str], List[str]] = defaultdict(list)
    base_set = set(LAUNCH_BASE_HERO_IDS)
    for entry in CHARACTER_BIBLE:
        if entry["id"] not in base_set:
            continue
        rarity = int(entry["native_rarity"])
        role = entry["role"]
        idx[(rarity, role)].append(entry["id"])
    for k in idx:
        idx[k] = sorted(idx[k])
    return dict(idx)


_ROLE_RARITY_INDEX = _build_role_rarity_index()


def _compute_floor_type(floor: int) -> str:
    if floor in (50, 100):
        return FLOOR_TYPE_MAJOR_BOSS_TEAM
    if floor % 10 == 0:
        return FLOOR_TYPE_BOSS_TEAM
    if floor % 5 == 0:
        return FLOOR_TYPE_MINI_SPIKE
    return FLOOR_TYPE_NORMAL


def _compute_tier(floor: int) -> int:
    """Restituisce la rarity target principale per il floor (1-6).

    Curve di difficolta\u0300 deterministica:
      floor  1- 9 -> rarity 1-2
      floor 10-19 -> rarity 2-3
      floor 20-29 -> rarity 3
      floor 30-39 -> rarity 3-4
      floor 40-49 -> rarity 4
      floor 50    -> rarity 5 (major boss)
      floor 51-69 -> rarity 4-5
      floor 70-89 -> rarity 5
      floor 90-99 -> rarity 5-6
      floor 100   -> rarity 6 (major boss strongest launch)
    """
    if floor >= 100:
        return 6
    if floor >= 90:
        return 6 if floor % 2 == 0 else 5
    if floor >= 70:
        return 5
    if floor >= 51:
        return 5 if floor % 2 == 0 else 4
    if floor >= 50:
        return 5
    if floor >= 40:
        return 4
    if floor >= 30:
        return 4 if floor % 2 == 0 else 3
    if floor >= 20:
        return 3
    if floor >= 10:
        return 3 if floor % 2 == 0 else 2
    return 2 if floor >= 5 else 1


def _pick_hero_for_slot(
    target_rarity: int,
    role: str,
    floor: int,
    slot_index: int,
    excluded: set,
) -> Optional[str]:
    """Selezione deterministica:

    1. prova `(target_rarity, role)`.
    2. fallback su rarity-1, rarity+1, rarity-2, rarity+2, etc.
    3. fallback su qualsiasi rarity per quello role.
    4. fallback su tank (sempre presente).

    Indice deterministico: `(floor * 7 + slot_index) % len(candidates)`.
    Esclude `excluded` per evitare duplicati nello stesso team.
    """
    # Costruisci sequenza di tentativi rarity con preferenza verso il target
    rarity_seq = [target_rarity]
    for delta in (1, -1, 2, -2, 3, -3, 4, -4, 5, -5):
        cand = target_rarity + delta
        if 1 <= cand <= 6 and cand not in rarity_seq:
            rarity_seq.append(cand)

    for r in rarity_seq:
        pool = [h for h in _ROLE_RARITY_INDEX.get((r, role), []) if h not in excluded]
        if pool:
            idx = (floor * 7 + slot_index * 13) % len(pool)
            return pool[idx]

    # Final fallback: any role/rarity combo for tank
    for r in rarity_seq:
        pool = [h for h in _ROLE_RARITY_INDEX.get((r, "tank"), []) if h not in excluded]
        if pool:
            idx = (floor * 7 + slot_index * 13) % len(pool)
            return pool[idx]
    return None


def _build_floor(floor: int) -> Dict[str, Any]:
    ftype = _compute_floor_type(floor)
    tier = _compute_tier(floor)
    is_boss = ftype in (FLOOR_TYPE_BOSS_TEAM, FLOOR_TYPE_MAJOR_BOSS_TEAM)
    is_mini = ftype == FLOOR_TYPE_MINI_SPIKE

    # Boss leader: rarity bumped, slot 0 = top role tank con rarity massima possibile
    if ftype == FLOOR_TYPE_MAJOR_BOSS_TEAM:
        leader_rarity = 6 if floor == 100 else 5
        roles = SLOT_ROLE_ORDER_BOSS
    elif is_boss:
        leader_rarity = min(6, tier + 1)
        roles = SLOT_ROLE_ORDER_BOSS
    elif is_mini:
        leader_rarity = tier
        roles = SLOT_ROLE_ORDER_MINI
    else:
        leader_rarity = tier
        roles = SLOT_ROLE_ORDER

    team: List[Dict[str, Any]] = []
    used: set = set()
    for slot, role in enumerate(roles):
        if slot == 0 and is_boss:
            slot_rarity = leader_rarity
        else:
            slot_rarity = tier
        hero_id = _pick_hero_for_slot(slot_rarity, role, floor, slot, used)
        # If still None, fallback to ANY hero not yet used
        if hero_id is None:
            for cand in LAUNCH_BASE_HERO_IDS:
                if cand not in used:
                    hero_id = cand
                    break
        used.add(hero_id)
        info = CHARACTER_BIBLE_BY_ID[hero_id]
        team.append({
            "slot_index": slot,
            "hero_id": hero_id,
            "display_name": info["display_name"],
            "native_rarity": int(info["native_rarity"]),
            "role": info["role"],
            "element": info["element"],
            "is_boss_leader": bool(slot == 0 and is_boss),
        })

    return {
        "floor": floor,
        "floor_type": ftype,
        "tier": tier,
        "team_size": TEAM_SIZE,
        "enemy_team": team,
        "boss_leader_slot": 0 if is_boss else None,
        "_slc_pack_102_tower_catalog_v1": True,
    }


# Costruzione one-shot e cached. NO side effects.
TOWER_FLOOR_CATALOG_V1: List[Dict[str, Any]] = [_build_floor(f) for f in range(1, TOTAL_LAUNCH_FLOORS + 1)]
TOWER_FLOOR_CATALOG_BY_FLOOR: Dict[int, Dict[str, Any]] = {f["floor"]: f for f in TOWER_FLOOR_CATALOG_V1}


def get_catalog_summary() -> Dict[str, Any]:
    counts: Dict[str, int] = defaultdict(int)
    boss_floors: List[int] = []
    mini_floors: List[int] = []
    major_floors: List[int] = []
    for f in TOWER_FLOOR_CATALOG_V1:
        counts[f["floor_type"]] += 1
        if f["floor_type"] == FLOOR_TYPE_BOSS_TEAM:
            boss_floors.append(f["floor"])
        elif f["floor_type"] == FLOOR_TYPE_MINI_SPIKE:
            mini_floors.append(f["floor"])
        elif f["floor_type"] == FLOOR_TYPE_MAJOR_BOSS_TEAM:
            major_floors.append(f["floor"])
    return {
        "catalog_version": CATALOG_VERSION,
        "total_floors": len(TOWER_FLOOR_CATALOG_V1),
        "team_size": TEAM_SIZE,
        "counts_by_type": dict(counts),
        "boss_floors": boss_floors,
        "mini_spike_floors": mini_floors,
        "major_boss_floors": major_floors,
        "pack_origin": CATALOG_PACK_ORIGIN,
        "content_identical_across_servers": True,
        "deterministic": True,
        "uses_only_launch_base_heroes": True,
        "borea_or_extra_premium_used": False,
    }


def get_floor(floor: int) -> Optional[Dict[str, Any]]:
    return TOWER_FLOOR_CATALOG_BY_FLOOR.get(int(floor))
