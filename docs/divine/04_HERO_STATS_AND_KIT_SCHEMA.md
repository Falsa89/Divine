# Hero Stats and Skill Kit Schema

Status: Draft for RM1.21-A.

## Stats

Core stats:

- HP
- ATK
- DEF
- Speed
- Crit Rate
- Crit Damage
- Effect Accuracy
- Effect Resistance
- Healing Power

## Kit Slots

- basic_attack
- skill
- ultimate_or_special
- passive

## Targeting

Default target rule:

If a skill does not declare a special target, it targets the tank first. If there is no valid tank, it targets the nearest enemy.

Taunt has maximum priority for single-target skills unless a future skill explicitly ignores taunt. Taunt does not intercept AoE, line, column, all-enemy, or multi-target declared effects.

## Design Method

Do not write all 100 kits blindly. First approve templates by role and rarity, then design 6★ + Borea, then 5★, then lower rarities.
