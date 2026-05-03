# Placeholder Asset & Contract Readiness Pipeline

Status: approved process draft  
Task: RM1.22-A  
Scope: asset/contract readiness planning, no runtime activation

## Purpose

This pipeline allows official heroes to be integrated and tested before final art is ready.

A hero may use role-based placeholder assets while keeping the same canonical filenames that final assets will later replace.

This prevents integration work from being blocked by final art production and lets us validate:

- DB import state;
- UI contract;
- portrait/card/fullscreen framing;
- battle runtime sheet wiring;
- asset preload;
- skill/effect behavior;
- Combat QA Lab animation states;
- mobile device presentation.

## Core principle

Placeholder assets are allowed, but they must be explicit and tracked.

A placeholder must never silently become final art.

Every hero using placeholders must remain marked as:

```json
"asset_status": "placeholder_dev"
```

or equivalent until final assets are approved.

## Canonical file strategy

Inside each hero folder, placeholders use the same final filenames.

Example:

```text
frontend/assets/heroes/celtic_archer/splash.jpg
frontend/assets/heroes/celtic_archer/transparent.png
frontend/assets/heroes/celtic_archer/combat_base.png
frontend/assets/heroes/celtic_archer/runtime/idle_sheet.png
frontend/assets/heroes/celtic_archer/runtime/attack_sheet.png
frontend/assets/heroes/celtic_archer/runtime/skill_sheet.png
frontend/assets/heroes/celtic_archer/runtime/hit_sheet.png
frontend/assets/heroes/celtic_archer/runtime/death_sheet.png
frontend/assets/heroes/celtic_archer/runtime/battle_animations.json
```

Even if these files initially come from a shared ranged-DPS placeholder profile, they live under the hero folder and use the final names.

When the final asset arrives, it replaces the placeholder file 1:1.

## Required statuses

Recommended DB/design status values:

- `asset_status: "pending_assets"` — imported but no usable assets yet.
- `asset_status: "placeholder_dev"` — placeholder files installed for integration/testing.
- `asset_status: "ready"` — usable asset set validated but not final.
- `asset_status: "approved_final"` — final art approved and validated.

Contract statuses:

- `contract_status: "pending_contract"`
- `contract_status: "placeholder_contract_ready"`
- `contract_status: "ready"`
- `contract_status: "approved_final"`

## Placeholder profiles

The profiles are defined in:

```text
data/design/placeholder_asset_profiles.json
```

Main profiles:

- `tank_standard_v1`
- `dps_melee_standard_v1`
- `dps_ranged_standard_v1`
- `mage_aoe_standard_v1`
- `assassin_burst_standard_v1`
- `support_buffer_standard_v1`
- `healer_standard_v1`
- `control_debuff_standard_v1`
- `hybrid_special_standard_v1`

## Readiness manifest

All official heroes are tracked in:

```text
data/design/official_hero_asset_readiness_manifest.json
```

The manifest maps each hero to:

- hero identity;
- role;
- placeholder profile;
- canonical asset paths;
- activation gates;
- current expected DB status.

## Activation gates

Before a hidden official hero can become visible, it must pass gates:

1. placeholder or final assets copied under canonical filenames;
2. asset contract created;
3. UI contract created;
4. battle contract created;
5. preload registered;
6. Combat QA Lab passed;
7. mobile UI passed;
8. catalog visibility approved;
9. summon visibility approved;
10. starter pool approval if applicable.

## Starter policy

After RM1.20-E, new users may temporarily receive 0 starter heroes.

Do not reactivate starter grant by exposing unfinished heroes.

To restore starters safely:

- prioritize official 1★/2★ heroes;
- install placeholder assets;
- validate contracts;
- validate QA Lab;
- activate starter-safe heroes in a controlled batch.

## Forbidden shortcuts

Do not:

- use another hero's final asset as a hidden fallback without tracking;
- mark placeholder art as final;
- expose `pending_assets` heroes;
- activate summon before asset/contract QA;
- create code fallback to random assets;
- bypass `show_in_*` flags;
- modify active teams automatically.

## Next phase

After this policy is installed and validated, the next task should create actual shared placeholder asset packs or placeholder asset installation scripts for selected priority heroes.
