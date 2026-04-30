"""
Divine Waifus - SANTUARIO EROE (Hero Sanctuary)
=================================================
Sistema centrale per l'eroe mostrato in homepage + Affinità + Costellazione.

PARTI IMPLEMENTATE (FASE 1):
- Home Hero selection (con logica tutorial Borea)
- Affinità: struttura dati, curva progressione, auto-gain a fine battaglia
- Costellazione: struttura dati base (stages, frammenti, limite 3 eroi/die)

I contenuti profondi (regali, dialoghi lore, sfide costellazione) saranno
popolati nelle FASE 2/3. Qui c'è solo la SPINA DORSALE dati + endpoint.
"""
from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException, Depends
from pydantic import BaseModel


# ===================== AFFINITA' =====================
# Curva MOLTO lenta — target ~2450 battaglie senza regali per 0→10.
# Formula: exp_for_level(n) = round(6 * 1.78 ^ n) per n in [0..9]
# Totale cumulativo: 6 + 11 + 19 + 34 + 60 + 107 + 191 + 340 + 605 + 1077 = 2450
AFFINITY_MAX_LEVEL = 10
AFFINITY_EXP_PER_LEVEL = [
    6,     # Lv 0 -> 1
    11,    # Lv 1 -> 2
    19,    # Lv 2 -> 3
    34,    # Lv 3 -> 4
    60,    # Lv 4 -> 5
    107,   # Lv 5 -> 6
    191,   # Lv 6 -> 7
    340,   # Lv 7 -> 8
    605,   # Lv 8 -> 9
    1077,  # Lv 9 -> 10
]

# Ricompense per livello affinità. I valori sono PRUDENTI e modulari.
# bonus_stats = aggregati applicabili come modificatori moltiplicativi sul personaggio in battle
# perk = effetto passivo battle-side (non applicato in questa fase, solo dichiarato)
# unlock = contenuto narrativo / profilo sbloccato
AFFINITY_REWARDS = {
    0: {
        "bonus_stats": {},
        "perk": None,
        "unlock": None,
        "title": "Sconosciuto",
    },
    1: {
        "bonus_stats": {"hp": 0.02},
        "perk": None,
        "unlock": None,
        "title": "Conoscente",
    },
    2: {
        "bonus_stats": {"physical_damage": 0.02, "magic_damage": 0.02},
        "perk": None,
        "unlock": None,
        "title": "Alleato",
    },
    3: {
        "bonus_stats": {"physical_defense": 0.03, "magic_defense": 0.03},
        "perk": None,
        "unlock": "profile_voice_1",
        "title": "Compagno",
    },
    4: {
        "bonus_stats": {"crit_chance": 0.03},
        "perk": None,
        "unlock": None,
        "title": "Fidato",
    },
    5: {
        "bonus_stats": {},
        "perk": {
            "id": "primo_sangue",
            "name": "Primo Sangue",
            "description": "+10% danno al primo colpo della battaglia",
            "effect": {"first_hit_damage_bonus": 0.10},
        },
        "unlock": None,
        "title": "Confidente",
    },
    6: {
        "bonus_stats": {"hp": 0.05},
        "perk": None,
        "unlock": "lore_entry_1",
        "title": "Amico",
    },
    7: {
        "bonus_stats": {"physical_damage": 0.05, "magic_damage": 0.05},
        "perk": None,
        "unlock": "dialogue_1",
        "title": "Caro",
    },
    8: {
        "bonus_stats": {},
        "perk": {
            "id": "secondo_fiato",
            "name": "Secondo Fiato",
            "description": "+15% cure ricevute quando HP < 30%",
            "effect": {"low_hp_heal_bonus": 0.15, "threshold_hp_pct": 0.30},
        },
        "unlock": "dialogue_2",
        "title": "Intimo",
    },
    9: {
        "bonus_stats": {"physical_defense": 0.05, "magic_defense": 0.05},
        "perk": None,
        "unlock": "profile_portrait_bonus",
        "title": "Devoto",
    },
    10: {
        "bonus_stats": {
            "hp": 0.04, "physical_damage": 0.04, "magic_damage": 0.04,
            "physical_defense": 0.04, "magic_defense": 0.04,
        },
        "perk": {
            "id": "legame_eterno",
            "name": "Legame Eterno",
            "description": "Bond massimo: piccolo bonus a tutte le statistiche principali",
            "effect": {"all_stats_bonus": 0.04},
        },
        "unlock": "title_legame_eterno",
        "title": "Legame Eterno",
    },
}


