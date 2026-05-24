# 147D — HOUSING PREVIEW UI

## Track D — `PROJECT_Y_TRACK_D`

**Verdict:** `TRACK_D_HOUSING_PREVIEW_UI_READY`

## 1. Route creata

```
/app/frontend/app/housing-preview.tsx
```

## 2. Endpoint call

`GET /api/housing/preview` (read-only). Endpoint attualmente restituisce **503**.

## 3. State machine

| State | Trigger | UI |
|---|---|---|
| `loading` | iniziale | spinner + “Verifica disponibilità…” |
| `preview_503` | HTTP 503 | SafeFeatureCard locked con copy IT + badge `503` |
| `live` | HTTP 200 | SafeFeatureCard read-only (bonus live restano disattivati) |
| `unavailable` | network error | SafeFeatureCard locked con badge `Offline` |

## 4. Locked feature card mostrati

- Stanze & Arredamento
- Residenti Eroi
- Bonus Passivi Giornalieri

Ognuno con `lockReason` puntato alla firma HOUSING_LIVE_BONUS_* richiesta.

## 5. Vincoli

| Voce | Stato |
|---|---|
| Read-only | ✅ |
| Live bonus button | ❌ |
| Room upgrade button | ❌ |
| Resident assignment | ❌ |
| Currency spend | ❌ |
| Solo GET endpoint | ✅ |
| 503 graceful | ✅ |

## 6. Validator

`validate_project_y_housing_preview_ui_v1.py` → **PASS**.
