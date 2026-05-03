"""
Divine Waifus - Synergy Routes
Team synergy endpoints for checking and displaying active synergies.

V1 endpoints (legacy, name-based):
    GET /api/synergies/guide
    GET /api/synergies/team

V2 endpoints (RM1.23-B, ID-based, read-only):
    GET /api/synergies/team_v2
    GET /api/synergies/v2/all       (lista enabled per UI guide)

V1 e V2 coesistono. V2 NON modifica V1.
"""
from fastapi import Depends
from synergy_system import calculate_team_synergies, get_all_synergy_definitions
from data.synergy_definitions_v2 import (
    get_enabled_team_synergies_v2,
)
from data.character_bible import CHARACTER_BIBLE_BY_ID as _BIBLE_BY_ID
from utils.team_synergy_v2_calculator import compute_team_synergies_v2


def register_synergy_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/synergies/guide")
    async def get_synergy_guide():
        """Get all synergy definitions for the guide/encyclopedia."""
        return get_all_synergy_definitions()

    @router.get("/synergies/team")
    async def get_team_synergies(current_user: dict = Depends(get_current_user)):
        """Get active synergies for the current team."""
        uid = current_user["id"]
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        if not team or not team.get("formation"):
            return {"active_synergies": [], "total_buffs": {}, "synergy_count": 0}

        names, elements, classes = [], [], []
        for pos in team.get("formation", []):
            uhid = pos.get("user_hero_id")
            if not uhid:
                continue
            uh = await db.user_heroes.find_one({"id": uhid, "user_id": uid})
            if not uh:
                continue
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            if hero:
                names.append(hero.get("name", ""))
                elements.append(hero.get("element", "neutral"))
                classes.append(hero.get("hero_class", "DPS"))
            else:
                names.append(uh.get("hero_name", ""))
                elements.append(uh.get("hero_element", "neutral"))
                classes.append(uh.get("hero_class", "DPS"))

        result = calculate_team_synergies(names, elements, classes)
        return result

    # ── RM1.23-B V2 endpoints (READ-ONLY, ID-based) ────────────────────
    @router.get("/synergies/team_v2")
    async def get_team_synergies_v2(current_user: dict = Depends(get_current_user)):
        """Get active V2 ID-based team synergies for the current team.

        Read-only. Nessuna mutazione DB. Coesiste con /api/synergies/team
        (V1). Per legacy team senza canonical IDs, ritorna safely empty.
        """
        uid = current_user["id"]
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        if not team or not team.get("formation"):
            return {
                "active_team_synergies_v2": [],
                "near_complete": [],
                "aggregated_buffs": {},
                "members_resolved": 0,
                "members_skipped_legacy_or_orphan": 0,
                "team_id": None,
            }

        # Resolve only the user_heroes referenced by this active team
        # (efficient: avoid loading all 1700+ user_heroes).
        slot_uhids = [
            pos.get("user_hero_id")
            for pos in team.get("formation", [])
            if pos.get("user_hero_id")
        ]
        user_heroes_list = await db.user_heroes.find(
            {"id": {"$in": slot_uhids}, "user_id": uid}
        ).to_list(None)
        user_heroes_by_id = {uh["id"]: uh for uh in user_heroes_list}

        # Resolve the heroes referenced (full collection for UI metadata)
        hero_ids = list({uh.get("hero_id") for uh in user_heroes_list if uh.get("hero_id")})
        heroes_list = await db.heroes.find(
            {"id": {"$in": hero_ids}}, {"image_base64": 0}
        ).to_list(None)
        heroes_by_id = {h["id"]: h for h in heroes_list}

        bible_ids = set(_BIBLE_BY_ID.keys())
        enabled = get_enabled_team_synergies_v2()

        result = compute_team_synergies_v2(
            team_doc=team,
            user_heroes_by_id=user_heroes_by_id,
            heroes_by_id=heroes_by_id,
            enabled_synergies=enabled,
            bible_ids=bible_ids,
        )
        result["team_id"] = team.get("id")
        result["enabled_synergy_count"] = len(enabled)
        return result

    @router.get("/synergies/v2/all")
    async def get_all_v2_definitions():
        """Public read-only list of enabled V2 synergies for UI guide."""
        enabled = get_enabled_team_synergies_v2()
        return {
            "version": 2,
            "team_synergies": [
                {
                    "id": s["id"],
                    "display_name": s.get("display_name") or s["id"],
                    "description": s.get("description"),
                    "lore_group": s.get("lore_group"),
                    "icon": s.get("icon"),
                    "rarity_tier": s.get("rarity_tier"),
                    "release_group": s.get("release_group"),
                    "required_hero_ids": s.get("required_hero_ids", []),
                    "min_required": s.get("min_required"),
                    "max_members": s.get("max_members"),
                    "effects": s.get("effects", []),
                    "target_filter": s.get("target_filter"),
                }
                for s in enabled
            ],
            "count": len(enabled),
        }

    # ── RM1.23-C: Synergy Codex enrichment (READ-ONLY) ───────────────────
    @router.get("/synergies/codex")
    async def get_synergy_codex(current_user: dict = Depends(get_current_user)):
        """Codex view: 10 V2 synergies enriched with player ownership/team status.

        Statuses per synergy:
          - active           → tutti required heroes nel team attivo
          - available_not_in_team → tutti required posseduti, non tutti in team
          - near_complete    → almeno 1/required posseduti, completion >= 0.5
          - not_owned        → 0 required posseduti
        """
        uid = current_user["id"]
        # Posseduti (set canonical IDs)
        owned_uh = await db.user_heroes.find(
            {"user_id": uid}, {"hero_id": 1, "stars": 1, "level": 1, "_id": 0}
        ).to_list(None)
        owned_hero_ids = list({uh.get("hero_id") for uh in owned_uh if uh.get("hero_id")})
        owned_heroes = await db.heroes.find(
            {"id": {"$in": owned_hero_ids}}, {"image_base64": 0}
        ).to_list(None)
        # Map ownership → canonical id (only canonical-resolvable, skip legacy)
        owned_canonical: dict = {}  # canonical_id → list of {stars, level, ...}
        for h in owned_heroes:
            if h.get("is_legacy_placeholder") is True:
                continue
            canonical = h.get("canonical_id")
            if not canonical and h.get("id") in _BIBLE_BY_ID:
                canonical = h["id"]
            if not canonical or canonical not in _BIBLE_BY_ID:
                continue
            for uh in owned_uh:
                if uh.get("hero_id") == h["id"]:
                    owned_canonical.setdefault(canonical, []).append({
                        "stars": int(uh.get("stars") or 1),
                        "level": int(uh.get("level") or 1),
                    })

        # Team attivo (set canonical IDs in formation)
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        in_team_canonical: set = set()
        if team and team.get("formation"):
            slot_uhids = [p.get("user_hero_id") for p in team["formation"] if p.get("user_hero_id")]
            team_uhs = await db.user_heroes.find(
                {"id": {"$in": slot_uhids}, "user_id": uid}
            ).to_list(None)
            team_h_ids = list({uh.get("hero_id") for uh in team_uhs if uh.get("hero_id")})
            team_h_docs = await db.heroes.find(
                {"id": {"$in": team_h_ids}}, {"image_base64": 0}
            ).to_list(None)
            for h in team_h_docs:
                if h.get("is_legacy_placeholder") is True:
                    continue
                cc = h.get("canonical_id")
                if not cc and h.get("id") in _BIBLE_BY_ID:
                    cc = h["id"]
                if cc and cc in _BIBLE_BY_ID:
                    in_team_canonical.add(cc)

        owned_canonical_ids = set(owned_canonical.keys())
        enabled = get_enabled_team_synergies_v2()

        # ── RM1.23-C2: micro-enrichment read-only per Hero Mini-Cards ─────
        # Raccogliamo TUTTI i canonical_ids richiesti dalle 10 sinergie attive
        # e mappiamo in un'unica query → image_url + hero doc id.
        all_required_canonicals: set = set()
        for syn in enabled:
            for cid in (syn.get("required_hero_ids") or []):
                all_required_canonicals.add(cid)
        # Match per canonical_id O per id (fallback legacy es. 'borea')
        canonical_list = list(all_required_canonicals)
        hero_docs_for_required = await db.heroes.find(
            {"$or": [
                {"canonical_id": {"$in": canonical_list}},
                {"id": {"$in": canonical_list}},
            ]},
            {"image_base64": 0, "sprite_sheet_base64": 0},
        ).to_list(None)
        # canonical_id → hero doc (preferiamo doc canonical, escludiamo legacy)
        canonical_to_hero_doc: dict = {}
        for hd in hero_docs_for_required:
            if hd.get("is_legacy_placeholder") is True:
                continue
            cc = hd.get("canonical_id") or (hd.get("id") if hd.get("id") in _BIBLE_BY_ID else None)
            if cc and cc in all_required_canonicals and cc not in canonical_to_hero_doc:
                canonical_to_hero_doc[cc] = hd

        out = []
        for syn in enabled:
            req = list(syn.get("required_hero_ids") or [])
            req_set = set(req)
            min_req = int(syn.get("min_required") or len(req_set) or 1)

            owned_match = req_set & owned_canonical_ids
            in_team_match = req_set & in_team_canonical
            completion_owned = len(owned_match) / max(1, len(req_set))
            completion_team = len(in_team_match) / max(1, len(req_set))

            if len(in_team_match) >= min_req:
                status = "active"
            elif len(owned_match) >= min_req:
                status = "available_not_in_team"
            elif completion_owned >= 0.5 and len(owned_match) >= 1:
                status = "near_complete"
            else:
                status = "not_owned"

            # Avg stars among owned matches (for star-scaling preview)
            star_samples = []
            for cid in owned_match:
                copies = owned_canonical.get(cid, [])
                if copies:
                    # Use the highest-star copy
                    star_samples.append(max(c["stars"] for c in copies))
            avg_stars = round(sum(star_samples) / len(star_samples), 2) if star_samples else 0.0

            # Members detail
            members = []
            for cid in req:
                copies = owned_canonical.get(cid, [])
                best_stars = max((c["stars"] for c in copies), default=0)
                bible_entry = _BIBLE_BY_ID.get(cid) or {}
                hero_doc = canonical_to_hero_doc.get(cid) or {}
                # RM1.23-C2: enrich with hero_id + image_url + rarity + element + faction
                # for graphical Hero Mini-Cards (read-only).
                members.append({
                    "canonical_id": cid,
                    "display_name": (bible_entry.get("display_name")
                                     or bible_entry.get("name") or cid),
                    "owned": cid in owned_canonical_ids,
                    "in_team": cid in in_team_canonical,
                    "best_stars": best_stars,
                    "max_stars": int(bible_entry.get("max_stars") or 5),
                    # Mini-card visual fields:
                    "hero_id": hero_doc.get("id") or cid,
                    "image_url": hero_doc.get("image_url"),
                    "rarity": int(hero_doc.get("rarity") or bible_entry.get("native_rarity") or 1),
                    "element": hero_doc.get("element") or bible_entry.get("element"),
                    "faction": hero_doc.get("faction") or bible_entry.get("faction"),
                    "asset_status": hero_doc.get("asset_status"),
                })

            out.append({
                "id": syn["id"],
                "display_name": syn.get("display_name") or syn["id"],
                "description": syn.get("description"),
                "lore_group": syn.get("lore_group"),
                "icon": syn.get("icon"),
                "rarity_tier": syn.get("rarity_tier"),
                "release_group": syn.get("release_group"),
                "required_hero_ids": req,
                "min_required": min_req,
                "max_members": int(syn.get("max_members") or len(req_set)),
                "effects": syn.get("effects", []),
                "target_filter": syn.get("target_filter"),
                "status": status,
                "owned_count": len(owned_match),
                "in_team_count": len(in_team_match),
                "required_count": len(req_set),
                "completion_owned": round(completion_owned, 3),
                "completion_team": round(completion_team, 3),
                "avg_owned_stars": avg_stars,
                "members": members,
            })

        # Counts per status
        status_counts: dict = {}
        for s in out:
            status_counts[s["status"]] = status_counts.get(s["status"], 0) + 1

        return {
            "version": 2,
            "team_synergies": out,
            "count": len(out),
            "status_counts": status_counts,
            "team_id": team.get("id") if team else None,
        }

    @router.get("/synergies/by_hero/{hero_id}")
    async def get_synergies_for_hero(
        hero_id: str,
        current_user: dict = Depends(get_current_user),
    ):
        """Hero Detail palette: tabbed in_team / active / inactive view."""
        codex = await get_synergy_codex(current_user=current_user)  # reuse
        per_hero = [s for s in codex["team_synergies"] if hero_id in s["required_hero_ids"]]
        # "active" tab = synergy attualmente attiva (status=active)
        active = [s for s in per_hero if s["status"] == "active"]
        # "inactive" = quelle non attive (può includere available/near/not_owned)
        inactive = [s for s in per_hero if s["status"] != "active"]
        # "in_team" = quelle dove l'eroe target è in active team
        in_team_only = [s for s in per_hero if hero_id in {m["canonical_id"] for m in s["members"] if m["in_team"]}]
        return {
            "hero_id": hero_id,
            "involved_in_total": len(per_hero),
            "tabs": {
                "in_team": in_team_only,
                "active": active,
                "inactive": inactive,
            },
        }
