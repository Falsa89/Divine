"""Pre-QA Stabilization 116A — Battle Power foundation (read-only, derived).

Formula version: `battle_power_v1_preqa_derived`.

Semantic contract:
- `source = derived_read_only`
- `runtime_attached = false`
- `combat_authoritative = false`
- `reward_authoritative = false`
- `balance_final = false`
- `server_scoped = true`

Esclusioni esplicite (NON contribuiscono al power di 116A):
- artifacts
- divine_weapons
- cosmetics
- titles
- skill_final_numbers
- live_rewards
- equipment            (deferred, non strictly server-scoped/read-only)
- runes                (deferred)
- gem_sockets          (deferred)
- account_wide_bonuses (vietati per design pre-QA)
- guild/server bonuses
- affinity/sanctuary bonuses

L'helper e' un PURE FUNCTION:
- nessun import di `battle_engine.py`;
- nessuna chiamata DB;
- nessun side-effect;
- deterministico dato (hero, user_hero).

Se mancano campi numerici su hero/user_hero, vengono usati fallback
conservativi dichiarati (commento accanto a ogni `dict.get`).
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

# ---- Metadata costanti (riusate da route + validator) -----------------------
BATTLE_POWER_FORMULA_VERSION = "battle_power_v1_preqa_derived"
BATTLE_POWER_SOURCE = "derived_read_only"
BATTLE_POWER_RUNTIME_ATTACHED = False
BATTLE_POWER_COMBAT_AUTHORITATIVE = False
BATTLE_POWER_REWARD_AUTHORITATIVE = False
BATTLE_POWER_BALANCE_FINAL = False
BATTLE_POWER_SERVER_SCOPED = True

# Campi sorgenti esplicitamente esclusi da 116A (dichiarati nell'output
# dell'endpoint cosi' il client/QA lo vede chiaramente).
BATTLE_POWER_EXCLUDED_SOURCES = (
    "artifacts",
    "divine_weapons",
    "cosmetics",
    "titles",
    "skill_final_numbers",
    "live_rewards",
    "equipment",
    "runes",
    "gem_sockets",
    "account_wide_bonuses",
    "guild_bonuses",
    "server_bonuses",
    "affinity_bonuses",
    "sanctuary_bonuses",
)

# Campi base eroe utilizzati (dichiarati per audit).
BATTLE_POWER_INCLUDED_HERO_FIELDS = (
    "base_stats.physical_damage_or_attack",
    "base_stats.magic_damage",
    "base_stats.physical_defense_or_defense",
    "base_stats.magic_defense",
    "base_stats.hp_div10",
    "base_stats.speed",
    "base_stats.healing_div2",
    "rarity",
)
BATTLE_POWER_INCLUDED_USER_HERO_FIELDS = (
    "level",
    "stars",
)

# Fallback conservativi dichiarati (usati SOLO se i campi base mancano):
# - hp:           1000  (sano per un eroe iniziale)
# - phys_damage:   100  (attack)
# - phys_defense:   50  (defense)
# - magic_*:         0
# - speed:          10
# - healing:         0
_FALLBACK_PHYSICAL_DAMAGE = 100
_FALLBACK_PHYSICAL_DEFENSE = 50
_FALLBACK_HP = 1000
_FALLBACK_SPEED = 10


def compute_hero_battle_power_v1(
    hero: Optional[Mapping[str, Any]],
    user_hero: Optional[Mapping[str, Any]] = None,
) -> int:
    """Calcola il battle power 116A per (hero catalog, user_hero owned).

    Pure function. No DB. No I/O. Deterministica.

    Args:
        hero: dict da `db.heroes` (catalog). Puo' avere `base_stats` e `rarity`.
        user_hero: dict da `db.user_heroes` (server-scoped). Puo' avere `level`,
                   `stars`. Se None, usa level=1.

    Returns:
        int >= 0 (mai negativo). Se hero e' None, ritorna 0 (caso conservativo).
    """
    if not hero:
        return 0
    stats = hero.get("base_stats") if isinstance(hero, Mapping) else None
    if not isinstance(stats, Mapping):
        stats = {}
    # NB: questa formula riusa la stessa shape di `calculate_hero_power` gia'
    # presente in `server.py` (Pack precedenti), MA dichiarata esplicitamente
    # come read-only/derived/foundation in metadata. Cio' evita duplicazioni
    # numeriche divergenti pur preservando l'invariante "no combat authoritative".
    physical_damage = int(
        stats.get("physical_damage", stats.get("attack", _FALLBACK_PHYSICAL_DAMAGE)) or 0
    )
    magic_damage = int(stats.get("magic_damage", 0) or 0)
    physical_defense = int(
        stats.get("physical_defense", stats.get("defense", _FALLBACK_PHYSICAL_DEFENSE)) or 0
    )
    magic_defense = int(stats.get("magic_defense", 0) or 0)
    hp = int(stats.get("hp", _FALLBACK_HP) or 0)
    speed = int(stats.get("speed", _FALLBACK_SPEED) or 0)
    healing = int(stats.get("healing", 0) or 0)

    base = (
        physical_damage
        + magic_damage
        + physical_defense
        + magic_defense
        + (hp // 10)
        + speed
        + (healing // 2)
    )

    level = 1
    if isinstance(user_hero, Mapping):
        try:
            level = int(user_hero.get("level", 1) or 1)
        except (TypeError, ValueError):
            level = 1
        if level < 1:
            level = 1
    try:
        rarity = int(hero.get("rarity", 1) or 1)
    except (TypeError, ValueError):
        rarity = 1
    if rarity < 0:
        rarity = 0

    power = int(base * (1 + (level - 1) * 0.05) * (1 + rarity * 0.2))
    # Bonus stars (foundation only, no balance final): +3% per star above
    # native rarity (capped at +15% pre-QA per non implicare runtime).
    stars = 0
    if isinstance(user_hero, Mapping):
        try:
            stars = int(user_hero.get("stars", 0) or 0)
        except (TypeError, ValueError):
            stars = 0
    star_delta = max(0, stars - rarity)
    star_bonus = min(0.15, star_delta * 0.03)
    if star_bonus > 0:
        power = int(power * (1 + star_bonus))
    return max(0, power)


def build_battle_power_metadata() -> dict:
    """Ritorna il dict di metadata invariante (semantic contract).

    Usato dall'endpoint per dichiarare esplicitamente lo stato read-only/derived
    a ogni risposta, e dal validator 116A per verificare le invarianti.
    """
    return {
        "formula_version": BATTLE_POWER_FORMULA_VERSION,
        "source": BATTLE_POWER_SOURCE,
        "runtime_attached": BATTLE_POWER_RUNTIME_ATTACHED,
        "combat_authoritative": BATTLE_POWER_COMBAT_AUTHORITATIVE,
        "reward_authoritative": BATTLE_POWER_REWARD_AUTHORITATIVE,
        "balance_final": BATTLE_POWER_BALANCE_FINAL,
        "server_scoped": BATTLE_POWER_SERVER_SCOPED,
        "excluded_power_sources": list(BATTLE_POWER_EXCLUDED_SOURCES),
        "included_hero_fields": list(BATTLE_POWER_INCLUDED_HERO_FIELDS),
        "included_user_hero_fields": list(BATTLE_POWER_INCLUDED_USER_HERO_FIELDS),
    }
