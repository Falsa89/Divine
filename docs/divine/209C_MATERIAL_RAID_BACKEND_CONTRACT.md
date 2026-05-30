# 209C — BACKEND CONTRACT (PREVIEW)

**Track**: C | **Verdict**: `TRACK_C_BACKEND_MATERIAL_RAID_PREVIEW_OR_RUNTIME_READY`

Runtime mode: **`PREVIEW_ONLY`**. Reward claim endpoint **NON aggiunto**.

## Endpoint

| Method | Path | Ruolo |
|---|---|---|
| GET  | `/api/material-raid/config`         | config + reward families + stage model |
| GET  | `/api/material-raid/stages`         | stages I..V + recommended_power |
| POST | `/api/material-raid/reward-preview` | preview reward envelope per track+stage |
| POST | `/api/material-raid/clear-preview`  | eligibility per team_power vs recommended |

Flag-off → HTTP **503** inert envelope. Zero DB write possibile.

Contract version: `project_material_raid_runtime_preview_v1`.
