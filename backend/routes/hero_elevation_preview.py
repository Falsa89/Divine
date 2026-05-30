"""PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME — Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

Questa route e\u2019 gated dietro HERO_ELEVATION_PREVIEW_ENABLED. Quando il flag non e\u2019
impostato o non e\u2019 'true' (case-insensitive), ogni richiesta a
`/api/hero/elevation/*` ritorna HTTP 503 con payload `{"status":"disabled", ...}`.

No DB writes. No mutation runtime di elevation. No combat/account stat mutation.
No external service calls. No materiali spesi. La route esiste solo per pubblicare il
contract shape read-only che pack futuri possono attivare esplicitamente.

Con il flag ON (NON default), la route emette envelope deterministici read-only:
- GET /api/hero/elevation/tiers      → lista canonica dei 15 tier E0..E14
- GET /api/hero/elevation/{hero_id}  → current tier con fallback a E0 se assente
- POST /api/hero/elevation/{hero_id}/upgrade/preview → preview-only (cost + next tier),
        NESSUN DB write, NESSUNA mutazione.

Vincoli di Bible 202 onorati: Hero Elevation e\u2019 separato da Star Up, Ascensione,
Level, Skill, Costellazioni, Reincarnation, Gear, Gemme, Rune, Artifact, Divine Weapon.
"""
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "HERO_ELEVATION_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_hero_elevation_quality_frame_runtime_preview_v1"

router = APIRouter(prefix="/api/hero/elevation", tags=["hero_elevation"])

# Tier canonici E0..E14 (15 tiers totali). Locked da Bible 202 + estensione per
# Verde / Verde+1 / Blu / Blu+1+2 / Viola+1+2+3 / Oro+1+2+3 / Rosso+1+2+3.
# NOTA: questi sono i VALORI DI DISPLAY. La logica di upgrade e\u2019 preview-only.
ELEVATION_TIERS = [
    {"tier_id": "E0",  "order": 0,  "color_id": "white",  "label_it": "Bianco",      "quality": 0, "frame_color_hint": "#e0e0ea"},
    {"tier_id": "E1",  "order": 1,  "color_id": "green",  "label_it": "Verde",       "quality": 0, "frame_color_hint": "#3ddc84"},
    {"tier_id": "E2",  "order": 2,  "color_id": "green",  "label_it": "Verde +1",    "quality": 1, "frame_color_hint": "#3ddc84"},
    {"tier_id": "E3",  "order": 3,  "color_id": "blue",   "label_it": "Blu",         "quality": 0, "frame_color_hint": "#4a90e2"},
    {"tier_id": "E4",  "order": 4,  "color_id": "blue",   "label_it": "Blu +1",      "quality": 1, "frame_color_hint": "#4a90e2"},
    {"tier_id": "E5",  "order": 5,  "color_id": "blue",   "label_it": "Blu +2",      "quality": 2, "frame_color_hint": "#4a90e2"},
    {"tier_id": "E6",  "order": 6,  "color_id": "purple", "label_it": "Viola +1",    "quality": 1, "frame_color_hint": "#a96bff"},
    {"tier_id": "E7",  "order": 7,  "color_id": "purple", "label_it": "Viola +2",    "quality": 2, "frame_color_hint": "#a96bff"},
    {"tier_id": "E8",  "order": 8,  "color_id": "purple", "label_it": "Viola +3",    "quality": 3, "frame_color_hint": "#a96bff"},
    {"tier_id": "E9",  "order": 9,  "color_id": "gold",   "label_it": "Oro +1",      "quality": 1, "frame_color_hint": "#ffb84a"},
    {"tier_id": "E10", "order": 10, "color_id": "gold",   "label_it": "Oro +2",      "quality": 2, "frame_color_hint": "#ffb84a"},
    {"tier_id": "E11", "order": 11, "color_id": "gold",   "label_it": "Oro +3",      "quality": 3, "frame_color_hint": "#ffb84a"},
    {"tier_id": "E12", "order": 12, "color_id": "red",    "label_it": "Rosso +1",    "quality": 1, "frame_color_hint": "#ff5470"},
    {"tier_id": "E13", "order": 13, "color_id": "red",    "label_it": "Rosso +2",    "quality": 2, "frame_color_hint": "#ff5470"},
    {"tier_id": "E14", "order": 14, "color_id": "red",    "label_it": "Rosso +3",    "quality": 3, "frame_color_hint": "#ff5470"},
]
DEFAULT_TIER_ID = "E0"