def _compute_affinity_progress(exp: int, level: int):
    """Ritorna info sul progresso corrente (exp nel livello, exp_to_next)."""
    if level >= AFFINITY_MAX_LEVEL:
        return {"exp_in_level": 0, "exp_to_next": 0, "progress": 1.0, "max_reached": True}
    exp_needed = AFFINITY_EXP_PER_LEVEL[level]
    return {
        "exp_in_level": exp,
        "exp_to_next": exp_needed,
        "progress": min(1.0, exp / max(1, exp_needed)),
        "max_reached": False,
    }


# ===================== COSTELLAZIONE =====================
CONSTELLATION_DAILY_HERO_LIMIT = 3  # massimo 3 eroi al giorno
CONSTELLATION_BOSS_EVERY = 3        # boss ogni 3 stage
CONSTELLATION_TOTAL_STAGES = 9      # Progressione fissa a 9 stage (boss a 3, 6, 9)
CONSTELLATION_BOSS_FRAGMENT_MIN = 1
CONSTELLATION_BOSS_FRAGMENT_MAX = 3


def _constellation_stage_is_boss(stage: int) -> bool:
    """Stage 3, 6, 9, 12... sono boss."""
    return stage > 0 and stage % CONSTELLATION_BOSS_EVERY == 0


# ===================== BOREA (Tutorial Hero — Extra Premium) =====================
# RM1.16 — Allineato al Character Bible:
#   id slug Bible: greek_borea
#   release_group: launch_extra_premium (fuori dai 100 launch_base)
#   native_rarity 6 / max_stars 15 / element wind / role mage_aoe / faction greek
#   origin_group anemoi / category deity
#
# COMPATIBILITÀ RUNTIME (deferred):
#   Il record DB attuale ha id="borea" (legacy) e 2 user_heroes lo possiedono.
#   Per non orfanare ownership, la ID migration "borea -> greek_borea" è
#   DEFERRED a una task futura. In questo task aggiorniamo i metadata Bible
#   sul record esistente, conservando id="borea" come anchor runtime e
#   aggiungendo canonical_id="greek_borea" come future-ready.
#
#   hero_class resta "DPS" runtime (battle_engine ramifica DPS/Tank/Support);
#   canonical_role="mage_aoe" è metadata Bible-compatible per il futuro
#   evaluator V2 (RM1.14).
BOREA_HERO_ID = "borea"  # legacy DB id (preservato per ownership integrity)
BOREA_CANONICAL_ID = "greek_borea"  # Character Bible slug (future migration)
BOREA_SEED = {
    "id": BOREA_HERO_ID,
    "canonical_id": BOREA_CANONICAL_ID,
    "name": "Borea",
    "rarity": 6,
    "max_stars": 15,
    "element": "wind",
    "hero_class": "DPS",            # runtime-compat (DPS/Tank/Support)
    "canonical_role": "mage_aoe",   # Bible-compat
    "faction": "greek",
    "origin_group": "anemoi",
    "category": "deity",
    "release_group": "launch_extra_premium",
    "is_official": True,
    "is_premium": True,
    "is_extra_premium": True,
    "image_url": None,  # fallback: gradient stylized (in UI)
    "image": "asset:greek_borea:splash",  # sentinel for future asset resolver
    "description": "Il Vento del Nord, guida dei Novizi. Eroe iconico del tutorial e Anemoi extra premium.",
    "base_stats": {
        "hp": 10200, "speed": 155, "physical_damage": 2400, "magic_damage": 3200,
        "physical_defense": 480, "magic_defense": 540, "healing": 0,
        "healing_received": 1.0, "damage_rate": 1.2, "penetration": 0.12,
        "dodge": 0.08, "crit_chance": 0.20, "crit_damage": 1.8,
        "hit_rate": 1.0, "combo_rate": 0.10, "block_rate": 0.05,
    },
}


