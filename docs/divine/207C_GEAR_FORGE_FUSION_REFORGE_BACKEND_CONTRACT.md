# 207C — BACKEND FORGE PREVIEW (OR RUNTIME)

**Track**: C | **Verdict**: `TRACK_C_BACKEND_FORGE_PREVIEW_OR_RUNTIME_READY`

## Runtime mode scelto

**`PREVIEW_ONLY`**. Fusion commit endpoint **NON aggiunto**.

## Endpoint

| Method | Path | Ruolo |
|---|---|---|
| GET  | `/api/gear-forge/config`          | config + staged caps + subsystems |
| POST | `/api/gear-forge/fusion/preview`  | preview outcome (no DB, no delete) |
| POST | `/api/gear-forge/enhance/preview` | preview cost current→target rispettando +50 |
| POST | `/api/gear-forge/reforge/preview` | preview design-only schema |
| POST | `/api/gear-forge/enchant/preview` | preview design-only schema (runtime disabled) |

## Stato di default

Flag `GEAR_FORGE_RUNTIME_PREVIEW_ENABLED` non impostato o != true ⇒ HTTP **503**
con payload `{"status":"disabled", ...}`. Nessun DB write possibile.

## Contract version

`project_gear_forge_fusion_reforge_runtime_preview_v1`
