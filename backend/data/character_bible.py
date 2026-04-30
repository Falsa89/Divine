"""
Divine Waifus — Character Bible (RM1.12 — Phase 1)
══════════════════════════════════════════════════════════════════════════════
Source of truth statica per il roster ufficiale al lancio:
    - 100 launch_base heroes
    - +1 launch_extra_premium hero (Borea), fuori dal conteggio dei 100

CONTRATTO:
    Questo modulo è IMPORT-SAFE e NON tocca il database.
    Non fa side effect, non scrive su DB, non interagisce col runtime.
    Definisce solo strutture dati statiche + helper di normalizzazione.

USAGE FUTURO (non in questo task):
    from data.character_bible import (
        CHARACTER_BIBLE, CHARACTER_BIBLE_BY_ID,
        LAUNCH_BASE_HERO_IDS, EXTRA_PREMIUM_HERO_IDS,
        normalize_element, normalize_role, get_max_stars,
        get_character_bible_entry,
    )

NOTE OPERATIVE:
    - Element naming canonico: 'water', 'fire', 'earth', 'wind',
      'lightning', 'light', 'dark'
      Aliases legacy DB (auto-mappati): 'thunder' → 'lightning', 'shadow' → 'dark'
    - Role canonici: tank, dps_melee, dps_ranged, mage_aoe, assassin_burst,
      support_buffer, healer, control_debuff, hybrid_special.
      Aliases legacy DB: 'Tank'/'tank' → 'tank', 'DPS'/'dps' → 'dps_melee',
      'Support'/'support' → 'support_buffer'.
    - Native rarity → max stars: 1→4, 2→6, 3→8, 4→10, 5→12, 6→15.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Set


# ════════════════════════════════════════════════════════════════════════
# CANONICAL ENUMS / CONSTANTS
# ════════════════════════════════════════════════════════════════════════

CANONICAL_ELEMENTS: Set[str] = {
    "water", "fire", "earth", "wind", "lightning", "light", "dark",
}

# Aliases legacy → canonical. Usati da normalize_element() per
# tollerare dati storici nel DB. NON migra il DB; serve solo a confrontare.
ELEMENT_ALIASES: Dict[str, str] = {
    "thunder": "lightning",
    "shadow": "dark",
    # idempotenti (canonici → se stessi)
    "water": "water", "fire": "fire", "earth": "earth", "wind": "wind",
    "lightning": "lightning", "light": "light", "dark": "dark",
}

CANONICAL_ROLES: Set[str] = {
    "tank",
    "dps_melee",
    "dps_ranged",
    "mage_aoe",
    "assassin_burst",
    "support_buffer",
    "healer",
    "control_debuff",
    "hybrid_special",
}

# Aliases legacy. Mappature scelte in modo conservativo:
#   - DPS legacy → 'dps_melee' come default safe (la maggior parte dei
#     vecchi DPS è melee; per i ranged/mage si dovrà fare reclassify nelle
#     fasi successive di import).
#   - Support legacy → 'support_buffer' (Hera che è healer è gestita
#     a parte come dev_test).
ROLE_ALIASES: Dict[str, str] = {
    "tank": "tank", "Tank": "tank", "TANK": "tank",
    "dps": "dps_melee", "DPS": "dps_melee",
    "support": "support_buffer", "Support": "support_buffer",
    # canonici → se stessi
    "dps_melee": "dps_melee",
    "dps_ranged": "dps_ranged",
    "mage_aoe": "mage_aoe",
    "assassin_burst": "assassin_burst",
    "support_buffer": "support_buffer",
    "healer": "healer",
    "control_debuff": "control_debuff",
    "hybrid_special": "hybrid_special",
}

CANONICAL_FACTIONS: Set[str] = {
    "greek",
    "norse",
    "egyptian",
    "japanese_yokai",
    "celtic",
    "angelic",
    "demonic",
    "creature_beast",
    "cursed",
    "arcane",
    "mesopotamian",
    "primordial",
    "tides",
}

# Alias legacy DB: il vecchio campo 'japanese' nel DB rimane valido come
# alias per 'japanese_yokai'. Non riscriviamo il DB in questo task.
FACTION_ALIASES: Dict[str, str] = {
    "japanese": "japanese_yokai",
    # canonici → se stessi
    **{f: f for f in CANONICAL_FACTIONS},
}

NATIVE_RARITY_MAX_STARS: Dict[int, int] = {
    1: 4,
    2: 6,
    3: 8,
    4: 10,
    5: 12,
    6: 15,
}

VALID_RELEASE_GROUPS: Set[str] = {"launch_base", "launch_extra_premium"}


# ════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════

def normalize_element(value: Optional[str]) -> Optional[str]:
    """Normalizza un element string → canonical (water/fire/earth/wind/
    lightning/light/dark). Ritorna None se non riconosciuto."""
    if value is None:
        return None
    key = str(value).strip().lower()
    return ELEMENT_ALIASES.get(key)


def normalize_role(value: Optional[str]) -> Optional[str]:
    """Normalizza un role string → canonical role. Tollera variants
    case-sensitive (Tank/DPS/Support legacy). Ritorna None se non
    riconosciuto."""
    if value is None:
        return None
    raw = str(value).strip()
    if raw in ROLE_ALIASES:
        return ROLE_ALIASES[raw]
    lowered = raw.lower()
    return ROLE_ALIASES.get(lowered)


def normalize_faction(value: Optional[str]) -> Optional[str]:
    """Normalizza un faction string → canonical faction. Ritorna None se
    non riconosciuto."""
    if value is None:
        return None
    key = str(value).strip().lower()
    return FACTION_ALIASES.get(key)


def get_max_stars(native_rarity: int) -> Optional[int]:
    """Restituisce il max_stars ufficiale per la rarity nativa indicata."""
    return NATIVE_RARITY_MAX_STARS.get(int(native_rarity))


def get_character_bible_entry(hero_id: str) -> Optional[Dict[str, Any]]:
    """Lookup veloce di un'entry per id slug. Ritorna None se non esiste."""
    return CHARACTER_BIBLE_BY_ID.get(hero_id)


