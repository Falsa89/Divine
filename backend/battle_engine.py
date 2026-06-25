"""
Divine Waifus - Battle Engine
Inspired by Hokage Crisis: Turn-based auto-battle with formation strategy
6 characters per team, 9x9 grid positioning with buffs
Features: NAD (Normal Attack), SAD (Strong Attack), SP (Ultimate Move)
Active/Passive skills, positional buffs, cinematic ultimate triggers
"""
import random
import math
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

# ───────────────────────────────────────────────────────────────────────────
# PROJECT_M Track B — STATUS FIRST SLICE single-point seam import.
# The seam is INERT by default (returns input unchanged unless the flag
# STATUS_RUNTIME_BUFF_SLICE_ENABLED is exactly 'true' AND dry_run=True).
# Importing here is a no-op at module load. The single call site is inside
# simulate_battle(), bound to the seam helper apply_prefight_status_slice_preview.
# Rollback: scripts/rollback_project_m_battle_engine_status_seam.py
# ───────────────────────────────────────────────────────────────────────────
try:
    from game_logic.status_prefight_runtime_seam import apply_prefight_status_slice_preview as _project_m_status_seam
except Exception:
    # Defensive fallback: if the seam module is unavailable for any reason,
    # bind to a strict identity function so battle_engine never crashes.
    def _project_m_status_seam(team_payload, active_statuses=None, *, dry_run=False):
        return team_payload

# ───────────────────────────────────────────────────────────────────────────
# PROJECT_T Track B — STATUS SECOND SLICE single-point seam import.
# Mirror of the PROJECT_M pattern. The seam is INERT by default (returns
# input unchanged unless STATUS_RUNTIME_SECOND_SLICE_ENABLED == 'true' AND
# dry_run=True). With flag OFF (default), the call is strict identity, so
# runtime behavior is unchanged. The single call site is inside
# simulate_battle(), adjacent to the first-slice seam.
# Rollback: scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py
# ───────────────────────────────────────────────────────────────────────────
try:
    from game_logic.status_second_slice_runtime_seam import apply_prefight_second_slice_preview as _project_t_second_slice_seam
except Exception:
    # Defensive fallback: identity function so battle_engine never crashes.
    def _project_t_second_slice_seam(team_payload, active_statuses=None, mode='campaign', *, dry_run=False):
        return team_payload

# ===================== POSITION BUFFS ON 3x3 GRID (3 rows, 3 columns) =====================
# Grid layout: 3 rows (top/mid/bottom) x 3 columns (left=Support, center=DPS, right=Tank)
# Max 6 heroes can be placed in 9 slots

COLUMN_ROLES = {
    0: {"name": "Supporto", "role": "support", "buff": {"speed": 0.15, "healing": 0.20}, "desc": "Colonna Sinistra: +15% Velocita, +20% Cure"},
    1: {"name": "Damage Dealer", "role": "dps", "buff": {"physical_damage": 0.15, "magic_damage": 0.15, "crit_damage": 0.20}, "desc": "Colonna Centrale: +15% Danno, +20% Danno Critico"},
    2: {"name": "Tank", "role": "tank", "buff": {"hp": 0.20, "physical_defense": 0.15, "magic_defense": 0.15}, "desc": "Colonna Destra: +20% HP, +15% Difese"},
}

POSITION_BUFFS = {
    "support": {"cols": [0], "buff": {"speed": 0.15, "healing": 0.20}, "name": "Supporto", "desc": "+15% SPD, +20% Cure"},
    "dps": {"cols": [1], "buff": {"physical_damage": 0.15, "magic_damage": 0.15, "crit_damage": 0.20}, "name": "Damage Dealer", "desc": "+15% DMG, +20% CRIT DMG"},
    "tank": {"cols": [2], "buff": {"hp": 0.20, "physical_defense": 0.15, "magic_defense": 0.15}, "name": "Tank", "desc": "+20% HP, +15% DEF"},
}

# Special formations that grant extra bonuses
FORMATION_PATTERNS = {
    "v_shape": {
        "name": "Formazione a V",
        "description": "3 davanti, 2 al centro, 1 dietro",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 3 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) == 2 and
            sum(1 for p in positions if p['y'] >= 6) == 1
        ),
        "buff": {"attack": 0.10, "defense": 0.10},
    },
    "wall": {
        "name": "Muro di Ferro",
        "description": "Tutti i 6 in prima/seconda riga",
        "check": lambda positions: all(p['y'] <= 3 for p in positions),
        "buff": {"defense": 0.25, "hp": 0.20},
    },
    "sniper": {
        "name": "Cecchini Divini",
        "description": "Tutti i 6 nelle ultime 3 righe",
        "check": lambda positions: all(p['y'] >= 6 for p in positions),
        "buff": {"crit_rate": 0.20, "attack": 0.15},
    },
    "diamond": {
        "name": "Diamante Sacro",
        "description": "1 davanti, 2 centro, 2 centro, 1 dietro",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 1 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) >= 3 and
            sum(1 for p in positions if p['y'] >= 6) == 1
        ),
        "buff": {"attack": 0.08, "defense": 0.08, "speed": 0.08, "crit_rate": 0.08},
    },
    "spread": {
        "name": "Dispersione Tattica",
        "description": "2 per ogni zona (davanti, centro, dietro)",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 2 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) == 2 and
            sum(1 for p in positions if p['y'] >= 6) == 2
        ),
        "buff": {"attack": 0.12, "speed": 0.12},
    },
    "column": {
        "name": "Colonna di Battaglia",
        "description": "Tutti nella stessa colonna (±1)",
        "check": lambda positions: (
            max(p['x'] for p in positions) - min(p['x'] for p in positions) <= 2
        ),
        "buff": {"attack": 0.18, "crit_damage": 0.20},
    },
}

# Adjacency bonus: characters next to each other get bonuses
def calculate_adjacency_bonus(positions: list) -> dict:
    """Check for adjacent characters and calculate bonuses"""
    bonus = {"attack": 0, "defense": 0, "hp": 0, "speed": 0}
    adj_count = 0
    for i, p1 in enumerate(positions):
        for j, p2 in enumerate(positions):
            if i >= j:
                continue
            dx = abs(p1['x'] - p2['x'])
            dy = abs(p1['y'] - p2['y'])
            if dx <= 1 and dy <= 1:  # Adjacent (including diagonal)
                adj_count += 1
    # More adjacent pairs = bigger bonus
    mult = adj_count * 0.03
    bonus["attack"] = mult
    bonus["defense"] = mult
    return {"bonus": bonus, "adjacent_pairs": adj_count}


# ===================== SKILL DEFINITIONS =====================

SKILL_TYPES = {
    "nad": {"name": "Attacco Normale", "type": "nad", "cooldown": 0, "hits": 3},
    "sad": {"name": "Attacco Forte", "type": "sad", "cooldown": 3, "hits": 1},
    "sp": {"name": "Mossa Finale", "type": "sp", "cooldown": 0, "gauge_cost": 100, "hits": 1},
}

