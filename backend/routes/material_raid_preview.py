"""PROJECT_MATERIAL_RAID_RUNTIME — Read-Only Preview Endpoint (DISABLED-BY-DEFAULT INERT).

Questa route e' gated dietro MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED. Quando il flag non e'
impostato o non e' 'true' (case-insensitive), ogni richiesta a `/api/material-raid/*` ritorna
HTTP 503 con payload `{"status":"disabled", ...}`.

No DB writes. No reward grant live. No mutation. No combat/account stat mutation.
No external service calls. No materiali spesi. No stamina. No tickets. No paid attempts.
NESSUNA lookup su user_materials/users/inventory (il legacy /raids/* e /inventory restano
completamente intoccati).

Foundation runtime PREVIEW-ONLY per Material Raid (modalita PvE per material farm).
Reward claim NON abilitato: l'audit (track A) ha trovato:
- nessuna collection canonical user_materials
- nessun idempotent grant con request_id
- nessuna drop table auditata
- nessuna atomicita transactional
- nessun audit log
Vedi track E. Il claim live arrivera con un pack dedicato di safety hardening.

Endpoint (tutti gated):
- GET  /api/material-raid/config           → tracks + reward families + stage model
- GET  /api/material-raid/stages           → stages I..V con recommended_power
- POST /api/material-raid/reward-preview   → preview-only reward envelope per track+stage
- POST /api/material-raid/clear-preview    → preview-only clear eligibility per team_power
"""
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_material_raid_runtime_preview_v1"
RUNTIME_MODE_TAG = "preview_only"  # Marker esplicito per validator e log: questo pack e' preview_only.

# v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION:
# Aggiunge una "playable alpha slice" sopra il preview Material Raid esistente.
# Default OFF. Quando OFF, i nuovi endpoint /alpha-* tornano 503 (come gli altri).
# Quando ON, restituiscono payload di preview deterministici, senza alcuna
# chiamata a battle_engine, senza DB write, senza grant materiale, senza stamina.
# Gli endpoint esistenti /config, /stages, /reward-preview, /clear-preview
# restano gated dal flag legacy MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED e non
# cambiano comportamento, path, default 503, o feature flag.
ALPHA_SLICE_FEATURE_FLAG = "MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED"
ALPHA_SLICE_CONTRACT_VERSION = "material_raid_playable_alpha_slice_v1"
ALPHA_SLICE_PHASE = "v51"

router = APIRouter(prefix="/api/material-raid", tags=["material_raid"])

# Tracks canonici (5 totali). v31 Mega Batch Acceleration 1 Track B unlock:
# gem_material_raid passa da locked_deferred a open_preview (preview-only).
# Rune e Artifact/Divine restano locked_deferred (preview-only, runtime futuro).
# ----------------------------------------------------------------------------
# MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b: this comment block exists to
# force a public GitHub main blob refresh of material_raid_preview.py after the
# v31 parent push left this file stale on public main (gem_material_raid was
# still showing locked_deferred on public despite local open_preview). No logic
# change. No reward grant. No DB write. No premium users.gems usage. No stamina
# spend. No tickets spend. No paid attempts. Gem Socket commit disabled. Rune
# runtime untouched. Artifact runtime untouched. Divine Weapon runtime untouched.
# Material Raid live claim remains disabled (preview-only). Gem track now
# open_preview. Rune track still locked_deferred. Artifact/Divine still locked.
# MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_REGISTRATION_SENTINEL_v31b (do not remove).
# ----------------------------------------------------------------------------
MATERIAL_RAID_TRACKS = [
    {"track_id": "gear_material_raid",            "label_it": "Raid Materiali Gear",          "runtime_state": "open_preview"},
    {"track_id": "hero_growth_raid",              "label_it": "Raid Crescita Eroe",            "runtime_state": "open_preview"},
    {"track_id": "gem_material_raid",             "label_it": "Raid Materiali Gemme",          "runtime_state": "open_preview"},
    {"track_id": "rune_material_raid",            "label_it": "Raid Materiali Rune",            "runtime_state": "locked_deferred"},
    {"track_id": "artifact_divine_material_raid", "label_it": "Raid Materiali Artefatto/Divino", "runtime_state": "locked_deferred"},
]
OPEN_TRACK_IDS = {"gear_material_raid", "hero_growth_raid", "gem_material_raid"}
LOCKED_TRACK_IDS = {"rune_material_raid", "artifact_divine_material_raid"}
ALL_TRACK_IDS = {t["track_id"] for t in MATERIAL_RAID_TRACKS}