# ════════════════════════════════════════════════════════════════════════
# CHARACTER BIBLE — 100 launch base + Borea extra premium
# ════════════════════════════════════════════════════════════════════════
# Schema entry:
#   {
#     "id": str (slug canonico),
#     "display_name": str,
#     "native_rarity": int (1..6),
#     "max_stars": int (deve combaciare NATIVE_RARITY_MAX_STARS[native_rarity]),
#     "element": str (canonico),
#     "role": str (canonico),
#     "faction": str (canonico),
#     "origin_group": str,
#     "category": str,
#     "release_group": "launch_base" | "launch_extra_premium",
#   }
# ════════════════════════════════════════════════════════════════════════

def _e(
    id: str, display_name: str, native_rarity: int, element: str, role: str,
    faction: str, origin_group: str, category: str,
    release_group: str = "launch_base",
) -> Dict[str, Any]:
    """Factory shorthand per ridurre il rumore visivo nelle definizioni."""
    return {
        "id": id,
        "display_name": display_name,
        "native_rarity": native_rarity,
        "max_stars": NATIVE_RARITY_MAX_STARS[native_rarity],
        "element": element,
        "role": role,
        "faction": faction,
        "origin_group": origin_group,
        "category": category,
        "release_group": release_group,
    }


# ── 1★ launch base (8) ────────────────────────────────────────────────
_BIBLE_1_STAR: List[Dict[str, Any]] = [
    _e("greek_phalanx_recruit",          "Recluta di Falange",   1, "earth",     "tank",            "greek",          "phalanx",            "common_unit"),
    _e("demonic_infernal_handmaiden",    "Ancella Infernale",    1, "fire",      "dps_melee",       "demonic",        "infernal_servants",  "common_unit"),
    _e("egyptian_nile_guard",            "Guardia del Nilo",     1, "water",     "dps_melee",       "egyptian",       "nile_guardians",     "common_unit"),
    _e("celtic_forest_archer",           "Arciera di Bosco",     1, "wind",      "dps_ranged",      "celtic",         "forest_warriors",    "common_unit"),
    _e("norse_rune_initiate",            "Iniziata Runica",      1, "lightning", "mage_aoe",        "norse",          "rune_acolytes",      "common_unit"),
    _e("angelic_sanctuary_acolyte",      "Accolita del Santuario", 1, "light",   "support_buffer",  "angelic",        "sanctuary",          "common_unit"),
    _e("angelic_sacred_novice",          "Novizia Sacra",        1, "light",     "healer",          "angelic",        "sanctuary",          "common_unit"),
    _e("yokai_veiled_spirit",            "Spirito Velato",       1, "dark",      "control_debuff",  "japanese_yokai", "minor_spirits",      "folklore_spirit"),
]

