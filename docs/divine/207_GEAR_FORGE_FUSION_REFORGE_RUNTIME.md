# 207 — PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME

**Verdict**: `PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Timestamp UTC**: 2026-05-30T12:00:00Z

**Runtime mode**: `PREVIEW_ONLY` (DISABLED-BY-DEFAULT — HTTP 503 inert envelope)

**Feature flag**: `GEAR_FORGE_RUNTIME_PREVIEW_ENABLED`

**Fusion commit enabled**: **NO** (blocco per audit safety legacy `/forge/fuse`)

---

## Decisione chiave: PREVIEW-ONLY

L'audit (track A) ha verificato il legacy `backend/routes/forge.py`. Il `/forge/fuse`
esistente ha guards parziali (auth, ownership, rarity cap, min fodder) ma **manca**:

- `fodder.equipped_to` (un fodder già equipaggiato può essere distrutto)
- `fodder.locked` / `favorite` / `protected`
- `base.in_active_team`
- atomicità transactional sui delete a cascata
- pre-check negative balance gold pre-mutation
- envelope di outcome deterministico esplicito

La policy del pack richiede tutte queste guards prima di abilitare fusion commit.
Quindi: **fusion commit NON abilitato**, nuovo namespace `/api/gear-forge/*` interamente
preview-only, gated. Il legacy `/forge/*` **non viene mai toccato**.

## Endpoint pubblicati

| Method | Path | Ruolo | DB writes | Mutation |
|---|---|---|---|---|
| GET  | `/api/gear-forge/config`           | Config canonico subsystems + staged caps | 0 | NO |
| POST | `/api/gear-forge/fusion/preview`   | Preview-only outcome (no delete, no DB lookup) | 0 | NO |
| POST | `/api/gear-forge/enhance/preview`  | Preview-only cost current→target rispettando +50 | 0 | NO |
| POST | `/api/gear-forge/reforge/preview`  | Preview-only schema (design-only) | 0 | NO |
| POST | `/api/gear-forge/enchant/preview`  | Preview-only schema (design-only, runtime disabled) | 0 | NO |

Tutti gated da `GEAR_FORGE_RUNTIME_PREVIEW_ENABLED`. Default flag-off → HTTP **503**.

## 4 Subsystem canonici

| id | label | runtime_state |
|---|---|---|
| enhance | Potenzia | `preview_only_aware_of_cap_plus_50` |
| fusion  | Fondi    | `preview_only_commit_disabled_safety_audit` |
| reforge | Riforgia | `preview_only_schema_only` |
| enchant | Incanta  | `design_only_schema_only` |

## Fusion rules preview

- min fodder per quality-up: **3**
- same-slot required, same-or-lower-quality required
- qualità canoniche: `common` → `uncommon` → `rare` → `epic` → `legendary` → `mythic`
- deterministic outcome, no paid currency
- (per commit futuro): `fodder_not_equipped`, `fodder_not_locked_or_favorite`, `base_not_in_active_team`, atomic transaction

## Enhance preview

- Calcolo step-by-step da `current_level` a `target_level` rispettando staged caps (+10/+20/+35/+50).
- Cost source: `data/design/gear_cap_plus_50/E_material_cost_policy_v1.json`.
- Blocca target > 50 con status `target_above_cap`.

## Cosa NON fa

- **NO** Gem socket runtime, Rune/scroll/talisman runtime, Artifact live, Divine Weapon runtime.
- **NO** Hero Elevation changes, **NO** Gear Cap preview route behavior changes.
- **NO** BP Delta runtime, Material Raid runtime/drop tables.
- **NO** combat / `battle_engine.py` / `combat.tsx` / Character Bible / `final_numbers`.
- **NO** Shop/BP/VIP/IAP unlock, stamina/tickets, paid currency.
- **NO** modifiche al legacy `/forge/*` (`forge.py` invariato).
- **NO** server profiles live, broad DB migration, broad player data mutation.
- **NO** REQUIRED/OPTIONAL validator weakening, tuple duplicate, fake PASS.

## Sandbox frontend

- Route deeplink-only: **`/gear-forge-test`** → `frontend/app/gear-forge-test.tsx`.
- Constants: `frontend/constants/gearForge.ts` (read-only).
- **NO** wiring in `home.tsx`, `menu.tsx`, `_layout.tsx`.

## Validator

- `backend/scripts/validate_project_gear_forge_fusion_reforge_runtime_v1.py` (OPTIONAL).
- Suite runner: 1 tupla aggiunta in blocco OPTIONAL.

## Release gates

- **R1** (questo pack): preview locale, flag default off. ✅ ACHIEVED LOCAL CONTAINER.
- **R2**: envelope preview attivabile in canary — DEFERRED.
- **R3**: fusion commit live — **BLOCKED** finché non arriva `PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING_PACK`.
- **R4**: enhance live — DEFERRED a `PROJECT_MATERIAL_RAID_RUNTIME_PACK`.

## Prossimo pack consigliato

Date le dipendenze e l'ordine logico:

1. **`PROJECT_MATERIAL_RAID_RUNTIME_PACK`** — senza inventario materiali runtime, neanche
   l'enhance commit può essere live.
2. **`PROJECT_GEM_SOCKET_RUNTIME_PACK`** — layer ortogonale, sblocca progressione.
3. **`PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING_PACK`** — per attivare il commit.
