"""PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME — Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

Questa route e' gated dietro GEAR_FORGE_RUNTIME_PREVIEW_ENABLED. Quando il flag non e'
impostato o non e' 'true' (case-insensitive), ogni richiesta a `/api/gear-forge/*` ritorna
HTTP 503 con payload `{"status":"disabled", ...}`.

No DB writes. No mutation runtime. No combat/account stat mutation. No external service calls.
No materiali spesi. NESSUNA lookup su user_equipment / users (il legacy /forge/* resta
completamente intoccato).

Fase 3 dalla Bible 202: foundation runtime PREVIEW-ONLY per Forge standard del Gear.
Fusion commit NON abilitato: l'audit (track A) ha trovato guards mancanti sul legacy
/forge/fuse (fodder.equipped_to, locked/favorite, base.active_team, atomicita). Vedi
track E. La fusion commit live arriverà con un pack dedicato di safety hardening.

Endpoint (tutti gated):
- GET  /api/gear-forge/config             → config canonico + staged caps
- POST /api/gear-forge/fusion/preview     → preview-only outcome (NO mutation, NO delete)
- POST /api/gear-forge/enhance/preview    → preview-only cost current->target rispettando +50
- POST /api/gear-forge/reforge/preview    → preview-only schema (design-only)
- POST /api/gear-forge/enchant/preview    → preview-only schema (design-only, runtime disabled)
"""
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

FEATURE_FLAG = "GEAR_FORGE_RUNTIME_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_gear_forge_fusion_reforge_runtime_preview_v1"

router = APIRouter(prefix="/api/gear-forge", tags=["gear_forge"])

# Valori canonici allineati a Bible 202 + Gear Cap +50 pack.
GEAR_CAP_CANONICAL = 50
GEAR_CAP_LEGACY_TO_REPLACE = 20
GEAR_CAP_MIN = 0

GEAR_STAGED_CAPS = [
    {"stage_id": "early",   "order": 0, "label_it": "Avvio",      "min": 0,  "max": 10},
    {"stage_id": "mid",     "order": 1, "label_it": "Intermedio", "min": 11, "max": 20},
    {"stage_id": "late",    "order": 2, "label_it": "Avanzato",   "min": 21, "max": 35},
    {"stage_id": "endgame", "order": 3, "label_it": "Endgame",    "min": 36, "max": 50},
]

# Cost preview replicato da gear_cap_plus_50/E_material_cost_policy_v1.json.
GEAR_COST_PREVIEW_BY_STAGE = {
    "early":   {"per_plus_level": {"gear_dust_common": 5},                                       "gold_per_plus_level": 200},
    "mid":     {"per_plus_level": {"gear_dust_common": 12, "gear_shard_uncommon": 1},            "gold_per_plus_level": 600},
    "late":    {"per_plus_level": {"gear_shard_uncommon": 3, "gear_core_rare": 1},               "gold_per_plus_level": 1800},
    "endgame": {"per_plus_level": {"gear_core_rare": 4, "gear_essence_epic": 1},                 "gold_per_plus_level": 5400},
}

FORGE_SUBSYSTEMS = [
    {"id": "enhance", "label_it": "Potenzia", "runtime_state": "preview_only_aware_of_cap_plus_50"},
    {"id": "fusion",  "label_it": "Fondi",    "runtime_state": "preview_only_commit_disabled_safety_audit"},
    {"id": "reforge", "label_it": "Riforgia", "runtime_state": "preview_only_schema_only"},
    {"id": "enchant", "label_it": "Incanta",  "runtime_state": "design_only_schema_only"},
]

FUSION_MIN_FODDER = 3
FUSION_QUALITIES = ["common", "uncommon", "rare", "epic", "legendary", "mythic"]
FUSION_COST_PREVIEW = {
    "common->uncommon":   {"gold": 500,   "gear_dust_common": 10},
    "uncommon->rare":     {"gold": 1500,  "gear_shard_uncommon": 3},
    "rare->epic":         {"gold": 4500,  "gear_core_rare": 2},
    "epic->legendary":    {"gold": 13500, "gear_essence_epic": 2},
    "legendary->mythic":  {"gold": 40500, "gear_essence_epic": 6},
}


class FusionPreviewRequest(BaseModel):
    base_id: Optional[str] = None
    fodder_ids: List[str] = Field(default_factory=list)
    current_quality: Optional[str] = None


class EnhancePreviewRequest(BaseModel):
    equipment_id: Optional[str] = None
    current_level: int = 0
    target_level: int = 1


class ReforgePreviewRequest(BaseModel):
    equipment_id: Optional[str] = None


class EnchantPreviewRequest(BaseModel):
    equipment_id: Optional[str] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "path": f"/api/gear-forge/{path_suffix}",
        "phase": "PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PREVIEW_INERT",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/207_GEAR_FORGE_FUSION_REFORGE_RUNTIME.md",
        "hint": (
            "Gear Forge runtime preview is disabled by default. "
            "Set GEAR_FORGE_RUNTIME_PREVIEW_ENABLED=true to enable inert envelope output. "
            "NO live mutation will ever happen from these endpoints. "
            "Fusion commit is NOT enabled in this pack (audit blocked, see track E)."
        ),
        "live_mutation_applied": False,
        "db_writes": False,
        "materials_spent": False,
        "fusion_commit_enabled": False,
    }


def _resolve_stage(level: int) -> Optional[dict]:
    if level < GEAR_CAP_MIN or level > GEAR_CAP_CANONICAL:
        return None
    for s in GEAR_STAGED_CAPS:
        if s["min"] <= level <= s["max"]:
            return s
    return None


