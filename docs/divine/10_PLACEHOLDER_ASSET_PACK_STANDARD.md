# Placeholder Asset Pack Standard

Status: placeholder development asset pack  
Task: RM1.22-B  
Scope: shared placeholder asset library only

## Purpose

This pack provides shared role-based placeholder assets for development and QA.

The assets are not final art.

They allow the team to test:

- hero folder structure;
- UI portrait paths;
- battle base pose paths;
- runtime sheet metadata;
- preload expectations;
- Combat QA Lab animation states;
- skill/effect behavior before final animation is ready.

## Included profiles

The pack includes 9 shared placeholder profiles:

- `tank_standard_v1`
- `dps_melee_standard_v1`
- `dps_ranged_standard_v1`
- `mage_aoe_standard_v1`
- `assassin_burst_standard_v1`
- `support_buffer_standard_v1`
- `healer_standard_v1`
- `control_debuff_standard_v1`
- `hybrid_special_standard_v1`

Root path:

```text
frontend/assets/placeholders/heroes/
```

## Files per profile

Each profile contains:

```text
splash.jpg
splash.png
transparent.png
card.png
detail.png
fullscreen.png
combat_base.png
runtime/idle_sheet.png
runtime/attack_sheet.png
runtime/skill_sheet.png
runtime/hit_sheet.png
runtime/death_sheet.png
runtime/battle_animations.json
README_PLACEHOLDER.md
```

Sprite sheets are transparent and contain no text.

## Usage policy

Do not use these files as final art.

A later assignment task may copy a profile into a specific hero folder using canonical hero filenames.

Example:

```text
frontend/assets/placeholders/heroes/dps_ranged_standard_v1/runtime/idle_sheet.png
```

may be copied later to:

```text
frontend/assets/heroes/celtic_archer/runtime/idle_sheet.png
```

The destination filename is final/canonical, but the asset status remains `placeholder_dev`.

## Activation policy

Installing this pack does not activate any hero.

Do not change:

- DB;
- `show_in_*` flags;
- `obtainable`;
- gacha;
- battle runtime;
- frontend runtime.

Hero activation requires a separate gated task.
