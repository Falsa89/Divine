# 148D — HOUSING PREVIEW MOBILE POLISH

## Track D — `PROJECT_Z_TRACK_D`

**Verdict:** `TRACK_D_HOUSING_PREVIEW_MOBILE_POLISH_READY`

## 1. Route polizzata

```
/app/frontend/app/housing-preview.tsx
```

## 2. Polish applicato

| Voce | Stato |
|---|---|
| Banner copy aggiornato | ✅ “Dimora Divina in preparazione — bonus e assegnazioni non ancora attivi.” |
| State machine 4-stati | ✅ (`loading`/`preview_503`/`live`/`unavailable`) |
| 503 gestito senza crash | ✅ |
| Endless retry | ❌ (single fetch on mount) |
| `SafeAreaView` | ✅ |
| Back button touch target | ✅ |

## 3. Cleanness

- 0 live bonus button
- 0 spend button
- 0 assignment button
- 0 room upgrade button
- Solo `GET` su `/api/housing/preview`
- Nessun overflow orizzontale

## 4. Validator

`validate_project_z_housing_preview_mobile_polish_v1.py` → **PASS**.