# Element-specific skill effects
ELEMENT_SKILLS = {
    "fire": {
        "nad": {"name": "Colpo Infernale", "animation": "slash_fire", "damage_mult": 1.0, "effect": None, "icon": "🔥"},
        "sad": {"name": "Tempesta di Fiamme", "animation": "burst_fire", "damage_mult": 2.5, "effect": {"type": "burn", "damage_per_turn": 0.05, "duration": 3}, "icon": "🌋", "description": "Infligge Ustione per 3 turni"},
        "sp": {"name": "Inferno Divino", "animation": "ultimate_fire", "damage_mult": 5.0, "effect": {"type": "burn", "damage_per_turn": 0.08, "duration": 3}, "icon": "☄️", "description": "Devastante attacco di fuoco che brucia tutto!"},
    },
    "water": {
        "nad": {"name": "Lama d'Acqua", "animation": "slash_water", "damage_mult": 1.0, "effect": None, "icon": "💧"},
        "sad": {"name": "Tsunami", "animation": "burst_water", "damage_mult": 2.3, "effect": {"type": "slow", "speed_reduction": 0.30, "duration": 2}, "icon": "🌊", "description": "Rallenta i nemici del 30%"},
        "sp": {"name": "Maremoto Celeste", "animation": "ultimate_water", "damage_mult": 4.5, "effect": {"type": "freeze", "duration": 1}, "icon": "🧊", "description": "Congela tutti i nemici per 1 turno!"},
    },
    "earth": {
        "nad": {"name": "Pugno di Terra", "animation": "slash_earth", "damage_mult": 1.0, "effect": None, "icon": "🪨"},
        "sad": {"name": "Terremoto", "animation": "burst_earth", "damage_mult": 2.0, "effect": {"type": "stun", "duration": 1}, "icon": "⛰️", "description": "Stordisce il nemico per 1 turno"},
        "sp": {"name": "Collasso Tettonico", "animation": "ultimate_earth", "damage_mult": 4.0, "effect": {"type": "defense_break", "reduction": 0.40, "duration": 3}, "icon": "🌍", "description": "Riduce la DEF nemica del 40%!"},
    },
    "wind": {
        "nad": {"name": "Taglio del Vento", "animation": "slash_wind", "damage_mult": 1.0, "effect": None, "icon": "💨"},
        "sad": {"name": "Lame di Vento", "animation": "burst_wind", "damage_mult": 2.8, "effect": {"type": "bleed", "damage_per_turn": 0.04, "duration": 3}, "icon": "🌪️", "description": "Provoca Sanguinamento per 3 turni"},
        "sp": {"name": "Uragano Divino", "animation": "ultimate_wind", "damage_mult": 5.5, "effect": {"type": "bleed", "damage_per_turn": 0.06, "duration": 3}, "icon": "🌀", "description": "Attacco devastante che lacera i nemici!"},
    },
    "light": {
        "nad": {"name": "Raggio Sacro", "animation": "slash_light", "damage_mult": 1.0, "effect": None, "icon": "✨"},
        "sad": {"name": "Giudizio Divino", "animation": "burst_light", "damage_mult": 2.4, "effect": {"type": "weaken", "attack_reduction": 0.25, "duration": 2}, "icon": "🌟", "description": "Indebolisce ATK nemica del 25%"},
        "sp": {"name": "Apocalisse Luminosa", "animation": "ultimate_light", "damage_mult": 6.0, "effect": {"type": "purify", "removes_buffs": True}, "icon": "💫", "description": "Rimuove tutti i buff nemici e infligge danno enorme!"},
    },
    "dark": {
        "nad": {"name": "Artiglio d'Ombra", "animation": "slash_dark", "damage_mult": 1.0, "effect": None, "icon": "🌑"},
        "sad": {"name": "Maledizione Oscura", "animation": "burst_dark", "damage_mult": 2.6, "effect": {"type": "poison", "damage_per_turn": 0.06, "duration": 4}, "icon": "💀", "description": "Avvelena per 4 turni"},
        "sp": {"name": "Eclissi Totale", "animation": "ultimate_dark", "damage_mult": 5.8, "effect": {"type": "death_mark", "instant_kill_chance": 0.15}, "icon": "🕳️", "description": "15% di eliminazione istantanea!"},
    },
    "shadow": {
        "nad": {"name": "Artiglio d'Ombra", "animation": "slash_shadow", "damage_mult": 1.0, "effect": None, "icon": "🌑"},
        "sad": {"name": "Maledizione Oscura", "animation": "burst_shadow", "damage_mult": 2.6, "effect": {"type": "poison", "damage_per_turn": 0.06, "duration": 4}, "icon": "💀", "description": "Avvelena per 4 turni"},
        "sp": {"name": "Eclissi Totale", "animation": "ultimate_shadow", "damage_mult": 5.8, "effect": {"type": "death_mark", "instant_kill_chance": 0.15}, "icon": "🕳️", "description": "15% di eliminazione istantanea!"},
    },
    "thunder": {
        "nad": {"name": "Scarica Elettrica", "animation": "slash_thunder", "damage_mult": 1.0, "effect": None, "icon": "⚡"},
        "sad": {"name": "Fulmine Divino", "animation": "burst_thunder", "damage_mult": 2.7, "effect": {"type": "stun", "duration": 1}, "icon": "🌩️", "description": "Stordisce per 1 turno con il fulmine"},
        "sp": {"name": "Tempesta di Fulmini", "animation": "ultimate_thunder", "damage_mult": 5.5, "effect": {"type": "chain_lightning", "bounces": 3, "damage_per_bounce": 0.6}, "icon": "⛈️", "description": "Il fulmine rimbalza tra 3 nemici!"},
    },
    "neutral": {
        "nad": {"name": "Colpo Rapido", "animation": "slash_neutral", "damage_mult": 1.0, "effect": None, "icon": "⚔️"},
        "sad": {"name": "Assalto Potenziato", "animation": "burst_neutral", "damage_mult": 2.2, "effect": None, "icon": "💥", "description": "Attacco forte senza effetti speciali"},
        "sp": {"name": "Furia Primordiale", "animation": "ultimate_neutral", "damage_mult": 4.5, "effect": None, "icon": "⚡", "description": "Attacco potente puro"},
    },
}

# Passive skill templates based on rarity
PASSIVE_SKILLS = {
    1: [{"name": "Resistenza Base", "effect": {"defense": 0.05}, "icon": "🛡️"}],
    2: [{"name": "Agilità", "effect": {"speed": 0.08}, "icon": "💨"}, {"name": "Forza Bruta", "effect": {"attack": 0.08}, "icon": "💪"}],
    3: [{"name": "Occhio Critico", "effect": {"crit_rate": 0.08}, "icon": "👁️"}, {"name": "Rigenerazione", "effect": {"heal_per_turn": 0.03}, "icon": "💚"}],
    4: [{"name": "Poise", "effect": {"damage_reduction": 0.10}, "icon": "🛡️"}, {"name": "Frenesia", "effect": {"attack_at_full_hp": 0.20}, "icon": "🔥"}],
    5: [{"name": "Immunità Status", "effect": {"status_immunity": 0.50}, "icon": "✨"}, {"name": "Colpo Fatale", "effect": {"crit_damage": 0.30}, "icon": "💥"}, {"name": "Schivata", "effect": {"dodge_rate": 0.12}, "icon": "💨"}],
    6: [{"name": "Divino", "effect": {"all_stats": 0.15}, "icon": "👑"}, {"name": "Invincibilità Temporanea", "effect": {"invincible_turns_start": 1}, "icon": "🌟"}, {"name": "Super Armatura", "effect": {"damage_reduction": 0.20, "status_immunity": 0.80}, "icon": "⚜️"}],
}

# ─────────────────────────────────────────────────────────────────────
# DEV TEST ONLY — temporary heal source for validating Battle Report
# `healing_done` counter end-to-end.
#
# This dict adds extra passives to specific heroes by NAME (stable across
# UUIDs/restarts). The merge happens in init_combat_char at the same site
# where rarity_passives are assigned to char['passives'].
#
# Reuses the EXISTING `heal_per_turn` branch in process_turn() — no new
# engine mechanic is introduced. Only data.
#
# NOT FINAL HERO DESIGN. Move/remove when the formal kit/skill system is
# wired up. Match by `name` so the same dev passive applies regardless of
# the user_hero instance used.
# ─────────────────────────────────────────────────────────────────────
DEV_TEST_HEAL_HEROES = {
    'Hera': [
        # Hera è una Support rarity 4 (greek/light) — semantica naturale per
        # un test di healing_done. heal_per_turn=0.05 (5% max_hp/turn) è
        # sufficientemente alto per essere chiaramente osservabile in UI senza
        # influenzare il balance complessivo della battle (passive scatta solo
        # se Hera è viva e ha subito damage; capped a max_hp).
        {
            "name": "Cura di Hera (DEV TEST)",
            "effect": {"heal_per_turn": 0.05},
            "icon": "💚",
            "note": "DEV_TEST_ONLY: temporary heal for healing_done validation. Not final design.",
        },
    ],
}


# ═════════════════════════════════════════════════════════════════════
# TARGETING RULES — v16.32 (TASK 4.4-F official targeting)
# ─────────────────────────────────────────────────────────────────────
# Default single-target rule for any skill/attack WITHOUT an explicit
# target spec:
#   1) first valid living enemy Tank
#   2) fallback: closest valid living enemy (Manhattan distance on the
#      9-grid grid_x/grid_y; ties broken by index)
#
# Taunt override (single-target only):
#   if any living enemy Tank has an active taunt status_effect AND the
#   skill is NOT multi-target AND the skill does not ignore_taunt
#   → redirect single target to that Tank.
#
# AoE / multi-target skills are NEVER intercepted by Taunt:
#   - legacy: `skill_type == 'sp'` is treated as AoE-all-enemies
#   - flagged: skill.get('target_type') in MULTI_TARGET_TYPES
#              OR skill.get('multi_target') is True
#              OR skill.get('aoe') is True
#
# Explicit target rules (kept available for future skills, NOT applied
# yet by default attacks/cycle): support / dps / lowest_hp / highest_atk
# / row / column / area / all_enemies / multiple. The dispatcher
# `select_explicit_target()` returns None if no explicit rule is set,
# letting the caller fall through to the Tank-first default.
# ═════════════════════════════════════════════════════════════════════

MULTI_TARGET_TYPES = {
    'all', 'all_enemies', 'aoe', 'row', 'column', 'line', 'area',
    'multiple', 'multi',
}

# hero_class values are 'Tank'/'Support'/'DPS' in DB — match case-insensitive.
def is_alive(unit) -> bool:
    return bool(unit) and bool(unit.get('is_alive'))


def is_tank(unit) -> bool:
    if not unit:
        return False
    hc = str(unit.get('hero_class', '')).strip().lower()
    return hc == 'tank'


def has_active_taunt(unit) -> bool:
    """True if unit has a non-expired taunt status_effect.
    Supports a few naming variants for forward-compat without locking-in
    a single canonical key (engine doesn't apply Taunt today; if/when a
    future skill applies it, any of these shapes will be detected)."""
    if not unit:
        return False
    if unit.get('is_taunting'):
        return True
    for eff in unit.get('status_effects', []) or []:
        t = str(eff.get('type', '')).lower()
        n = str(eff.get('name', '')).lower()
        if t == 'taunt' or n == 'taunt' or eff.get('taunt') is True:
            duration = eff.get('duration', 1)
            if duration is None or duration > 0:
                return True
    return False


def is_multi_target_skill(skill, skill_type: str = None) -> bool:
    """A skill counts as multi-target if:
      - it is the legacy ultimate (`skill_type == 'sp'`), OR
      - skill metadata flags it explicitly.
    Used to bypass Taunt override for AoE/row/area/multi attacks."""
    if skill_type == 'sp':
        return True
    if not isinstance(skill, dict):
        return False
    if skill.get('multi_target') is True or skill.get('aoe') is True:
        return True
    tt = str(skill.get('target_type', '')).strip().lower()
    if tt and tt in MULTI_TARGET_TYPES:
        return True
    # Explicit count > 1 also counts as multi
    try:
        if int(skill.get('target_count', 1)) > 1:
            return True
    except (TypeError, ValueError):
        pass
    return False


def skill_ignores_taunt(skill) -> bool:
    return isinstance(skill, dict) and skill.get('ignore_taunt') is True


def _grid_distance(a, b) -> int:
    """Manhattan distance on the 9-grid using grid_x/grid_y when available."""
    try:
        dx = abs(int(a.get('grid_x', 4)) - int(b.get('grid_x', 4)))
        dy = abs(int(a.get('grid_y', 4)) - int(b.get('grid_y', 4)))
        return dx + dy
    except (TypeError, ValueError):
        return 0


def select_default_single_target(attacker, enemies):
    """Tank-first default targeting:
      1) first living enemy Tank (input order),
      2) fallback closest living enemy by Manhattan grid distance,
      3) safety net: first living enemy.
    Returns None if no living enemy."""
    living = [e for e in (enemies or []) if is_alive(e)]
    if not living:
        return None
    tanks = [e for e in living if is_tank(e)]
    if tanks:
        return tanks[0]
    if attacker is not None:
        return min(living, key=lambda e: _grid_distance(attacker, e))
    return living[0]