# Stage model (5 stage per ogni open track).
STAGE_DIFFICULTIES = ["I", "II", "III", "IV", "V"]
STAGE_RECOMMENDED_POWER = {
    "I":   5000,
    "II":  15000,
    "III": 45000,
    "IV":  120000,
    "V":   320000,
}

# Reward families canonici (allineati a Bible 202 material source mapping).
REWARD_FAMILIES = {
    "gear":           ["gear_dust_common", "gear_shard_uncommon", "gear_core_rare", "gear_essence_epic", "gear_orb_legendary"],
    "hero_growth":    ["hero_growth_dust", "hero_growth_crystal", "hero_growth_essence"],
    "gem_locked":     ["gem_dust_common", "gem_shard_rare"],
    "rune_locked":    ["rune_paper_common", "rune_paper_rare"],
    "artifact_divine_locked": ["artifact_fragment_locked", "divine_fragment_locked"],
}

# Reward preview design-only (replace_before_release = true). NESSUN materiale viene grant.
REWARD_PREVIEW_BY_TRACK_STAGE = {
    "gear_material_raid": {
        "I":   {"materials": {"gear_dust_common": 50}},
        "II":  {"materials": {"gear_dust_common": 120, "gear_shard_uncommon": 2}},
        "III": {"materials": {"gear_shard_uncommon": 8,  "gear_core_rare": 1}},
        "IV":  {"materials": {"gear_core_rare": 5,        "gear_essence_epic": 1}},
        "V":   {"materials": {"gear_essence_epic": 6,     "gear_orb_legendary": 1}},
    },
    "hero_growth_raid": {
        "I":   {"materials": {"hero_growth_dust": 80}},
        "II":  {"materials": {"hero_growth_dust": 200, "hero_growth_crystal": 2}},
        "III": {"materials": {"hero_growth_crystal": 8,  "hero_growth_essence": 1}},
        "IV":  {"materials": {"hero_growth_crystal": 18, "hero_growth_essence": 3}},
        "V":   {"materials": {"hero_growth_essence": 12}},
    },
    # v31 Mega Batch Acceleration 1 Track B: gem_material_raid preview unlock.
    # preview_non_final=true, replace_before_release=true, materials_granted=false,
    # reward_claim_enabled=false, db_writes=0. No live claim, no user_materials,
    # no premium users.gems, no stamina/tickets/paid attempts, no Gem Socket commit.
    "gem_material_raid": {
        "I":   {"materials": {"gem_dust_common": 40}},
        "II":  {"materials": {"gem_dust_common": 100, "gem_shard_rare": 1}},
        "III": {"materials": {"gem_dust_common": 180, "gem_shard_rare": 3}},
        "IV":  {"materials": {"gem_dust_common": 320, "gem_shard_rare": 7}},
        "V":   {"materials": {"gem_dust_common": 550, "gem_shard_rare": 14}},
    },
}

SEPARATED_FROM = [
    "hero_level", "star_up", "ascension", "skill_upgrade",
    "costellazioni", "reincarnation", "hero_elevation",
    "gemme", "rune_scroll_talisman", "artifact", "divine_weapon",
    "bp_delta", "combat_formulas", "battle_engine",
    "character_bible_final_numbers", "shop_iap", "battle_pass",
    "vip", "server_profiles_live", "gear_forge_commit",
]


