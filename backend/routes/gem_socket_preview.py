"""PROJECT_GEM_SOCKET_RUNTIME_PACK — Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

Foundation runtime PREVIEW-ONLY per il sistema Gemme Socket.
- Gemme = socket/incastonabili nei gear/equip (NON Rune/scroll/talisman).
- Gemme NON sono la valuta premium `gems`.
- Tutto preview-only. NO mutation. NO DB. NO material spend. NO premium gems spend.

Gated da GEM_SOCKET_RUNTIME_PREVIEW_ENABLED. Default flag-off → HTTP 503 inert envelope.

Endpoints (tutti gated):
- GET  /api/gem-socket/config
- GET  /api/gem-socket/catalog
- POST /api/gem-socket/socket-preview
- POST /api/gem-socket/replace-preview
- POST /api/gem-socket/unsocket-preview
- POST /api/gem-socket/power-preview
"""
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

FEATURE_FLAG = "GEM_SOCKET_RUNTIME_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_gem_socket_runtime_preview_v1"
RUNTIME_MODE_TAG = "preview_only"

router = APIRouter(prefix="/api/gem-socket", tags=["gem_socket"])

# Gear rarity → max socket slots
MAX_SOCKETS_BY_RARITY = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 3}
# Socket unlock thresholds (livello gear richiesto)
SOCKET_LEVEL_UNLOCKS = {1: 10, 2: 20, 3: 35}
# Gear slots canonici (Gear Cap +50 alignment)
GEAR_SLOTS_CANONICAL = ["weapon", "armor", "helm", "boots", "gloves", "accessory"]
GEAR_SLOTS_LEGACY = ["weapon", "armor", "accessory"]

# 6 famiglie canoniche
GEM_FAMILIES = [
    {"family_id": "ruby",     "label_it": "Rubino",    "color": "red",    "stat_family": "attack",       "preferred_slots": ["weapon", "gloves", "accessory"]},
    {"family_id": "sapphire", "label_it": "Zaffiro",   "color": "blue",   "stat_family": "defense",      "preferred_slots": ["armor", "helm"]},
    {"family_id": "emerald",  "label_it": "Smeraldo",  "color": "green",  "stat_family": "hp",           "preferred_slots": ["armor", "helm", "accessory"]},
    {"family_id": "topaz",    "label_it": "Topazio",   "color": "yellow", "stat_family": "speed",        "preferred_slots": ["boots", "accessory"]},
    {"family_id": "amethyst", "label_it": "Ametista",  "color": "purple", "stat_family": "crit_chance",  "preferred_slots": ["weapon", "gloves", "accessory"]},
    {"family_id": "diamond",  "label_it": "Diamante",  "color": "white",  "stat_family": "all_stat",     "preferred_slots": GEAR_SLOTS_CANONICAL, "max_per_item_preview": 1},
]
GEM_FAMILY_IDS = {f["family_id"] for f in GEM_FAMILIES}

TIERS = ["common", "uncommon", "rare", "epic", "legendary", "divine"]
# Deltas preview NON-FINAL (clearly_non_final). Pattern lineare per tier index.
TIER_DELTA_BASE = {
    "common": 20, "uncommon": 45, "rare": 90, "epic": 180, "legendary": 320, "divine": 550,
}

SAFETY_FLAGS_CANON = {
    "live_commit_enabled": False,
    "premium_gems_currency_used": False,
    "rewards_disabled": True,
    "db_writes_enabled": False,
    "gear_mutation_enabled": False,
    "material_spend_enabled": False,
}


class SampleGear(BaseModel):
    gear_id: Optional[str] = None
    slot: Optional[str] = None
    rarity: int = 1
    level: int = 0
    base_stats: dict = Field(default_factory=dict)
    socketed_gems: List[dict] = Field(default_factory=list)


class SampleGem(BaseModel):
    gem_id: Optional[str] = None
    family: Optional[str] = None
    tier: Optional[str] = None