def select_explicit_target(skill, attacker, enemies):
    """If skill metadata declares an explicit single-target rule, return it.
    Returns None when no explicit rule is set (caller falls through to
    default Tank-first). DOES NOT handle multi-target skills (caller checks
    `is_multi_target_skill` first)."""
    if not isinstance(skill, dict):
        return None
    living = [e for e in (enemies or []) if is_alive(e)]
    if not living:
        return None
    rule = str(skill.get('target_type', '') or skill.get('target_role', '')).strip().lower()
    if not rule:
        return None
    # Role-based rules
    if rule in ('tank', 'frontline'):
        cands = [e for e in living if is_tank(e)]
        return cands[0] if cands else None
    if rule in ('support', 'backline', 'cleric', 'healer'):
        cands = [e for e in living if str(e.get('hero_class', '')).lower() == 'support']
        return cands[0] if cands else None
    if rule == 'dps':
        cands = [e for e in living if str(e.get('hero_class', '')).lower() == 'dps']
        return cands[0] if cands else None
    # Stat-based rules
    if rule in ('lowest_hp', 'execute'):
        return min(living, key=lambda e: e.get('current_hp', 0))
    if rule == 'highest_hp':
        return max(living, key=lambda e: e.get('current_hp', 0))
    if rule in ('highest_attack', 'highest_atk'):
        return max(living, key=lambda e: e.get('attack', 0) or e.get('physical_damage', 0))
    if rule == 'closest':
        return select_default_single_target(attacker, enemies)
    return None


def apply_taunt_override(original_target, enemies, skill, skill_type=None):
    """If a single-target attack should be intercepted by a taunting Tank,
    return that Tank; otherwise return the original_target unchanged.
    Multi-target / ignore_taunt skills are passed through unchanged.

    v95 — aoe_partial taunt rule:
    - aoe_all / line / column / all_enemies => Taunt NON intercetta (pass-through).
    - aoe_partial / cleave_partial / multi-hit con target_count limitato =>
      la Taunt deve essere rispettata: ritorna il Tank tauntante come priorità,
      così il chiamante può includerlo nel set ridotto.
    - single_target / priority_target => comportamento legacy invariato.
    """
    if original_target is None:
        return None
    if skill_ignores_taunt(skill):
        return original_target
    # v95: distingui aoe_partial dagli aoe pieni.
    tt = str(isinstance(skill, dict) and skill.get('target_type', '') or '').strip().lower()
    is_aoe_partial = bool(isinstance(skill, dict) and (
        skill.get('aoe_partial') is True or
        tt in ('aoe_partial', 'cleave_partial', 'partial')
    ))
    if is_multi_target_skill(skill, skill_type) and not is_aoe_partial:
        return original_target
    living_taunting_tanks = [
        e for e in (enemies or [])
        if is_alive(e) and is_tank(e) and has_active_taunt(e)
    ]
    if not living_taunting_tanks:
        return original_target
    # Choose the first taunting tank by input order (stable behavior).
    chosen = living_taunting_tanks[0]
    if chosen is not original_target:
        try:
            # v95 counter (best-effort, safe se simulate_battle non è ancora chiamato).
            simulate_battle._v95_counters['taunt_redirect_count'] += 1
        except Exception:
            pass
    return chosen
# ═════════════════════════════════════════════════════════════════════


