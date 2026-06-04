"""
v95 — Read-only catalog router (runtime).

Endpoints read-only / idempotent / NO DB writes:
- GET /api/encounter-source/catalog
- GET /api/encounter-source/get?mode=X&source_id=Y
- GET /api/live-mode/catalog
- GET /api/avatar-placeholder/catalog

Serve i catalog JSON da disco (data/design/...) come read-only.
Nessuna scrittura DB. Nessun reward. Nessun ranking. Nessun PII.

MEGA_RELEASE_ACCELERATION_44_v95
"""
import json
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["v95_readonly_catalog"])

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESIGN_DIR = os.path.join(ROOT, "data", "design")

# Catalog file map
_ENCOUNTER_CATALOGS = {
    "story": "battle_mode_enemy_sources/story_encounter_stub_catalog_v1.json",
    "tower": "battle_mode_enemy_sources/tower_encounter_stub_catalog_v1.json",
    "arena": "battle_mode_enemy_sources/arena_opponent_source_stub_catalog_v1.json",
    "training": "battle_mode_enemy_sources/training_encounter_stub_catalog_v1.json",
    "raid": "battle_mode_enemy_sources/raid_boss_encounter_stub_catalog_v1.json",
    "event": "battle_mode_enemy_sources/event_encounter_stub_catalog_v1.json",
    "guild_live": "battle_mode_enemy_sources/guild_live_encounter_source_stub_catalog_v1.json",
}
_LIVE_MODE_CATALOG = "live_mode_testability/live_guild_special_mode_encounter_source_catalog_v1.json"
_AVATAR_REGISTRY = "avatar_placeholders/avatar_placeholder_dev_registry_v1.json"


def _read_json(rel_path: str):
    full = os.path.join(DESIGN_DIR, rel_path)
    if not os.path.isfile(full):
        raise HTTPException(status_code=404, detail=f"catalog not found: {rel_path}")
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/encounter-source/catalog")
def encounter_source_catalog():
    """Read-only: ritorna tutti i 7 encounter catalog (story/tower/arena/training/raid/event/guild_live)."""
    out = {}
    for key, rel in _ENCOUNTER_CATALOGS.items():
        try:
            out[key] = _read_json(rel)
        except HTTPException:
            out[key] = None
    return {
        "v95_readonly": True,
        "db_writes": 0,
        "reward_live": False,
        "ranking_live": False,
        "catalogs": out,
    }


@router.get("/encounter-source/get")
def encounter_source_get(
    mode: str = Query(..., description="story|tower|arena|training|raid|event|guild_live"),
    source_id: Optional[str] = Query(None),
):
    """Read-only: ritorna specifica fonte encounter."""
    if mode not in _ENCOUNTER_CATALOGS:
        raise HTTPException(status_code=400, detail=f"unknown mode: {mode}")
    data = _read_json(_ENCOUNTER_CATALOGS[mode])
    if source_id is None:
        return {"v95_readonly": True, "db_writes": 0, "catalog": data}
    # find record by source_id across known list keys
    for list_key in ("encounters", "opponent_sources", "presets", "bosses", "events", "sources"):
        records = data.get(list_key) or []
        for r in records:
            if r.get("source_id") == source_id:
                return {"v95_readonly": True, "db_writes": 0, "record": r}
    raise HTTPException(status_code=404, detail=f"source_id not found: {source_id}")


@router.get("/live-mode/catalog")
def live_mode_catalog():
    """Read-only: ritorna catalog modalita' live/guild/special."""
    return {"v95_readonly": True, "db_writes": 0, "catalog": _read_json(_LIVE_MODE_CATALOG)}


@router.get("/avatar-placeholder/catalog")
def avatar_placeholder_catalog():
    """Read-only: ritorna registry avatar placeholder dev."""
    return {"v95_readonly": True, "db_writes": 0, "registry": _read_json(_AVATAR_REGISTRY)}
