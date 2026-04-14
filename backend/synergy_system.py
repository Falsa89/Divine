"""
Divine Waifus - Team Synergy System
Mythological, elemental, class, and special synergies.
Extensible: add new synergies here when new heroes are added.
"""

# =====================================================================
# SYNERGY DEFINITIONS
# Each synergy has:
#   - id: unique identifier
#   - name: display name
#   - icon: emoji icon
#   - description: flavor text
#   - heroes: list of hero NAMES required (all must be present)
#   - min_required: minimum heroes from the list needed (default: all)
#   - buffs: dict of stat bonuses applied to the WHOLE team
#   - category: "mythological" | "elemental" | "class" | "special"
# =====================================================================

MYTHOLOGICAL_SYNERGIES = [
    # === JAPANESE PANTHEON ===
    {
        "id": "shinra_bansho",
        "name": "Shinra Bansho - Trinita Giapponese",
        "icon": "\u26E9\uFE0F",
        "description": "Amaterasu, Tsukuyomi e Susanoo: i tre figli di Izanagi uniti scatenano il potere primordiale.",
        "heroes": ["Amaterasu", "Tsukuyomi", "Susanoo"],
        "min_required": 3,
        "buffs": {"attack": 0.25, "magic_damage": 0.20, "speed": 0.10},
        "category": "mythological",
    },
    {
        "id": "izanagi_legacy",
        "name": "Eredita di Izanagi",
        "icon": "Luna",
        "description": "Izanami con i suoi figli divini. Il legame familiare rafforza lo spirito.",
        "heroes": ["Izanami", "Amaterasu", "Tsukuyomi", "Susanoo"],
        "min_required": 3,
        "buffs": {"hp": 0.15, "healing_received": 0.15, "ultimate_charge": 0.10},
        "category": "mythological",
    },
    {
        "id": "yokai_masters",
        "name": "Signori degli Yokai",
        "icon": "Fiore",
        "description": "Kaguya, Inari e Fujin: i maestri dello spirito giapponese.",
        "heroes": ["Kaguya", "Inari", "Fujin"],
        "min_required": 3,
        "buffs": {"dodge": 0.12, "crit_chance": 0.10, "speed": 0.08},
        "category": "mythological",
    },
    {
        "id": "shrine_maidens",
        "name": "Sacerdotesse del Tempio",
        "icon": "\u26E9\uFE0F",
        "description": "Sakuya, Benzaiten e Hestia: la benedizione delle sacerdotesse protegge il team.",
        "heroes": ["Sakuya", "Benzaiten", "Hestia"],
        "min_required": 3,
        "buffs": {"healing": 0.20, "magic_defense": 0.12, "hp": 0.08},
        "category": "mythological",
    },
    {
        "id": "storm_duo",
        "name": "Tempesta Divina",
        "icon": "\u26C8\uFE0F",
        "description": "Raijin e Fujin: tuono e vento uniti in una tempesta devastante.",
        "heroes": ["Raijin", "Fujin"],
        "min_required": 2,
        "buffs": {"attack": 0.15, "speed": 0.15, "penetration": 0.08},
        "category": "mythological",
    },

    # === GREEK PANTHEON ===
    {
        "id": "olympus_triad",
        "name": "Triade dell'Olimpo",
        "icon": "Tempio",
        "description": "Athena, Artemis e Hera: la potenza delle dee olimpiche unite.",
        "heroes": ["Athena", "Artemis", "Hera"],
        "min_required": 3,
        "buffs": {"physical_defense": 0.18, "crit_damage": 0.15, "healing": 0.12},
        "category": "mythological",
    },
    {
        "id": "underworld_queens",
        "name": "Regine degli Inferi",
        "icon": "Teschio",
        "description": "Persephone, Hecate e Nyx: le signore dell'oscurita corrompono i nemici.",
        "heroes": ["Persephone", "Hecate", "Nyx"],
        "min_required": 3,
        "buffs": {"magic_damage": 0.22, "penetration": 0.12, "lifesteal": 0.08},
        "category": "mythological",
    },
    {
        "id": "gorgon_huntress",
        "name": "Cacciatrice e Gorgone",
        "icon": "Serpente",
        "description": "Medusa e Artemis: la bestia e la cacciatrice in una danza mortale.",
        "heroes": ["Medusa", "Artemis"],
        "min_required": 2,
        "buffs": {"crit_chance": 0.15, "crit_damage": 0.20, "attack": 0.08},
        "category": "mythological",
    },
    {
        "id": "love_beauty",
        "name": "Amore e Bellezza",
        "icon": "Cuori",
        "description": "Aphrodite e Psyche: il legame eterno tra amore divino e mortale.",
        "heroes": ["Aphrodite", "Psyche"],
        "min_required": 2,
        "buffs": {"healing": 0.18, "healing_received": 0.15, "hp": 0.10},
        "category": "mythological",
    },
    {
        "id": "wisdom_victory",
        "name": "Saggezza e Vittoria",
        "icon": "Medaglia",
        "description": "Athena e Nike: la strategia incontra il trionfo.",
        "heroes": ["Athena", "Nike"],
        "min_required": 2,
        "buffs": {"physical_defense": 0.15, "block_rate": 0.12, "hp": 0.12},
        "category": "mythological",
    },

    # === NORSE PANTHEON ===
    {
        "id": "norse_warriors",
        "name": "Guerriere del Nord",
        "icon": "\u2694\uFE0F",
        "description": "Valkyrie e Freya: le guerriere del Valhalla scendono in battaglia.",
        "heroes": ["Valkyrie", "Freya"],
        "min_required": 2,
        "buffs": {"attack": 0.18, "physical_defense": 0.10, "crit_chance": 0.08},
        "category": "mythological",
    },

    # === CROSS-MYTHOLOGY ===
    {
        "id": "divine_mothers",
        "name": "Madri Divine",
        "icon": "Ibisco",
        "description": "Demeter, Hera e Izanami: le madri degli dei proteggono la vita.",
        "heroes": ["Demeter", "Hera", "Izanami"],
        "min_required": 3,
        "buffs": {"healing": 0.25, "hp": 0.15, "magic_defense": 0.10},
        "category": "mythological",
    },
    {
        "id": "moon_sisters",
        "name": "Sorelle della Luna",
        "icon": "Luna",
        "description": "Selene, Tsukuyomi e Kaguya: tre incarnazioni del potere lunare.",
        "heroes": ["Selene", "Tsukuyomi", "Kaguya"],
        "min_required": 3,
        "buffs": {"magic_damage": 0.20, "dodge": 0.10, "crit_damage": 0.15},
        "category": "mythological",
    },
    {
        "id": "shadow_embrace",
        "name": "Abbraccio dell'Ombra",
        "icon": "NuovaLuna",
        "description": "Izanami, Nyx e Hecate: tre dee oscure avvolgono il campo di battaglia.",
        "heroes": ["Izanami", "Nyx", "Hecate"],
        "min_required": 3,
        "buffs": {"magic_damage": 0.18, "lifesteal": 0.10, "penetration": 0.15},
        "category": "mythological",
    },
    {
        "id": "nature_guardians",
        "name": "Guardiane della Natura",
        "icon": "Erba",
        "description": "Demeter, Chloris e Daphne: le forze della terra si risvegliano.",
        "heroes": ["Demeter", "Chloris", "Daphne"],
        "min_required": 3,
        "buffs": {"hp": 0.20, "physical_defense": 0.15, "healing_received": 0.12},
        "category": "mythological",
    },
    {
        "id": "thunder_gods",
        "name": "Dei del Tuono",
        "icon": "\u26A1",
        "description": "Susanoo, Raijin e Nike: la furia del fulmine colpisce senza pieta.",
        "heroes": ["Susanoo", "Raijin", "Nike"],
        "min_required": 3,
        "buffs": {"attack": 0.20, "speed": 0.12, "crit_chance": 0.10},
        "category": "mythological",
    },
    {
        "id": "light_bearers",
        "name": "Portatrici di Luce",
        "icon": "\u2728",
        "description": "Amaterasu, Freya, Selene e Hera: la luce sacra guarisce e protegge.",
        "heroes": ["Amaterasu", "Freya", "Selene", "Hera"],
        "min_required": 3,
        "buffs": {"healing": 0.15, "magic_defense": 0.15, "hp": 0.10, "ultimate_charge": 0.08},
        "category": "mythological",
    },
    {
        "id": "wind_dancers",
        "name": "Danzatrici del Vento",
        "icon": "Vento",
        "description": "Aura, Echo e Artemis: veloci come il vento, impossibili da colpire.",
        "heroes": ["Aura", "Echo", "Artemis"],
        "min_required": 3,
        "buffs": {"speed": 0.20, "dodge": 0.15, "crit_chance": 0.10},
        "category": "mythological",
    },
]