def simulate_battle(team_a: list, team_b: list, max_turns: int = 20) -> dict:
    """
    Simulate a full battle between two teams.
    Each team is a list of character dicts with stats and skills.
    Returns detailed battle log with animations.
    """
    # PROJECT_M Track B — pre-fight status seam call (single point).
    # With the canary flag OFF the seam is strictly identity, so team_a /
    # team_b references are unchanged. With the flag ON + dry_run=True
    # (NOT used in live runtime), the seam attaches a preview envelope to a
    # shallow copy WITHOUT mutating the originals. The live path therefore
    # remains byte-identical with the pre-patch behavior while the flag is OFF.
    team_a = _project_m_status_seam(team_a)
    team_b = _project_m_status_seam(team_b)

    # PROJECT_T Track B — second-slice seam call (single point, identity when flag OFF).
    # Mirrors the first-slice pattern above. With STATUS_RUNTIME_SECOND_SLICE_ENABLED
    # OFF/unset (default), the call is strict identity, so team_a / team_b are
    # unchanged. Flag ON behavior is only reachable from explicit dry_run=True
    # callers (tests/canary), never from live runtime in this pack.
    team_a = _project_t_second_slice_seam(team_a)
    team_b = _project_t_second_slice_seam(team_b)

    battle_log = []
    turn = 0
    
    # ══════════════════════════════════════════════════════════════════════
    # RAGE SYSTEM — regole finali (Msg 498):
    #   range: 0..150 (cap hard 150)
    #   ultimate READY quando rage >= 100 (soglia di attivazione)
    #   overflow (>100) scala SOLO l'effetto principale della ultimate:
    #       multiplier = 1 + max(0, rage - 100) / 100
    #   ultimate cast → rage resettata a 0
    #   rage guadagnata SOLO su colpi che vanno a segno:
    #       attaccante: +25 (attack), +35 (skill_1), +40 (skill_2)
    #       difensore:  +10 per colpo subito
    #       miss/dodge: +0 a entrambi
    #   rarity <= 3 (★1..3) NON ha ultimate e non la lancia mai.
    # ══════════════════════════════════════════════════════════════════════
    RAGE_CAP = 150
    ULT_READY_THRESHOLD = 100
    RAGE_GAIN_ATTACK = 25
    RAGE_GAIN_SKILL_1 = 35
    RAGE_GAIN_SKILL_2 = 40
    RAGE_GAIN_DEFENDER_HIT = 10
    
    # Initialize combat state
    for char in team_a + team_b:
        char['current_hp'] = char.get('max_hp', char.get('hp', 10000))
        char['max_hp_battle'] = char['current_hp']
        # Rage: cap 150, display threshold a 100 (ult ready)
        char['max_rage'] = RAGE_CAP
        char['rage_threshold'] = ULT_READY_THRESHOLD
        char['rage'] = int(char.get('start_rage', char.get('initial_rage', 0)))
        # Legacy alias — mantenuto per codice che ancora legge sp_gauge
        char['sp_gauge'] = char['rage']
        # Cycle: attack → skill_1 → skill_2 → loop (saltando slot assenti)
        char['action_cycle_idx'] = 0
        char['status_effects'] = []
        char['is_alive'] = True
        char['total_damage_dealt'] = 0
        # v16.29 — Battle Report counters: damage subito + heal effettuato.
        # Usati solo per stats post-battle (NON influenzano combat balance).
        # damage_received: incrementato dove total_damage_received per target
        # quando damage viene applicato a HP (skill, AoE, DoT). Usa l'actual
        # HP delta (capped a 0..max_hp) per evitare di contare overkill.
        # healing_done:    incrementato per il caster di un'azione di heal
        # con l'actual HP restored (capped a max_hp_battle) per evitare overheal.
        char['total_damage_received'] = 0
        char['total_healing_done'] = 0
        # has_ultimate: rarità ≤ 3 NON ha ultimate (per volontà utente)
        char['has_ultimate'] = int(char.get('rarity', 1)) > 3
    
    # v95 — Battle Report extension counters (NON modifica balance, solo report).
    v95_counters = {
        "dot_damage_done": 0,
        "status_applied_count": 0,
        "healing_done": 0,
        "cleanse_count": 0,
        "status_prevented_by_immunity_count": 0,
        "taunt_redirect_count": 0,
    }
    # Espone il riferimento per execute_skill via attributo del simulate scope.
    simulate_battle._v95_counters = v95_counters
    
    while turn < max_turns:
        turn += 1
        turn_log = {"turn": turn, "actions": []}
        
        # Combine and sort by speed
        all_chars = [(c, 'team_a') for c in team_a if c['is_alive']] + \
                    [(c, 'team_b') for c in team_b if c['is_alive']]
        all_chars.sort(key=lambda x: x[0].get('speed', 100), reverse=True)
        
        for char, team_id in all_chars:
            if not char['is_alive']:
                continue
            
            # Process status effects
            status_actions = process_status_effects(char, v95_counters=v95_counters)
            turn_log['actions'].extend(status_actions)
            
            if not char['is_alive']:
                continue
            
            # Check if stunned/frozen
            if any(s['type'] in ('stun', 'freeze') for s in char['status_effects']):
                turn_log['actions'].append({
                    "type": "skip",
                    "actor": char['name'],
                    "actor_id": char['id'],
                    "team": team_id,
                    "reason": "Stordito/Congelato",
                    "animation": "stunned",
                })
                continue
            
            # Pick target — v16.32 official targeting rules:
            #   Default = Tank-first → fallback closest living enemy.
            #   Old behavior (lowest HP execute) is preserved as the
            #   `lowest_hp` explicit rule, NOT default.
            enemies = [c for c in (team_b if team_id == 'team_a' else team_a) if c['is_alive']]
            if not enemies:
                break

            target = select_default_single_target(char, enemies)
            if target is None:
                break
            
            # ═════════════════════════════════════════════════════════════
            # ACTION SELECTION — cycle deterministico + rage (Msg 498).
            # ---------------------------------------------------------------
            # Priorità:
            #   1. Se rage ≥ 100 E l'eroe HA l'ultimate → lancia ultimate
            #      (overflow oltre 100 scala solo l'effetto principale).
            #   2. Altrimenti cycle: attack → skill_1 → skill_2 → loop
            #      (saltando gli slot assenti).
            # Rage guadagnata SOLO su colpi a segno (dopo execute_skill).
            # ═════════════════════════════════════════════════════════════
            element = char.get('element', 'neutral')
            skills = ELEMENT_SKILLS.get(element, ELEMENT_SKILLS['neutral'])

            # Slot del cycle disponibili per questo eroe.
            has_skill_1 = bool(skills.get('sad'))
            has_skill_2 = bool(char.get('skill_2'))  # hero-specific, opt-in

            cycle_slots = ['attack']
            if has_skill_1: cycle_slots.append('skill_1')
            if has_skill_2: cycle_slots.append('skill_2')

            action = None
            used_rage_at_cast = 0
            rage_gain_if_hit = 0
            # --- ULTIMATE ---
            if char['rage'] >= ULT_READY_THRESHOLD and char.get('has_ultimate', False):
                # Overflow multiplier: 1 + max(0, rage-100)/100
                # Es: rage=100 → 1.00x, rage=125 → 1.25x, rage=150 → 1.50x
                overflow_mult = 1.0 + max(0, char['rage'] - ULT_READY_THRESHOLD) / 100.0
                action = execute_skill(
                    char, target, enemies, skills['sp'], 'sp', team_id,
                    overflow_multiplier=overflow_mult,
                )
                # Reset rage dopo il cast (before defender gain below)
                char['rage'] = 0
                char['sp_gauge'] = 0
                # Attaccante NON guadagna rage sul cast ult (azzeramento)
                rage_gain_if_hit = 0
            else:
                slot = cycle_slots[char['action_cycle_idx'] % len(cycle_slots)]
                char['action_cycle_idx'] = (char['action_cycle_idx'] + 1) % len(cycle_slots)

                if slot == 'attack':
                    attack_data = dict(skills['nad'])
                    char_hero_id_a = str(char.get('hero_id', ''))
                    char_name_a = str(char.get('name', ''))
                    if char_hero_id_a == 'greek_hoplite' or 'Hoplite' in char_name_a:
                        attack_data['name'] = 'Affondo di Falange'
                        attack_data['description'] = 'Thrust lineare con la lancia da guardia neutra.'
                    action = execute_skill(char, target, enemies, attack_data, 'nad', team_id)
                    rage_gain_if_hit = RAGE_GAIN_ATTACK
                elif slot == 'skill_1':
                    skill_data = dict(skills['sad'])
                    char_hero_id = str(char.get('hero_id', ''))
                    char_name = str(char.get('name', ''))
                    if char_hero_id == 'greek_hoplite' or char_name == 'Hoplite' or 'Hoplite' in char_name:
                        skill_data['name'] = 'Guardia Ferrea'
                        skill_data['description'] = 'Stance difensiva Phalanx: riduce damage in arrivo.'
                    action = execute_skill(char, target, enemies, skill_data, 'sad', team_id)
                    rage_gain_if_hit = RAGE_GAIN_SKILL_1
                elif slot == 'skill_2':
                    skill_data = char['skill_2']
                    action = execute_skill(char, target, enemies, skill_data, 'sad', team_id)
                    rage_gain_if_hit = RAGE_GAIN_SKILL_2

                # Rage gain SOLO se il colpo è andato a segno (non dodge)
                if action and action.get('type') != 'dodge':
                    char['rage'] = min(RAGE_CAP, char['rage'] + rage_gain_if_hit)

            # Difensori colpiti: +10 rage ciascuno (per QUALSIASI tipo di hit,
            # ultimate inclusa). Applicato solo se action non è dodge.
            if action and action.get('type') != 'dodge':
                hit_ids = [t['id'] for t in action.get('targets', []) if t.get('damage', 0) > 0]
                if hit_ids:
                    all_chars_set = team_a + team_b
                    for c in all_chars_set:
                        if c.get('id') in hit_ids and c['is_alive']:
                            c['rage'] = min(RAGE_CAP, c.get('rage', 0) + RAGE_GAIN_DEFENDER_HIT)
                            c['sp_gauge'] = c['rage']
            char['sp_gauge'] = char['rage']  # legacy alias
            
            if action:
                turn_log['actions'].append(action)
            
            # Passive: heal per turn
            for passive in char.get('passives', []):
                if 'heal_per_turn' in passive.get('effect', {}):
                    heal_amount = int(char['max_hp_battle'] * passive['effect']['heal_per_turn'])
                    # v16.29: actual_heal = HP delta reale (capped a max_hp_battle)
                    # per evitare di contare overheal nel total_healing_done.
                    old_hp = char['current_hp']
                    char['current_hp'] = min(char['max_hp_battle'], char['current_hp'] + heal_amount)
                    actual_heal = char['current_hp'] - old_hp
                    char['total_healing_done'] = char.get('total_healing_done', 0) + actual_heal
                    turn_log['actions'].append({
                        "type": "heal", "actor": char['name'], "actor_id": char['id'],
                        "team": team_id, "amount": heal_amount, "animation": "heal_green",
                    })
            
            # Check if battle is over
            if not any(c['is_alive'] for c in team_b):
                break
            if not any(c['is_alive'] for c in team_a):
                break
        
        battle_log.append(turn_log)
        
        # Check victory conditions
        team_a_alive = any(c['is_alive'] for c in team_a)
        team_b_alive = any(c['is_alive'] for c in team_b)
        
        if not team_a_alive or not team_b_alive:
            break
    
    # Determine winner
    team_a_hp = sum(c['current_hp'] for c in team_a if c['is_alive'])
    team_b_hp = sum(c['current_hp'] for c in team_b if c['is_alive'])
    team_a_alive_count = sum(1 for c in team_a if c['is_alive'])
    team_b_alive_count = sum(1 for c in team_b if c['is_alive'])
    
    victory = team_a_alive_count > team_b_alive_count or (team_a_alive_count == team_b_alive_count and team_a_hp > team_b_hp)
    
    # Build result
    result = {
        "victory": victory,
        "turns": turn,
        "battle_log": battle_log,
        "team_a_survivors": team_a_alive_count,
        "team_b_survivors": team_b_alive_count,
        "team_a_final": [{"id": c['id'], "name": c['name'], "hp": c['current_hp'], "max_hp": c['max_hp_battle'], "rage": c.get('rage', 0), "max_rage": c.get('max_rage', 150), "rage_threshold": c.get('rage_threshold', 100), "has_ultimate": c.get('has_ultimate', False), "is_alive": c['is_alive'], "damage_dealt": c['total_damage_dealt'], "damage_received": c.get('total_damage_received', 0), "healing_done": c.get('total_healing_done', 0), "image": c.get('image'), "element": c.get('element'), "hero_class": c.get('hero_class'), "rarity": c.get('rarity', 1), "faction": c.get('faction'), "sprite_url": c.get('sprite_url'), "grid_x": c.get('grid_x', 4), "grid_y": c.get('grid_y', 4)} for c in team_a],
        "team_b_final": [{"id": c['id'], "name": c['name'], "hp": c['current_hp'], "max_hp": c['max_hp_battle'], "rage": c.get('rage', 0), "max_rage": c.get('max_rage', 150), "rage_threshold": c.get('rage_threshold', 100), "has_ultimate": c.get('has_ultimate', False), "is_alive": c['is_alive'], "damage_dealt": c['total_damage_dealt'], "damage_received": c.get('total_damage_received', 0), "healing_done": c.get('total_healing_done', 0), "image": c.get('image'), "element": c.get('element'), "hero_class": c.get('hero_class'), "rarity": c.get('rarity', 1), "faction": c.get('faction'), "sprite_url": c.get('sprite_url'), "grid_x": c.get('grid_x', 4), "grid_y": c.get('grid_y', 4)} for c in team_b],
        "mvp": max(team_a, key=lambda c: c['total_damage_dealt'])['name'] if victory else None,
    }

    # v95 — Battle Report extension: aggiunge metriche aggregate senza alterare
    # team_a_final, team_b_final, mvp o altri campi legacy.
    total_dmg_done = sum(c.get('total_damage_dealt', 0) for c in (team_a + team_b))
    total_dmg_taken = sum(c.get('total_damage_received', 0) for c in (team_a + team_b))
    total_heal_done = sum(c.get('total_healing_done', 0) for c in (team_a + team_b))
    v95_counters['healing_done'] = total_heal_done
    result["total_damage_done"] = total_dmg_done
    result["total_damage_taken"] = total_dmg_taken
    result["v95_battle_report"] = dict(v95_counters)
    result["v95_battle_report"]["pack"] = "MEGA_RELEASE_ACCELERATION_44_v95"

    return result