# ── 2★ launch base (12) ───────────────────────────────────────────────
_BIBLE_2_STAR: List[Dict[str, Any]] = [
    _e("egyptian_temple_guardian",       "Guardiana del Tempio", 2, "earth",     "tank",            "egyptian",       "temple_guardians",   "mythic_archetype"),
    _e("norse_valhalla_warden",          "Custode del Valhalla", 2, "wind",      "tank",            "norse",          "valhalla",           "mythic_archetype"),
    _e("egyptian_desert_blade",          "Lama del Deserto",     2, "fire",      "dps_melee",       "egyptian",       "desert_warriors",    "mythic_archetype"),
    _e("celtic_menhir_warrior",          "Guerriera dei Menhir", 2, "earth",     "dps_melee",       "celtic",         "menhir_clans",       "mythic_archetype"),
    _e("egyptian_oasis_markswoman",      "Tiratrice dell'Oasi",  2, "water",     "dps_ranged",      "egyptian",       "oasis_guardians",    "mythic_archetype"),
    _e("yokai_huntress",                 "Cacciatrice Yokai",    2, "wind",      "dps_ranged",      "japanese_yokai", "yokai_hunters",      "mythic_archetype"),
    _e("yokai_thunder_novice",           "Novizia del Tuono",    2, "lightning", "mage_aoe",        "japanese_yokai", "storm_acolytes",     "mythic_archetype"),
    _e("yokai_shinobi_shadow",           "Ombra Shinobi",        2, "dark",      "assassin_burst",  "japanese_yokai", "shinobi",            "mythic_archetype"),
    _e("angelic_cantor",                 "Cantora Angelica",     2, "light",     "support_buffer",  "angelic",        "celestial_choir",    "angel"),
    _e("egyptian_nile_healer",           "Curatrice del Nilo",   2, "water",     "healer",          "egyptian",       "nile_priesthood",    "mythic_archetype"),
    _e("cursed_bone_sibyl",              "Sibilla d'Ossa",       2, "dark",      "control_debuff",  "cursed",         "bone_omens",         "cursed_entity"),
    _e("demonic_infernal_adept",         "Adepta Infernale",     2, "fire",      "hybrid_special",  "demonic",        "infernal_adepts",    "demon"),
]