# Cost preview canonico (design-only / preview-only). NESSUN materiale viene speso.
# Tutte le quantita\u2019 sono DESIGN_ONLY e replace_before_release.
ELEVATION_COST_PREVIEW = {
    # transition_from -> required_materials (preview only)
    "E0->E1":   {"elevation_dust_common": 10},
    "E1->E2":   {"elevation_dust_common": 20},
    "E2->E3":   {"elevation_dust_common": 40, "elevation_crystal_rare": 1},
    "E3->E4":   {"elevation_crystal_rare": 3},
    "E4->E5":   {"elevation_crystal_rare": 5},
    "E5->E6":   {"elevation_crystal_rare": 8, "elevation_essence_epic": 1},
    "E6->E7":   {"elevation_essence_epic": 2},
    "E7->E8":   {"elevation_essence_epic": 4},
    "E8->E9":   {"elevation_essence_epic": 6, "elevation_orb_legendary": 1},
    "E9->E10":  {"elevation_orb_legendary": 2},
    "E10->E11": {"elevation_orb_legendary": 4},
    "E11->E12": {"elevation_orb_legendary": 6, "elevation_essence_epic": 5},
    "E12->E13": {"elevation_orb_legendary": 8, "elevation_essence_epic": 10},
    "E13->E14": {"elevation_orb_legendary": 12, "elevation_essence_epic": 20},
}


class UpgradePreviewRequest(BaseModel):
    user_id: Optional[str] = None
    current_tier_id: Optional[str] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "path": f"/api/hero/elevation/{path_suffix}",
        "phase": "PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PREVIEW_INERT",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/202_HERO_GEAR_PROGRESSION_BIBLE.md",
        "hint": (
            "Hero Elevation read-only preview is disabled by default. "
            "Set HERO_ELEVATION_PREVIEW_ENABLED=true to enable inert envelope output. "
            "NO live mutation will ever happen from these endpoints."
        ),
        "live_mutation_applied": False,
        "db_writes": False,
        "combat_mutation": False,
        "materials_spent": False,
    }


@router.get("/tiers")
async def hero_elevation_tiers() -> dict:
    """Lista canonica dei tier Hero Elevation. Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "tiers"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "default_tier_id": DEFAULT_TIER_ID,
        "tiers": ELEVATION_TIERS,
        "separated_from": [
            "hero_level", "star_up", "ascension", "skill_upgrade",
            "costellazioni", "reincarnation", "gear", "gemme",
            "rune_scroll_talisman", "artifact", "divine_weapon",
        ],
    }


@router.get("/{hero_id}")
async def hero_elevation_current(hero_id: str) -> dict:
    """Current tier dell'eroe. Fallback a E0 se assente. Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", hero_id))
    # Inert read-only envelope: NESSUNA lettura DB in questo pack preview-only.
    # In una futura attivazione, qui si leggera\u2019 da DB user_heroes.<hero_id>.elevation_tier_id
    # con fallback a DEFAULT_TIER_ID se assente.
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "hero_id": hero_id,
        "current_tier_id": DEFAULT_TIER_ID,
        "fallback_used": True,
        "fallback_reason": "preview_only_no_db_read_in_this_pack",
    }


@router.post("/{hero_id}/upgrade/preview")
async def hero_elevation_upgrade_preview(hero_id: str, payload: UpgradePreviewRequest) -> dict:
    """Preview-only upgrade flow. NESSUNA mutation. NESSUN DB write. NESSUN materiale speso."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", f"{hero_id}/upgrade/preview"))
    current = payload.current_tier_id or DEFAULT_TIER_ID
    # Trova next tier in lista
    current_index = next((i for i, t in enumerate(ELEVATION_TIERS) if t["tier_id"] == current), -1)
    if current_index < 0:
        return {
            "status": "invalid_current_tier",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "hero_id": hero_id,
            "current_tier_id": current,
            "next_tier_id": None,
            "cost_preview": None,
            "hint": f"current_tier_id '{current}' non e\u2019 in {[t['tier_id'] for t in ELEVATION_TIERS]}",
        }
    next_index = current_index + 1
    if next_index >= len(ELEVATION_TIERS):
        return {
            "status": "max_tier_reached",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_spent": False,
            "hero_id": hero_id,
            "current_tier_id": current,
            "next_tier_id": None,
            "cost_preview": None,
        }
    next_tier = ELEVATION_TIERS[next_index]
    cost_key = f"{current}->{next_tier['tier_id']}"
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_spent": False,
        "hero_id": hero_id,
        "current_tier_id": current,
        "next_tier_id": next_tier["tier_id"],
        "next_tier_label_it": next_tier["label_it"],
        "next_tier_frame_color_hint": next_tier["frame_color_hint"],
        "cost_preview": ELEVATION_COST_PREVIEW.get(cost_key, {}),
        "design_only_replace_before_release": True,
    }