# =====================================================================
# ELEMENTAL SYNERGIES - Activated by having X heroes of same element
# =====================================================================
ELEMENTAL_SYNERGIES = {
    2: {"name": "Risonanza {element}", "icon": "F", "buffs": {"attack": 0.05, "hp": 0.05}},
    3: {"name": "Dominio {element}", "icon": "FF", "buffs": {"attack": 0.10, "magic_damage": 0.10, "hp": 0.08}},
    4: {"name": "Supremazia {element}", "icon": "FFF", "buffs": {"attack": 0.18, "magic_damage": 0.18, "hp": 0.12, "penetration": 0.08}},
    5: {"name": "Apoteosi {element}", "icon": "Stella", "buffs": {"attack": 0.25, "magic_damage": 0.25, "hp": 0.15, "penetration": 0.12, "speed": 0.10}},
}

ELEMENT_NAMES = {
    "fire": "del Fuoco", "water": "dell'Acqua", "earth": "della Terra",
    "wind": "del Vento", "thunder": "del Tuono", "light": "della Luce",
    "shadow": "dell'Ombra",
}

ELEMENT_ICONS = {
    "fire": "F", "water": "Goccia", "earth": "Roccia",
    "wind": "Aria", "thunder": "\u26A1", "light": "\u2728",
    "shadow": "NuovaLuna",
}