async def _ensure_borea_exists(db):
    """Seed/patch idempotente: se Borea non esiste lo crea, altrimenti
    sincronizza i campi Bible-canonical sul record esistente senza
    sovrascrivere campi runtime non gestiti dal Bible (es. base_stats già
    bilanciate, sprite_sheet_base64 generati).

    RM1.16: idempotente. Sicuro a rieseguire più volte.
    """
    existing = await db.heroes.find_one({"id": BOREA_HERO_ID})
    if not existing:
        doc = {**BOREA_SEED, "created_at": datetime.utcnow()}
        await db.heroes.insert_one(doc)
        return True
    # Sincronizza solo i campi canonical Bible-mandated. NON tocchiamo
    # base_stats/sprite_sheet_base64/image_base64 se già presenti — solo
    # metadata.
    canonical_patch = {
        "canonical_id": BOREA_CANONICAL_ID,
        "rarity": 6,
        "max_stars": 15,
        "element": "wind",
        "canonical_role": "mage_aoe",
        "faction": "greek",
        "origin_group": "anemoi",
        "category": "deity",
        "release_group": "launch_extra_premium",
        "is_official": True,
        "is_premium": True,
        "is_extra_premium": True,
    }
    # Patch only fields that differ to keep this update minimal and safe.
    diff = {k: v for k, v in canonical_patch.items() if existing.get(k) != v}
    if diff:
        await db.heroes.update_one({"id": BOREA_HERO_ID}, {"$set": diff})
    return False


# ===================== BERSERKER (Launch Base — Norse 3*) =====================
# RM1.16 — Nuovo seed ufficiale: Berserker non era in DB nonostante gli
# asset esistano (/app/frontend/assets/heroes/berserker_sprites/* +
# norse_berserker.jpg). Aggiunto come launch_base ufficiale Bible-compat.
BERSERKER_HERO_ID = "norse_berserker"  # Character Bible canonical slug
BERSERKER_SEED = {
    "id": BERSERKER_HERO_ID,
    "canonical_id": BERSERKER_HERO_ID,
    "name": "Berserker",
    "rarity": 3,
    "max_stars": 8,
    "element": "fire",
    "hero_class": "DPS",            # runtime-compat
    "canonical_role": "dps_melee",  # Bible-compat
    "faction": "norse",
    "origin_group": "berserkers",
    "category": "mythic_archetype",
    "release_group": "launch_base",
    "is_official": True,
    "is_premium": False,
    "is_extra_premium": False,
    "image_url": None,
    "image": "asset:norse_berserker:splash",  # sentinel for future resolver
    "description": (
        "Furia del nord. Guerriero norreno in stato di trance battagliera, "
        "infligge danno crescente quanto è ferito."
    ),
    "base_stats": {
        # Profilo 3* fire dps_melee: HP medio, attack alto melee, velocità
        # decente, defense bassa-media, crit rate competitivo per 3*.
        "hp": 8200, "speed": 110, "physical_damage": 1800, "magic_damage": 600,
        "physical_defense": 700, "magic_defense": 450, "healing": 0,
        "healing_received": 1.0, "damage_rate": 1.15, "penetration": 0.08,
        "dodge": 0.05, "crit_chance": 0.18, "crit_damage": 1.7,
        "hit_rate": 1.0, "combo_rate": 0.10, "block_rate": 0.04,
    },
}


