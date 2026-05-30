"""PROJECT_GEAR_CAP_PLUS_50_RUNTIME — Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

Questa route e' gated dietro GEAR_CAP_PLUS_50_PREVIEW_ENABLED. Quando il flag non e'
impostato o non e' 'true' (case-insensitive), ogni richiesta a `/api/gear-cap/*` ritorna
HTTP 503 con payload `{"status":"disabled", ...}`.

No DB writes. No mutation runtime di gear level. No combat/account stat mutation.
No external service calls. No materiali spesi. La route esiste solo per pubblicare
il contract shape read-only che pack futuri (forge enhance/fusion/reforge) possono
attivare esplicitamente.

Con il flag ON (NON default), la route emette envelope deterministici read-only:
- GET  /api/gear-cap/tiers                          → lista canonica staged caps (4 stage)
- GET  /api/gear-cap/preview-tiers                  → alias preview-only di /tiers
- GET  /api/gear-cap/{hero_id}/preview              → current cap preview con fallback 0 (no DB read)
- POST /api/gear-cap/{hero_id}/upgrade/preview      → next stage + cost preview, NESSUNA mutation

Vincoli di Bible 202 (track D) onorati: Gear cap canonico=50 e legacy=20 documentato come debt.
Separato da Hero Elevation, Gemme, Rune, Artifact, Divine Weapon, BP Delta, combat, character bible.
"""
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "GEAR_CAP_PLUS_50_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_gear_cap_plus_50_runtime_preview_v1"

router = APIRouter(prefix="/api/gear-cap", tags=["gear_cap"])

# Valori canonici locked da Bible 202 (track D_gear_progression_bible_v1.json)
GEAR_CAP_CANONICAL = 50
GEAR_CAP_LEGACY_TO_REPLACE = 20
GEAR_CAP_MIN = 0

# Stage canonici (4 stage). Replicati da B_gear_cap_constants_and_schema_v1.json.
GEAR_STAGED_CAPS = [
    {"stage_id": "early",   "order": 0, "label_it": "Avvio",      "min": 0,  "max": 10, "display_color_hint": "#9ea0c8", "unlock_via": "hero_level_or_ascension_low"},
    {"stage_id": "mid",     "order": 1, "label_it": "Intermedio", "min": 11, "max": 20, "display_color_hint": "#4a90e2", "unlock_via": "hero_level_mid + ascension_unlock"},
    {"stage_id": "late",    "order": 2, "label_it": "Avanzato",   "min": 21, "max": 35, "display_color_hint": "#a96bff", "unlock_via": "forge_enhance + materials_late"},
    {"stage_id": "endgame", "order": 3, "label_it": "Endgame",    "min": 36, "max": 50, "display_color_hint": "#ff5470", "unlock_via": "forge_reforge + endgame_materials + costellazione_gate_optional"},
]

# Cost preview canonico (design-only / preview-only). NESSUN materiale viene speso.
# Replicato da E_material_cost_policy_v1.json.
GEAR_COST_PREVIEW_BY_STAGE = {
    "early":   {"per_plus_level": {"gear_dust_common": 5},                                       "gold_per_plus_level": 200},
    "mid":     {"per_plus_level": {"gear_dust_common": 12, "gear_shard_uncommon": 1},            "gold_per_plus_level": 600},
    "late":    {"per_plus_level": {"gear_shard_uncommon": 3, "gear_core_rare": 1},               "gold_per_plus_level": 1800},
    "endgame": {"per_plus_level": {"gear_core_rare": 4, "gear_essence_epic": 1},                 "gold_per_plus_level": 5400},
}

SEPARATED_FROM = [
    "hero_level", "star_up", "ascension", "skill_upgrade",
    "costellazioni", "reincarnation", "hero_elevation",
    "gemme", "rune_scroll_talisman", "artifact", "divine_weapon",
    "bp_delta", "combat_formulas", "battle_engine",
    "character_bible_final_numbers", "shop_iap", "battle_pass",
    "vip", "server_profiles_live",
]


