"""
Migration script: Update all 30 heroes with new comprehensive stat system
New stats: hp, speed, magic_damage, physical_damage, magic_defense, physical_defense,
           healing, healing_received, damage_rate, penetration, dodge,
           crit_chance, crit_damage, hit_rate, combo_rate, block_rate
Elements: water, fire, earth, wind, thunder, light, shadow
"""
import asyncio
import os
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Rarity multiplier
RARITY_MULT = {1: 0.5, 2: 0.7, 3: 0.85, 4: 1.0, 5: 1.2, 6: 1.5}

# Class-based base stat profiles
CLASS_PROFILES = {
    "DPS": {
        "hp": 8000, "speed": 120,
        "physical_damage": 2200, "magic_damage": 1800,
        "physical_defense": 400, "magic_defense": 350,
        "healing": 0, "healing_received": 1.0,
        "damage_rate": 1.15, "penetration": 0.12,
        "dodge": 0.08, "crit_chance": 0.22, "crit_damage": 1.8,
        "hit_rate": 0.92, "combo_rate": 0.15, "block_rate": 0.05,
    },
    "Tank": {
        "hp": 15000, "speed": 90,
        "physical_damage": 1000, "magic_damage": 600,
        "physical_defense": 900, "magic_defense": 750,
        "healing": 0, "healing_received": 1.2,
        "damage_rate": 0.85, "penetration": 0.05,
        "dodge": 0.05, "crit_chance": 0.08, "crit_damage": 1.3,
        "hit_rate": 0.88, "combo_rate": 0.08, "block_rate": 0.25,
    },
    "Support": {
        "hp": 10000, "speed": 110,
        "physical_damage": 800, "magic_damage": 1400,
        "physical_defense": 500, "magic_defense": 650,
        "healing": 1800, "healing_received": 1.3,
        "damage_rate": 0.90, "penetration": 0.06,
        "dodge": 0.10, "crit_chance": 0.12, "crit_damage": 1.4,
        "hit_rate": 0.95, "combo_rate": 0.10, "block_rate": 0.10,
    },
}

# Per-hero customizations (element updates + stat variations)
HERO_OVERRIDES = {
    "Amaterasu": {"element": "fire", "variant": {"magic_damage": 1.3, "crit_chance": 1.2}},
    "Tsukuyomi": {"element": "shadow", "variant": {"physical_damage": 1.2, "crit_damage": 1.15, "penetration": 1.3}},
    "Susanoo": {"element": "thunder", "variant": {"hp": 1.1, "physical_defense": 1.2, "block_rate": 1.3}},
    "Izanami": {"element": "shadow", "variant": {"healing": 1.3, "magic_damage": 1.1, "speed": 1.1}},
    "Athena": {"element": "light", "variant": {"physical_defense": 1.3, "magic_defense": 1.2, "block_rate": 1.2}},
    "Aphrodite": {"element": "water", "variant": {"healing": 1.4, "healing_received": 1.2, "speed": 1.15}},
    "Artemis": {"element": "wind", "variant": {"physical_damage": 1.25, "speed": 1.2, "crit_chance": 1.15}},
    "Freya": {"element": "light", "variant": {"magic_damage": 1.2, "crit_damage": 1.2, "combo_rate": 1.3}},
    "Valkyrie": {"element": "thunder", "variant": {"hp": 1.15, "physical_defense": 1.15, "damage_rate": 1.1}},
    "Medusa": {"element": "earth", "variant": {"magic_damage": 1.3, "penetration": 1.4, "dodge": 0.8}},
    "Hera": {"element": "light", "variant": {"healing": 1.2, "magic_defense": 1.2, "hp": 1.1}},
    "Persephone": {"element": "shadow", "variant": {"magic_damage": 1.2, "penetration": 1.2, "crit_chance": 1.1}},
    "Nyx": {"element": "shadow", "variant": {"magic_damage": 1.25, "dodge": 1.3, "speed": 1.1}},
    "Demeter": {"element": "earth", "variant": {"healing": 1.3, "hp": 1.15, "healing_received": 1.15}},
    "Hecate": {"element": "shadow", "variant": {"magic_damage": 1.3, "crit_damage": 1.1, "penetration": 1.2}},
    "Selene": {"element": "light", "variant": {"healing": 1.2, "speed": 1.15, "magic_defense": 1.1}},
    "Sakuya": {"element": "water", "variant": {"healing": 1.15, "speed": 1.1, "dodge": 1.2}},
    "Kaguya": {"element": "light", "variant": {"magic_damage": 1.15, "crit_chance": 1.1, "hit_rate": 1.05}},
    "Inari": {"element": "fire", "variant": {"physical_damage": 1.1, "combo_rate": 1.3, "speed": 1.1}},
    "Benzaiten": {"element": "water", "variant": {"healing": 1.2, "magic_damage": 1.05, "speed": 1.1}},
    "Raijin": {"element": "thunder", "variant": {"physical_damage": 1.2, "speed": 1.2, "combo_rate": 1.2}},
    "Fujin": {"element": "wind", "variant": {"speed": 1.2, "dodge": 1.3, "physical_defense": 1.1}},
    "Iris": {"element": "light", "variant": {"healing": 1.1, "speed": 1.15, "magic_defense": 1.05}},
    "Echo": {"element": "wind", "variant": {"speed": 1.2, "combo_rate": 1.2, "dodge": 1.15}},
    "Daphne": {"element": "earth", "variant": {"hp": 1.2, "physical_defense": 1.15, "block_rate": 1.1}},
    "Chloris": {"element": "earth", "variant": {"healing": 1.1, "hp": 1.1}},
    "Aura": {"element": "wind", "variant": {"speed": 1.15, "dodge": 1.1}},
    "Hestia": {"element": "fire", "variant": {"healing": 1.15, "hp": 1.1}},
    "Nike": {"element": "thunder", "variant": {"physical_defense": 1.1, "block_rate": 1.15}},
    "Psyche": {"element": "water", "variant": {"healing": 1.1, "healing_received": 1.1}},
}