# ── 3★ launch base (24) ───────────────────────────────────────────────
_BIBLE_3_STAR: List[Dict[str, Any]] = [
    _e("greek_hoplite",                  "Hoplite",              3, "earth",     "tank",            "greek",          "phalanx",            "mythic_archetype"),
    _e("norse_berserker",                "Berserker",            3, "fire",      "dps_melee",       "norse",          "berserkers",         "mythic_archetype"),
    _e("celtic_archer",                  "Arciera",              3, "wind",      "dps_ranged",      "celtic",         "forest_warriors",    "mythic_archetype"),
    _e("angelic_priestess",              "Sacerdotessa",         3, "light",     "healer",          "angelic",        "sanctuary",          "mythic_archetype"),
    _e("arcane_lightning_enchantress",   "Incantatrice della Folgore", 3, "lightning", "mage_aoe",  "arcane",         "storm_magic",        "mythic_archetype"),
    _e("yokai_night_assassin",           "Assassina della Notte",3, "dark",      "assassin_burst",  "japanese_yokai", "shadow_blades",      "mythic_archetype"),
    _e("creature_coral_guardian",        "Guardiana di Corallo", 3, "water",     "tank",            "creature_beast", "tides",              "mythic_creature"),
    _e("celtic_dolmen_guardian",         "Guardiana dei Dolmen", 3, "earth",     "tank",            "celtic",         "dolmens",            "mythic_archetype"),
    _e("angelic_cherubic_warden",        "Custode Cherubica",    3, "light",     "tank",            "angelic",        "cherubim",           "angel"),
    _e("norse_thunder_spear",            "Lancia del Tuono",     3, "lightning", "dps_melee",       "norse",          "storm_warriors",     "mythic_archetype"),
    _e("norse_ragnarok_she_wolf",        "Lupa del Ragnarok",    3, "fire",      "dps_melee",       "norse",          "ragnarok_beasts",    "mythic_creature"),
    _e("greek_chthonic_gladiatrix",      "Gladiatrice Ctonia",   3, "earth",     "dps_melee",       "greek",          "chthonic_warriors",  "mythic_archetype"),
    _e("tides_corsair",                  "Corsara delle Maree",  3, "water",     "dps_ranged",      "creature_beast", "tides",              "mythic_archetype"),
    _e("celtic_peak_huntress",           "Cacciatrice dei Picchi", 3, "wind",    "dps_ranged",      "celtic",         "mountain_clans",     "mythic_archetype"),
    _e("egyptian_tide_sibyl",            "Sibilla delle Maree",  3, "water",     "mage_aoe",        "egyptian",       "oracle_tides",       "mythic_archetype"),
    _e("norse_runic_pyromancer",         "Piromante Runica",     3, "fire",      "mage_aoe",        "norse",          "rune_magic",         "mythic_archetype"),
    _e("yokai_kitsune_blade",            "Lama Kitsune",         3, "wind",      "assassin_burst",  "japanese_yokai", "kitsune",            "folklore_spirit"),
    _e("egyptian_serpent_dancer",        "Danzatrice del Serpente", 3, "dark",   "assassin_burst",  "egyptian",       "serpent_cult",       "mythic_archetype"),
    _e("greek_sanctuary_muse",           "Musa del Santuario",   3, "light",     "support_buffer",  "greek",          "muses",              "mythic_archetype"),
    _e("celtic_moor_druidess",           "Druida della Brughiera", 3, "earth",   "support_buffer",  "celtic",         "druids",             "mythic_archetype"),
    _e("norse_rune_keeper",              "Custode delle Rune",   3, "lightning", "support_buffer",  "norse",          "rune_keepers",       "mythic_archetype"),
    _e("tides_healer",                   "Guaritrice delle Maree", 3, "water",   "healer",          "creature_beast", "tides",              "mythic_archetype"),
    _e("yokai_exorcist",                 "Esorcista Yokai",      3, "light",     "control_debuff",  "japanese_yokai", "exorcists",          "mythic_archetype"),
    _e("cursed_famine_herald_minor",     "Aralda della Carestia",3, "dark",      "control_debuff",  "cursed",         "famine_omens",       "cursed_entity"),
]

# ── 4★ launch base (24) ───────────────────────────────────────────────
_BIBLE_4_STAR: List[Dict[str, Any]] = [
    _e("angelic_seraph",                 "Serafino",             4, "light",     "support_buffer",  "angelic",        "seraphim",           "angel"),
    _e("greek_amazon_of_ares",           "Amazzone di Ares",     4, "fire",      "dps_melee",       "greek",          "ares_warriors",      "legendary_hero"),
    _e("egyptian_priestess_of_sekhmet",  "Sacerdotessa di Sekhmet", 4, "fire",   "mage_aoe",        "egyptian",       "sekhmet_cult",       "mythic_archetype"),
    _e("norse_shieldbreaker_valkyrie",   "Valchiria Spezzascudi",4, "wind",      "dps_melee",       "norse",          "valkyries",          "legendary_hero"),
    _e("yokai_storm_onmyoji",            "Onmyoji delle Tempeste", 4, "lightning", "mage_aoe",      "japanese_yokai", "onmyoji",            "mythic_archetype"),
    _e("greek_labyrinth_guardian",       "Guardiana del Labirinto", 4, "earth",  "tank",            "greek",          "labyrinth",          "mythic_creature"),
    _e("egyptian_duat_sentinel",         "Sentinella del Duat",  4, "dark",      "tank",            "egyptian",       "duat",               "mythic_archetype"),
    _e("norse_valhalla_shield",          "Scudo del Valhalla",   4, "earth",     "tank",            "norse",          "valhalla",           "mythic_archetype"),
    _e("cursed_threshold_keeper",        "Custode della Soglia", 4, "dark",      "tank",            "cursed",         "threshold",          "cursed_entity"),
    _e("creature_phoenix_daughter",      "Figlia della Fenice",  4, "fire",      "dps_ranged",      "creature_beast", "phoenix",            "mythic_creature"),
    _e("celtic_thunder_huntress",        "Cacciatrice del Tuono",4, "lightning", "dps_ranged",      "celtic",         "storm_hunters",      "mythic_archetype"),
    _e("yokai_red_moon_blade",           "Lama della Luna Rossa",4, "dark",      "assassin_burst",  "japanese_yokai", "moon_blades",        "mythic_archetype"),
    _e("celtic_mist_predator",           "Predatrice delle Nebbie", 4, "wind",   "assassin_burst",  "celtic",         "mist_spirits",       "folklore_spirit"),
    _e("greek_oracle_of_delphi",         "Oracolo di Delfi",     4, "light",     "support_buffer",  "greek",          "delphi",             "mythic_archetype"),
    _e("norse_ancient_rune_cantor",      "Cantora delle Rune Antiche", 4, "lightning", "support_buffer", "norse",     "rune_magic",         "mythic_archetype"),
    _e("angelic_sacred_sun_healer",      "Guaritrice del Sole Sacro", 4, "light", "healer",         "angelic",        "sacred_sun",         "angel"),
    _e("celtic_menhir_shamaness",        "Sciamana dei Menhir",  4, "earth",     "healer",          "celtic",         "menhir_clans",       "mythic_archetype"),
    _e("cursed_twilight_witch",          "Strega del Vespro",    4, "dark",      "control_debuff",  "cursed",         "twilight_curses",    "cursed_entity"),
    _e("yokai_chain_miko",               "Miko delle Catene",    4, "lightning", "control_debuff",  "japanese_yokai", "binding_rituals",    "mythic_archetype"),
    _e("creature_lesser_hydra",          "Idra Minore",          4, "water",     "hybrid_special",  "creature_beast", "hydra",              "mythic_creature"),
    _e("egyptian_tide_lady",             "Dama delle Maree",     4, "water",     "mage_aoe",        "egyptian",       "tides",              "mythic_archetype"),
    _e("demonic_sacred_brazier_pyromancer", "Piromante del Braciere Sacro", 4, "fire", "mage_aoe",  "demonic",        "infernal_fire",      "demon"),
    _e("creature_depths_warrior",        "Guerriera delle Profondita", 4, "water", "dps_melee",     "creature_beast", "depths",             "mythic_archetype"),
    _e("creature_cyclone_daughter",      "Figlia del Ciclone",   4, "wind",      "dps_melee",       "creature_beast", "storm_beasts",       "mythic_creature"),
]