class UpgradePreviewRequest(BaseModel):
    user_id: Optional[str] = None
    current_level: Optional[int] = 0


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "path": f"/api/gear-cap/{path_suffix}",
        "phase": "PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PREVIEW_INERT",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/205_GEAR_CAP_PLUS_50_RUNTIME.md",
        "hint": (
            "Gear Cap +50 read-only preview is disabled by default. "
            "Set GEAR_CAP_PLUS_50_PREVIEW_ENABLED=true to enable inert envelope output. "
            "NO live mutation will ever happen from these endpoints."
        ),
        "live_mutation_applied": False,
        "db_writes": False,
        "combat_mutation": False,
        "materials_spent": False,
    }


def _resolve_stage(level: int) -> Optional[dict]:
    if level < GEAR_CAP_MIN or level > GEAR_CAP_CANONICAL:
        return None
    for s in GEAR_STAGED_CAPS:
        if s["min"] <= level <= s["max"]:
            return s
    return None


@router.get("/tiers")
async def gear_cap_tiers() -> dict:
    """Lista canonica staged caps. Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "tiers"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "gear_cap_legacy_to_replace": GEAR_CAP_LEGACY_TO_REPLACE,
        "staged_caps": GEAR_STAGED_CAPS,
        "separated_from": SEPARATED_FROM,
    }


@router.get("/preview-tiers")
async def gear_cap_preview_tiers() -> dict:
    """Alias preview-only di /tiers. Stessa payload shape."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "preview-tiers"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "alias_of": "/api/gear-cap/tiers",
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "gear_cap_legacy_to_replace": GEAR_CAP_LEGACY_TO_REPLACE,
        "staged_caps": GEAR_STAGED_CAPS,
        "separated_from": SEPARATED_FROM,
    }


@router.get("/{hero_id}/preview")
async def gear_cap_current_preview(hero_id: str) -> dict:
    """Current cap preview per hero_id. Fallback 0 (no DB read). Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", f"{hero_id}/preview"))
    # In una futura attivazione, qui si leggera' da DB user_heroes.<hero_id>.gear_level
    # con fallback a 0 se assente.
    fallback_level = 0
    stage = _resolve_stage(fallback_level)
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "hero_id": hero_id,
        "current_level": fallback_level,
        "current_stage_id": stage["stage_id"] if stage else None,
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "fallback_used": True,
        "fallback_reason": "preview_only_no_db_read_in_this_pack",
    }


@router.post("/{hero_id}/upgrade/preview")
async def gear_cap_upgrade_preview(hero_id: str, payload: UpgradePreviewRequest) -> dict:
    """Preview-only upgrade flow. NESSUNA mutation. NESSUN DB write. NESSUN materiale speso."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", f"{hero_id}/upgrade/preview"))
    current_level = max(GEAR_CAP_MIN, min(int(payload.current_level or 0), GEAR_CAP_CANONICAL))
    if current_level >= GEAR_CAP_CANONICAL:
        return {
            "status": "max_cap_reached",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "hero_id": hero_id,
            "current_level": current_level,
            "next_level": None,
            "gear_cap_canonical": GEAR_CAP_CANONICAL,
            "cost_preview": None,
        }
    next_level = current_level + 1
    stage = _resolve_stage(next_level)
    cost = GEAR_COST_PREVIEW_BY_STAGE.get(stage["stage_id"]) if stage else None
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "hero_id": hero_id,
        "current_level": current_level,
        "next_level": next_level,
        "next_stage_id": stage["stage_id"] if stage else None,
        "next_stage_label_it": stage["label_it"] if stage else None,
        "gear_cap_canonical": GEAR_CAP_CANONICAL,
        "cost_preview": cost,
        "design_only_replace_before_release": True,
    }