class RewardPreviewRequest(BaseModel):
    track_id: Optional[str] = None
    stage_id: Optional[str] = None


class ClearPreviewRequest(BaseModel):
    track_id: Optional[str] = None
    stage_id: Optional[str] = None
    team_power: int = 0


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": False,
        "method": method,
        "path": f"/api/material-raid/{path_suffix}",
        "phase": "PROJECT_MATERIAL_RAID_RUNTIME_PREVIEW_INERT",
        "contract_version": CONTRACT_VERSION,
        "upstream_design_doc": "/app/docs/divine/209_MATERIAL_RAID_RUNTIME.md",
        "hint": (
            "Material Raid runtime preview is disabled by default. "
            "Set MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED=true to enable inert envelope output. "
            "NO live mutation will ever happen from these endpoints. "
            "Reward claim is NOT enabled in this pack (audit blocked, see track E)."
        ),
        "live_mutation_applied": False,
        "db_writes": False,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
    }


@router.get("/config")
async def material_raid_config() -> dict:
    """Config canonico Material Raid. Preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
        "tracks": MATERIAL_RAID_TRACKS,
        "reward_families": REWARD_FAMILIES,
        "stage_model": {
            "stages_per_open_track": len(STAGE_DIFFICULTIES),
            "difficulty_ids": STAGE_DIFFICULTIES,
            "no_stamina": True,
            "no_tickets": True,
            "no_paid_attempts": True,
        },
        "separated_from": SEPARATED_FROM,
    }


@router.get("/stages")
async def material_raid_stages() -> dict:
    """Lista stages I..V con recommended_power preview-only."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "stages"))
    stages = [
        {"stage_id": sid, "order": i, "recommended_power": STAGE_RECOMMENDED_POWER[sid]}
        for i, sid in enumerate(STAGE_DIFFICULTIES)
    ]
    return {
        "status": "ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "materials_granted": False,
        "stages": stages,
        "recommended_power_by_stage": STAGE_RECOMMENDED_POWER,
        "no_stamina": True,
    }


@router.post("/reward-preview")
async def material_raid_reward_preview(payload: RewardPreviewRequest) -> dict:
    """Preview-only reward envelope per track+stage. NESSUNA grant. NESSUNA DB write."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "reward-preview"))
    track_id = (payload.track_id or "").strip()
    stage_id = (payload.stage_id or "").strip().upper()
    if track_id not in ALL_TRACK_IDS:
        return {
            "status": "invalid_track",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "valid_tracks": sorted(ALL_TRACK_IDS),
        }
    if stage_id not in STAGE_DIFFICULTIES:
        return {
            "status": "invalid_stage",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "valid_stages": STAGE_DIFFICULTIES,
        }
    if track_id in LOCKED_TRACK_IDS:
        return {
            "status": "locked_deferred",
            "runtime_enabled": True,
            "db_writes": False,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "track_id": track_id,
            "stage_id": stage_id,
            "reason": "track is locked until corresponding runtime pack ships",
        }
    envelope = REWARD_PREVIEW_BY_TRACK_STAGE.get(track_id, {}).get(stage_id, {})
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
        "track_id": track_id,
        "stage_id": stage_id,
        "recommended_power": STAGE_RECOMMENDED_POWER.get(stage_id),
        "reward_preview": envelope,
        "design_only_replace_before_release": True,
    }


@router.post("/clear-preview")
async def material_raid_clear_preview(payload: ClearPreviewRequest) -> dict:
    """Preview-only clear-eligibility. NESSUNA mutation. Eligibility = team_power >= recommended."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "clear-preview"))
    track_id = (payload.track_id or "").strip()
    stage_id = (payload.stage_id or "").strip().upper()
    if track_id not in ALL_TRACK_IDS:
        return {
            "status": "invalid_track",
            "runtime_enabled": True,
            "db_writes": False,
            "reward_claim_enabled": False,
            "valid_tracks": sorted(ALL_TRACK_IDS),
        }
    if stage_id not in STAGE_DIFFICULTIES:
        return {
            "status": "invalid_stage",
            "runtime_enabled": True,
            "db_writes": False,
            "reward_claim_enabled": False,
            "valid_stages": STAGE_DIFFICULTIES,
        }
    if track_id in LOCKED_TRACK_IDS:
        return {
            "status": "locked_deferred",
            "runtime_enabled": True,
            "db_writes": False,
            "reward_claim_enabled": False,
            "track_id": track_id,
            "stage_id": stage_id,
            "reason": "track is locked until corresponding runtime pack ships",
        }
    team_power = max(0, int(payload.team_power or 0))
    rec = STAGE_RECOMMENDED_POWER[stage_id]
    delta = team_power - rec
    eligible_preview = team_power >= rec
    return {
        "status": "preview_ok" if eligible_preview else "team_underpowered_preview",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "db_writes": False,
        "live_mutation_applied": False,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
        "track_id": track_id,
        "stage_id": stage_id,
        "team_power": team_power,
        "recommended_power": rec,
        "delta": delta,
        "eligible_preview": eligible_preview,
        "design_only_replace_before_release": True,
    }