async def _ensure_berserker_exists(db):
    """Seed/patch idempotente per Berserker. RM1.16."""
    existing = await db.heroes.find_one({"id": BERSERKER_HERO_ID})
    if not existing:
        doc = {**BERSERKER_SEED, "created_at": datetime.utcnow()}
        await db.heroes.insert_one(doc)
        return True
    canonical_patch = {
        "canonical_id": BERSERKER_HERO_ID,
        "rarity": 3,
        "max_stars": 8,
        "element": "fire",
        "canonical_role": "dps_melee",
        "faction": "norse",
        "origin_group": "berserkers",
        "category": "mythic_archetype",
        "release_group": "launch_base",
        "is_official": True,
        "is_premium": False,
        "is_extra_premium": False,
    }
    diff = {k: v for k, v in canonical_patch.items() if existing.get(k) != v}
    if diff:
        await db.heroes.update_one({"id": BERSERKER_HERO_ID}, {"$set": diff})
    return False


# ===================== HOPLITE (Launch Base — Greek 3*) =====================
# RM1.16 — Hoplite è già perfettamente Bible-compat su id/element/rarity/
# faction. Aggiungiamo solo i metadata Bible (max_stars, canonical_role,
# origin_group, category, release_group, is_official, canonical_id) come
# patch idempotente non distruttiva.
HOPLITE_HERO_ID = "greek_hoplite"


async def _ensure_hoplite_canonical(db):
    """Patch idempotente metadata canonici Hoplite. RM1.16.
    Non tocca element/rarity/hero_class/base_stats/asset esistenti."""
    existing = await db.heroes.find_one({"id": HOPLITE_HERO_ID})
    if not existing:
        # Hoplite assente è uno scenario anomalo (è il record-pilota); in
        # tal caso NON facciamo seed automatico: lasciamo segnale al log e
        # ritorniamo. La ricreazione spetta al seed_database originale.
        return None
    canonical_patch = {
        "canonical_id": HOPLITE_HERO_ID,
        "max_stars": 8,
        "canonical_role": "tank",
        "origin_group": "phalanx",
        "category": "mythic_archetype",
        "release_group": "launch_base",
        "is_official": True,
        "is_premium": False,
        "is_extra_premium": False,
    }
    diff = {k: v for k, v in canonical_patch.items() if existing.get(k) != v}
    if diff:
        await db.heroes.update_one({"id": HOPLITE_HERO_ID}, {"$set": diff})
    return False


async def _ensure_canonical_roster_metadata(db):
    """RM1.16 — Esegue tutti i seed/patch canonici idempotenti
    (Borea, Berserker, Hoplite) in un solo punto.
    Sicuro a chiamare ad ogni request (le find_one + update mirate sono
    O(1) con index su id)."""
    await _ensure_borea_exists(db)
    await _ensure_berserker_exists(db)
    await _ensure_hoplite_canonical(db)


