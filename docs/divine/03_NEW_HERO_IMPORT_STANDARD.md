# New Hero Import Standard

Status: Draft standard based on RM1.17-FINAL, RM1.17-S, RM1.18 and RM1.19.

## Mandatory Rule

No hero is accepted unless it has:

- canonical roster identity
- asset folder
- variants mapping
- UI contract
- battle contract
- preload compatibility
- Combat QA Lab validation

## Required Asset Contract

Every hero must define variants:

- splash
- portrait
- card
- detail
- fullscreen
- transparent if eligible for Home/overlay
- combat_base
- idle/attack/skill/hit/death or runtimeSheets

## Required UI Contract

Slots:

- home
- card
- detailIcon
- selectedPreview
- fullscreen

The face must be visible. If cover cuts the face, use contain.

## Required Battle Contract

Runtime-sheet heroes:

- useRuntimeSheets = true
- removeDefaultGlow = true unless intentional
- useLegacyDefaultMotion = false
- runtimeRenderScale tuned against Hoplite/Berserker
- no external BattleSprite motion

## QA Gate

Use Combat QA Lab:

- Idle
- Attack
- Skill
- Hit
- Death
- Normal enemy
- Lethal enemy
- Immortal enemy
- 6-enemy AoE
- Taunt
- DoT
- Shield/Heal if relevant
- contract warnings = 0
