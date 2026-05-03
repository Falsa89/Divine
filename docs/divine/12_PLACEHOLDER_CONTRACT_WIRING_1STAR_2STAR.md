# Placeholder Contract Wiring 1★/2★

Status: planned code wiring task  
Task: RM1.22-D  
Scope: frontend asset resolver contracts only

## Purpose

RM1.22-C copied placeholder files into the canonical folders for the 20 official 1★/2★ heroes.

RM1.22-D wires those files into the existing frontend resolver system without activating the heroes in DB.

## Files

The generated module is:

```text
frontend/components/ui/placeholderHeroContracts1star2star.ts
```

It exports:

- `PLACEHOLDER_HERO_IDS_1STAR_2STAR`
- `PLACEHOLDER_HERO_ASSET_REGISTRY_1STAR_2STAR`
- `PLACEHOLDER_HERO_CONTRACTS_1STAR_2STAR`
- `PLACEHOLDER_LAB_HERO_OPTIONS_1STAR_2STAR`

## Required integration

Patch:

```text
frontend/components/ui/hopliteAssets.ts
```

to import and spread the placeholder registry into:

- `HERO_ASSET_REGISTRY`
- `HERO_CONTRACTS`

Patch:

```text
frontend/app/dev-combat-qa-lab.tsx
```

to append `PLACEHOLDER_LAB_HERO_OPTIONS_1STAR_2STAR` to `LAB_HERO_OPTIONS`.

## Forbidden

Do not:

- write DB;
- activate pending heroes;
- change `show_in_*`;
- set `obtainable=true`;
- touch gacha;
- touch backend runtime;
- touch battle engine;
- change Hoplite or Berserker contracts.