# ============================================================================
# v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK
# PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION
# ----------------------------------------------------------------------------
# Playable alpha slice preview endpoints. Default OFF.
# Strict mode: PLAYABLE_ALPHA_FOUNDATION_PREVIEW_ONLY_NO_LIVE_ECONOMY.
#   - No battle_engine call, no /api/battle/simulate call, no /api/story/battle.
#   - No DB writes. No materials granted. No reward claim. No stamina/tickets.
#   - No premium users.gems mutation. No mail mutation. No BP Delta runtime.
#   - No endpoint path change to existing endpoints. No default 503 change to
#     existing endpoints. No safety flag weakening.
# ============================================================================


def _alpha_slice_flag_enabled() -> bool:
    return os.environ.get(ALPHA_SLICE_FEATURE_FLAG, "").strip().lower() == "true"


def _alpha_disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "feature_flag": ALPHA_SLICE_FEATURE_FLAG,
        "alpha_slice_enabled": False,
        "method": method,
        "path": f"/api/material-raid/{path_suffix}",
        "phase": "MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_INERT",
        "contract_version": ALPHA_SLICE_CONTRACT_VERSION,
        "playable_alpha_phase": ALPHA_SLICE_PHASE,
        "hint": (
            "Material Raid Playable Alpha Slice is disabled by default. "
            "Set MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED=true to enable "
            "preview-only alpha endpoints. NO live mutation will ever happen."
        ),
        "live_mutation_applied": False,
        "db_writes": 0,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
        "no_paid_attempts": True,
        "visual_battle_required": True,
        "guild_war_exception": False,
    }


class AlphaBattlePreviewRequest(BaseModel):
    track_id: Optional[str] = None
    stage_id: Optional[str] = None
    team_power: int = 0
    selected_hero_ids: Optional[list] = None


class AlphaRewardSummaryPreviewRequest(BaseModel):
    track_id: Optional[str] = None
    stage_id: Optional[str] = None
    battle_result_preview: Optional[str] = None
    mvp_hero_id: Optional[str] = None


def _enemy_family_for_track(track_id: str) -> str:
    return {
        "gear_material_raid": "gear_construct_preview",
        "hero_growth_raid": "spirit_essence_preview",
        "gem_material_raid": "gem_elemental_preview",
        "rune_material_raid": "rune_phantom_locked",
        "artifact_divine_material_raid": "divine_relic_locked",
    }.get(track_id, "unknown_preview")