def generate_stats(hero_class: str, rarity: int, hero_name: str) -> dict:
    profile = CLASS_PROFILES.get(hero_class, CLASS_PROFILES["DPS"])
    mult = RARITY_MULT.get(rarity, 1.0)
    overrides = HERO_OVERRIDES.get(hero_name, {})
    variant = overrides.get("variant", {})

    stats = {}
    for stat, base_val in profile.items():
        val = base_val * mult
        # Apply hero-specific variant
        if stat in variant:
            val *= variant[stat]
        # Add small randomness (±3%)
        val *= random.uniform(0.97, 1.03)
        # Round appropriately
        if stat in ("hp",):
            stats[stat] = int(val)
        elif stat in ("speed", "physical_damage", "magic_damage", "physical_defense", "magic_defense", "healing"):
            stats[stat] = int(val)
        elif isinstance(base_val, float) and base_val < 5:
            stats[stat] = round(val, 3)
        else:
            stats[stat] = round(val, 2)

    return stats


async def migrate():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    db = client["divine_waifus"]

    heroes = await db.heroes.find({}).to_list(100)
    print(f"Migrating {len(heroes)} heroes to new stat system...")

    for hero in heroes:
        name = hero["name"]
        hero_class = hero.get("hero_class", "DPS")
        rarity = hero.get("rarity", 3)

        # Generate new stats
        new_stats = generate_stats(hero_class, rarity, name)

        # Get new element
        overrides = HERO_OVERRIDES.get(name, {})
        new_element = overrides.get("element", hero.get("element", "fire"))

        # Update hero
        await db.heroes.update_one(
            {"name": name},
            {"$set": {
                "base_stats": new_stats,
                "element": new_element,
            }}
        )
        print(f"  ✓ {rarity}★ {name:20s} [{hero_class:8s}] → {new_element:8s} | HP:{new_stats['hp']} PDMG:{new_stats['physical_damage']} MDMG:{new_stats['magic_damage']} SPD:{new_stats['speed']}")

    print(f"\n✅ Migration complete! {len(heroes)} heroes updated.")
    print("\nNew elements distribution:")
    for elem in ["fire", "water", "earth", "wind", "thunder", "light", "shadow"]:
        count = await db.heroes.count_documents({"element": elem})
        print(f"  {elem:8s}: {count}")


if __name__ == "__main__":
    asyncio.run(migrate())
