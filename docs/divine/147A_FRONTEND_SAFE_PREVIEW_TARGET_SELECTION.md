# 147A — FRONTEND SAFE PREVIEW TARGET SELECTION

## Track A — `PROJECT_Y_TRACK_A`

**Verdict:** `TRACK_A_FRONTEND_SAFE_PREVIEW_TARGET_SELECTION_READY`

## 1. Obiettivo

Selezionare gli esatti target di implementazione del Pack Y dal backlog `project_x_frontend_safe_preview_backlog_v1.json` (6 item). Priorità a chi non richiede gate dev nuovo.

## 2. Target inclusi nel Pack Y (3)

| ID | Nome | Priorità | File creato |
|---|---|---|---|
| BL-X-01 | Artifact Collection Preview | **P1** | `/app/frontend/app/artifacts-preview.tsx` |
| BL-X-02 | Housing Preview Screen | **P2** | `/app/frontend/app/housing-preview.tsx` |
| BL-X-03 | Status Codex / Catalog | **P1** | `/app/frontend/app/status-codex.tsx` |

## 3. Target deferred (3)

| ID | Nome | Priorità | Motivo |
|---|---|---|---|
| BL-X-04 | Server Profile Disabled Preview | P3 | low priority — valore minimo immediato |
| BL-X-05 | Dev Readiness Dashboard | P2 | richiede gate dev non ancora implementato |
| BL-X-06 | Approval Matrix Viewer | P3 | richiede gate dev non ancora implementato |

## 4. Componente condiviso

`SafeFeatureCard` — nuovo componente in `/app/frontend/components/SafeFeatureCard.tsx` con 4 classi di visibility supportate, locked-by-default behavior.

## 5. Vincoli rispettati

- `menu_mutation_planned`: ❌ no
- `new_bottom_tab_planned`: ❌ no
- `backend_mutation_planned`: ❌ no
- `db_writes_planned`: ❌ no

## 6. Validator

`validate_project_y_safe_preview_target_selection_v1.py` → **PASS**.
