"""
battle_core.py — DEPRECATED PROXY MODULE
==========================================

Questo modulo era una copia legacy della logica battle. NON è più la
source-of-truth: tutta la logica vive ora in `battle_engine.py`
(rage system, action cycle attack→skill_1→skill_2, hero-specific name
overrides come "Affondo di Falange" e "Guardia Ferrea" per Hoplite,
team size enemy=6 sempre, payload con rage/max_rage, ecc.).

Questo file è mantenuto come THIN PROXY per retrocompat: qualsiasi
importazione esterna di `simulate_battle` / `execute_skill` /
`generate_enemy_team` risolverà automaticamente alla versione
aggiornata in battle_engine.py, garantendo COERENZA PER COSTRUZIONE
tra i due file.

Non aggiungere logica qui. Modifica solo battle_engine.py.
"""

from battle_engine import (
    simulate_battle,
    execute_skill,
    generate_enemy_team,
    ELEMENT_SKILLS,
)

__all__ = [
    'simulate_battle',
    'execute_skill',
    'generate_enemy_team',
    'ELEMENT_SKILLS',
]