def execute_skill(attacker: dict, target: dict, all_enemies: list, skill: dict, skill_type: str, team_id: str, overflow_multiplier: float = 1.0) -> dict:
    """Execute a skill and return the action log.
    
    overflow_multiplier: applicato SOLO all'effetto principale della
    ultimate (damage se offensiva, heal se cura, shield se difensiva).
    Default 1.0 per attacchi non-ultimate.

    v16.32 — Targeting redirect:
      - For SINGLE-TARGET skills, an explicit target rule on the skill
        (target_type/target_role: tank/dps/support/lowest_hp/...) takes
        precedence over the caller-provided `target`. If no explicit rule
        is set, `target` is used as-is (caller already applied Tank-first
        default via `select_default_single_target`).
      - Then Taunt override redirects single-target attacks to a living
        taunting Tank if any (skipped for AoE/multi-target/ignore_taunt).
      - Multi-target skills (ultimate `sp`, or skill metadata flagged)
        are NOT redirected; they keep hitting their intended target set
        (`all_enemies` for `sp`, etc.).
    """
    if not is_multi_target_skill(skill, skill_type):
        # Explicit target rule overrides the caller's default pick.
        explicit = select_explicit_target(skill, attacker, all_enemies)
        if explicit is not None:
            target = explicit
        # Taunt override (single-target only).
        target = apply_taunt_override(target, all_enemies, skill, skill_type) or target

    atk = attacker.get('attack', 1000)
    dfn = target.get('defense', 500)
    
    # Apply passive bonuses
    for passive in attacker.get('passives', []):
        eff = passive.get('effect', {})
        if 'attack_at_full_hp' in eff and attacker['current_hp'] >= attacker['max_hp_battle'] * 0.99:
            atk *= (1 + eff['attack_at_full_hp'])
        if 'all_stats' in eff:
            atk *= (1 + eff['all_stats'])
    
    # Base damage
    base_damage = max(1, atk - dfn * 0.5)
    damage_mult = skill.get('damage_mult', 1.0)
    total_damage = int(base_damage * damage_mult * random.uniform(0.9, 1.1))
    
    # Ultimate overflow: scala SOLO l'effetto principale (danno offensivo)
    if skill_type == 'sp' and overflow_multiplier > 1.0:
        total_damage = int(total_damage * overflow_multiplier)
    
    # Crit check
    crit = False
    crit_rate = attacker.get('crit_rate', 0.10)
    crit_damage = attacker.get('crit_damage', 1.5)
    if random.random() < crit_rate:
        crit = True
        total_damage = int(total_damage * crit_damage)
    
    # Dodge check
    dodge_rate = target.get('dodge_rate', 0)
    dodged = random.random() < dodge_rate
    
    if dodged:
        return {
            "type": "dodge", "actor": attacker['name'], "actor_id": attacker['id'],
            "target": target['name'], "target_id": target['id'],
            "team": team_id, "skill": skill, "skill_type": skill_type,
            "animation": "dodge",
        }
    
    # Apply damage reduction
    for passive in target.get('passives', []):
        if 'damage_reduction' in passive.get('effect', {}):
            total_damage = int(total_damage * (1 - passive['effect']['damage_reduction']))
    
    # Apply damage
    targets_hit = []
    if skill_type == 'sp':
        # Ultimate hits all enemies
        for enemy in all_enemies:
            if enemy['is_alive']:
                dmg = int(total_damage * random.uniform(0.85, 1.0))
                # v16.29: actual_dmg cattura il HP delta reale (capped a remaining_hp)
                # per evitare di contare overkill nel total_damage_received.
                old_hp = enemy['current_hp']
                enemy['current_hp'] = max(0, enemy['current_hp'] - dmg)
                actual_dmg = old_hp - enemy['current_hp']
                if enemy['current_hp'] <= 0:
                    enemy['is_alive'] = False
                attacker['total_damage_dealt'] += dmg
                enemy['total_damage_received'] = enemy.get('total_damage_received', 0) + actual_dmg
                targets_hit.append({"name": enemy['name'], "id": enemy['id'], "damage": dmg, "killed": not enemy['is_alive'], "hp_remaining": enemy['current_hp']})
    else:
        # Single target
        # v16.29: actual_dmg HP delta reale (capped) per total_damage_received.
        old_hp = target['current_hp']
        target['current_hp'] = max(0, target['current_hp'] - total_damage)
        actual_dmg = old_hp - target['current_hp']
        if target['current_hp'] <= 0:
            target['is_alive'] = False
        attacker['total_damage_dealt'] += total_damage
        target['total_damage_received'] = target.get('total_damage_received', 0) + actual_dmg
        targets_hit.append({"name": target['name'], "id": target['id'], "damage": total_damage, "killed": not target['is_alive'], "hp_remaining": target['current_hp']})
    
    # Apply status effect
    effect_applied = None
    if skill.get('effect'):
        eff = skill['effect']
        eff_type = eff.get('type')
        # v95 — Cleanse handling (skill che applica cleanse direttamente).
        if eff_type == 'cleanse':
            cleanse_mode = eff.get('mode', 'all')
            removed = _v95_apply_cleanse(target, mode=cleanse_mode, category=eff.get('category'), priority_key=eff.get('priority'))
            try:
                simulate_battle._v95_counters['cleanse_count'] += removed
            except Exception:
                pass
            effect_applied = {"type": "cleanse", "mode": cleanse_mode, "removed": removed}
        elif eff_type == 'death_mark' and random.random() < eff.get('instant_kill_chance', 0):
            target['current_hp'] = 0
            target['is_alive'] = False
            effect_applied = {"type": "instant_kill", "target": target['name']}
        # v95 DoT: estende a burn/poison/bleed/shock/frostbite/curse con stack policy.
        elif eff_type in ('burn', 'poison', 'bleed', 'shock', 'frostbite', 'curse'):
            applied_count = 0
            blocked_immunity = 0
            for enemy in (all_enemies if skill_type == 'sp' else [target]):
                if not enemy.get('is_alive', True):
                    continue
                # immunity blocca nuove applicazioni (non rimuove esistenti).
                if _v95_has_immunity(enemy, eff_type):
                    blocked_immunity += 1
                    continue
                if _v95_apply_dot_with_stack_policy(
                    enemy, eff_type,
                    eff.get('damage_per_turn', 0.05),
                    eff.get('duration', 3),
                    attacker.get('name', '?'),
                ):
                    applied_count += 1
            try:
                simulate_battle._v95_counters['status_applied_count'] += applied_count
                simulate_battle._v95_counters['status_prevented_by_immunity_count'] += blocked_immunity
            except Exception:
                pass
            effect_applied = {"type": eff_type, "duration": eff.get('duration', 0), "applied": applied_count, "immunity_blocks": blocked_immunity}
        # v95 — Hard control (stun/freeze/silence/sleep/petrify): conversione su boss.
        elif eff_type in ('stun', 'freeze', 'silence', 'sleep', 'petrify'):
            blocked_immunity = 0
            if _v95_has_immunity(target, eff_type):
                blocked_immunity = 1
                try:
                    simulate_battle._v95_counters['status_prevented_by_immunity_count'] += 1
                except Exception:
                    pass
                effect_applied = {"type": eff_type, "blocked_by_immunity": True}
            else:
                converted = _v95_maybe_convert_boss_hardcontrol(target, eff_type, eff.get('duration', 1))
                if converted is not None:
                    # boss: nessun hard-lock, applica versione convertita
                    target.setdefault('status_effects', []).append(converted)
                    try:
                        simulate_battle._v95_counters['status_applied_count'] += 1
                    except Exception:
                        pass
                    effect_applied = {"type": eff_type, "converted_for_boss": converted['type'], "duration": converted['turns_remaining']}
                else:
                    target.setdefault('status_effects', []).append({
                        "type": eff_type,
                        "turns_remaining": eff.get('duration', 1),
                    })
                    try:
                        simulate_battle._v95_counters['status_applied_count'] += 1
                    except Exception:
                        pass
                    effect_applied = {"type": eff_type, "duration": eff.get('duration', 1)}
        elif eff_type == 'slow':
            target['speed'] = int(target.get('speed', 100) * (1 - eff.get('speed_reduction', 0.3)))
            effect_applied = {"type": "slow", "reduction": eff.get('speed_reduction', 0.3)}
        elif eff_type == 'weaken':
            target['attack'] = int(target.get('attack', 1000) * (1 - eff.get('attack_reduction', 0.25)))
            effect_applied = {"type": "weaken", "reduction": eff.get('attack_reduction', 0.25)}
        elif eff_type == 'defense_break':
            target['defense'] = int(target.get('defense', 500) * (1 - eff.get('reduction', 0.4)))
            effect_applied = {"type": "defense_break", "reduction": eff.get('reduction', 0.4)}
    
    return {
        "type": "attack",
        "actor": attacker['name'],
        "actor_id": attacker['id'],
        "team": team_id,
        "skill_type": skill_type,
        "skill": {
            "name": skill.get('name', 'Attacco'),
            "icon": skill.get('icon', '⚔️'),
            "description": skill.get('description', ''),
            "animation": skill.get('animation', 'slash_neutral'),
        },
        "targets": targets_hit,
        "total_damage": sum(t['damage'] for t in targets_hit),
        "crit": crit,
        "effect": effect_applied,
    }


def process_status_effects(char: dict, v95_counters: dict = None) -> list:
    """Process DoT and other status effects at start of turn.

    v95 runtime apply (MEGA_RELEASE_ACCELERATION_44):
    - Estende il DoT a: burn, poison, bleed, frostbite, curse (tick end_of_target_turn).
    - 'shock' è gestito come ridotto-skill-power on_action_attempt (no DoT tick).
    - 'frostbite' applica anche un breve speed-down (capped, una sola volta).
    - Aggiorna v95_counters['dot_damage_done'] (additivo sul battle report).
    - NESSUN side effect su balance esistente.
    """
    actions = []
    new_effects = []
    dot_types = ('burn', 'poison', 'bleed', 'frostbite', 'curse')

    for effect in char.get('status_effects', []):
        if effect['type'] in dot_types:
            dot_damage = int(char['max_hp_battle'] * effect.get('damage_per_turn', 0.05))
            old_hp = char['current_hp']
            char['current_hp'] = max(0, char['current_hp'] - dot_damage)
            actual_dmg = old_hp - char['current_hp']
            char['total_damage_received'] = char.get('total_damage_received', 0) + actual_dmg
            if v95_counters is not None:
                v95_counters['dot_damage_done'] = v95_counters.get('dot_damage_done', 0) + actual_dmg
            if char['current_hp'] <= 0:
                char['is_alive'] = False

            effect_names = {
                'burn': '🔥 Ustione',
                'poison': '☠️ Veleno',
                'bleed': '🩸 Sanguinamento',
                'frostbite': '❄️ Congelamento Lento',
                'curse': '🕯️ Maledizione',
            }
            actions.append({
                "type": "dot",
                "target": char['name'],
                "target_id": char['id'],
                "damage": dot_damage,
                "effect_type": effect['type'],
                "effect_name": effect_names.get(effect['type'], effect['type']),
                "animation": f"dot_{effect['type']}",
            })

            # v95 frostbite: applica un piccolo speed-down a runtime (additivo, capped).
            if effect['type'] == 'frostbite' and not effect.get('_v95_slow_applied'):
                try:
                    cur_speed = int(char.get('speed', 100))
                    char['speed'] = max(20, int(cur_speed * 0.85))
                    effect['_v95_slow_applied'] = True
                except Exception:
                    pass

        effect['turns_remaining'] -= 1
        if effect['turns_remaining'] > 0:
            new_effects.append(effect)

    char['status_effects'] = new_effects
    return actions


