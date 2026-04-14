"""
Divine Waifus - Battle Routes
Team formation and battle simulation endpoints
"""
import uuid
import random
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from battle_core import (
    simulate_battle, prepare_battle_character, generate_enemy_team,
    calculate_adjacency_bonus, ELEMENT_SKILLS, PASSIVE_SKILLS,
    POSITION_BUFFS, FORMATION_PATTERNS,
)
from synergy_system import calculate_team_synergies, get_all_synergy_definitions, get_element_multiplier


def register_battle_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== SYNERGY ENDPOINTS ====================
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

    @router.get("/battle/skills")
    async def get_skill_info():
        """Get all skill definitions"""
        return {
            "element_skills": ELEMENT_SKILLS,
            "passive_skills": PASSIVE_SKILLS,
            "position_buffs": {k: {"name": v["name"], "desc": v["desc"], "buff": v["buff"]} for k, v in POSITION_BUFFS.items()},
            "formation_patterns": {k: {"name": v["name"], "description": v["description"], "buff": v["buff"]} for k, v in FORMATION_PATTERNS.items()},
        }

    @router.post("/battle/simulate")
    async def simulate_battle_endpoint(current_user: dict = Depends(get_current_user)):
        """Simulate a battle with the user's active team"""
        user_id = current_user['id']
        team = await db.teams.find_one({"user_id": user_id, "is_active": True})
        if not team or not team.get('formation'):
            raise HTTPException(status_code=400, detail="Configura un team prima!")
        player_team = []
        for pos in team['formation']:
            if not pos.get('user_hero_id'):
                continue
            user_hero = await db.user_heroes.find_one({"id": pos['user_hero_id'], "user_id": user_id})
            if not user_hero:
                continue
            hero = await db.heroes.find_one({"id": user_hero['hero_id']})
            if not hero:
                continue
            char = prepare_battle_character(hero, user_hero, pos)
            player_team.append(char)
        if len(player_team) == 0:
            raise HTTPException(status_code=400, detail="Nessun eroe nel team!")
        positions = [{"x": p.get('x', 0), "y": p.get('y', 0)} for p in team['formation'] if p.get('user_hero_id')]
        active_formations = []
        for pat_id, pat in FORMATION_PATTERNS.items():
            try:
                if pat['check'](positions):
                    active_formations.append({"id": pat_id, "name": pat['name'], "buff": pat['buff']})
                    for char in player_team:
                        for stat, val in pat['buff'].items():
                            if stat in char:
                                char[stat] = int(char[stat] * (1 + val))
            except Exception:
                pass
        adj_result = calculate_adjacency_bonus(positions)
        for char in player_team:
            for stat, val in adj_result['bonus'].items():
                if stat in char and val > 0:
                    char[stat] = int(char[stat] * (1 + val))

        # === SYNERGY BONUSES (applied automatically) ===
        team_names = [c.get("name", "") for c in player_team]
        team_elements = [c.get("element", "neutral") for c in player_team]
        team_classes = [c.get("hero_class", "DPS") for c in player_team]
        synergy_result = calculate_team_synergies(team_names, team_elements, team_classes)
        synergy_buffs = synergy_result.get("total_buffs", {})
        # Apply synergy buffs to all team members
        for char in player_team:
            for stat, val in synergy_buffs.items():
                if stat in char:
                    if isinstance(char[stat], int):
                        char[stat] = int(char[stat] * (1 + val))
                    elif isinstance(char[stat], float):
                        char[stat] = round(char[stat] + val, 4)

        team_power = sum(c['attack'] + c['hp'] // 10 + c['defense'] for c in player_team)
        enemy_team = generate_enemy_team(int(team_power * 0.15), count=min(len(player_team), 6))
        result = simulate_battle(player_team, enemy_team)
        result['active_formations'] = active_formations
        result['adjacency_pairs'] = adj_result['adjacent_pairs']
        result['active_synergies'] = synergy_result.get('active_synergies', [])
        result['synergy_buffs'] = synergy_buffs
        if result['victory']:
            gold_reward = int(team_power * 0.5)
            exp_reward = int(team_power * 0.2)
            hero_exp = int(team_power * 0.15)
            
            # Give EXP + gold to account
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"gold": gold_reward, "experience": exp_reward}}
            )
            
            # Give EXP to each participating hero
            hero_levelups = []
            for uh in user_heroes:
                uh_id = uh.get('id') or str(uh.get('_id', ''))
                old_level = uh.get('level', 1)
                old_exp = uh.get('exp', 0)
                new_exp = old_exp + hero_exp
                
                # Calculate level ups
                new_level = old_level
                level_cap = uh.get('level_cap', 100)
                while new_level < level_cap:
                    needed = new_level * 100 + 50
                    if new_exp >= needed:
                        new_exp -= needed
                        new_level += 1
                    else:
                        break
                
                await db.user_heroes.update_one(
                    {"id": uh_id, "user_id": user_id},
                    {"$set": {"level": new_level, "exp": new_exp}}
                )
                
                hero_name = uh.get('hero_name', '?')
                if new_level > old_level:
                    hero_levelups.append({
                        "hero_name": hero_name,
                        "old_level": old_level,
                        "new_level": new_level,
                    })
            
            # Check if account leveled up
            user = await db.users.find_one({"id": user_id})
            account_level = user.get('level', 1)
            account_exp = user.get('experience', 0)
            new_account_level = account_level
            while True:
                needed = new_account_level * 500 + 200
                if account_exp >= needed:
                    account_exp -= needed
                    new_account_level += 1
                else:
                    break
            if new_account_level > account_level:
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"level": new_account_level, "experience": account_exp}}
                )
            
            # Item drops
            from routes.items import BATTLE_DROPS
            drops = []
            num_drops = random.randint(2, 5)
            total_weight = sum(d['weight'] for d in BATTLE_DROPS)
            for _ in range(num_drops):
                roll = random.randint(1, total_weight)
                cumulative = 0
                for drop in BATTLE_DROPS:
                    cumulative += drop['weight']
                    if roll <= cumulative:
                        drops.append(drop['item_id'])
                        break
            
            # Add drops to inventory
            drop_summary = {}
            for item_id in drops:
                drop_summary[item_id] = drop_summary.get(item_id, 0) + 1
            for item_id, qty in drop_summary.items():
                await db.inventory.update_one(
                    {"user_id": user_id, "item_id": item_id},
                    {"$inc": {"quantity": qty}},
                    upsert=True
                )
            
            # Format drops for display
            from routes.items import EXP_ITEMS, SKILL_MATERIALS
            drop_display = []
            for item_id, qty in drop_summary.items():
                item_def = EXP_ITEMS.get(item_id) or SKILL_MATERIALS.get(item_id) or {}
                drop_display.append({
                    "item_id": item_id,
                    "name": item_def.get('name', item_id),
                    "icon": item_def.get('icon', '\U0001f381'),
                    "quantity": qty,
                })
            
            result['rewards'] = {
                "gold": gold_reward,
                "exp": exp_reward,
                "hero_exp": hero_exp,
                "hero_levelups": hero_levelups,
                "account_level_up": new_account_level > account_level,
                "new_account_level": new_account_level,
                "drops": drop_display,
            }
        return result

    class UpdateTeamRequest(BaseModel):
        formation: list
        constellation_id: str = None
        mode: str = "battle"

    @router.post("/team/update-formation")
    async def update_team_formation(req: UpdateTeamRequest, current_user: dict = Depends(get_current_user)):
        """Update team formation (max 9 slots, max 9 heroes on 3x3 grid)"""
        user_id = current_user['id']
        filled = [f for f in req.formation if f.get('user_hero_id')]
        if len(filled) > 9:
            raise HTTPException(status_code=400, detail="Massimo 9 eroi per team!")
        for pos in req.formation:
            if pos.get('x', 0) < 0 or pos.get('x', 0) > 8 or pos.get('y', 0) < 0 or pos.get('y', 0) > 8:
                raise HTTPException(status_code=400, detail="Posizione non valida (0-8)")
        positions = [{"x": p.get('x', 0), "y": p.get('y', 0)} for p in req.formation if p.get('user_hero_id')]
        active_formations = []
        for pat_id, pat in FORMATION_PATTERNS.items():
            try:
                if pat['check'](positions):
                    active_formations.append({"id": pat_id, "name": pat['name'], "description": pat['description'], "buff": pat['buff']})
            except Exception:
                pass
        adj = calculate_adjacency_bonus(positions)
        total_power = 0
        for pos in req.formation:
            if not pos.get('user_hero_id'):
                continue
            user_hero = await db.user_heroes.find_one({"id": pos['user_hero_id'], "user_id": user_id})
            if user_hero:
                hero = await db.heroes.find_one({"id": user_hero['hero_id']})
                if hero:
                    total_power += calculate_hero_power(hero, user_hero)
        existing = await db.teams.find_one({"user_id": user_id, "is_active": True})
        team_data = {
            "user_id": user_id,
            "is_active": True,
            "formation": req.formation,
            "total_power": total_power,
            "updated_at": datetime.utcnow(),
        }
        if req.constellation_id:
            team_data["constellation_id"] = req.constellation_id
        if existing:
            await db.teams.update_one({"_id": existing["_id"]}, {"$set": team_data})
        else:
            team_data["id"] = str(uuid.uuid4())
            await db.teams.insert_one(team_data)
        return {
            "success": True,
            "total_power": total_power,
            "active_formations": active_formations,
            "adjacency_pairs": adj['adjacent_pairs'],
            "adjacency_bonus": adj['bonus'],
        }
