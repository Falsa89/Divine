"""
Divine Waifus — Synergy & Player Faction V2 (RM1.14 — Foundation)
══════════════════════════════════════════════════════════════════════════════
Definizioni canoniche statiche per i 4 sistemi di sinergia/identità approvati
dalla Game Director Roadmap:

    1. FORMATION_SYNERGY_RULES_V2     (composition-based active formation)
    2. TEAM_SYNERGY_DEFINITIONS_V2    (lore-specific, ID-based, 2-6 heroes)
    3. COLLECTION_SYNERGY_DEFINITIONS_V2 (account-wide, ownership-based)
    4. PLAYER_FACTION_DEFINITIONS_V2  (account identity, separate from hero
                                       faction)

CONTRATTO RM1.14:
    - Tutto importa-safe, ZERO side effect.
    - NON connesso a runtime (battle_engine, /synergies/team, ecc.).
    - Tutte le entry sono `is_enabled = False` (foundation-only).
    - Coesiste con il vecchio synergy_system.py (legacy intoccato).

ALLINEAMENTO BIBLE:
    - Element canonici: water/fire/earth/wind/lightning/light/dark
    - Role canonici: tank/dps_melee/dps_ranged/mage_aoe/assassin_burst/
      support_buffer/healer/control_debuff/hybrid_special
    - Faction canoniche: 13 valori in CANONICAL_FACTIONS
    - Hero ID slug: deve risolvere a CHARACTER_BIBLE_BY_ID

USAGE FUTURO (non in questo task):
    from data.synergy_definitions_v2 import (
        FORMATION_SYNERGY_RULES_V2, TEAM_SYNERGY_DEFINITIONS_V2,
        COLLECTION_SYNERGY_DEFINITIONS_V2, PLAYER_FACTION_DEFINITIONS_V2,
        validate_synergy_v2,
    )
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from .character_bible import (
    CHARACTER_BIBLE_BY_ID,
    CANONICAL_ELEMENTS,
    CANONICAL_ROLES,
    CANONICAL_FACTIONS,
)


# ════════════════════════════════════════════════════════════════════════
# FORMATION SYNERGY V2 — composition-based, fields-driven
# ════════════════════════════════════════════════════════════════════════
# Condition types supportati:
#   - same_element_count    (allowed_values=elementi; required_count=N)
#   - same_faction_count    (allowed_values=faction; required_count=N)
#   - same_role_count       (allowed_values=role; required_count=N)
#   - category_count        (allowed_values=category; required_count=N)
#   - origin_group_count    (allowed_values=origin_group; required_count=N)
#   - role_pattern          (required_pattern={role: min_count, ...})
#
# Tutti i buff sono "team-wide" multipliers placeholder (non bilanciati).
# Tutti i record sono is_enabled=False finché Game Director non approva.
# ════════════════════════════════════════════════════════════════════════

VALID_FORMATION_CONDITION_TYPES = {
    "same_element_count",
    "same_faction_count",
    "same_role_count",
    "category_count",
    "origin_group_count",
    "role_pattern",
}

FORMATION_SYNERGY_RULES_V2: List[Dict[str, Any]] = [
    {
        "id": "same_element_3",
        "display_name": "Risonanza Elementale",
        "description": "3 eroi dello stesso elemento attivano una risonanza di base.",
        "type": "formation",
        "condition_type": "same_element_count",
        "required_count": 3,
        "allowed_values": None,  # any element
        "tiers": [
            {"count": 3, "buffs": {"attack": 0.08, "magic_damage": 0.08}},
            {"count": 4, "buffs": {"attack": 0.14, "magic_damage": 0.14, "hp": 0.06}},
            {"count": 5, "buffs": {"attack": 0.22, "magic_damage": 0.22, "hp": 0.10}},
        ],
        "buffs": None,
        "is_enabled": False,
        "notes": "V2 foundation. Sostituirà ELEMENTAL_SYNERGIES legacy una volta approvato.",
    },
    {
        "id": "same_faction_3",
        "display_name": "Banda di Fazione",
        "description": "3 eroi della stessa faction (Bible) si rafforzano a vicenda.",
        "type": "formation",
        "condition_type": "same_faction_count",
        "required_count": 3,
        "allowed_values": None,  # any canonical faction
        "tiers": [
            {"count": 3, "buffs": {"hp": 0.06, "physical_defense": 0.05}},
            {"count": 5, "buffs": {"hp": 0.12, "physical_defense": 0.10, "attack": 0.08}},
        ],
        "buffs": None,
        "is_enabled": False,
        "notes": "V2 foundation. Nessun equivalente nel synergy_system.py legacy.",
    },
    {
        "id": "balanced_core",
        "display_name": "Core Bilanciato",
        "description": "Almeno 1 tank + 1 healer + 2 dps (qualsiasi tipo) nel team.",
        "type": "formation",
        "condition_type": "role_pattern",
        "required_count": None,
        "required_pattern": {
            "tank": 1,
            "healer": 1,
            "dps_melee_or_ranged": 2,  # logica composta (vedi notes)
        },
        "allowed_values": None,
        "tiers": None,
        "buffs": {"hp": 0.05, "attack": 0.05, "healing": 0.05},
        "is_enabled": False,
        "notes": (
            "V2 foundation. Sostituisce CLASS_SYNERGIES.balanced_force con "
            "ruoli canonici. La chiave 'dps_melee_or_ranged' richiederà un "
            "evaluator custom (somma di dps_melee + dps_ranged)."
        ),
    },
    {
        "id": "mythic_creature_pack",
        "display_name": "Branco Mitico",
        "description": "3+ eroi categoria 'mythic_creature' nel team.",
        "type": "formation",
        "condition_type": "category_count",
        "required_count": 3,
        "allowed_values": ["mythic_creature"],
        "tiers": [
            {"count": 3, "buffs": {"crit_chance": 0.08, "lifesteal": 0.06}},
            {"count": 5, "buffs": {"crit_chance": 0.15, "lifesteal": 0.12, "hp": 0.08}},
        ],
        "buffs": None,
        "is_enabled": False,
        "notes": "V2 foundation. Categorie da CHARACTER_BIBLE.category.",
    },
    {
        "id": "cursed_lineage",
        "display_name": "Stirpe Maledetta",
        "description": "3+ eroi di faction 'cursed' o categoria 'cursed_entity'.",
        "type": "formation",
        "condition_type": "same_faction_count",
        "required_count": 3,
        "allowed_values": ["cursed"],
        "tiers": [
            {"count": 3, "buffs": {"penetration": 0.10, "magic_damage": 0.08}},
        ],
        "buffs": None,
        "is_enabled": False,
        "notes": (
            "V2 foundation. Bible ha 5 eroi cursed: cursed_bone_sibyl(2*), "
            "cursed_famine_herald_minor(3*), cursed_threshold_keeper(4*), "
            "cursed_twilight_witch(4*), cursed_pestilence_herald(5*), "
            "cursed_pestilence_horseman(6*)."
        ),
    },
]


# ════════════════════════════════════════════════════════════════════════
# TEAM SYNERGY V2 — lore-specific, ID-based, 2..6 heroes
# ════════════════════════════════════════════════════════════════════════
# Buff scaling regole:
#   - tier_by_member_count: { N: buffs } (più membri completi = buff più forti)
#   - star_scaling: { "per_avg_star": float } (avg stelle dei membri presenti
#     × moltiplicatore aggiuntivo)
#   - is_enabled = False per tutti finché Game Director non approva i set
#     finali. Le entry sotto sono SCHEMA EXAMPLES, non set ufficiali.
# ════════════════════════════════════════════════════════════════════════

TEAM_SYNERGY_DEFINITIONS_V2: List[Dict[str, Any]] = [
    {
        "id": "olympian_council_partial_v2_foundation",
        "display_name": "Concilio Olimpico (foundation)",
        "description": (
            "Le divinità dell'Olimpo unite — schema example, NON approvato. "
            "Set Olympian completo del Bible: greek_athena, greek_artemis, "
            "greek_gaia, greek_nike."
        ),
        "type": "team",
        "required_hero_ids": [
            "greek_athena",
            "greek_artemis",
            "greek_gaia",
            "greek_nike",
        ],
        "min_required": 3,
        "max_members": 4,
        "tier_by_member_count": {
            3: {"attack": 0.08, "hp": 0.06},
            4: {"attack": 0.14, "hp": 0.10, "magic_damage": 0.08},
        },
        "star_scaling": {"per_avg_star": 0.005},
        "buffs_by_tier": None,
        "is_enabled": False,
        "notes": (
            "Schema example only. Game Director must approve final synergies. "
            "Tutte le entry referenziano IDs Bible esistenti."
        ),
    },
    {
        "id": "anemoi_winds_v2_foundation",
        "display_name": "Anemoi - Venti Olimpici (foundation)",
        "description": (
            "Borea (Vento del Nord) — set Anemoi completo richiede futuri "
            "fratelli (Zephyr, Notus, Eurus) non ancora nel Bible."
        ),
        "type": "team",
        "required_hero_ids": ["greek_borea"],
        "min_required": 1,
        "max_members": 4,
        "tier_by_member_count": {
            1: {"speed": 0.05, "dodge": 0.04},
        },
        "star_scaling": {"per_avg_star": 0.004},
        "buffs_by_tier": None,
        "is_enabled": False,
        "notes": (
            "Set incompleto: solo Borea esiste. I fratelli Anemoi (Zephyr/"
            "Notus/Eurus) sono future expansion oltre i 100 launch base."
        ),
    },
    {
        "id": "pestilence_line_v2_foundation",
        "display_name": "Linea della Pestilenza (foundation)",
        "description": (
            "Le incarnazioni della peste: Aralda + Cavaliere dell'Apocalisse."
        ),
        "type": "team",
        "required_hero_ids": [
            "cursed_pestilence_herald",
            "cursed_pestilence_horseman",
        ],
        "min_required": 2,
        "max_members": 2,
        "tier_by_member_count": {
            2: {"penetration": 0.15, "magic_damage": 0.12, "lifesteal": 0.06},
        },
        "star_scaling": {"per_avg_star": 0.006},
        "buffs_by_tier": None,
        "is_enabled": False,
        "notes": "Schema example only. Duo cursed → control_debuff×hybrid_special.",
    },
    {
        "id": "hydra_lineage_v2_foundation",
        "display_name": "Lignaggio dell'Idra (foundation)",
        "description": "Dall'Idra Minore all'Idra di Lerna — la stirpe acquatica.",
        "type": "team",
        "required_hero_ids": [
            "creature_lesser_hydra",
            "creature_lernaean_hydra",
        ],
        "min_required": 2,
        "max_members": 2,
        "tier_by_member_count": {
            2: {"hp": 0.15, "magic_defense": 0.10, "healing_received": 0.10},
        },
        "star_scaling": {"per_avg_star": 0.005},
        "buffs_by_tier": None,
        "is_enabled": False,
        "notes": "Schema example only. Hybrid_special × hybrid_special, water/water.",
    },
    {
        "id": "phoenix_kin_v2_foundation",
        "display_name": "Stirpe della Fenice (foundation)",
        "description": (
            "Figlia della Fenice + Fenice Cremisi — la rinascita di fuoco."
        ),
        "type": "team",
        "required_hero_ids": [
            "creature_phoenix_daughter",
            "creature_crimson_phoenix",
        ],
        "min_required": 2,
        "max_members": 2,
        "tier_by_member_count": {
            2: {"attack": 0.10, "crit_chance": 0.08, "ultimate_charge": 0.10},
        },
        "star_scaling": {"per_avg_star": 0.005},
        "buffs_by_tier": None,
        "is_enabled": False,
        "notes": "Schema example only. Fire creature_beast × fire creature_beast.",
    },
]


# ════════════════════════════════════════════════════════════════════════
# COLLECTION SYNERGY V2 — account-wide, ownership-based
# ════════════════════════════════════════════════════════════════════════
# Buff PIÙ DEBOLI delle Team Synergies (account-passive, no team presence).
# is_enabled=False per tutti.
# ════════════════════════════════════════════════════════════════════════

COLLECTION_SYNERGY_DEFINITIONS_V2: List[Dict[str, Any]] = [
    {
        "id": "olympian_collection_v2_foundation",
        "display_name": "Collezione Olimpica (foundation)",
        "description": (
            "Possedere divinità dell'Olimpo conferisce un piccolo bonus "
            "permanente all'account."
        ),
        "type": "collection",
        "required_hero_ids": [
            "greek_athena",
            "greek_artemis",
            "greek_gaia",
            "greek_nike",
        ],
        "min_owned": 2,
        "star_scaling": {
            # Esempio: bonus = base × (avg_stars_owned / 6)
            "per_avg_star": 0.001,
        },
        "account_buff": {"hp": 0.02, "attack": 0.02},
        "is_enabled": False,
        "notes": (
            "Account-wide passive. Più debole di TEAM_SYNERGY 'olympian_council'. "
            "Eroi NON necessari nell'active team."
        ),
    },
    {
        "id": "japanese_kami_collection_v2_foundation",
        "display_name": "Collezione Kami (foundation)",
        "description": (
            "I Kami giapponesi del Bible: Amaterasu, Susanoo, Raijin."
        ),
        "type": "collection",
        "required_hero_ids": [
            "japanese_amaterasu",
            "japanese_susanoo",
            "japanese_raijin",
        ],
        "min_owned": 2,
        "star_scaling": {"per_avg_star": 0.001},
        "account_buff": {"speed": 0.02, "magic_damage": 0.02},
        "is_enabled": False,
        "notes": "Account-wide passive. origin_group=kami.",
    },
    {
        "id": "norse_pantheon_collection_v2_foundation",
        "display_name": "Collezione Norrena (foundation)",
        "description": (
            "Le divinità nordiche del Bible: Eir + Jotunn + Valchiria dell'Alba "
            "+ Volva del Fato."
        ),
        "type": "collection",
        "required_hero_ids": [
            "norse_eir",
            "norse_rime_jotunn",
            "norse_dawn_valkyrie",
            "norse_volva_of_fate",
        ],
        "min_owned": 2,
        "star_scaling": {"per_avg_star": 0.001},
        "account_buff": {"hp": 0.02, "physical_defense": 0.02},
        "is_enabled": False,
        "notes": "Account-wide passive. Faction=norse, mix di ruoli.",
    },
    {
        "id": "creature_beast_collection_v2_foundation",
        "display_name": "Collezione Bestie Mitiche (foundation)",
        "description": (
            "Possedere creature mitiche multiple (hydra/phoenix/coral guardian/"
            "depths warrior/cyclone daughter)."
        ),
        "type": "collection",
        "required_hero_ids": [
            "creature_coral_guardian",
            "creature_lesser_hydra",
            "creature_lernaean_hydra",
            "creature_phoenix_daughter",
            "creature_crimson_phoenix",
            "creature_depths_warrior",
            "creature_cyclone_daughter",
        ],
        "min_owned": 3,
        "star_scaling": {"per_avg_star": 0.001},
        "account_buff": {"crit_chance": 0.02, "dodge": 0.02},
        "is_enabled": False,
        "notes": "Account-wide passive. Faction=creature_beast.",
    },
    {
        "id": "cursed_omens_collection_v2_foundation",
        "display_name": "Collezione Maledizioni (foundation)",
        "description": "Tutti gli eroi cursed del Bible.",
        "type": "collection",
        "required_hero_ids": [
            "cursed_bone_sibyl",
            "cursed_famine_herald_minor",
            "cursed_threshold_keeper",
            "cursed_twilight_witch",
            "cursed_pestilence_herald",
            "cursed_pestilence_horseman",
        ],
        "min_owned": 3,
        "star_scaling": {"per_avg_star": 0.0015},
        "account_buff": {"penetration": 0.02, "lifesteal": 0.02},
        "is_enabled": False,
        "notes": "Account-wide passive. Faction=cursed, hard to complete.",
    },
]


# ════════════════════════════════════════════════════════════════════════
# PLAYER FACTION V2 — account identity (separate from hero faction)
# ════════════════════════════════════════════════════════════════════════
# Schema:
#   - id (riusa CANONICAL_FACTIONS dove possibile)
#   - display_name
#   - description
#   - identity_theme (scelta narrativa per il player)
#   - allowed_at_onboarding (bool)
#   - change_token_id (item richiesto per il cambio)
#   - buff_preview (placeholder, NON applicato in battle)
#   - future_event_hooks (lista di event id)
#   - is_enabled (foundation false)
#   - notes
# ════════════════════════════════════════════════════════════════════════

# Token per cambio fazione — placeholder
PLAYER_FACTION_CHANGE_TOKEN_ID = "faction_change_token"

PLAYER_FACTION_DEFINITIONS_V2: List[Dict[str, Any]] = [
    {
        "id": "greek",
        "display_name": "Olimpo (Greco)",
        "description": "Il pantheon olimpico — saggezza strategica e gloria eroica.",
        "identity_theme": "olympian_glory",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"magic_damage": 0.05, "speed": 0.04},
        "future_event_hooks": ["faction_daily_boss", "olympian_solstice"],
        "is_enabled": False,
        "notes": "Player faction. Hero faction 'greek' indipendente.",
    },
    {
        "id": "norse",
        "display_name": "Asgard (Norreno)",
        "description": "I guerrieri del Nord — furia e Ragnarok.",
        "identity_theme": "ragnarok_fury",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"physical_damage": 0.05, "penetration": 0.04},
        "future_event_hooks": ["faction_daily_boss", "ragnarok_eve"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "egyptian",
        "display_name": "Duat (Egizio)",
        "description": "I culti del Nilo e del Duat — mistero e potere solare.",
        "identity_theme": "nile_solar",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"crit_damage": 0.06, "crit_chance": 0.04},
        "future_event_hooks": ["faction_daily_boss", "nile_flood"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "japanese_yokai",
        "display_name": "Yokai (Giapponese)",
        "description": "Spiriti, Kami e Yokai dell'arcipelago.",
        "identity_theme": "shinto_yokai",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"speed": 0.05, "combo_rate": 0.05},
        "future_event_hooks": ["faction_daily_boss", "obon_festival"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "celtic",
        "display_name": "Druidi (Celtico)",
        "description": "Le brume di Avalon e la magia druidica.",
        "identity_theme": "druidic_mists",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"physical_defense": 0.04, "magic_defense": 0.04, "dodge": 0.03},
        "future_event_hooks": ["faction_daily_boss", "samhain_night"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "angelic",
        "display_name": "Coro Celeste (Angelico)",
        "description": "Le schiere angeliche e i Cherubini guardiani.",
        "identity_theme": "celestial_choir",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"healing": 0.06, "magic_defense": 0.04},
        "future_event_hooks": ["faction_daily_boss", "ascension_dawn"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "demonic",
        "display_name": "Inferno (Demoniaco)",
        "description": "Le fiamme infernali e i patti oscuri.",
        "identity_theme": "infernal_pact",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"attack": 0.05, "lifesteal": 0.05},
        "future_event_hooks": ["faction_daily_boss", "blood_eclipse"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "cursed",
        "display_name": "Maledizioni (Cursed)",
        "description": "Gli aralda dei Sigilli e le strege del Vespro.",
        "identity_theme": "cursed_omens",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"penetration": 0.05, "control_resistance": 0.05},
        "future_event_hooks": ["faction_daily_boss", "famine_moon"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "creature_beast",
        "display_name": "Bestie Mitiche",
        "description": "Idre, Fenici, e le creature delle profondità.",
        "identity_theme": "mythic_beasts",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"hp": 0.06, "crit_chance": 0.04},
        "future_event_hooks": ["faction_daily_boss", "primal_hunt"],
        "is_enabled": False,
        "notes": "Player faction.",
    },
    {
        "id": "primordial",
        "display_name": "Primordiali",
        "description": "Gaia, Nyx, Tiamat — le forze antiche del cosmo.",
        "identity_theme": "primordial_chaos",
        "allowed_at_onboarding": True,
        "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
        "buff_preview": {"hp": 0.05, "magic_damage": 0.05},
        "future_event_hooks": ["faction_daily_boss", "void_eclipse"],
        "is_enabled": False,
        "notes": "Player faction. Bible heroes: greek_gaia, primordial_nyx, mesopotamian_tiamat.",
    },
    # Faction ESCLUSE dall'onboarding (internal/hero faction only):
    {
        "id": "arcane",
        "display_name": "Arcani",
        "description": "Magia arcana pura — uso interno per hero faction.",
        "identity_theme": "arcane_magic",
        "allowed_at_onboarding": False,
        "change_token_id": None,
        "buff_preview": None,
        "future_event_hooks": [],
        "is_enabled": False,
        "notes": "Internal/hero faction only. NON selezionabile come player faction.",
    },
    {
        "id": "mesopotamian",
        "display_name": "Mesopotamica",
        "description": "Pantheon mesopotamico — uso interno per hero faction.",
        "identity_theme": "mesopotamian_primordial",
        "allowed_at_onboarding": False,
        "change_token_id": None,
        "buff_preview": None,
        "future_event_hooks": [],
        "is_enabled": False,
        "notes": (
            "Internal/hero faction only. Bible: mesopotamian_tiamat. "
            "NON selezionabile come player faction al lancio."
        ),
    },
    {
        "id": "tides",
        "display_name": "Maree",
        "description": "Tides flavor — uso interno per hero faction.",
        "identity_theme": "tides_corsair",
        "allowed_at_onboarding": False,
        "change_token_id": None,
        "buff_preview": None,
        "future_event_hooks": [],
        "is_enabled": False,
        "notes": (
            "Internal/hero faction only. NON selezionabile come player "
            "faction al lancio."
        ),
    },
]


# ════════════════════════════════════════════════════════════════════════
# VALIDATION
# ════════════════════════════════════════════════════════════════════════

def _validate_formation_rule(r: Dict[str, Any], errors: List[str]) -> None:
    rid = r.get("id", "?")
    if r.get("type") != "formation":
        errors.append(f"formation rule {rid}: type must be 'formation'")
    ct = r.get("condition_type")
    if ct not in VALID_FORMATION_CONDITION_TYPES:
        errors.append(f"formation rule {rid}: invalid condition_type {ct}")
    # If allowed_values reference elements/roles/factions, validate canonicality
    av = r.get("allowed_values")
    if av:
        if ct == "same_element_count":
            for v in av:
                if v not in CANONICAL_ELEMENTS:
                    errors.append(f"formation rule {rid}: non-canonical element {v}")
        elif ct == "same_faction_count":
            for v in av:
                if v not in CANONICAL_FACTIONS:
                    errors.append(f"formation rule {rid}: non-canonical faction {v}")
        elif ct == "same_role_count":
            for v in av:
                if v not in CANONICAL_ROLES:
                    errors.append(f"formation rule {rid}: non-canonical role {v}")
    # role_pattern
    if ct == "role_pattern":
        pattern = r.get("required_pattern") or {}
        for role_key in pattern.keys():
            # 'dps_melee_or_ranged' è una chiave composta legittima
            if role_key == "dps_melee_or_ranged":
                continue
            if role_key not in CANONICAL_ROLES:
                errors.append(
                    f"formation rule {rid}: pattern role '{role_key}' "
                    f"not canonical"
                )


def _validate_team_synergy(s: Dict[str, Any], errors: List[str]) -> None:
    sid = s.get("id", "?")
    if s.get("type") != "team":
        errors.append(f"team synergy {sid}: type must be 'team'")
    ids = s.get("required_hero_ids") or []
    if not isinstance(ids, list) or len(ids) == 0:
        errors.append(f"team synergy {sid}: required_hero_ids must be non-empty list")
    # Hero IDs in Bible
    for hid in ids:
        if hid not in CHARACTER_BIBLE_BY_ID:
            errors.append(f"team synergy {sid}: hero_id '{hid}' not in Character Bible")
    # min_required and max_members in [1, 6]; foundation allows min_required=1
    # for incomplete future-set placeholders (e.g. anemoi only Borea exists).
    mr = s.get("min_required")
    mm = s.get("max_members")
    if not (isinstance(mr, int) and 1 <= mr <= 6):
        errors.append(f"team synergy {sid}: min_required must be int in [1,6], got {mr}")
    if not (isinstance(mm, int) and 1 <= mm <= 6):
        errors.append(f"team synergy {sid}: max_members must be int in [1,6], got {mm}")
    if mr is not None and mm is not None and mr > mm:
        errors.append(f"team synergy {sid}: min_required {mr} > max_members {mm}")
    # If member count >= 2, that satisfies 'standard' team synergy criteria;
    # entries with only 1 member must be marked as foundation/incomplete-set.
    if mm is not None and mm < 2:
        if "foundation" not in (s.get("notes") or "").lower() \
                and "incompleto" not in (s.get("notes") or "").lower():
            errors.append(
                f"team synergy {sid}: max_members<2 must be flagged as "
                f"foundation/incomplete in notes"
            )


def _validate_collection_synergy(c: Dict[str, Any], errors: List[str]) -> None:
    cid = c.get("id", "?")
    if c.get("type") != "collection":
        errors.append(f"collection {cid}: type must be 'collection'")
    ids = c.get("required_hero_ids") or []
    if not isinstance(ids, list) or len(ids) == 0:
        errors.append(f"collection {cid}: required_hero_ids must be non-empty list")
    for hid in ids:
        if hid not in CHARACTER_BIBLE_BY_ID:
            errors.append(f"collection {cid}: hero_id '{hid}' not in Character Bible")
    mo = c.get("min_owned")
    if not (isinstance(mo, int) and 1 <= mo <= len(ids)):
        errors.append(f"collection {cid}: min_owned must be 1..len(required_hero_ids)")


def _validate_player_faction(f: Dict[str, Any], errors: List[str]) -> None:
    fid = f.get("id", "?")
    # ID must be canonical Bible faction (CANONICAL_FACTIONS contains the
    # internal-only ones too: arcane, mesopotamian, tides).
    if fid not in CANONICAL_FACTIONS:
        errors.append(f"player faction {fid}: id not in CANONICAL_FACTIONS")
    # If allowed_at_onboarding=True it must have a change_token_id and buff_preview.
    if f.get("allowed_at_onboarding") is True:
        if not f.get("change_token_id"):
            errors.append(f"player faction {fid}: allowed_at_onboarding=True requires change_token_id")
        if not f.get("buff_preview"):
            errors.append(f"player faction {fid}: allowed_at_onboarding=True requires buff_preview")


def validate_synergy_v2() -> Dict[str, Any]:
    """Validazione strutturale completa V2. Read-only."""
    errors: List[str] = []
    warnings: List[str] = []

    # Formation rules
    seen_f: set = set()
    for r in FORMATION_SYNERGY_RULES_V2:
        if r["id"] in seen_f:
            errors.append(f"duplicate formation id {r['id']}")
        seen_f.add(r["id"])
        _validate_formation_rule(r, errors)

    # Team synergies
    seen_t: set = set()
    for s in TEAM_SYNERGY_DEFINITIONS_V2:
        if s["id"] in seen_t:
            errors.append(f"duplicate team synergy id {s['id']}")
        seen_t.add(s["id"])
        _validate_team_synergy(s, errors)

    # Collection synergies
    seen_c: set = set()
    for c in COLLECTION_SYNERGY_DEFINITIONS_V2:
        if c["id"] in seen_c:
            errors.append(f"duplicate collection id {c['id']}")
        seen_c.add(c["id"])
        _validate_collection_synergy(c, errors)

    # Player factions
    seen_pf: set = set()
    for f in PLAYER_FACTION_DEFINITIONS_V2:
        if f["id"] in seen_pf:
            errors.append(f"duplicate player faction id {f['id']}")
        seen_pf.add(f["id"])
        _validate_player_faction(f, errors)

    # Foundation invariant: no entry should be is_enabled=True yet
    enabled_violations: List[str] = []
    for collection_name, items in (
        ("FORMATION", FORMATION_SYNERGY_RULES_V2),
        ("TEAM", TEAM_SYNERGY_DEFINITIONS_V2),
        ("COLLECTION", COLLECTION_SYNERGY_DEFINITIONS_V2),
        ("PLAYER_FACTION", PLAYER_FACTION_DEFINITIONS_V2),
    ):
        for it in items:
            if it.get("is_enabled") is True:
                enabled_violations.append(f"{collection_name}.{it['id']} is_enabled=True (foundation must be False)")
    if enabled_violations:
        errors.extend(enabled_violations)

    # Counts
    counts = {
        "formation_rules": len(FORMATION_SYNERGY_RULES_V2),
        "team_synergies": len(TEAM_SYNERGY_DEFINITIONS_V2),
        "collection_synergies": len(COLLECTION_SYNERGY_DEFINITIONS_V2),
        "player_factions_total": len(PLAYER_FACTION_DEFINITIONS_V2),
        "player_factions_onboarding": sum(
            1 for f in PLAYER_FACTION_DEFINITIONS_V2
            if f.get("allowed_at_onboarding") is True
        ),
        "player_factions_internal_only": sum(
            1 for f in PLAYER_FACTION_DEFINITIONS_V2
            if f.get("allowed_at_onboarding") is False
        ),
        "all_disabled": (
            all(not r.get("is_enabled") for r in FORMATION_SYNERGY_RULES_V2)
            and all(not s.get("is_enabled") for s in TEAM_SYNERGY_DEFINITIONS_V2)
            and all(not c.get("is_enabled") for c in COLLECTION_SYNERGY_DEFINITIONS_V2)
            and all(not f.get("is_enabled") for f in PLAYER_FACTION_DEFINITIONS_V2)
        ),
    }

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "counts": counts,
    }


__all__ = [
    "FORMATION_SYNERGY_RULES_V2",
    "TEAM_SYNERGY_DEFINITIONS_V2",
    "COLLECTION_SYNERGY_DEFINITIONS_V2",
    "PLAYER_FACTION_DEFINITIONS_V2",
    "PLAYER_FACTION_CHANGE_TOKEN_ID",
    "VALID_FORMATION_CONDITION_TYPES",
    "validate_synergy_v2",
]