def prepare_battle_character(hero_data: dict, user_hero_data: dict = None, position: dict = None) -> dict:
    """Prepare a character for battle with comprehensive stats"""
    stats = hero_data.get('base_stats', {})
    element = hero_data.get('element', 'neutral')
    rarity = hero_data.get('rarity', 1)
    
    # Level multiplier
    level = user_hero_data.get('level', 1) if user_hero_data else 1
    level_mult = 1 + (level - 1) * 0.05
    
    # Build combat stats from new comprehensive system
    char = {
        'id': hero_data.get('id', str(uuid.uuid4())),
        'name': hero_data.get('name', 'Sconosciuto'),
        'element': element,
        'rarity': rarity,
        'faction': hero_data.get('faction'),  # needed for battle background resolver
        'image': hero_data.get('image_url') or hero_data.get('image'),
        'hero_class': hero_data.get('hero_class', 'DPS'),
        'sprite_url': f"/api/sprites/{hero_data.get('id', '')}" if hero_data.get('sprite_sheet_base64') else None,
        'hp': int(stats.get('hp', 8000) * level_mult),
        'speed': int(stats.get('speed', 100) * level_mult),
        'physical_damage': int(stats.get('physical_damage', 1000) * level_mult),
        'magic_damage': int(stats.get('magic_damage', 800) * level_mult),
        'physical_defense': int(stats.get('physical_defense', 400) * level_mult),
        'magic_defense': int(stats.get('magic_defense', 350) * level_mult),
        'healing': int(stats.get('healing', 0) * level_mult),
        'healing_received': stats.get('healing_received', 1.0),
        'damage_rate': stats.get('damage_rate', 1.0),
        'penetration': stats.get('penetration', 0.05),
        'dodge': stats.get('dodge', 0.05),
        'crit_chance': stats.get('crit_chance', 0.10),
        'crit_damage': stats.get('crit_damage', 1.5),
        'hit_rate': stats.get('hit_rate', 0.90),
        'combo_rate': stats.get('combo_rate', 0.10),
        'block_rate': stats.get('block_rate', 0.05),
        # Legacy compat
        'attack': int((stats.get('physical_damage', 1000) + stats.get('magic_damage', 800)) / 2 * level_mult),
        'defense': int((stats.get('physical_defense', 400) + stats.get('magic_defense', 350)) / 2 * level_mult),
        'crit_rate': stats.get('crit_chance', 0.10),
        'dodge_rate': stats.get('dodge', 0.05),
    }
    
    # Get skills based on element
    element_skills = ELEMENT_SKILLS.get(element, ELEMENT_SKILLS.get('neutral', ELEMENT_SKILLS.get('fire', {})))
    if element_skills:
        char['skills'] = {
            'nad': element_skills.get('nad', {}),
            'sad': element_skills.get('sad', {}),
            'sp': element_skills.get('sp', {}),
        }
    else:
        char['skills'] = {}
    
    # Get passives based on rarity (+ DEV_TEST_HEAL_HEROES extras by name)
    rarity_passives = PASSIVE_SKILLS.get(min(rarity, 6), PASSIVE_SKILLS.get(1, []))
    # DEV TEST ONLY — append per-hero extra passives keyed by name.
    # Does NOT replace rarity_passives; only adds entries (e.g. Hera +heal_per_turn).
    extra_passives = DEV_TEST_HEAL_HEROES.get(char.get('name'), [])
    char['passives'] = list(rarity_passives) + list(extra_passives)
    
    # Apply passive stat bonuses
    for passive in char['passives']:
        eff = passive.get('effect', {})
        if 'dodge_rate' in eff:
            char['dodge'] += eff['dodge_rate']
            char['dodge_rate'] += eff['dodge_rate']
        if 'all_stats' in eff:
            m = 1 + eff['all_stats']
            char['physical_damage'] = int(char['physical_damage'] * m)
            char['magic_damage'] = int(char['magic_damage'] * m)
            char['physical_defense'] = int(char['physical_defense'] * m)
            char['magic_defense'] = int(char['magic_defense'] * m)
            char['hp'] = int(char['hp'] * m)
            char['speed'] = int(char['speed'] * m)
            char['attack'] = int(char['attack'] * m)
            char['defense'] = int(char['defense'] * m)
    
    # Apply column-based position buffs (3x3 grid)
    if position:
        col = position.get('x', 1)  # 0=support, 1=dps, 2=tank
        for role_name, role_data in COLUMN_ROLES.items():
            if col == role_name:
                for stat, buff_val in role_data['buff'].items():
                    if stat in char:
                        if isinstance(char[stat], int):
                            char[stat] = int(char[stat] * (1 + buff_val))
                        else:
                            char[stat] = char[stat] * (1 + buff_val)
                char['position_zone'] = role_data['name']
                break
        # Preserve original formation coordinates for UI grid rendering
        char['grid_x'] = position.get('x', 1)
        char['grid_y'] = position.get('y', 1)
    else:
        # default center (non dovrebbe accadere in battle reali)
        char['grid_x'] = 4
        char['grid_y'] = 4
    
    char['max_hp'] = char['hp']
    
    return char


def generate_enemy_team(power_level: int, count: int = 6) -> list:
    """Generate an enemy team based on power level"""
    elements = ['fire', 'water', 'earth', 'wind', 'thunder', 'light', 'shadow']
    enemy_names = [
        "Ombra Errante", "Spirito Maligno", "Bestia Infernale",
        "Guerriero Oscuro", "Mago Corrotto", "Titano Caduto",
        "Demone Minore", "Custode Antico", "Drago d'Ombra",
    ]
    
    enemies = []
    for i in range(count):
        element = elements[i % len(elements)]
        mult = power_level / 10000
        # Grid positioning 3x3: 6 enemies usano 2 righe (1,4) x 3 colonne (1,4,7)
        col_idx = i % 3        # 0,1,2
        row_idx = i // 3       # 0,1 (per 6 unità), 2 solo se count>6
        grid_x = 1 + col_idx * 3   # → 1 / 4 / 7
        grid_y = 1 + row_idx * 3   # → 1 / 4 / 7
        enemy = {
            'id': f'enemy_{i}',
            'name': random.choice(enemy_names),
            'element': element,
            'rarity': min(6, max(1, int(mult))),
            'hero_class': random.choice(['DPS', 'Tank', 'Support']),
            'hp': int(8000 * mult * random.uniform(0.8, 1.2)),
            'attack': int(1000 * mult * random.uniform(0.8, 1.2)),
            'physical_damage': int(1200 * mult * random.uniform(0.8, 1.2)),
            'magic_damage': int(900 * mult * random.uniform(0.8, 1.2)),
            'defense': int(500 * mult * random.uniform(0.8, 1.2)),
            'physical_defense': int(500 * mult * random.uniform(0.8, 1.2)),
            'magic_defense': int(400 * mult * random.uniform(0.8, 1.2)),
            'speed': int(100 * mult * random.uniform(0.8, 1.2)),
            'crit_rate': 0.08,
            'crit_chance': 0.08,
            'crit_damage': 1.4,
            'dodge_rate': 0.03,
            'dodge': 0.03,
            'hit_rate': 0.88,
            'combo_rate': 0.08,
            'block_rate': 0.08,
            'penetration': 0.05,
            'damage_rate': 1.0,
            'healing': 0,
            'healing_received': 1.0,
            'skills': ELEMENT_SKILLS.get(element, ELEMENT_SKILLS['neutral']),
            'passives': PASSIVE_SKILLS.get(min(int(mult), 6), PASSIVE_SKILLS[1]),
            'grid_x': grid_x,
            'grid_y': grid_y,
        }
        enemies.append(enemy)
    
    return enemies


# ===================== ROUTES =====================

