# 205C — BACKEND CONTRACT PREVIEW

**Track**: C | **Verdict**: `TRACK_C_BACKEND_GEAR_CAP_CONTRACT_PREVIEW_READY`

## Endpoint

| Method | Path                                       | Ruolo                                                        |
|--------|--------------------------------------------|--------------------------------------------------------------|
| GET    | `/api/gear-cap/tiers`                      | staged caps + cap canonico + legacy                          |
| GET    | `/api/gear-cap/preview-tiers`              | alias preview-only                                            |
| GET    | `/api/gear-cap/{hero_id}/preview`          | current cap (fallback 0, NO DB read)                          |
| POST   | `/api/gear-cap/{hero_id}/upgrade/preview`  | next stage + cost preview design-only (ZERO mutation)         |

## Stato di default

Flag `GEAR_CAP_PLUS_50_PREVIEW_ENABLED` **non impostato o != true** ⇒ HTTP **503**
con payload `{"status":"disabled", ...}`. Nessun DB write, nessuna mutation possibile.

## Contract version

`project_gear_cap_plus_50_runtime_preview_v1`.
