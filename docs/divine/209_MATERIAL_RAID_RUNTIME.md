# 209 — PROJECT_MATERIAL_RAID_RUNTIME

**Verdict**: `PROJECT_MATERIAL_RAID_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Timestamp UTC**: 2026-05-30T14:00:00Z

**Runtime mode**: `PREVIEW_ONLY` (DISABLED-BY-DEFAULT — HTTP 503 inert envelope)

**Feature flag**: `MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED`

**Reward claim enabled**: **NO** (blocco per audit safety inventory model)

---

## Decisione: PREVIEW-ONLY

Audit (track A) sul codebase per material grant infrastructure:

- Nessuna collection canonical `user_materials`. Solo `db.inventory` per `EXP_ITEMS`/`SKILL_MATERIALS`.
- I material_id Bible 202 (`gear_dust_common`, `gear_shard_uncommon`, `gear_core_rare`,
  `gear_essence_epic`, `gear_orb_legendary`, ecc.) **non esistono** ancora come item_id nel DB.
- Nessun idempotent grant con `request_id`.
- Nessuna atomicità transactional su grant.
- Nessun audit log.
- Drop tables non definite per material raid.

Policy del pack: **se inventory/material grant non è chiaramente sicuro, NON abilitare claim live**.
→ **PREVIEW-ONLY**. Legacy `/raids/*`, `/raid/*`, `/inventory`, `/item-shop` **intoccati**.

## Endpoint pubblicati

| Method | Path | DB writes | Mutation | Status flag-off |
|---|---|---|---|---|
| GET  | `/api/material-raid/config`         | **0** | NO | 503 |
| GET  | `/api/material-raid/stages`         | **0** | NO | 503 |
| POST | `/api/material-raid/reward-preview` | **0** | NO | 503 |
| POST | `/api/material-raid/clear-preview`  | **0** | NO | 503 |

Tutti gated da `MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED`. **Zero query DB** su
`user_materials`/`users`/`inventory`/`active_raids` (validator enforce).

## 5 Tracks canonici

| track_id | label | runtime_state | feed |
|---|---|---|---|
| gear_material_raid            | Raid Materiali Gear           | `open_preview`     | gear enhance/fusion/reforge |
| hero_growth_raid              | Raid Crescita Eroe            | `open_preview`     | hero level/star/ascension |
| gem_material_raid             | Raid Materiali Gemme          | `locked_deferred`  | (PROJECT_GEM_SOCKET_RUNTIME_PACK) |
| rune_material_raid            | Raid Materiali Rune            | `locked_deferred`  | (PROJECT_RUNE_SCROLL_TALISMAN_RUNTIME_PACK) |
| artifact_divine_material_raid | Raid Materiali Artefatto/Divino| `locked_deferred`  | (PROJECT_ARTIFACT/DIVINE_WEAPON_RUNTIME_PACK) |

## Stage model

- 5 stage per open track: **I, II, III, IV, V**
- recommended_power preview-only: 5k / 15k / 45k / 120k / 320k
- **NO stamina**, **NO tickets**, **NO paid attempts**

## Reward families canoniche

- **gear**: `gear_dust_common, gear_shard_uncommon, gear_core_rare, gear_essence_epic, gear_orb_legendary`
- **hero_growth**: `hero_growth_dust, hero_growth_crystal, hero_growth_essence`
- **gem_locked**: `gem_dust_common, gem_shard_rare`
- **rune_locked**: `rune_paper_common, rune_paper_rare`
- **artifact_divine_locked**: `artifact_fragment_locked, divine_fragment_locked`

Valori reward preview design-only (replace_before_release = true). NESSUNA grant.

## Cosa NON fa

- **NO** Gem/Rune/Artifact/DW runtime; **NO** Hero Elevation/Gear Cap behavior changes.
- **NO** Gear Forge commit enabling; **NO** BP Delta runtime.
- **NO** combat / `battle_engine.py` / `combat.tsx` / Character Bible / `final_numbers`.
- **NO** Shop/BP/VIP/IAP unlock; **NO** server profiles live; **NO** broad DB migration.
- **NO** modifiche legacy `/raids/*`, `/raid/*`, `/inventory`, `/item-shop`.
- **NO** stamina/tickets/paid currency.
- **NO** REQUIRED/OPTIONAL validator weakening; **NO** tuple duplicate; **NO** fake PASS.

## Sandbox frontend

- Route deeplink-only: **`/material-raid-test`** → `frontend/app/material-raid-test.tsx`.
- Constants: `frontend/constants/materialRaid.ts`.
- **NO** wiring in `home.tsx`, `menu.tsx`, `_layout.tsx`.

## Validator

- `backend/scripts/validate_project_material_raid_runtime_v1.py` (OPTIONAL).
- Suite runner: 1 tupla aggiunta in blocco OPTIONAL.

## Release gates

- **R1** (questo pack): preview locale, flag default off. ✅ ACHIEVED LOCAL CONTAINER.
- **R2**: envelope preview attivabile in canary — DEFERRED.
- **R3**: claim live (mutation reale) — **BLOCKED** finché non arriva `PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK`.
- **R4**: sblocco tracks locked (Gemme/Rune/Artifact/DW) — DEFERRED ai pack runtime corrispondenti.

## Prossimo pack consigliato

1. **`PROJECT_GEM_SOCKET_RUNTIME_PACK`** — layer ortogonale Bible 202; sblocca anche la track `gem_material_raid`.
2. **`PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK`** — introduce `user_materials` canonical, idempotent grant, audit log.
3. **`PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`** — collega entries Material Raid alla guide/codex runtime.