def create_battle_routes(db, get_current_user, serialize_doc, calculate_hero_power):
    router = APIRouter(prefix="/api")

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
    async def simulate_battle_endpoint(request: Request, current_user: dict = Depends(get_current_user)):
        """Simulate a battle with the user's active team.

        SECURITY_HOTFIX_A — Fail-closed guard PRIMA di qualsiasi DB read/write.
        L'endpoint legacy resta DISABLED in pre-QA: concedeva gold/EXP/inventory drops
        in modo non server-scoped, non idempotente, senza ledger. Riabilitabile solo
        via env esplicito BATTLE_SIMULATE_LIVE_ENABLED=true, e SOLO transitoriamente
        finche' non esiste un runtime authoritative server-scoped.

        v108_POSTQA_A preview guard: kept as defense in depth dopo il primo gate.
        """
        # SECURITY_HOTFIX_A — fail-closed PRIMA di tutto (no body parse, no DB).
        if os.getenv('BATTLE_SIMULATE_LIVE_ENABLED', '').strip().lower() not in ('true', '1', 'yes', 'on'):
            raise HTTPException(status_code=423, detail={
                'code': 'BATTLE_SIMULATE_LIVE_DISABLED_PRE_QA',
                'message': 'Legacy live battle simulate is disabled before authoritative server-scoped battle runtime.',
                'status': 'blocked',
                'device_qa_status': 'blocked',
                'hotfix': 'SECURITY_HOTFIX_A',
            })
        # v108_POSTQA_A — Preview guard (defense in depth).
        try:
            body = await request.json()
        except Exception:
            body = None
        if isinstance(body, dict):
            preview_markers = (
                str(body.get('battle_engine_mode') or '').lower() == 'preview' or
                bool(body.get('preview')) is True or
                str(body.get('reward_policy') or '').lower() == 'preview' or
                str(body.get('progress_policy') or '').lower() == 'preview'
            )
            if preview_markers:
                raise HTTPException(status_code=409, detail={
                    'code': 'PREVIEW_SIMULATE_MUTATION_BLOCKED',
                    'message': 'v108_POSTQA_A preview guard: /api/battle/simulate non puo\' essere chiamato in modalita\' preview. Il battle engine legacy e\' mutante e concede reward/EXP/gold/drops live. Usa il preview flow non-authoritative lato client (PREVIEW_REWARD_LOCK_ACTIVE) oppure attendi v108 authoritative.',
                    'pack': 'MEGA_RELEASE_ACCELERATION_61_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A',
                })
        user_id = current_user['id']
        
        # Get active team
        team = await db.teams.find_one({"user_id": user_id, "is_active": True})
        if not team or not team.get('formation'):
            raise HTTPException(status_code=400, detail="Configura un team prima!")
        
        # Build player team
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
        
        # Calculate team power and formation buffs
        positions = [{"x": p.get('x', 0), "y": p.get('y', 0)} for p in team['formation'] if p.get('user_hero_id')]
        
        # Check formation patterns
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
        
        # Adjacency bonus
        adj_result = calculate_adjacency_bonus(positions)
        for char in player_team:
            for stat, val in adj_result['bonus'].items():
                if stat in char and val > 0:
                    char[stat] = int(char[stat] * (1 + val))
        
        # === SYNERGY BONUSES (applied automatically in real-time) ===
        try:
            from synergy_system import calculate_team_synergies
            team_names = [c.get("name", "") for c in player_team]
            team_elements = [c.get("element", "neutral") for c in player_team]
            team_classes = [c.get("hero_class", "DPS") for c in player_team]
            synergy_result = calculate_team_synergies(team_names, team_elements, team_classes)
            synergy_buffs = synergy_result.get("total_buffs", {})
            for char in player_team:
                for stat, val in synergy_buffs.items():
                    if stat in char:
                        if isinstance(char[stat], int):
                            char[stat] = int(char[stat] * (1 + val))
                        elif isinstance(char[stat], float):
                            char[stat] = round(char[stat] + val, 4)
        except Exception:
            synergy_result = {"active_synergies": [], "total_buffs": {}}
            synergy_buffs = {}

        # ── RM1.23-B: TEAM SYNERGIES V2 (gated, additive, no-op default) ──
        # Feature flag: SYNERGY_V2_BATTLE_ENABLED (env-var, default false).
        # When false the V2 calculator is NOT invoked at all and the result
        # block is empty. When true V2 buffs are applied additively AFTER V1
        # without replacing or removing any V1 logic.
        v2_synergy_block = {
            "enabled": False,
            "active_team_synergies_v2": [],
            "near_complete": [],
            "aggregated_buffs": {},
            "members_resolved": 0,
            "members_skipped_legacy_or_orphan": 0,
        }
        if os.getenv("SYNERGY_V2_BATTLE_ENABLED", "false").lower() == "true":
            try:
                from data.synergy_definitions_v2 import get_enabled_team_synergies_v2
                from data.character_bible import CHARACTER_BIBLE_BY_ID as _BIBLE
                from utils.team_synergy_v2_calculator import compute_team_synergies_v2
                # Resolve active team for V2 calc
                _v2_team = await db.teams.find_one({"user_id": user_id, "is_active": True})
                if _v2_team and _v2_team.get("formation"):
                    _v2_uhids = [p.get("user_hero_id") for p in _v2_team.get("formation", []) if p.get("user_hero_id")]
                    _v2_uhs = await db.user_heroes.find({"id": {"$in": _v2_uhids}, "user_id": user_id}).to_list(None)
                    _v2_uh_map = {u["id"]: u for u in _v2_uhs}
                    _v2_hids = list({u.get("hero_id") for u in _v2_uhs if u.get("hero_id")})
                    _v2_h_list = await db.heroes.find({"id": {"$in": _v2_hids}}, {"image_base64": 0}).to_list(None)
                    _v2_h_map = {h["id"]: h for h in _v2_h_list}
                    _v2_res = compute_team_synergies_v2(
                        team_doc=_v2_team,
                        user_heroes_by_id=_v2_uh_map,
                        heroes_by_id=_v2_h_map,
                        enabled_synergies=get_enabled_team_synergies_v2(),
                        bible_ids=set(_BIBLE.keys()),
                    )
                    v2_synergy_block.update(_v2_res)
                    v2_synergy_block["enabled"] = True
                    # Apply V2 aggregated_buffs additively on player_team
                    for char in player_team:
                        for stat, val in v2_synergy_block["aggregated_buffs"].items():
                            if stat.endswith("__flat"):
                                continue  # flat buffs: future battle-handler
                            if stat in char:
                                if isinstance(char[stat], int):
                                    char[stat] = int(char[stat] * (1 + val))
                                elif isinstance(char[stat], float):
                                    char[stat] = round(char[stat] * (1 + val), 4)
            except Exception as _e_v2:
                v2_synergy_block["enabled"] = True
                v2_synergy_block["error"] = str(_e_v2)[:200]
        # ── end RM1.23-B V2 block ──────────────────────────────────────────

        # Generate enemy team — dimensione INDIPENDENTE dalla squadra player.
        # Il team nemico è SEMPRE pieno (6 unità) così l'utente può testare
        # battaglie asimmetriche (es. 3 vs 6, 4 vs 6) per osservare
        # idle/attack/skill dei suoi eroi in pace senza che il gioco
        # "rispecchi" automaticamente il lato opposto.
        team_power = sum(c['attack'] + c['hp'] // 10 + c['defense'] for c in player_team)
        enemy_team = generate_enemy_team(int(team_power * 0.15), count=6)
        
        # Simulate battle
        result = simulate_battle(player_team, enemy_team)
        result['active_formations'] = active_formations
        result['adjacency_pairs'] = adj_result['adjacent_pairs']
        result['active_synergies'] = synergy_result.get('active_synergies', [])
        result['synergy_buffs'] = synergy_buffs
        # RM1.23-B: telemetry V2 (always present; empty if flag off)
        result['team_synergies_v2'] = v2_synergy_block
        
        # Awards on victory
        if result['victory']:
            gold_reward = int(team_power * 0.5)
            exp_reward = int(team_power * 0.2)
            hero_exp = int(team_power * 0.15)
            
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"gold": gold_reward, "experience": exp_reward}}
            )
            
            # Give EXP to each hero
            hero_levelups = []
            for pos in team['formation']:
                uh_id = pos.get('user_hero_id')
                if not uh_id:
                    continue
                uh = await db.user_heroes.find_one({"id": uh_id, "user_id": user_id})
                if not uh:
                    continue
                old_level = uh.get('level', 1)
                new_exp = uh.get('exp', 0) + hero_exp
                new_level = old_level
                while new_level < uh.get('level_cap', 100):
                    needed = new_level * 100 + 50
                    if new_exp >= needed:
                        new_exp -= needed
                        new_level += 1
                    else:
                        break
                await db.user_heroes.update_one({"id": uh_id}, {"$set": {"level": new_level, "exp": new_exp}})
                if new_level > old_level:
                    hero_levelups.append({"hero_name": uh.get('hero_name', '?'), "old_level": old_level, "new_level": new_level})
            
            # Item drops
            import random as _rnd
            try:
                from routes.items import BATTLE_DROPS, EXP_ITEMS, SKILL_MATERIALS
                drops = []
                for _ in range(_rnd.randint(2, 5)):
                    total_w = sum(d['weight'] for d in BATTLE_DROPS)
                    roll = _rnd.randint(1, total_w)
                    cum = 0
                    for dr in BATTLE_DROPS:
                        cum += dr['weight']
                        if roll <= cum:
                            drops.append(dr['item_id'])
                            break
                drop_summary = {}
                for did in drops:
                    drop_summary[did] = drop_summary.get(did, 0) + 1
                for did, qty in drop_summary.items():
                    await db.inventory.update_one({"user_id": user_id, "item_id": did}, {"$inc": {"quantity": qty}}, upsert=True)
                drop_display = []
                for did, qty in drop_summary.items():
                    idef = EXP_ITEMS.get(did) or SKILL_MATERIALS.get(did) or {}
                    drop_display.append({"item_id": did, "name": idef.get('name', did), "icon": idef.get('icon', '\U0001f381'), "quantity": qty})
            except Exception:
                drop_display = []
                hero_levelups = hero_levelups if 'hero_levelups' in dir() else []
            
            result['rewards'] = {
                "gold": gold_reward, "exp": exp_reward, "hero_exp": hero_exp,
                "hero_levelups": hero_levelups, "drops": drop_display,
            }
        
        return result

    class UpdateTeamRequest(BaseModel):
        formation: list  # List of {x, y, user_hero_id}

    @router.post("/team/update-formation")
    async def update_team_formation(req: UpdateTeamRequest, current_user: dict = Depends(get_current_user)):
        """Update team formation (max 6 heroes on 9x9 grid)"""
        # Pre-QA Stabilization 110 — Team formation legacy account-wide quarantine.
        # Il path player-facing deve essere server-scoped. Finche' non lo e',
        # quarantineiamo la mutation. Pack futuro: AUTORIZZO_V110_TEAM_FORMATION_SERVER_SCOPE_PACK_NEXT.
        import os as _os
        if str(_os.environ.get("TEAM_FORMATION_LEGACY_QUARANTINED", "true")).strip().lower() in ("true", "1", "yes", "on"):
            raise HTTPException(423, detail={
                "blocker": "TEAM_FORMATION_LEGACY_QUARANTINED",
                "alternative": "TEAM_FORMATION_SERVER_SCOPE_REQUIRED",
                "pack_origin": "pre_qa_stabilization_110",
                "no_account_wide_teams_write": True,
                "no_silent_s1_fallback": True,
                "deferred_next_step": "AUTORIZZO_V110_TEAM_FORMATION_SERVER_SCOPE_PACK_NEXT",
            })
        user_id = current_user['id']
        
        if len([f for f in req.formation if f.get('user_hero_id')]) > 6:
            raise HTTPException(status_code=400, detail="Massimo 6 eroi per team!")
        
        # Validate positions
        for pos in req.formation:
            if pos.get('x', 0) < 0 or pos.get('x', 0) > 8 or pos.get('y', 0) < 0 or pos.get('y', 0) > 8:
                raise HTTPException(status_code=400, detail="Posizione non valida (0-8)")
        
        # Calculate position buffs info
        positions = [{"x": p.get('x', 0), "y": p.get('y', 0)} for p in req.formation if p.get('user_hero_id')]
        active_formations = []
        for pat_id, pat in FORMATION_PATTERNS.items():
            try:
                if pat['check'](positions):
                    active_formations.append({"id": pat_id, "name": pat['name'], "description": pat['description'], "buff": pat['buff']})
            except Exception:
                pass
        
        adj = calculate_adjacency_bonus(positions)
        
        # Calculate total power
        total_power = 0
        for pos in req.formation:
            if not pos.get('user_hero_id'):
                continue
            user_hero = await db.user_heroes.find_one({"id": pos['user_hero_id'], "user_id": user_id})
            if user_hero:
                hero = await db.heroes.find_one({"id": user_hero['hero_id']})
                if hero:
                    total_power += calculate_hero_power(hero, user_hero)
        
        # Save team
        existing = await db.teams.find_one({"user_id": user_id, "is_active": True})
        team_data = {
            "user_id": user_id,
            "is_active": True,
            "formation": req.formation,
            "total_power": total_power,
            "updated_at": datetime.utcnow(),
        }
        
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

    return router


