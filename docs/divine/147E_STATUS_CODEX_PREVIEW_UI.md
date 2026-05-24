# 147E — STATUS CODEX PREVIEW UI

## Track E — `PROJECT_Y_TRACK_E`

**Verdict:** `TRACK_E_STATUS_CODEX_PREVIEW_UI_READY`

## 1. Route creata

```
/app/frontend/app/status-codex.tsx
```

## 2. Contenuto

### First-Slice (4 famiglie, `player_visible_active_read_only`)

- Buff Offensivi
- Buff Difensivi
- Heal-over-Time
- Crit Buff

### Second-Slice (4 famiglie, `player_visible_locked`)

- Debuff Offensivi
- Debuff Difensivi
- Speed Up
- Speed Down

Lock reason: “In attesa di firme PROD_ROLLOUT_* e STATUS_SECOND_SLICE_PROD_STAGE_*_APPROVAL.”

## 3. Vincoli

| Voce | Stato |
|---|---|
| Read-only | ✅ |
| Runtime toggle button | ❌ |
| Status activation button | ❌ |
| Prod rollout button | ❌ |
| Riferimenti a flag/env | ❌ |
| Flag state mutato | ❌ |

## 4. Validator

`validate_project_y_status_codex_preview_ui_v1.py` → **PASS**.