# ── 5★ launch base (20) ───────────────────────────────────────────────
_BIBLE_5_STAR: List[Dict[str, Any]] = [
    _e("greek_nemean_lioness",           "Leonessa Nemea",       5, "earth",     "tank",            "greek",          "nemean_lion",        "mythic_creature"),
    _e("norse_rime_jotunn",              "Jotunn delle Brine",   5, "water",     "tank",            "norse",          "jotunn",             "titan"),
    _e("angelic_bastion_angel",          "Angelo dei Bastioni",  5, "light",     "tank",            "angelic",        "bastions",           "angel"),
    _e("norse_dawn_valkyrie",            "Valchiria dell'Alba",  5, "wind",      "dps_melee",       "norse",          "valkyries",          "legendary_hero"),
    _e("egyptian_claw_of_sekhmet",       "Artiglio di Sekhmet",  5, "fire",      "dps_melee",       "egyptian",       "sekhmet_cult",       "mythic_archetype"),
    _e("greek_atalanta",                 "Atalanta",             5, "wind",      "dps_ranged",      "greek",          "heroic_hunters",     "legendary_hero"),
    _e("greek_circe",                    "Circe",                5, "dark",      "mage_aoe",        "greek",          "sorceresses",        "legendary_hero"),
    _e("japanese_miko_of_raijin",        "Miko di Raijin",       5, "lightning", "mage_aoe",        "japanese_yokai", "raijin_shrine",      "mythic_archetype"),
    _e("demonic_gehenna_witch",          "Strega della Geenna",  5, "fire",      "mage_aoe",        "demonic",        "gehenna",            "demon"),
    _e("egyptian_bastet",                "Bastet",               5, "lightning", "assassin_burst",  "egyptian",       "feline_deities",     "deity"),
    _e("yokai_oni_kunoichi",             "Kunoichi Oni",         5, "dark",      "assassin_burst",  "japanese_yokai", "oni",                "folklore_spirit"),
    _e("greek_nike",                     "Nike",                 5, "light",     "support_buffer",  "greek",          "victory",            "deity"),
    _e("norse_volva_of_fate",            "Volva del Fato",       5, "lightning", "support_buffer",  "norse",          "fate_seers",         "mythic_archetype"),
    _e("norse_eir",                      "Eir",                  5, "light",     "healer",          "norse",          "healing_deities",    "deity"),
    _e("greek_medusa",                   "Medusa",               5, "earth",     "control_debuff",  "greek",          "gorgons",            "mythic_creature"),
    _e("celtic_mist_banshee",            "Banshee delle Nebbie", 5, "wind",      "control_debuff",  "celtic",         "banshees",           "folklore_spirit"),
    _e("yokai_yuki_onna",                "Yuki-Onna",            5, "water",     "control_debuff",  "japanese_yokai", "snow_spirits",       "folklore_spirit"),
    _e("creature_crimson_phoenix",       "Fenice Cremisi",       5, "fire",      "hybrid_special",  "creature_beast", "phoenix",            "mythic_creature"),
    _e("creature_lernaean_hydra",        "Idra di Lerna",        5, "water",     "hybrid_special",  "creature_beast", "hydra",              "mythic_creature"),
    _e("cursed_pestilence_herald",       "Aralda della Pestilenza", 5, "dark",   "hybrid_special",  "cursed",         "pestilence_omens",   "cursed_entity"),
]