# =====================================================================
# CLASS SYNERGIES - Activated by class composition
# =====================================================================
CLASS_SYNERGIES = [
    {
        "id": "balanced_force",
        "name": "Forza Bilanciata",
        "icon": "\u2696\uFE0F",
        "description": "Almeno 1 Tank, 1 DPS e 1 Support nel team.",
        "condition": {"Tank": 1, "DPS": 1, "Support": 1},
        "buffs": {"hp": 0.08, "attack": 0.08, "healing": 0.08},
    },
    {
        "id": "perfect_formation",
        "name": "Formazione Perfetta",
        "icon": "Trofeo",
        "description": "Almeno 2 Tank, 3 DPS e 2 Support nel team.",
        "condition": {"Tank": 2, "DPS": 3, "Support": 2},
        "buffs": {"hp": 0.12, "attack": 0.12, "healing": 0.12, "speed": 0.05},
    },
    {
        "id": "full_offense",
        "name": "Assalto Totale",
        "icon": "\u2694\uFE0F",
        "description": "5 o piu DPS nel team.",
        "condition": {"DPS": 5},
        "buffs": {"attack": 0.25, "crit_chance": 0.15, "crit_damage": 0.20},
    },
    {
        "id": "iron_fortress",
        "name": "Fortezza di Ferro",
        "icon": "Scudo",
        "description": "4 o piu Tank nel team.",
        "condition": {"Tank": 4},
        "buffs": {"hp": 0.30, "physical_defense": 0.25, "magic_defense": 0.15, "block_rate": 0.10},
    },
    {
        "id": "holy_chorus",
        "name": "Coro Sacro",
        "icon": "CuoreVerde",
        "description": "4 o piu Support nel team.",
        "condition": {"Support": 4},
        "buffs": {"healing": 0.30, "hp": 0.20, "speed": 0.10, "ultimate_charge": 0.15},
    },
]

# =====================================================================
# ELEMENT ADVANTAGE SYSTEM (for Tower and battles)
# =====================================================================
ELEMENT_ADVANTAGES = {
    "fire": {"strong": ["wind", "earth"], "weak": ["water"]},
    "water": {"strong": ["fire"], "weak": ["thunder", "earth"]},
    "earth": {"strong": ["water", "thunder"], "weak": ["fire", "wind"]},
    "wind": {"strong": ["earth"], "weak": ["fire", "thunder"]},
    "thunder": {"strong": ["water", "wind"], "weak": ["earth"]},
    "light": {"strong": ["shadow"], "weak": ["shadow"]},
    "shadow": {"strong": ["light"], "weak": ["light"]},
}
ELEMENT_ADVANTAGE_BONUS = 0.25   # +25% damage when strong
ELEMENT_DISADVANTAGE_PENALTY = 0.15  # -15% damage when weak