# ===================== ROUTE REGISTRATION =====================
def register_sanctuary_routes(router, db, get_current_user, serialize_doc):

    # -------------- HOME HERO --------------
    class SetHomeHeroRequest(BaseModel):
        hero_id: str

    @router.get("/sanctuary/home-hero")
    async def get_home_hero(current_user: dict = Depends(get_current_user)):
        """Quale eroe mostrare in homepage.
        Regole:
         1. Se user.in_tutorial == True (default per nuovi user) → Borea
         2. Altrimenti → user.home_hero_id se presente
         3. Fallback → primo eroe 6★ posseduto, poi qualsiasi primo posseduto
        """
        # RM1.16 — Ensure canonical roster metadata (Borea + Berserker +
        # Hoplite) idempotently. Replaces the legacy _ensure_borea_exists
        # call with the wrapper that also handles Berserker seed + Hoplite
        # canonical patch.
        await _ensure_canonical_roster_metadata(db)

        # Tutorial mode?
        in_tutorial = current_user.get("in_tutorial", True)
        if in_tutorial:
            borea = await db.heroes.find_one({"id": BOREA_HERO_ID})
            if borea:
                return {
                    "source": "tutorial",
                    "hero": serialize_doc(borea),
                    "is_owned": False,
                    "in_tutorial": True,
                }

        # Post-tutorial: user's chosen home hero
        uid = current_user["id"]
        chosen_id = current_user.get("home_hero_id")
        if chosen_id:
            # Verify the user still owns this hero
            uh = await db.user_heroes.find_one({"user_id": uid, "hero_id": chosen_id})
            if uh:
                hero = await db.heroes.find_one({"id": chosen_id})
                if hero:
                    return {
                        "source": "user_choice",
                        "hero": serialize_doc(hero),
                        "is_owned": True,
                        "in_tutorial": False,
                    }

        # Fallback: first owned 6★ or first owned
        owned = await db.user_heroes.find({"user_id": uid}).to_list(200)
        if owned:
            # Try 6★ first
            for uh in owned:
                hero = await db.heroes.find_one({"id": uh["hero_id"]})
                if hero and hero.get("rarity", 0) == 6:
                    return {
                        "source": "fallback_top_rarity",
                        "hero": serialize_doc(hero),
                        "is_owned": True,
                        "in_tutorial": False,
                    }
            # Any owned
            hero = await db.heroes.find_one({"id": owned[0]["hero_id"]})
            if hero:
                return {
                    "source": "fallback_first",
                    "hero": serialize_doc(hero),
                    "is_owned": True,
                    "in_tutorial": False,
                }

        # Ultima risorsa: Borea
        borea = await db.heroes.find_one({"id": BOREA_HERO_ID})
        return {
            "source": "fallback_borea",
            "hero": serialize_doc(borea) if borea else None,
            "is_owned": False,
            "in_tutorial": False,
        }

    @router.post("/sanctuary/home-hero")
    async def set_home_hero(req: SetHomeHeroRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        # Verify hero exists
        hero = await db.heroes.find_one({"id": req.hero_id})
        if not hero:
            raise HTTPException(404, "Eroe non trovato")
        # Must be owned UNLESS it's Borea during tutorial (Borea is never "owned")
        if req.hero_id != BOREA_HERO_ID:
            uh = await db.user_heroes.find_one({"user_id": uid, "hero_id": req.hero_id})
            if not uh:
                raise HTTPException(400, "Devi possedere questo eroe per impostarlo come home hero")
        await db.users.update_one(
            {"id": uid},
            {"$set": {"home_hero_id": req.hero_id}},
        )
        return {"success": True, "home_hero_id": req.hero_id, "hero_name": hero.get("name")}

    @router.post("/sanctuary/complete-tutorial")
    async def complete_tutorial(current_user: dict = Depends(get_current_user)):
        """Chiude il tutorial. Dopo questo l'homepage usa user.home_hero_id."""
        uid = current_user["id"]
        await db.users.update_one(
            {"id": uid},
            {"$set": {"in_tutorial": False}},
        )
        return {"success": True, "in_tutorial": False}

    # -------------- SANTUARIO PANORAMICA --------------
    @router.get("/sanctuary/{hero_id}")
    async def get_sanctuary(hero_id: str, current_user: dict = Depends(get_current_user)):
        """Restituisce tutto lo stato santuario per un eroe: affinity + constellation.
        Funziona anche per eroi non posseduti (es. Borea durante tutorial)."""
        uid = current_user["id"]
        hero = await db.heroes.find_one({"id": hero_id})
        if not hero:
            raise HTTPException(404, "Eroe non trovato")

        # Affinity state
        aff = await db.user_affinity.find_one({"user_id": uid, "hero_id": hero_id})
        if not aff:
            aff = {"user_id": uid, "hero_id": hero_id, "level": 0, "exp": 0,
                   "total_exp": 0, "created_at": datetime.utcnow()}
        aff_level = aff.get("level", 0)
        aff_exp = aff.get("exp", 0)
        aff_progress = _compute_affinity_progress(aff_exp, aff_level)

        # Unlocked rewards summary (tutti i livelli <= level)
        unlocked_rewards = []
        for lv in range(0, aff_level + 1):
            r = AFFINITY_REWARDS.get(lv, {})
            unlocked_rewards.append({
                "level": lv,
                "bonus_stats": r.get("bonus_stats", {}),
                "perk": r.get("perk"),
                "unlock": r.get("unlock"),
                "title": r.get("title"),
            })

        # Next reward preview
        next_reward = None
        if aff_level < AFFINITY_MAX_LEVEL:
            r_next = AFFINITY_REWARDS.get(aff_level + 1, {})
            next_reward = {
                "level": aff_level + 1,
                "bonus_stats": r_next.get("bonus_stats", {}),
                "perk": r_next.get("perk"),
                "unlock": r_next.get("unlock"),
                "title": r_next.get("title"),
            }

        # Full rewards catalog (static, L'intera tabella Lv0-10 per consentire al
        # client di mostrare sia passato che futuro senza round-trip aggiuntivi)
        all_rewards = []
        for lv in range(0, AFFINITY_MAX_LEVEL + 1):
            r = AFFINITY_REWARDS.get(lv, {})
            all_rewards.append({
                "level": lv,
                "bonus_stats": r.get("bonus_stats", {}),
                "perk": r.get("perk"),
                "unlock": r.get("unlock"),
                "title": r.get("title"),
                "unlocked": lv <= aff_level,
            })

        # Constellation state
        con = await db.user_constellation.find_one({"user_id": uid, "hero_id": hero_id})
        if not con:
            con = {"user_id": uid, "hero_id": hero_id, "highest_stage": 0,
                   "fragments": 0, "last_attempt_date": None,
                   "created_at": datetime.utcnow()}
        highest = con.get("highest_stage", 0)
        next_stage = highest + 1
        next_is_boss = _constellation_stage_is_boss(next_stage)

        # Daily quota (limite 3 eroi/die)
        today_str = date.today().isoformat()
        daily = await db.user_constellation_daily.find_one({"user_id": uid, "date": today_str})
        heroes_attempted_today = daily.get("heroes_attempted", []) if daily else []
        hero_already_attempted_today = hero_id in heroes_attempted_today
        daily_slots_used = len(heroes_attempted_today)
        daily_slots_left = max(0, CONSTELLATION_DAILY_HERO_LIMIT - daily_slots_used)

        # Is this hero owned?
        is_owned = False
        if hero_id != BOREA_HERO_ID:
            uh = await db.user_heroes.find_one({"user_id": uid, "hero_id": hero_id})
            is_owned = uh is not None

        # Is this the currently-selected home hero?
        is_home = (current_user.get("home_hero_id") == hero_id)

        return {
            "hero": serialize_doc(hero),
            "is_owned": is_owned,
            "is_home": is_home,
            "in_tutorial": current_user.get("in_tutorial", True),
            "affinity": {
                "level": aff_level,
                "exp": aff_exp,
                "total_exp": aff.get("total_exp", 0),
                "max_level": AFFINITY_MAX_LEVEL,
                "progress": aff_progress,
                "current_title": AFFINITY_REWARDS.get(aff_level, {}).get("title", "Sconosciuto"),
                "unlocked_rewards": unlocked_rewards,
                "next_reward": next_reward,
                "all_rewards": all_rewards,
                "full_curve": AFFINITY_EXP_PER_LEVEL,
            },
            "constellation": {
                "highest_stage": highest,
                "next_stage": next_stage,
                "next_is_boss": next_is_boss,
                "boss_every": CONSTELLATION_BOSS_EVERY,
                "total_stages": CONSTELLATION_TOTAL_STAGES,
                "is_complete": highest >= CONSTELLATION_TOTAL_STAGES,
                "fragments": con.get("fragments", 0),
                "fragment_name": f"Frammenti d'Anima di {hero.get('name')}",
                "daily_limit": CONSTELLATION_DAILY_HERO_LIMIT,
                "daily_slots_used": daily_slots_used,
                "daily_slots_left": daily_slots_left,
                "hero_already_attempted_today": hero_already_attempted_today,
                "can_attempt_today": (
                    hero_already_attempted_today or daily_slots_left > 0
                ),
            },
        }

    # -------------- AFFINITA': GUADAGNO EXP --------------
    class AffinityGainRequest(BaseModel):
        hero_ids: list[str]  # eroi presenti nel team della battle appena finita
        source: str = "battle_complete"

    @router.post("/sanctuary/affinity/gain")
    async def gain_affinity(req: AffinityGainRequest, current_user: dict = Depends(get_current_user)):
        """Chiamato a fine battaglia per ogni eroe del team.
        Per regola utente: +1 Affinity EXP a battaglia completata, SOLO presenza team.
        Niente bonus per kill / HP / performance.
        """
        uid = current_user["id"]
        results = []
        for hero_id in req.hero_ids:
            # Verify hero exists (protezione da ID fake)
            hero = await db.heroes.find_one({"id": hero_id})
            if not hero:
                continue

            aff = await db.user_affinity.find_one({"user_id": uid, "hero_id": hero_id})
            if not aff:
                aff = {"user_id": uid, "hero_id": hero_id, "level": 0, "exp": 0,
                       "total_exp": 0, "created_at": datetime.utcnow()}
                await db.user_affinity.insert_one(aff)

            level = aff.get("level", 0)
            exp = aff.get("exp", 0)
            total = aff.get("total_exp", 0)

            # Già al massimo
            if level >= AFFINITY_MAX_LEVEL:
                results.append({
                    "hero_id": hero_id, "hero_name": hero.get("name"),
                    "level": level, "exp": exp, "gained": 0, "leveled_up": False,
                })
                continue

            gained = 1  # regola del sistema: +1 per battle completata
            exp += gained
            total += gained
            leveled_up = False
            new_levels = []

            # Overflow a livelli successivi
            while level < AFFINITY_MAX_LEVEL and exp >= AFFINITY_EXP_PER_LEVEL[level]:
                exp -= AFFINITY_EXP_PER_LEVEL[level]
                level += 1
                leveled_up = True
                new_levels.append(level)

            await db.user_affinity.update_one(
                {"user_id": uid, "hero_id": hero_id},
                {"$set": {"level": level, "exp": exp, "total_exp": total,
                          "updated_at": datetime.utcnow()}},
                upsert=True,
            )

            results.append({
                "hero_id": hero_id, "hero_name": hero.get("name"),
                "level": level, "exp": exp, "total_exp": total,
                "gained": gained,
                "leveled_up": leveled_up,
                "new_levels": new_levels,
                "new_title": AFFINITY_REWARDS.get(level, {}).get("title"),
            })
        return {"results": results}

    # -------------- COSTELLAZIONE: CLAIM ATTEMPT / DROP --------------
    class ConstellationAttemptRequest(BaseModel):
        hero_id: str
        stage: int
        success: bool = True

    @router.post("/sanctuary/constellation/attempt")
    async def constellation_attempt(
        req: ConstellationAttemptRequest,
        current_user: dict = Depends(get_current_user),
    ):
        """Registra un tentativo di costellazione. Se success=True e stage > highest,
        avanza highest_stage. Se stage è boss e success=True, droppa 1-3 frammenti.

        Enforcement:
         - Si può attentare solo sullo stage immediatamente successivo a highest (o ritentare highest)
         - Limite 3 eroi diversi al giorno (se hero_id non è in daily, serve slot libero)
        """
        import random
        uid = current_user["id"]
        hero = await db.heroes.find_one({"id": req.hero_id})
        if not hero:
            raise HTTPException(404, "Eroe non trovato")

        # Must be owned (Borea excluded for tutorial)
        if req.hero_id != BOREA_HERO_ID:
            uh = await db.user_heroes.find_one({"user_id": uid, "hero_id": req.hero_id})
            if not uh:
                raise HTTPException(400, "Devi possedere questo eroe")

        con = await db.user_constellation.find_one({"user_id": uid, "hero_id": req.hero_id})
        if not con:
            con = {"user_id": uid, "hero_id": req.hero_id, "highest_stage": 0,
                   "fragments": 0, "created_at": datetime.utcnow()}
            await db.user_constellation.insert_one(con)

        highest = con.get("highest_stage", 0)
        if req.stage > highest + 1:
            raise HTTPException(400, f"Devi completare prima lo stage {highest + 1}")
        if req.stage > CONSTELLATION_TOTAL_STAGES:
            raise HTTPException(400, f"La costellazione ha un massimo di {CONSTELLATION_TOTAL_STAGES} stage")
        if highest >= CONSTELLATION_TOTAL_STAGES:
            raise HTTPException(400, "Costellazione già completata")

        # Daily quota check
        today_str = date.today().isoformat()
        daily = await db.user_constellation_daily.find_one({"user_id": uid, "date": today_str})
        attempted = daily.get("heroes_attempted", []) if daily else []
        if req.hero_id not in attempted:
            if len(attempted) >= CONSTELLATION_DAILY_HERO_LIMIT:
                raise HTTPException(400, f"Limite giornaliero raggiunto: {CONSTELLATION_DAILY_HERO_LIMIT} eroi")
            attempted.append(req.hero_id)
            await db.user_constellation_daily.update_one(
                {"user_id": uid, "date": today_str},
                {"$set": {"heroes_attempted": attempted, "updated_at": datetime.utcnow()}},
                upsert=True,
            )

        # Apply result
        fragments_dropped = 0
        new_highest = highest
        if req.success:
            if req.stage > highest:
                new_highest = req.stage
            if _constellation_stage_is_boss(req.stage):
                fragments_dropped = random.randint(
                    CONSTELLATION_BOSS_FRAGMENT_MIN,
                    CONSTELLATION_BOSS_FRAGMENT_MAX,
                )

        await db.user_constellation.update_one(
            {"user_id": uid, "hero_id": req.hero_id},
            {"$set": {"highest_stage": new_highest,
                      "last_attempt_date": today_str,
                      "updated_at": datetime.utcnow()},
             "$inc": {"fragments": fragments_dropped}},
            upsert=True,
        )

        return {
            "success": req.success,
            "hero_id": req.hero_id,
            "hero_name": hero.get("name"),
            "stage": req.stage,
            "is_boss": _constellation_stage_is_boss(req.stage),
            "new_highest_stage": new_highest,
            "fragments_dropped": fragments_dropped,
            "fragment_name": f"Frammenti d'Anima di {hero.get('name')}",
            "daily_slots_used": len(attempted),
            "daily_slots_left": max(0, CONSTELLATION_DAILY_HERO_LIMIT - len(attempted)),
        }

    # -------------- COSTELLAZIONE: SKIP (placeholder FASE 3) --------------
    @router.post("/sanctuary/constellation/skip/{hero_id}")
    async def constellation_skip(hero_id: str, current_user: dict = Depends(get_current_user)):
        """Placeholder: in FASE 3 permetterà di saltare direttamente al highest_stage
        già raggiunto. Per ora ritorna info diagnostiche senza side-effects.
        Sarà potenzialmente gated da VIP1+."""
        uid = current_user["id"]
        con = await db.user_constellation.find_one({"user_id": uid, "hero_id": hero_id})
        highest = con.get("highest_stage", 0) if con else 0
        return {
            "available": False,  # Non attivo in FASE 1
            "reason": "Feature disponibile in prossime versioni",
            "highest_stage": highest,
            "would_skip_to": highest,
            "vip_gated": True,  # placeholder
            "min_vip_level": 1,
        }