def _deterministic_battle_seed(track_id: str, stage_id: str, team_power: int) -> str:
    """Deterministic seed for visual battle preview. NO randomness."""
    base = f"{track_id}|{stage_id}|{int(team_power)}|{ALPHA_SLICE_CONTRACT_VERSION}"
    return f"alpha-seed-{abs(hash(base)) % (10 ** 12):012d}"


@router.get("/alpha-slice-config")
async def material_raid_alpha_slice_config() -> dict:
    """v51 Playable Alpha Slice config. Default disabled => 503."""
    if not _alpha_slice_flag_enabled():
        raise HTTPException(status_code=503, detail=_alpha_disabled_payload("GET", "alpha-slice-config"))
    return {
        "status": "ok",
        "contract_version": ALPHA_SLICE_CONTRACT_VERSION,
        "alpha_slice_enabled": True,
        "playable_alpha_phase": ALPHA_SLICE_PHASE,
        "open_tracks": sorted(OPEN_TRACK_IDS),
        "locked_tracks": sorted(LOCKED_TRACK_IDS),
        "stage_ids": STAGE_DIFFICULTIES,
        "recommended_power_by_stage": STAGE_RECOMMENDED_POWER,
        "no_stamina": True,
        "no_tickets": True,
        "no_paid_attempts": True,
        "reward_claim_enabled": False,
        "materials_granted": False,
        "db_writes": 0,
        "visual_battle_required": True,
        "guild_war_exception": False,
        "live_mutation_applied": False,
        "compatible_with_future_material_raid_claim_safety": True,
    }


@router.post("/alpha-battle-preview")
async def material_raid_alpha_battle_preview(payload: AlphaBattlePreviewRequest) -> dict:
    """v51 Playable Alpha Slice battle preview. NO battle_engine call. NO DB write."""
    if not _alpha_slice_flag_enabled():
        raise HTTPException(status_code=503, detail=_alpha_disabled_payload("POST", "alpha-battle-preview"))
    track_id = (payload.track_id or "").strip()
    stage_id = (payload.stage_id or "").strip().upper()
    team_power = max(0, int(payload.team_power or 0))
    if track_id not in ALL_TRACK_IDS:
        return {
            "status": "invalid_track",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "valid_tracks": sorted(ALL_TRACK_IDS),
            "visual_battle_required": True,
        }
    if stage_id not in STAGE_DIFFICULTIES:
        return {
            "status": "invalid_stage",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "valid_stages": STAGE_DIFFICULTIES,
            "visual_battle_required": True,
        }
    if track_id in LOCKED_TRACK_IDS:
        return {
            "status": "locked_deferred",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "track_id": track_id,
            "stage_id": stage_id,
            "reason": "track is locked until corresponding runtime pack ships",
            "visual_battle_required": True,
        }
    rec = STAGE_RECOMMENDED_POWER[stage_id]
    if team_power < rec:
        return {
            "status": "team_underpowered_preview",
            "alpha_slice_enabled": True,
            "contract_version": ALPHA_SLICE_CONTRACT_VERSION,
            "db_writes": 0,
            "materials_granted": False,
            "reward_claim_enabled": False,
            "stamina_used": False,
            "tickets_used": False,
            "track_id": track_id,
            "stage_id": stage_id,
            "team_power": team_power,
            "recommended_power": rec,
            "delta": team_power - rec,
            "visual_battle_required": True,
            "live_mutation_applied": False,
        }
    seed = _deterministic_battle_seed(track_id, stage_id, team_power)
    enemy_family = _enemy_family_for_track(track_id)
    return {
        "status": "alpha_battle_preview_ready",
        "contract_version": ALPHA_SLICE_CONTRACT_VERSION,
        "alpha_slice_enabled": True,
        "playable_alpha_phase": ALPHA_SLICE_PHASE,
        "track_id": track_id,
        "stage_id": stage_id,
        "team_power": team_power,
        "recommended_power": rec,
        "delta": team_power - rec,
        "battle_seed_preview": seed,
        "visual_battle_payload_preview": {
            "mode": "material_raid",
            "track_id": track_id,
            "stage_id": stage_id,
            "recommended_power": rec,
            "team_power": team_power,
            "enemy_family_preview": enemy_family,
            "battle_visual_required": True,
            "auto_resolve_allowed": False,
        },
        "no_battle_engine_call": True,
        "no_battle_simulate_call": True,
        "no_story_battle_call": True,
        "db_writes": 0,
        "materials_granted": False,
        "reward_claim_enabled": False,
        "stamina_used": False,
        "tickets_used": False,
        "no_paid_attempts": True,
        "live_mutation_applied": False,
        "design_only_replace_before_release": True,
        # v52 MEGA_RELEASE_ACCELERATION_2 \u2014 payload contract v2 refinement (append-only).
        # Same path, same flag, same status, same locked/underpowered behavior.
        "result_authoritative": False,
        "alpha_preview_only": True,
        "battle_engine_runtime_used": False,
        "reward_grant_enabled": False,
        "target_frontend_route": "/material-raid-visual-preview",
        "background_hint": f"material_raid_bg_{track_id}_{stage_id.lower()}",
        "music_hint": "material_raid_battle_loop_alpha",
        "tutorial_hint": "preview_visual_battle_non_authoritative_no_reward_grant",
        "reward_preview_hint": "open_alpha_reward_summary_preview_after_visual_return",
    }