class SocketPreviewRequest(BaseModel):
    gear: SampleGear
    gem: SampleGem
    socket_index: int = 1


class ReplacePreviewRequest(BaseModel):
    gear: SampleGear
    new_gem: SampleGem
    socket_index: int = 1


class UnsocketPreviewRequest(BaseModel):
    gear: SampleGear
    socket_index: int = 1


class PowerPreviewRequest(BaseModel):
    gear: SampleGear
    gems: List[SampleGem] = Field(default_factory=list)


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "path": f"/api/gem-socket/{path_suffix}",
        "phase": "PROJECT_GEM_SOCKET_RUNTIME_PREVIEW_INERT",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/213_GEM_SOCKET_RUNTIME.md",
        "hint": (
            "Gem Socket runtime preview is disabled by default. "
            "Set GEM_SOCKET_RUNTIME_PREVIEW_ENABLED=true to enable inert envelope output. "
            "NO live mutation will ever happen from these endpoints. "
            "Live socket commit is NOT enabled in this pack."
        ),
        "live_mutation_applied": False,
        "db_writes": False,
        "materials_spent": False,
        "premium_gems_currency_used": False,
        "live_socket_commit_enabled": False,
    }


def _max_sockets_for(rarity: int) -> int:
    return MAX_SOCKETS_BY_RARITY.get(int(rarity), 0)


def _level_required_for_socket(socket_index: int) -> Optional[int]:
    return SOCKET_LEVEL_UNLOCKS.get(int(socket_index))


