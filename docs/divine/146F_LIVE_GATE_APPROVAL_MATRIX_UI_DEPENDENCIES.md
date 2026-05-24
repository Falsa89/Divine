# 146F — LIVE GATE APPROVAL MATRIX & UI DEPENDENCIES

## Track F — `PROJECT_X_TRACK_F`

**Verdict:** `TRACK_F_LIVE_GATE_APPROVAL_MATRIX_UI_DEPENDENCIES_READY`

## 1. Obiettivo

Mappare ogni live gate alle relative dipendenze di visibilità UI futura, **senza spoofare alcuna approval**.

## 2. Gates (7)

| Gate | # Firme richieste | Firme presenti | UI visibility | Mai visibile a player |
|---|---|---|---|---|
| Status first-slice prod | 6 | 0 | `hidden_until_approved` | No (dev/admin yes) |
| Status second-slice prod | 11 (7 + 4 stage) | 0 | `hidden_until_approved` | No (dev/admin yes) |
| Artifact live import | 5 | 0 | `locked_card_coming_soon` | No |
| Housing live bonus | 3 | 0 | `locked_card_coming_soon` | No |
| AF2-N public rollout | 3 | 0 | `hidden_until_approved` | ✅ **Sì** |
| Second server / Phase 11 | 2 | 0 | `hidden_until_approved` | ✅ **Sì** |
| Gacha/pricing/economy live | già live | n/a | `player_visible_active` | No |

## 3. Locked card mostrabili come "coming soon" sul percorso giocatore

- Artifact live import
- Housing live bonus

## 4. Gates da nascondere ai giocatori fino all'approvazione completa

- Status first-slice prod
- Status second-slice prod
- AF2-N public rollout (giocatore mai)
- Second server / Phase 11 (giocatore mai)

## 5. Tutti i gate sono visibili in dev/admin (read-only viewer)

Futuro screen suggerito: `/dev-approval-matrix`.

## 6. Validator

`validate_project_x_live_gate_approval_matrix_ui_dependencies_v1.py` → **PASS**. Nessuna approval spoofata.