@router.get("/config")
async def gear_forge_config() -> dict:
    """Config canonico Forge. Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "fusion_commit_enabled": False,
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "gear_cap_legacy_to_replace": GEAR_CAP_LEGACY_TO_REPLACE,
        "staged_caps": GEAR_STAGED_CAPS,
        "subsystems": FORGE_SUBSYSTEMS,
        "fusion_qualities": FUSION_QUALITIES,
        "fusion_min_fodder": FUSION_MIN_FODDER,
        "cost_source": {
            "enhance": "data/design/gear_cap_plus_50/E_material_cost_policy_v1.json",
            "fusion":  "in-route FUSION_COST_PREVIEW (design-only)",
        },
    }


@router.post("/fusion/preview")
async def gear_forge_fusion_preview(payload: FusionPreviewRequest) -> dict:
    """Preview-only fusion outcome. NESSUNA mutation. NESSUN DB read. NESSUN delete."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "fusion/preview"))
    fodder_ids = [fid for fid in (payload.fodder_ids or []) if fid]
    if payload.base_id and payload.base_id in fodder_ids:
        return {
            "status": "invalid_base_in_fodder",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "fusion_commit_enabled": False,
            "hint": "base_id non puo' essere presente in fodder_ids",
        }
    if len(fodder_ids) < FUSION_MIN_FODDER:
        return {
            "status": "insufficient_fodder",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "fusion_commit_enabled": False,
            "required_min_fodder": FUSION_MIN_FODDER,
            "received": len(fodder_ids),
        }
    current_q = (payload.current_quality or "common").lower()
    if current_q not in FUSION_QUALITIES:
        return {
            "status": "invalid_current_quality",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "fusion_commit_enabled": False,
            "valid_qualities": FUSION_QUALITIES,
        }
    idx = FUSION_QUALITIES.index(current_q)
    if idx >= len(FUSION_QUALITIES) - 1:
        return {
            "status": "max_quality_reached",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "fusion_commit_enabled": False,
            "current_quality": current_q,
            "next_quality": None,
        }
    next_q = FUSION_QUALITIES[idx + 1]
    cost_key = f"{current_q}->{next_q}"
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "fusion_commit_enabled": False,
        "base_id": payload.base_id,
        "fodder_ids": fodder_ids,
        "fodder_count": len(fodder_ids),
        "current_quality": current_q,
        "next_quality": next_q,
        "cost_preview": FUSION_COST_PREVIEW.get(cost_key, {}),
        "required_guards_for_future_commit": [
            "fodder_not_equipped", "fodder_not_locked_or_favorite",
            "base_not_in_active_team", "atomic_transaction",
            "no_paid_currency", "no_negative_balance",
        ],
        "design_only_replace_before_release": True,
    }


@router.post("/enhance/preview")
async def gear_forge_enhance_preview(payload: EnhancePreviewRequest) -> dict:
    """Preview-only enhance cost current->target rispettando cap +50 e stage gates."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "enhance/preview"))
    cur = int(payload.current_level or 0)
    tgt = int(payload.target_level or 0)
    if cur < GEAR_CAP_MIN:
        cur = GEAR_CAP_MIN
    if cur > GEAR_CAP_CANONICAL:
        return {
            "status": "current_above_cap",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "gear_cap_canonical": GEAR_CAP_CANONICAL,
            "current_level": cur,
        }
    if tgt > GEAR_CAP_CANONICAL:
        return {
            "status": "target_above_cap",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "gear_cap_canonical": GEAR_CAP_CANONICAL,
            "target_level": tgt,
        }
    if tgt <= cur:
        return {
            "status": "target_not_above_current",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "current_level": cur,
            "target_level": tgt,
        }
    # Accumula cost per ogni +1 livello allo stage di destinazione
    steps = []
    total_gold = 0
    total_mats: dict = {}
    for lvl in range(cur + 1, tgt + 1):
        st = _resolve_stage(lvl)
        if not st:
            continue
        cost = GEAR_COST_PREVIEW_BY_STAGE.get(st["stage_id"], {})
        gold = int(cost.get("gold_per_plus_level", 0))
        total_gold += gold
        for mat, qty in (cost.get("per_plus_level") or {}).items():
            total_mats[mat] = total_mats.get(mat, 0) + int(qty)
        steps.append({"level": lvl, "stage_id": st["stage_id"], "gold": gold, "materials": cost.get("per_plus_level") or {}})
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "equipment_id": payload.equipment_id,
        "current_level": cur,
        "target_level": tgt,
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "steps": steps,
        "totals": {"gold": total_gold, "materials": total_mats},
        "design_only_replace_before_release": True,
    }


@router.post("/reforge/preview")
async def gear_forge_reforge_preview(payload: ReforgePreviewRequest) -> dict:
    """Preview-only reforge shape. Design-only. Runtime DISABLED."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "reforge/preview"))
    return {
        "status": "preview_design_only",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "materials_spent": False,
        "equipment_id": payload.equipment_id,
        "rules": {
            "preserves_plus_level": True,
            "preserves_quality": True,
            "rerolls_only_sub_stats": True,
        },
        "runtime_disabled": True,
        "design_only_replace_before_release": True,
    }


@router.post("/enchant/preview")
async def gear_forge_enchant_preview(payload: EnchantPreviewRequest) -> dict:
    """Preview-only enchant shape. Design-only. Runtime DISABLED."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "enchant/preview"))
    return {
        "status": "preview_design_only",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "materials_spent": False,
        "equipment_id": payload.equipment_id,
        "rules": {
            "adds_temp_or_perm_property": True,
            "future_pack_will_define": True,
        },
        "runtime_disabled": True,
        "design_only_replace_before_release": True,
    }
