# RM1.25-A — Skill / Status / Icon / VFX Foundation Plan

## Goal

Create a safe, data-only foundation for the next gameplay layer of Divine RPG / Divine Waifus:

- skill package schema;
- status runtime schema;
- status icon metadata;
- modular VFX metadata;
- validation rules.

This task must not activate skill balance, status runtime, status icon rendering, or VFX in live battle.

## Canonical decisions

### Skill slot progression by native rarity

| Native rarity | Slots |
|---|---|
| 1★ | Basic Attack only |
| 2★ | Basic Attack + Passive Base |
| 3★ | Basic Attack + Passive Base + Skill 1 |
| 4★ | Basic Attack + Passive Base + Skill 1 + Passive Advanced |
| 5★ | Basic Attack + Passive Base + Skill 1 + Passive Advanced + Skill 2 |
| 6★ | Basic Attack + Passive Base + Skill 1 + Passive Advanced + Skill 2 + Ultimate |

This is a structural rule. Future unlock timing can be a separate layer, but the base kit contract must remain stable.

### Official elements

Allowed gameplay elements only:

```text
water, fire, earth, wind, lightning, light, dark
```

Forbidden as primary elements:

```text
ice, nature, holy, shadow, thunder
```

Those can only appear as visual/theme tags.

Example:

```json
{
  "element": "wind",
  "theme_tags": ["frost_wind", "north_wind", "ice_visual"]
}
```

### Runtime safety

RM1.25-A is foundation-only:

- no DB writes;
- no migrations;
- no battle engine activation;
- no balance numbers finalized;
- no live status effects;
- no live skill runtime;
- no UI icon rendering activation;
- no gacha changes;
- no roster activation;
- no Borea activation.

## Status runtime foundation

Status effects must separate:

1. gameplay effect;
2. runtime rule;
3. presentation;
4. balance layer.

Core categories:

```text
control
damage_over_time
buff
debuff
protection
healing
special
stacking_unique
field_domain
```

Core v1 statuses:

```text
stun, freeze, silence, blind, taunt,
slow, speed_down, speed_up,
burn, bleed, poison, curse, frostbite, shock,
atk_up, def_up, crit_up, crit_damage_up, vulnerability, def_down, effect_accuracy_up, magic_damage_up,
physical_shield, magical_shield, hybrid_shield, damage_reduction, guard, immunity,
healing_up, healing_reduction, healing_block, regeneration, cleanse, revive, revive_pending, death_protection,
mark, marchio_boreale, berserk, domain_effect
```

### Boss behavior

Hard control must not perma-lock bosses.

Examples:

- Freeze on normal enemy can block action.
- Freeze on boss converts/reduces into Speed Down or Vulnerability.
- Stun on boss uses reduced duration, reduced chance, or converted effect.
- Silence on boss has reduced duration/effect.
- DoT statuses work with cap/reduction in world boss contexts.
- Marchio Boreale works on bosses, but linked hard-freeze must be reduced/converted.

## Marchio Boreale

Marchio Boreale is a unique Borea status.

Rules:

- `status_id = marchio_boreale`
- source-locked to `greek_borea`
- not applicable by other heroes
- cleanseable, but cleanse behavior may remove one stack or multiple stacks depending on balance
- not generic Freeze
- not generic Frostbite
- not water magic
- visual identity: north wind frost rune, ice blue / white / wind cyan

## Status icon metadata

Icon rules:

- master: 128x128 PNG transparent;
- exports: 64/48/32/24;
- no text;
- no numbers;
- no letters;
- no watermark;
- no baked stack count;
- no baked duration;
- stack and duration are runtime overlays.

Priority:

- critical: Freeze, Stun, Revive Pending, Death Protection, Immunity;
- high: Marchio Boreale, Healing Block, Silence, Taunt, Guard, Revive, important Hybrid Shield;
- medium: Burn, Poison, Bleed, Shock, Frostbite, Vulnerability, Mark, DEF Down, Speed Down;
- low: ATK Up, DEF Up, Speed Up, Crit Up, Healing Up, Effect Accuracy Up and small buffs.

## Modular VFX metadata

Every skill/status VFX must describe:

```text
Where does it start?
Where does it travel?
Where does it impact?
What remains?
When does it disappear?
```

VFX types:

```text
apply_vfx
projectile_vfx / travel_vfx
impact_vfx
persistent_status_vfx
stack_gain_vfx
stack_decay_vfx
expire_vfx
cleanse_vfx
field_domain_vfx
screen_edge_vfx / fullscreen_vfx
```

VFX intensity levels:

```text
low, medium, high, premium, ultimate, domain
```

Layering order:

1. battle background;
2. field/domain background layer;
3. ground/area VFX;
4. character sprites;
5. character-attached persistent VFX;
6. projectile VFX;
7. impact VFX;
8. HP bar;
9. status icons;
10. screen edge VFX;
11. UI overlay.

HP bars and status icons must remain above most VFX.

## Presentation flow schema

A skill presentation flow must separate:

- source actor motion;
- projectile VFX;
- target impact VFX;
- return motion;
- persistent status VFX;
- screen/field VFX.

This prevents mistakes such as an arrow starting correctly from the caster but the explosion appearing on the caster instead of on the target.

## Acceptance criteria

1. Requirements validator passes.
2. Foundation docs/files are installed in expected locations.
3. No battle behavior changes.
4. No runtime skill activation.
5. No runtime status activation.
6. No icon rendering activation.
7. Official elements remain restricted to the seven approved elements.
8. Rarity skill slot map matches the approved structure.
9. Marchio Boreale is source-locked to `greek_borea`.
10. Borea remains hidden/pending; legacy `borea` remains non-official and hidden.
11. TypeScript/Ruff checks are reported where relevant.
12. Final report includes touched files, validation output, and safety checks.

## Suggested implementation strategy

Best first implementation step after installing this package:

1. Add data-only metadata files.
2. Add a validator for those metadata files.
3. Do not import them into battle runtime yet.
4. Expose no new live endpoints unless specifically requested.
5. Keep everything inert and safely inspectable.