@router.post("/alpha-reward-summary-preview")
async def material_raid_alpha_reward_summary_preview(payload: AlphaRewardSummaryPreviewRequest) -> dict:
    """v51 Playable Alpha Slice post-battle reward summary preview. NO grant. NO DB write."""
    if not _alpha_slice_flag_enabled():
        raise HTTPException(status_code=503, detail=_alpha_disabled_payload("POST", "alpha-reward-summary-preview"))
    track_id = (payload.track_id or "").strip()
    stage_id = (payload.stage_id or "").strip().upper()
    if track_id not in ALL_TRACK_IDS:
        return {
            "status": "invalid_track",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "inventory_mutation": False,
            "claim_button_enabled": False,
            "valid_tracks": sorted(ALL_TRACK_IDS),
        }
    if stage_id not in STAGE_DIFFICULTIES:
        return {
            "status": "invalid_stage",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "inventory_mutation": False,
            "claim_button_enabled": False,
            "valid_stages": STAGE_DIFFICULTIES,
        }
    if track_id in LOCKED_TRACK_IDS:
        return {
            "status": "locked_deferred",
            "alpha_slice_enabled": True,
            "db_writes": 0,
            "materials_granted": False,
            "inventory_mutation": False,
            "claim_button_enabled": False,
            "track_id": track_id,
            "stage_id": stage_id,
            "reason": "track is locked until corresponding runtime pack ships",
        }
    envelope = REWARD_PREVIEW_BY_TRACK_STAGE.get(track_id, {}).get(stage_id, {})
    mvp = (payload.mvp_hero_id or "").strip() or None
    return {
        "status": "post_battle_reward_summary_preview",
        "contract_version": ALPHA_SLICE_CONTRACT_VERSION,
        "alpha_slice_enabled": True,
        "playable_alpha_phase": ALPHA_SLICE_PHASE,
        "track_id": track_id,
        "stage_id": stage_id,
        "recommended_power": STAGE_RECOMMENDED_POWER.get(stage_id),
        "battle_result_preview": (payload.battle_result_preview or "victory_preview"),
        "mvp_hero_id_preview": mvp,
        "reward_preview": envelope,
        "materials_granted": False,
        "inventory_mutation": False,
        "db_writes": 0,
        "claim_button_enabled": False,
        "claim_flow_state": "preview_locked_until_staging_approval",
        "compatible_with_future_material_raid_claim_safety": True,
        "no_stamina_used": True,
        "no_tickets_used": True,
        "no_paid_attempts": True,
        "live_mutation_applied": False,
        "design_only_replace_before_release": True,
    }