# ── 6★ launch base (12) ───────────────────────────────────────────────
_BIBLE_6_STAR: List[Dict[str, Any]] = [
    _e("greek_athena",                   "Atena",                6, "earth",     "tank",            "greek",          "olympian",           "deity"),
    _e("mesopotamian_tiamat",            "Tiamat",               6, "water",     "tank",            "mesopotamian",   "primordial",         "primordial"),
    _e("egyptian_sekhmet",               "Sekhmet",              6, "fire",      "dps_melee",       "egyptian",       "solar_lioness",      "deity"),
    _e("greek_artemis",                  "Artemide",             6, "wind",      "dps_ranged",      "greek",          "olympian",           "deity"),
    _e("japanese_raijin",                "Raijin",               6, "lightning", "mage_aoe",        "japanese_yokai", "kami",               "deity"),
    _e("japanese_susanoo",               "Susanoo",              6, "lightning", "assassin_burst",  "japanese_yokai", "kami",               "deity"),
    _e("celtic_morrigan",                "Morrigan",             6, "wind",      "assassin_burst",  "celtic",         "war_fate",           "deity"),
    _e("greek_gaia",                     "Gaia",                 6, "earth",     "support_buffer",  "greek",          "primordial",         "primordial"),
    _e("japanese_amaterasu",             "Amaterasu",            6, "light",     "support_buffer",  "japanese_yokai", "kami",               "deity"),
    _e("egyptian_isis",                  "Iside",                6, "light",     "healer",          "egyptian",       "divine_mother",      "deity"),
    _e("cursed_pestilence_horseman",     "Pestilenza, Cavaliere dell'Apocalisse", 6, "dark", "control_debuff", "cursed", "apocalypse_horsemen", "personification"),
    _e("primordial_nyx",                 "Nyx",                  6, "dark",      "hybrid_special",  "primordial",     "night",              "primordial"),
]

# ── Extra premium (1, fuori dai 100) ──────────────────────────────────
_BIBLE_EXTRA_PREMIUM: List[Dict[str, Any]] = [
    _e(
        "greek_borea", "Borea", 6, "wind", "mage_aoe",
        "greek", "anemoi", "deity",
        release_group="launch_extra_premium",
    ),
]


# ════════════════════════════════════════════════════════════════════════
# AGGREGATES
# ════════════════════════════════════════════════════════════════════════

CHARACTER_BIBLE: List[Dict[str, Any]] = (
    _BIBLE_1_STAR
    + _BIBLE_2_STAR
    + _BIBLE_3_STAR
    + _BIBLE_4_STAR
    + _BIBLE_5_STAR
    + _BIBLE_6_STAR
    + _BIBLE_EXTRA_PREMIUM
)

CHARACTER_BIBLE_BY_ID: Dict[str, Dict[str, Any]] = {
    e["id"]: e for e in CHARACTER_BIBLE
}

LAUNCH_BASE_HERO_IDS: List[str] = [
    e["id"] for e in CHARACTER_BIBLE if e["release_group"] == "launch_base"
]
EXTRA_PREMIUM_HERO_IDS: List[str] = [
    e["id"] for e in CHARACTER_BIBLE if e["release_group"] == "launch_extra_premium"
]


# ════════════════════════════════════════════════════════════════════════
# IMPORT-SAFE VALIDATION
# ════════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS = (
    "id", "display_name", "native_rarity", "max_stars", "element",
    "role", "faction", "origin_group", "category", "release_group",
)


