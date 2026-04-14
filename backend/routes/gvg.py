"""
Divine Waifus - Guild vs Guild (GvG) Battle Routes
"""
import random
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from pydantic import BaseModel


def register_gvg_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== GvG WARS ====================
    @router.get("/gvg/wars")
    async def get_gvg_wars(current_user: dict = Depends(get_current_user)):
        """Get active and recent wars for user's guild."""
        guild_id = current_user.get("guild_id")
        if not guild_id:
            return {"active_war": None, "recent_wars": [], "can_matchmake": False}

        guild = await db.guilds.find_one({"id": guild_id})
        if not guild:
            return {"active_war": None, "recent_wars": [], "can_matchmake": False}

        # Active war
        active = await db.gvg_wars.find_one({
            "$or": [{"guild_a_id": guild_id}, {"guild_b_id": guild_id}],
            "status": "active"
        })

        active_war = None
        if active:
            active_war = await _build_war_details(active, guild_id, current_user["id"])

        # Recent wars (last 10)
        recent = await db.gvg_wars.find({
            "$or": [{"guild_a_id": guild_id}, {"guild_b_id": guild_id}],
            "status": "completed"
        }).sort("completed_at", -1).limit(10).to_list(10)

        recent_wars = []
        for w in recent:
            is_a = w["guild_a_id"] == guild_id
            my_name = w["guild_a_name"] if is_a else w["guild_b_name"]
            enemy_name = w["guild_b_name"] if is_a else w["guild_a_name"]
            my_score = w.get("guild_a_score", 0) if is_a else w.get("guild_b_score", 0)
            enemy_score = w.get("guild_b_score", 0) if is_a else w.get("guild_a_score", 0)
            won = w.get("winner_guild_id") == guild_id
            recent_wars.append({
                "id": w["id"],
                "enemy_guild": enemy_name,
                "my_score": my_score,
                "enemy_score": enemy_score,
                "won": won,
                "draw": w.get("winner_guild_id") is None and w["status"] == "completed",
                "completed_at": str(w.get("completed_at", "")),
            })

        # Check cooldown for matchmaking (1 war at a time, 5 min cooldown)
        can_matchmake = active is None
        if can_matchmake and recent:
            last_completed = recent[0].get("completed_at")
            if last_completed and isinstance(last_completed, datetime):
                can_matchmake = (datetime.utcnow() - last_completed).total_seconds() > 300

        return {
            "active_war": active_war,
            "recent_wars": recent_wars,
            "can_matchmake": can_matchmake,
            "guild_name": guild.get("name", "???"),
            "guild_members": len(guild.get("members", [])),
        }

    async def _build_war_details(war: dict, guild_id: str, user_id: str) -> dict:
        is_a = war["guild_a_id"] == guild_id
        my_guild_key = "guild_a" if is_a else "guild_b"
        enemy_guild_key = "guild_b" if is_a else "guild_a"

        my_attacks = war.get(f"{my_guild_key}_attacks", {})
        enemy_attacks = war.get(f"{enemy_guild_key}_attacks", {})

        # Build attack details with usernames
        my_attack_details = []
        for uid, dmg in my_attacks.items():
            u = await db.users.find_one({"id": uid})
            my_attack_details.append({
                "user_id": uid,
                "username": u.get("username", "???") if u else "???",
                "damage": dmg,
                "is_you": uid == user_id,
            })
        my_attack_details.sort(key=lambda x: x["damage"], reverse=True)

        enemy_attack_details = []
        for uid, dmg in enemy_attacks.items():
            u = await db.users.find_one({"id": uid})
            enemy_attack_details.append({
                "user_id": uid,
                "username": u.get("username", "???") if u else "???",
                "damage": dmg,
            })
        enemy_attack_details.sort(key=lambda x: x["damage"], reverse=True)

        my_total = war.get(f"{my_guild_key}_score", 0)
        enemy_total = war.get(f"{enemy_guild_key}_score", 0)

        # Time remaining (wars last 30 min, simplified)
        created = war.get("created_at", datetime.utcnow())
        if isinstance(created, str):
            created = datetime.utcnow()
        elapsed = (datetime.utcnow() - created).total_seconds()
        time_remaining = max(0, 1800 - elapsed)  # 30 min wars

        # My contribution
        my_damage = my_attacks.get(user_id, 0)
        my_attacks_count = len([1 for uid in my_attacks if uid == user_id])

        return {
            "id": war["id"],
            "my_guild": war[f"{my_guild_key}_name"],
            "enemy_guild": war[f"{enemy_guild_key}_name"],
            "my_score": my_total,
            "enemy_score": enemy_total,
            "my_attacks": my_attack_details,
            "enemy_attacks": enemy_attack_details,
            "my_damage": my_damage,
            "time_remaining": int(time_remaining),
            "status": war["status"],
            "total_attacks_my": len(my_attacks),
            "total_attacks_enemy": len(enemy_attacks),
            "created_at": str(war.get("created_at", "")),
        }

    @router.post("/gvg/matchmake")
    async def gvg_matchmake(current_user: dict = Depends(get_current_user)):
        """Find or create a GvG match."""
        guild_id = current_user.get("guild_id")
        if not guild_id:
            raise HTTPException(400, "Devi essere in una gilda!")

        guild = await db.guilds.find_one({"id": guild_id})
        if not guild:
            raise HTTPException(404, "Gilda non trovata")

        # Check no active war
        active = await db.gvg_wars.find_one({
            "$or": [{"guild_a_id": guild_id}, {"guild_b_id": guild_id}],
            "status": "active"
        })
        if active:
            raise HTTPException(400, "La tua gilda ha gia una guerra attiva!")

        # Find opponent guild (not self, has members)
        all_guilds = await db.guilds.find({"id": {"$ne": guild_id}}).to_list(50)
        if not all_guilds:
            # Create a bot guild as opponent
            bot_guild = {
                "id": f"bot_guild_{uuid.uuid4().hex[:8]}",
                "name": random.choice([
                    "Ombre del Crepuscolo", "Fiamme Eterne", "Cavalieri di Luna",
                    "Draghi d'Acciaio", "Tempesta Divina", "Lame Silenziose",
                    "Guardiani dell'Alba", "Furia dei Titani"
                ]),
                "members": [f"bot_{i}" for i in range(random.randint(3, 8))],
                "level": random.randint(1, 5),
                "is_bot_guild": True,
            }
            all_guilds = [bot_guild]

        # Pick best match (similar member count)
        my_size = len(guild.get("members", []))
        all_guilds.sort(key=lambda g: abs(len(g.get("members", [])) - my_size))
        opponent = all_guilds[0]

        # Create war
        war = {
            "id": str(uuid.uuid4()),
            "guild_a_id": guild_id,
            "guild_a_name": guild.get("name", "???"),
            "guild_b_id": opponent["id"],
            "guild_b_name": opponent.get("name", "???"),
            "guild_a_score": 0,
            "guild_b_score": 0,
            "guild_a_attacks": {},
            "guild_b_attacks": {},
            "status": "active",
            "created_at": datetime.utcnow(),
            "winner_guild_id": None,
        }
        await db.gvg_wars.insert_one(war)

        # If opponent is a real guild, simulate some initial attacks from bot members
        if opponent.get("is_bot_guild"):
            bot_attacks = {}
            bot_total = 0
            for bot_id in opponent.get("members", []):
                dmg = random.randint(3000, 15000)
                bot_attacks[bot_id] = dmg
                bot_total += dmg
            await db.gvg_wars.update_one(
                {"id": war["id"]},
                {"$set": {"guild_b_attacks": bot_attacks, "guild_b_score": bot_total}}
            )
        else:
            # Real guild - simulate some bot attacks for fun
            for member_id in opponent.get("members", [])[:3]:
                u = await db.users.find_one({"id": member_id})
                if u and u.get("is_bot"):
                    dmg = random.randint(2000, 10000)
                    await db.gvg_wars.update_one(
                        {"id": war["id"]},
                        {"$inc": {f"guild_b_attacks.{member_id}": dmg, "guild_b_score": dmg}}
                    )

        return {"success": True, "war_id": war["id"], "opponent": opponent.get("name", "???")}

    @router.post("/gvg/attack")
    async def gvg_attack(current_user: dict = Depends(get_current_user)):
        """Contribute an attack in the active GvG war."""
        uid = current_user["id"]
        guild_id = current_user.get("guild_id")
        if not guild_id:
            raise HTTPException(400, "Devi essere in una gilda!")

        # Find active war
        war = await db.gvg_wars.find_one({
            "$or": [{"guild_a_id": guild_id}, {"guild_b_id": guild_id}],
            "status": "active"
        })
        if not war:
            raise HTTPException(404, "Nessuna guerra attiva!")

        # Check stamina
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < 12:
            raise HTTPException(400, "Stamina insufficiente! (12 richiesti)")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -12}})

        # Check war time limit (30 min)
        created = war.get("created_at", datetime.utcnow())
        if isinstance(created, datetime) and (datetime.utcnow() - created).total_seconds() > 1800:
            # Auto-complete the war
            await _complete_war(war)
            raise HTTPException(400, "La guerra e terminata! Tempo scaduto.")

        # Calculate damage
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        damage = int(team_power * random.uniform(0.6, 1.4))

        # Determine which guild the user is in
        is_a = war["guild_a_id"] == guild_id
        guild_key = "guild_a" if is_a else "guild_b"

        # Update war
        await db.gvg_wars.update_one(
            {"id": war["id"]},
            {
                "$inc": {
                    f"{guild_key}_attacks.{uid}": damage,
                    f"{guild_key}_score": damage,
                }
            }
        )

        # Counter-attack from enemy (simulated)
        enemy_key = "guild_b" if is_a else "guild_a"
        enemy_guild_id = war["guild_b_id"] if is_a else war["guild_a_id"]
        enemy_guild = await db.guilds.find_one({"id": enemy_guild_id})

        counter_damage = 0
        if enemy_guild:
            # Pick a random enemy member to counter-attack
            enemy_members = enemy_guild.get("members", [])
            if enemy_members:
                counter_uid = random.choice(enemy_members)
                counter_damage = random.randint(2000, int(damage * 0.8))
                await db.gvg_wars.update_one(
                    {"id": war["id"]},
                    {"$inc": {f"{enemy_key}_attacks.{counter_uid}": counter_damage, f"{enemy_key}_score": counter_damage}}
                )

        # Get updated scores
        updated_war = await db.gvg_wars.find_one({"id": war["id"]})
        my_score = updated_war.get(f"{guild_key}_score", 0)
        enemy_score = updated_war.get(f"{enemy_key}_score", 0)

        return {
            "success": True,
            "damage": damage,
            "counter_damage": counter_damage,
            "my_score": my_score,
            "enemy_score": enemy_score,
            "my_total_damage": updated_war.get(f"{guild_key}_attacks", {}).get(uid, 0),
        }

    @router.post("/gvg/end-war")
    async def end_war(current_user: dict = Depends(get_current_user)):
        """Force end the current war (leader only or timeout)."""
        guild_id = current_user.get("guild_id")
        if not guild_id:
            raise HTTPException(400, "Devi essere in una gilda!")

        war = await db.gvg_wars.find_one({
            "$or": [{"guild_a_id": guild_id}, {"guild_b_id": guild_id}],
            "status": "active"
        })
        if not war:
            raise HTTPException(404, "Nessuna guerra attiva!")

        result = await _complete_war(war)
        return result

    async def _complete_war(war: dict) -> dict:
        """Complete a war and distribute rewards."""
        score_a = war.get("guild_a_score", 0)
        score_b = war.get("guild_b_score", 0)

        winner_id = None
        if score_a > score_b:
            winner_id = war["guild_a_id"]
        elif score_b > score_a:
            winner_id = war["guild_b_id"]
        # else: draw

        await db.gvg_wars.update_one(
            {"id": war["id"]},
            {"$set": {
                "status": "completed",
                "winner_guild_id": winner_id,
                "completed_at": datetime.utcnow(),
            }}
        )

        # Distribute rewards
        for guild_key in ["guild_a", "guild_b"]:
            g_id = war[f"{guild_key}_id"]
            is_winner = g_id == winner_id
            attacks = war.get(f"{guild_key}_attacks", {})
            total_dmg = sum(attacks.values()) if attacks else 0

            for uid, dmg in attacks.items():
                if uid.startswith("bot_"):
                    continue
                contribution = dmg / max(1, total_dmg)
                base_gold = 8000 if is_winner else 3000
                base_gems = 15 if is_winner else 5
                gold = int(base_gold * (0.5 + contribution))
                gems = int(base_gems * (0.5 + contribution))
                exp = int(2000 * (0.5 + contribution))
                await db.users.update_one({"id": uid}, {"$inc": {"gold": gold, "gems": gems, "experience": exp}})
                # Send mail
                await db.user_mail.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": uid,
                    "subject": f"Guerra GvG {'Vinta!' if is_winner else 'Persa' if winner_id else 'Pareggio'}",
                    "body": f"Risultato: {war['guild_a_name']} {score_a:,} vs {war['guild_b_name']} {score_b:,}\nI tuoi danni: {dmg:,}",
                    "rewards": {"gold": gold, "gems": gems},
                    "claimed": True,
                    "timestamp": datetime.utcnow(),
                })

        winner_name = war["guild_a_name"] if winner_id == war["guild_a_id"] else war["guild_b_name"] if winner_id else "Pareggio"
        return {
            "success": True,
            "winner": winner_name,
            "score_a": score_a,
            "score_b": score_b,
            "guild_a_name": war["guild_a_name"],
            "guild_b_name": war["guild_b_name"],
        }