def _compute_gem_delta(gem: SampleGem) -> dict:
    family_id = (gem.family or "").lower()
    tier = (gem.tier or "").lower()
    if family_id not in GEM_FAMILY_IDS:
        return {}
    if tier not in TIER_DELTA_BASE:
        return {}
    base = TIER_DELTA_BASE[tier]
    fam = next(f for f in GEM_FAMILIES if f["family_id"] == family_id)
    stat = fam["stat_family"]
    if stat == "all_stat":
        # Diamond: ripartisce delta su più stat in modo conservativo
        small = max(1, base // 6)
        return {"attack": small, "defense": small, "hp": small * 2, "speed": small // 2}
    if stat == "hp":
        return {"hp": base * 4}
    if stat == "crit_chance":
        # crit è espresso come permille (1/1000) per evitare numeri irrealistici
        return {"crit_chance_permille": base // 10}
    if stat == "speed":
        return {"speed": max(1, base // 10)}
    return {stat: base}


def _validate_socket_eligibility(gear: SampleGear, socket_index: int) -> Optional[dict]:
    """Ritorna None se eligible, altrimenti payload blocked."""
    max_slots = _max_sockets_for(gear.rarity)
    if max_slots <= 0:
        return {
            "preview_ok": False,
            "reason": "socket_locked_by_rarity",
            "rarity": gear.rarity,
            "max_sockets_for_rarity": max_slots,
            "mutation": False,
            "db_writes": 0,
        }
    if socket_index < 1 or socket_index > max_slots:
        return {
            "preview_ok": False,
            "reason": "socket_index_out_of_range",
            "socket_index": socket_index,
            "max_sockets_for_rarity": max_slots,
            "mutation": False,
            "db_writes": 0,
        }
    req_lvl = _level_required_for_socket(socket_index)
    if req_lvl is not None and (gear.level or 0) < req_lvl:
        return {
            "preview_ok": False,
            "reason": "socket_locked_by_level",
            "required_level": req_lvl,
            "current_level": gear.level,
            "mutation": False,
            "db_writes": 0,
        }
    return None


@router.get("/config")
async def gem_socket_config() -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "mode": "PREVIEW_ONLY",
        "db_writes": False,
        "premium_gems_currency_used": False,
        "live_socket_commit_enabled": False,
        "max_sockets_by_rarity": MAX_SOCKETS_BY_RARITY,
        "socket_level_unlocks": SOCKET_LEVEL_UNLOCKS,
        "gear_slots_canonical": GEAR_SLOTS_CANONICAL,
        "gear_slots_legacy": GEAR_SLOTS_LEGACY,
        "tiers": TIERS,
        "gem_families": [f["family_id"] for f in GEM_FAMILIES],
        "safety_flags": SAFETY_FLAGS_CANON,
        "separation_from_other_layers": [
            "rune_scroll_talisman", "artifact", "divine_weapon",
            "premium_gems_currency", "material_raid_runtime_grant",
            "gear_forge_commit", "battle_engine", "combat",
            "bp_delta_overlay", "character_bible_final_numbers",
        ],
    }


@router.get("/catalog")
async def gem_socket_catalog() -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "catalog"))
    catalog = []
    for fam in GEM_FAMILIES:
        for tier in TIERS:
            gem_id = f"socket_gem_{fam['family_id']}_{tier}"
            catalog.append({
                "gem_id": gem_id,
                "family": fam["family_id"],
                "tier": tier,
                "label_it": f"{fam['label_it']} ({tier})",
                "color": fam["color"],
            })
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "premium_gems_currency_used": False,
        "gem_families": GEM_FAMILIES,
        "tiers": TIERS,
        "catalog": catalog,
        "final_numbers": None,
        "balance_status": "preview_non_final",
    }


@router.post("/socket-preview")
async def gem_socket_socket_preview(payload: SocketPreviewRequest) -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "socket-preview"))
    blocked = _validate_socket_eligibility(payload.gear, payload.socket_index)
    if blocked is not None:
        blocked.update({
            "runtime_enabled": True,
            "mode": "PREVIEW_ONLY",
            "premium_gems_currency_used": False,
            "live_socket_commit_enabled": False,
        })
        return blocked
    family_id = (payload.gem.family or "").lower()
    tier = (payload.gem.tier or "").lower()
    if family_id not in GEM_FAMILY_IDS:
        return {
            "preview_ok": False,
            "reason": "invalid_gem_family",
            "mutation": False,
            "db_writes": 0,
            "valid_families": sorted(GEM_FAMILY_IDS),
        }
    if tier not in TIER_DELTA_BASE:
        return {
            "preview_ok": False,
            "reason": "invalid_gem_tier",
            "mutation": False,
            "db_writes": 0,
            "valid_tiers": TIERS,
        }
    delta = _compute_gem_delta(payload.gem)
    warnings = []
    fam = next(f for f in GEM_FAMILIES if f["family_id"] == family_id)
    if payload.gear.slot and payload.gear.slot not in fam["preferred_slots"]:
        warnings.append({"code": "non_preferred_slot", "slot": payload.gear.slot, "preferred": fam["preferred_slots"]})
    if family_id == "diamond":
        diamond_count = sum(1 for g in payload.gear.socketed_gems if (g.get("family") or "").lower() == "diamond")
        if diamond_count >= 1:
            warnings.append({"code": "diamond_max_per_item_preview", "limit": 1})
    return {
        "preview_ok": True,
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "mode": "PREVIEW_ONLY",
        "mutation": False,
        "db_writes": 0,
        "socket_allowed": True,
        "socket_index": payload.socket_index,
        "gem_id": payload.gem.gem_id,
        "delta_stats": delta,
        "warnings": warnings,
        "safety": SAFETY_FLAGS_CANON,
        "final_numbers": None,
        "balance_status": "preview_non_final",
    }