# ===========================================================================
# MEGA_RELEASE_ACCELERATION_44_v95 — Engine status/DoT/taunt patch metadata.
# Old MD5: 151ca35ad3bc35f0a6209cb3744ed440 (v94 unchanged)
# This append is ADDITIVE-ONLY: nessuna modifica alla logica esistente.
# Espone le costanti del design contract v94 come metadata importabili per
# eventuali integrazioni runtime future. Le esistenti funzioni del battle
# engine NON sono modificate.
# v95 unlock authorized for this minimal additive metadata block.
# ===========================================================================

V95_ENGINE_STATUS_DOT_METADATA = {
    "pack": "MEGA_RELEASE_ACCELERATION_44_v95",
    "applied_runtime": "runtime_apply_active",
    "dot_core": {
        "Burn": {"category": "elemental_fire", "tick": "end_of_target_turn", "duration": 3, "stack": "sum_ticks", "max_stacks": 5},
        "Poison": {"category": "bio", "tick": "end_of_target_turn", "duration": 4, "stack": "sum_ticks", "max_stacks": 5},
        "Bleed": {"category": "physical", "tick": "end_of_target_turn", "duration": 3, "stack": "sum_ticks", "max_stacks": 5},
        "Shock": {"category": "elemental_thunder", "tick": "on_action_attempt", "duration": 2, "stack": "reset_duration", "max_stacks": 1},
        "Frostbite": {"category": "elemental_ice", "tick": "end_of_target_turn", "duration": 3, "stack": "cap_stacks", "max_stacks": 3},
        "Curse": {"category": "shadow", "tick": "end_of_target_turn", "duration": 4, "stack": "overwrite", "max_stacks": 1},
    },
    "cleanse_policies": ["all", "top", "by_category", "by_priority", "one_stack", "remove_status"],
    "immunity_behavior": "blocks_new_application_only",
    "taunt": {
        "single_target_intercepts": True,
        "aoe_all_intercepts": False,
        "aoe_partial_must_respect": True,
    },
    "boss_hard_control_conversion": {
        "Freeze": "speed_down_30pct",
        "Stun": "skill_power_reduction_25pct",
        "Silence": "skill_power_reduction_15pct",
        "Sleep": "turn_delay_1",
        "Petrify": "defense_down_20pct",
    },
    "battle_report_extension_fields": [
        "dot_damage_done", "status_applied_count", "healing_done",
        "cleanse_count", "status_prevented_by_immunity_count", "taunt_redirect_count",
    ],
    "safety": {"db_writes": 0, "reward_live": False, "final_numbers_balance_lock": False},
}


# ---------------------------------------------------------------------------
# v95 runtime helpers (additive, behavior-safe).
# ---------------------------------------------------------------------------
_V95_DOT_CATEGORY = {
    'burn': 'elemental_fire',
    'poison': 'bio',
    'bleed': 'physical',
    'shock': 'elemental_thunder',
    'frostbite': 'elemental_ice',
    'curse': 'shadow',
}
_V95_DOT_STACK_POLICY = {
    'burn': 'sum_ticks',
    'poison': 'sum_ticks',
    'bleed': 'sum_ticks',
    'shock': 'reset_duration',
    'frostbite': 'cap_stacks',
    'curse': 'overwrite',
}
_V95_DOT_MAX_STACKS = {
    'burn': 5, 'poison': 5, 'bleed': 5, 'shock': 1, 'frostbite': 3, 'curse': 1,
}
_V95_HARD_CONTROL_BOSS_CONVERSION = {
    # control_type -> (converted_status_effect)
    'freeze': {'type': 'slow', 'speed_reduction': 0.30, 'turns_remaining': 2, 'damage_per_turn': 0.0},
    'stun': {'type': 'weaken', 'attack_reduction': 0.25, 'turns_remaining': 1, 'damage_per_turn': 0.0},
    'silence': {'type': 'weaken', 'attack_reduction': 0.15, 'turns_remaining': 1, 'damage_per_turn': 0.0},
    'sleep': {'type': 'slow', 'speed_reduction': 0.20, 'turns_remaining': 1, 'damage_per_turn': 0.0},
    'petrify': {'type': 'defense_break', 'reduction': 0.20, 'turns_remaining': 2, 'damage_per_turn': 0.0},
}


def _v95_is_boss(unit: dict) -> bool:
    """True se l'unit è marcato come boss (boss/raid_boss/world_boss)."""
    if not isinstance(unit, dict):
        return False
    if unit.get('is_boss') is True:
        return True
    klass = str(unit.get('hero_class') or unit.get('class') or '').lower()
    role = str(unit.get('role') or '').lower()
    tag = str(unit.get('enemy_type') or unit.get('unit_type') or '').lower()
    return any('boss' in v for v in (klass, role, tag))


def _v95_has_immunity(target: dict, eff_type: str) -> bool:
    """True se target è immune a un nuovo debuff (immunity NON rimuove esistenti)."""
    if not isinstance(target, dict):
        return False
    # check passive flag
    for passive in (target.get('passives') or []):
        eff = (passive or {}).get('effect') or {}
        if eff.get('status_immunity', 0) >= 1.0:
            return True
        immune_list = eff.get('immune_to') or []
        if eff_type in immune_list:
            return True
    # check active immunity status
    for s in (target.get('status_effects') or []):
        if s.get('type') == 'immunity':
            return True
        immune_to = s.get('immune_to') or []
        if eff_type in immune_to:
            return True
    return False


def _v95_apply_dot_with_stack_policy(target: dict, eff_type: str, damage_per_turn: float, duration: int, source_name: str) -> bool:
    """Applica un DoT a target rispettando la stack policy v95.

    Ritorna True se lo status è stato applicato/aggiornato.
    """
    if target is None or not target.get('is_alive', True):
        return False
    policy = _V95_DOT_STACK_POLICY.get(eff_type, 'sum_ticks')
    max_stacks = _V95_DOT_MAX_STACKS.get(eff_type, 5)

    effects = target.setdefault('status_effects', [])
    same = [e for e in effects if e.get('type') == eff_type]

    new_eff = {
        'type': eff_type,
        'damage_per_turn': damage_per_turn,
        'turns_remaining': duration,
        'source': source_name,
        'category': _V95_DOT_CATEGORY.get(eff_type, 'generic'),
    }

    if policy == 'sum_ticks':
        if len(same) >= max_stacks:
            # rimpiazza lo stack più vecchio
            oldest = min(same, key=lambda e: e.get('turns_remaining', 0))
            effects.remove(oldest)
        effects.append(new_eff)
    elif policy == 'reset_duration':
        if same:
            for e in same:
                e['turns_remaining'] = max(e.get('turns_remaining', 0), duration)
                e['damage_per_turn'] = max(e.get('damage_per_turn', 0), damage_per_turn)
        else:
            effects.append(new_eff)
    elif policy == 'overwrite':
        for e in list(same):
            effects.remove(e)
        effects.append(new_eff)
    elif policy == 'cap_stacks':
        if len(same) >= max_stacks:
            return False  # capped, no new stack
        effects.append(new_eff)
    else:
        effects.append(new_eff)
    return True


def _v95_apply_cleanse(target: dict, mode: str = 'all', category: str = None, priority_key: str = None) -> int:
    """Rimuove status dal target seguendo la policy cleanse v95.

    mode: 'all' | 'top' | 'by_category' | 'by_priority' | 'one_stack' | 'remove_status'
    Ritorna il numero di status rimossi.
    """
    if not isinstance(target, dict):
        return 0
    effects = target.get('status_effects') or []
    removed = 0
    if mode == 'all':
        removed = len(effects)
        target['status_effects'] = []
    elif mode == 'top':
        if effects:
            effects.pop(-1)
            removed = 1
    elif mode == 'by_category' and category:
        keep = [e for e in effects if e.get('category') != category and _V95_DOT_CATEGORY.get(e.get('type'), '') != category]
        removed = len(effects) - len(keep)
        target['status_effects'] = keep
    elif mode == 'by_priority' and priority_key:
        keep = [e for e in effects if e.get('priority') != priority_key]
        removed = len(effects) - len(keep)
        target['status_effects'] = keep
    elif mode == 'one_stack':
        if effects:
            effects.pop(0)
            removed = 1
    elif mode == 'remove_status' and category:
        keep = [e for e in effects if e.get('type') != category]
        removed = len(effects) - len(keep)
        target['status_effects'] = keep
    return removed


def _v95_maybe_convert_boss_hardcontrol(target: dict, eff_type: str, duration: int) -> dict:
    """Se target è boss e eff_type è hard-control, converte secondo la policy.

    Ritorna None se non c'è conversione, altrimenti dict status effect convertito.
    Non boss-hard-lock: hard control mai applicato pieno su boss.
    """
    if not _v95_is_boss(target):
        return None
    conv = _V95_HARD_CONTROL_BOSS_CONVERSION.get(eff_type)
    if not conv:
        return None
    converted = dict(conv)
    # rispetta la duration originale ma cap a quella standard di conversione
    converted['turns_remaining'] = min(int(duration or 1), converted.get('turns_remaining', 1))
    return converted