def calculate_team_synergies(hero_names: list[str], hero_elements: list[str], hero_classes: list[str]) -> dict:
    """
    Given lists of hero names, elements, and classes in a team,
    return all active synergies and cumulative buffs.
    """
    active_synergies = []
    total_buffs: dict[str, float] = {}

    # 1) Check Mythological Synergies
    name_set = set(hero_names)
    for syn in MYTHOLOGICAL_SYNERGIES:
        matching = [h for h in syn["heroes"] if h in name_set]
        min_req = syn.get("min_required", len(syn["heroes"]))
        if len(matching) >= min_req:
            active_synergies.append({
                "id": syn["id"],
                "name": syn["name"],
                "icon": syn["icon"],
                "description": syn["description"],
                "category": "mythological",
                "heroes_matched": matching,
                "buffs": syn["buffs"],
            })
            for stat, val in syn["buffs"].items():
                total_buffs[stat] = total_buffs.get(stat, 0) + val

    # 2) Check Elemental Synergies
    from collections import Counter
    elem_counts = Counter(hero_elements)
    for elem, count in elem_counts.items():
        if count < 2:
            continue
        # Find highest tier that applies
        best_tier = 0
        for tier in sorted(ELEMENTAL_SYNERGIES.keys()):
            if count >= tier:
                best_tier = tier
        if best_tier > 0:
            syn_template = ELEMENTAL_SYNERGIES[best_tier]
            elem_name = ELEMENT_NAMES.get(elem, elem)
            elem_icon = ELEMENT_ICONS.get(elem, "\u2B50")
            active_synergies.append({
                "id": f"elem_{elem}_{best_tier}",
                "name": syn_template["name"].format(element=elem_name),
                "icon": elem_icon,
                "description": f"{count} eroi {elem_name} nel team (livello {best_tier})",
                "category": "elemental",
                "element": elem,
                "count": count,
                "tier": best_tier,
                "buffs": syn_template["buffs"],
            })
            for stat, val in syn_template["buffs"].items():
                total_buffs[stat] = total_buffs.get(stat, 0) + val

    # 3) Check Class Synergies
    class_counts = Counter(hero_classes)
    for syn in CLASS_SYNERGIES:
        met = all(class_counts.get(cls, 0) >= req for cls, req in syn["condition"].items())
        if met:
            active_synergies.append({
                "id": syn["id"],
                "name": syn["name"],
                "icon": syn["icon"],
                "description": syn["description"],
                "category": "class",
                "buffs": syn["buffs"],
            })
            for stat, val in syn["buffs"].items():
                total_buffs[stat] = total_buffs.get(stat, 0) + val

    return {
        "active_synergies": active_synergies,
        "total_buffs": total_buffs,
        "synergy_count": len(active_synergies),
    }


def get_element_multiplier(attacker_element: str, defender_element: str) -> float:
    """Returns damage multiplier based on element advantage."""
    adv = ELEMENT_ADVANTAGES.get(attacker_element, {})
    if defender_element in adv.get("strong", []):
        return 1.0 + ELEMENT_ADVANTAGE_BONUS
    elif defender_element in adv.get("weak", []):
        return 1.0 - ELEMENT_DISADVANTAGE_PENALTY
    return 1.0


def get_all_synergy_definitions() -> dict:
    """Return all synergy definitions for the frontend guide."""
    return {
        "mythological": [
            {
                "id": s["id"], "name": s["name"], "icon": s["icon"],
                "description": s["description"], "heroes": s["heroes"],
                "min_required": s.get("min_required", len(s["heroes"])),
                "buffs": s["buffs"],
            }
            for s in MYTHOLOGICAL_SYNERGIES
        ],
        "elemental_tiers": {
            str(k): {"name": v["name"], "buffs": v["buffs"]}
            for k, v in ELEMENTAL_SYNERGIES.items()
        },
        "class": [
            {"id": s["id"], "name": s["name"], "icon": s["icon"],
             "description": s["description"], "condition": s["condition"], "buffs": s["buffs"]}
            for s in CLASS_SYNERGIES
        ],
        "element_advantages": ELEMENT_ADVANTAGES,
    }
