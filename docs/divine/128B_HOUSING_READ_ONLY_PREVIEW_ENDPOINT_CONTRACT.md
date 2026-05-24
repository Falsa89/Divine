# 128B — Housing Read-Only Preview Endpoint Contract (Track B)

**Verdict:** `TRACK_B_HOUSING_READ_ONLY_PREVIEW_SKELETON_APPLIED_INERT`

## Scope
Creato skeleton `/api/housing/preview` disabilitato di default. Senza il flag
`HOUSING_PREVIEW_ENABLED=true`, ogni richiesta GET ritorna HTTP 503 con payload
`{"status":"disabled", ...}`. Nessuna scrittura DB, nessun bonus live, nessuna
mutazione combat/account.

## File
- `/app/backend/routes/housing_preview.py` (nuovo)
- `server.py` ⇒ `include_router(housing_preview_router)` aggiunto
- Rollback: `/app/backend/scripts/rollback_project_f_housing_read_only_preview.py`

## Contract
- `FEATURE_FLAG = HOUSING_PREVIEW_ENABLED`
- GET `/api/housing/preview` ⇒ 503 con flag OFF; con flag ON, envelope
  read-only inerte (zero bonus values).
- `housing_bonus_resolver_stub` NON importato dal route.

## Vincoli rispettati
- NO live Housing bonus, NO DB writes, NO battle/account stat mutation, NO frontend.
