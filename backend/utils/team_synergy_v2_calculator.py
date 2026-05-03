"""
RM1.23-B — Team Synergy V2 Calculator (PURE, READ-ONLY)
═══════════════════════════════════════════════════════════════════════════
Calcolatore puro per Team Synergies V2 ID-based. Nessuna scrittura DB,
nessun side effect. Usato da:
  • GET /api/synergies/team_v2
  • battle_engine.py (gated da SYNERGY_V2_BATTLE_ENABLED env-var)

Resolution chain:
    team.formation[i].user_hero_id
        → user_heroes (.hero_id)
            → heroes (.id, .canonical_id)

Solo membri con `canonical_id` risolvibile in Character Bible contano per
V2 (i legacy UUID heroes vengono naturalmente skipped).

Coesistenza con V1 sinergy_system: questo modulo NON tocca V1, NON sostituisce
calculate_team_synergies. Lavora additivamente.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple


def _resolve_team_members(
    team_doc: Dict[str, Any],
    user_heroes_by_id: Dict[str, Dict[str, Any]],
    heroes_by_id: Dict[str, Dict[str, Any]],
    bible_ids: set,
) -> List[Dict[str, Any]]:
    """Resolve formation slots → list of canonical members.

    Returns members with: canonical_id, stars, role, element, faction, slot_idx.
    Skips legacy/orphan/missing slots silently.
    """
    members: List[Dict[str, Any]] = []
    formation = team_doc.get("formation") or []
    for idx, slot in enumerate(formation):
        if not isinstance(slot, dict):
            continue
        uhid = slot.get("user_hero_id")
        if not uhid:
            continue
        uh = user_heroes_by_id.get(uhid)
        if not uh:
            continue
        h_id = uh.get("hero_id")
        h = heroes_by_id.get(h_id) if h_id else None
        if not h:
            continue
        # Resolve canonical_id: prefer field, fallback to .id if it itself
        # is a Bible slug (e.g. greek_hoplite, norse_berserker).
        canonical = h.get("canonical_id")
        if not canonical and h.get("id") in bible_ids:
            canonical = h["id"]
        if not canonical or canonical not in bible_ids:
            # Legacy UUID-based heroes are skipped from V2.
            continue
        # Skip legacy placeholders even if canonical_id is set (defense-
        # in-depth: legacy borea has canonical_id="greek_borea" but should
        # never participate in V2 synergies).
        if h.get("is_legacy_placeholder") is True:
            continue
        max_stars = int(h.get("max_stars") or 5)
        raw_stars = int(uh.get("stars") or 1)
        stars = max(1, min(raw_stars, max_stars))
        members.append({
            "canonical_id": canonical,
            "stars": stars,
            "max_stars": max_stars,
            "role": h.get("canonical_role") or h.get("hero_class") or "unknown",
            "element": h.get("canonical_element") or h.get("element") or "neutral",
            "faction": h.get("canonical_faction") or h.get("faction") or "unknown",
            "slot_idx": idx,
            "user_hero_id": uhid,
            "level": int(uh.get("level") or 1),
        })
    return members


def _matches_target_filter(member: Dict[str, Any], tf: Optional[Dict[str, Any]]) -> bool:
    """Apply optional target_filter (faction/role/element)."""
    if not tf:
        return True
    if "faction" in tf and member.get("faction") != tf["faction"]:
        return False
    if "role" in tf and member.get("role") != tf["role"]:
        return False
    if "element" in tf and member.get("element") != tf["element"]:
        return False
    return True


def _compute_buffs_for_synergy(
    syn_def: Dict[str, Any],
    matched_members: List[Dict[str, Any]],
    all_team_members: List[Dict[str, Any]],
) -> Tuple[Dict[str, float], List[str]]:
    """Compute (buffs_dict, affected_member_canonical_ids) for one synergy."""
    matched_count = len(matched_members)
    if matched_count < int(syn_def.get("min_required") or 1):
        return {}, []

    # Tier selection: tier_by_member_count fallback or pick highest applicable
    tiers = syn_def.get("tier_by_member_count") or {}
    base_buffs: Dict[str, float] = {}
    if tiers:
        applicable_keys = [int(k) for k in tiers.keys() if int(k) <= matched_count]
        if applicable_keys:
            picked = max(applicable_keys)
            t = tiers[picked] if picked in tiers else tiers[str(picked)]
            base_buffs = dict(t)

    # Star scaling
    star_cfg = syn_def.get("star_scaling") or {}
    per_avg = float(star_cfg.get("per_avg_star") or 0.0)
    min_avg = float(star_cfg.get("min_avg_stars_to_activate") or 1)
    avg_stars = (
        sum(m["stars"] for m in matched_members) / matched_count
        if matched_count > 0 else 0.0
    )
    star_multiplier = 1.0
    if per_avg > 0 and avg_stars >= min_avg:
        star_multiplier = 1.0 + per_avg * max(0.0, avg_stars - 1.0)

    # Effects (V2 schema): re-derive buffs from effects[] when present
    # (more expressive than tier_by_member_count). Effects override tier
    # buffs when both are present.
    effects = syn_def.get("effects")
    target_filter = syn_def.get("target_filter")
    affected_ids: set = set()

    if effects:
        derived: Dict[str, float] = {}
        for eff in effects:
            stat = eff.get("stat")
            mode = eff.get("mode", "percent")
            val = float(eff.get("value") or 0.0)
            tgt = eff.get("target", "synergy_members")
            if not stat:
                continue
            # Compute affected members for this effect
            if tgt == "synergy_members":
                affected = matched_members
            elif tgt == "all_allies":
                affected = all_team_members
            elif tgt == "faction_match":
                affected = [m for m in all_team_members if _matches_target_filter(m, target_filter)]
            elif tgt == "role_match":
                affected = [m for m in all_team_members if _matches_target_filter(m, target_filter)]
            elif tgt == "element_match":
                affected = [m for m in all_team_members if _matches_target_filter(m, target_filter)]
            else:
                affected = matched_members
            for m in affected:
                affected_ids.add(m["canonical_id"])
            if mode == "percent":
                derived[stat] = derived.get(stat, 0.0) + val
            elif mode == "flat":
                # Flat values are passed-through (battle apply must
                # know how to handle flat vs percent).
                derived[f"{stat}__flat"] = derived.get(f"{stat}__flat", 0.0) + val
        base_buffs = derived

    # Apply star scaling
    final = {k: round(v * star_multiplier, 6) for k, v in base_buffs.items()}
    return final, sorted(affected_ids)


def compute_team_synergies_v2(
    team_doc: Optional[Dict[str, Any]],
    user_heroes_by_id: Dict[str, Dict[str, Any]],
    heroes_by_id: Dict[str, Dict[str, Any]],
    enabled_synergies: List[Dict[str, Any]],
    bible_ids: set,
    near_complete_threshold: float = 0.5,
) -> Dict[str, Any]:
    """Compute Team Synergies V2 active for a given team.

    Args:
        team_doc: db.teams document (active team) or None → empty result.
        user_heroes_by_id: user_heroes documents indexed by id (user-scoped).
        heroes_by_id: heroes documents indexed by id (full).
        enabled_synergies: list from get_enabled_team_synergies_v2().
        bible_ids: set of CHARACTER_BIBLE_BY_ID keys.
        near_complete_threshold: report syngs with completion >= this fraction
            but < min_required (UI hint).

    Returns dict with:
        active_team_synergies_v2: list of activated synergy results
        near_complete: list of close-to-active synergies for UI hints
        aggregated_buffs: combined dict[stat, float] across all active
        members_resolved: count of resolved canonical members in team
        members_skipped_legacy_or_orphan: count
    """
    result = {
        "active_team_synergies_v2": [],
        "near_complete": [],
        "aggregated_buffs": {},
        "members_resolved": 0,
        "members_skipped_legacy_or_orphan": 0,
    }

    if not team_doc:
        return result

    members = _resolve_team_members(team_doc, user_heroes_by_id, heroes_by_id, bible_ids)
    formation_count = len(team_doc.get("formation") or [])
    result["members_resolved"] = len(members)
    result["members_skipped_legacy_or_orphan"] = max(0, formation_count - len(members))

    if not members:
        return result

    # Active canonical id set (dedup per duplicate_policy=unique_canonical_id)
    canonical_set = {m["canonical_id"] for m in members}
    members_by_canon = {}
    for m in members:
        if m["canonical_id"] not in members_by_canon:
            members_by_canon[m["canonical_id"]] = m

    aggregated: Dict[str, float] = {}
    for syn in enabled_synergies:
        required = syn.get("required_hero_ids") or []
        required_set = set(required)
        matched_canon = canonical_set & required_set
        matched_members = [members_by_canon[c] for c in matched_canon]
        completion = (
            len(matched_canon) / len(required_set) if required_set else 0.0
        )
        min_required = int(syn.get("min_required") or len(required_set) or 1)
        if len(matched_canon) >= min_required:
            buffs, affected_ids = _compute_buffs_for_synergy(
                syn, matched_members, members
            )
            entry = {
                "id": syn["id"],
                "version": syn.get("version", 2),
                "display_name": syn.get("display_name") or syn["id"],
                "description": syn.get("description"),
                "lore_group": syn.get("lore_group"),
                "icon": syn.get("icon"),
                "rarity_tier": syn.get("rarity_tier"),
                "matched_hero_ids": sorted(matched_canon),
                "matched_count": len(matched_canon),
                "required_count": len(required_set),
                "completion": round(completion, 3),
                "buffs": buffs,
                "affected_member_ids": affected_ids,
                "avg_member_stars": round(
                    sum(m["stars"] for m in matched_members) / len(matched_members), 2
                ),
            }
            result["active_team_synergies_v2"].append(entry)
            for stat, val in buffs.items():
                aggregated[stat] = aggregated.get(stat, 0.0) + val
        elif (
            len(matched_canon) >= 1
            and completion >= near_complete_threshold
            and len(matched_canon) < min_required
        ):
            result["near_complete"].append({
                "id": syn["id"],
                "display_name": syn.get("display_name") or syn["id"],
                "missing_hero_ids": sorted(required_set - matched_canon),
                "matched_hero_ids": sorted(matched_canon),
                "matched_count": len(matched_canon),
                "required_count": len(required_set),
                "completion": round(completion, 3),
            })

    # Apply per-stat caps (anti-overflow) — modest defaults; tunable.
    STAT_CAPS = {
        "attack": 0.50, "hp": 0.50, "defense": 0.50,
        "speed": 0.40, "magic_damage": 0.50, "magic_defense": 0.40,
        "healing_power": 0.50, "crit_rate": 0.40, "crit_damage": 0.60,
        "penetration": 0.40, "lifesteal": 0.30, "ultimate_charge": 0.40,
        "dodge": 0.30, "effect_accuracy": 0.40, "damage_reduction": 0.30,
    }
    capped: Dict[str, float] = {}
    for stat, val in aggregated.items():
        # leave __flat keys untouched
        if stat.endswith("__flat"):
            capped[stat] = val
            continue
        cap = STAT_CAPS.get(stat, 1.0)
        capped[stat] = round(min(val, cap), 6)
    result["aggregated_buffs"] = capped
    return result


__all__ = ["compute_team_synergies_v2"]