def validate_character_bible() -> Dict[str, Any]:
    """Validazione strutturale completa. Ritorna un dict con stato + dettagli.
    Non solleva eccezioni: pensata per essere chiamabile sia da CLI che da
    runtime (e.g. health-check) senza side-effect.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Required fields + canonical values
    seen_ids: Set[str] = set()
    for entry in CHARACTER_BIBLE:
        for f in REQUIRED_FIELDS:
            if f not in entry or entry[f] in (None, ""):
                errors.append(f"missing field '{f}' on entry {entry.get('id', '?')}")
        eid = entry.get("id", "")
        if eid in seen_ids:
            errors.append(f"duplicate id: {eid}")
        seen_ids.add(eid)

        nr = entry.get("native_rarity")
        ms = entry.get("max_stars")
        expected_ms = NATIVE_RARITY_MAX_STARS.get(int(nr)) if nr else None
        if expected_ms != ms:
            errors.append(
                f"max_stars mismatch on {eid}: native_rarity={nr} "
                f"expects {expected_ms} but got {ms}"
            )

        if entry.get("element") not in CANONICAL_ELEMENTS:
            errors.append(f"non-canonical element on {eid}: {entry.get('element')}")
        if entry.get("role") not in CANONICAL_ROLES:
            errors.append(f"non-canonical role on {eid}: {entry.get('role')}")
        if entry.get("faction") not in CANONICAL_FACTIONS:
            errors.append(f"non-canonical faction on {eid}: {entry.get('faction')}")
        if entry.get("release_group") not in VALID_RELEASE_GROUPS:
            errors.append(f"invalid release_group on {eid}: {entry.get('release_group')}")

    # Counts
    base_count = len(LAUNCH_BASE_HERO_IDS)
    extra_count = len(EXTRA_PREMIUM_HERO_IDS)
    if base_count != 100:
        errors.append(f"launch_base count {base_count} != 100")
    if extra_count != 1:
        errors.append(f"launch_extra_premium count {extra_count} != 1")

    # Borea-specific assertions
    borea = CHARACTER_BIBLE_BY_ID.get("greek_borea")
    if not borea:
        errors.append("Borea (greek_borea) missing from Character Bible")
    else:
        if borea.get("release_group") != "launch_extra_premium":
            errors.append("Borea release_group must be launch_extra_premium")
        if borea.get("native_rarity") != 6:
            errors.append(f"Borea native_rarity must be 6, got {borea.get('native_rarity')}")
        if borea.get("element") != "wind":
            errors.append(f"Borea element must be wind, got {borea.get('element')}")
        if borea.get("role") != "mage_aoe":
            errors.append(f"Borea role must be mage_aoe, got {borea.get('role')}")
        if borea.get("max_stars") != 15:
            errors.append(f"Borea max_stars must be 15, got {borea.get('max_stars')}")

    # Per-rarity counts (informational; expected per Game Director)
    per_rarity_expected = {1: 8, 2: 12, 3: 24, 4: 24, 5: 20, 6: 12}
    per_rarity_actual: Dict[int, int] = {r: 0 for r in range(1, 7)}
    for e in CHARACTER_BIBLE:
        if e["release_group"] == "launch_base":
            per_rarity_actual[e["native_rarity"]] += 1
    for r, expected in per_rarity_expected.items():
        if per_rarity_actual[r] != expected:
            errors.append(
                f"launch_base rarity {r}* count {per_rarity_actual[r]} != expected {expected}"
            )

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "total": len(CHARACTER_BIBLE),
            "launch_base": base_count,
            "launch_extra_premium": extra_count,
            "per_rarity_launch_base": per_rarity_actual,
        },
    }


__all__ = [
    "CHARACTER_BIBLE",
    "CHARACTER_BIBLE_BY_ID",
    "LAUNCH_BASE_HERO_IDS",
    "EXTRA_PREMIUM_HERO_IDS",
    "NATIVE_RARITY_MAX_STARS",
    "CANONICAL_ELEMENTS",
    "ELEMENT_ALIASES",
    "CANONICAL_ROLES",
    "ROLE_ALIASES",
    "CANONICAL_FACTIONS",
    "FACTION_ALIASES",
    "VALID_RELEASE_GROUPS",
    "normalize_element",
    "normalize_role",
    "normalize_faction",
    "get_max_stars",
    "get_character_bible_entry",
    "validate_character_bible",
]