@router.post("/replace-preview")
async def gem_socket_replace_preview(payload: ReplacePreviewRequest) -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "replace-preview"))
    blocked = _validate_socket_eligibility(payload.gear, payload.socket_index)
    if blocked is not None:
        blocked.update({"runtime_enabled": True, "mode": "PREVIEW_ONLY"})
        return blocked
    existing = None
    for g in payload.gear.socketed_gems:
        if int(g.get("socket_index") or 0) == payload.socket_index:
            existing = g
            break
    new_delta = _compute_gem_delta(payload.new_gem)
    old_delta = {}
    if existing:
        # ricostruisci old gem da existing dict
        old = SampleGem(gem_id=existing.get("gem_id"), family=existing.get("family"), tier=existing.get("tier"))
        old_delta = _compute_gem_delta(old)
    # diff netto: new - old (per stat)
    diff: dict = {}
    keys = set(list(new_delta.keys()) + list(old_delta.keys()))
    for k in keys:
        diff[k] = int(new_delta.get(k, 0)) - int(old_delta.get(k, 0))
    return {
        "preview_ok": True,
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "mode": "PREVIEW_ONLY",
        "mutation": False,
        "db_writes": 0,
        "socket_index": payload.socket_index,
        "existing_gem": existing,
        "new_gem": payload.new_gem.model_dump(),
        "old_delta_stats": old_delta,
        "new_delta_stats": new_delta,
        "diff_stats": diff,
        "safety": SAFETY_FLAGS_CANON,
        "hint": "In preview-only, replace non distrugge la vecchia gemma. Il commit policy verra' definita nel safety hardening pack.",
        "final_numbers": None,
        "balance_status": "preview_non_final",
    }


@router.post("/unsocket-preview")
async def gem_socket_unsocket_preview(payload: UnsocketPreviewRequest) -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "unsocket-preview"))
    existing = None
    for g in payload.gear.socketed_gems:
        if int(g.get("socket_index") or 0) == payload.socket_index:
            existing = g
            break
    if not existing:
        return {
            "preview_ok": False,
            "reason": "no_gem_in_socket",
            "socket_index": payload.socket_index,
            "mutation": False,
            "db_writes": 0,
        }
    old = SampleGem(gem_id=existing.get("gem_id"), family=existing.get("family"), tier=existing.get("tier"))
    removed_delta = _compute_gem_delta(old)
    return {
        "preview_ok": True,
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "mode": "PREVIEW_ONLY",
        "mutation": False,
        "db_writes": 0,
        "socket_index": payload.socket_index,
        "removed_gem": existing,
        "removed_delta_stats": removed_delta,
        "safety": SAFETY_FLAGS_CANON,
        "hint": "In preview-only, l'unsocket policy (restituzione integrale/parziale/distruzione) sara' definita nel safety hardening pack.",
        "final_numbers": None,
        "balance_status": "preview_non_final",
    }


@router.post("/power-preview")
async def gem_socket_power_preview(payload: PowerPreviewRequest) -> dict:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "power-preview"))
    max_slots = _max_sockets_for(payload.gear.rarity)
    accepted: List[dict] = []
    rejected: List[dict] = []
    aggregate: dict = {}
    for i, gem in enumerate(payload.gems[:max_slots], start=1):
        req_lvl = _level_required_for_socket(i)
        if req_lvl is not None and (payload.gear.level or 0) < req_lvl:
            rejected.append({"socket_index": i, "reason": "socket_locked_by_level", "required_level": req_lvl})
            continue
        delta = _compute_gem_delta(gem)
        if not delta:
            rejected.append({"socket_index": i, "reason": "invalid_gem", "gem": gem.model_dump()})
            continue
        accepted.append({"socket_index": i, "gem": gem.model_dump(), "delta_stats": delta})
        for k, v in delta.items():
            aggregate[k] = aggregate.get(k, 0) + int(v)
    return {
        "preview_ok": True,
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "mode": "PREVIEW_ONLY",
        "mutation": False,
        "db_writes": 0,
        "max_sockets_for_rarity": max_slots,
        "accepted_gems": accepted,
        "rejected_gems": rejected,
        "aggregate_delta_stats": aggregate,
        "safety": SAFETY_FLAGS_CANON,
        "final_numbers": None,
        "balance_status": "preview_non_final",
    }
