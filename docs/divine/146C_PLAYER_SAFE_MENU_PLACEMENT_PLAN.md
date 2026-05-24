# 146C — PLAYER-SAFE MENU PLACEMENT PLAN

## Track C — `PROJECT_X_TRACK_C`

**Verdict:** `TRACK_C_PLAYER_SAFE_MENU_PLACEMENT_PLAN_READY`

## 1. Obiettivo

Definire dove ciascuna feature safe / preview dovrebbe apparire nella UI futura, **senza implementare nulla**.

## 2. Raccomandazioni menu / hub

| Feature | Placement | Copy IT | Visibility |
|---|---|---|---|
| Artifact Collection Preview | `menu → Progressione` (locked card) | "In arrivo — Collezione Artefatti" | `player_visible_locked` |
| Housing Preview | `menu → Altro` (locked card) | "Prossimamente — Dimora" | `player_visible_locked` |
| Status Codex / Catalog | `menu → Altro` (link attivo) | "Catalogo Skill & Status" | `player_visible_active` |
| Server Profile Preview | `menu → Altro` (locked card) | "Prossimamente — Profili Server" | `player_visible_locked` |
| QA / Readiness Panel | hidden dev/admin section | "DEV - Pannello Readiness" | `dev_admin_only` |
| Approval Matrix Viewer | hidden dev/admin section | "DEV - Approval Matrix" | `dev_admin_only` |

## 3. Home / bottom nav

- 5 tab esistenti **mantenute invariate** (home, heroes, battle, gacha, menu)
- **Nessuna nuova tab**
- **Nessun nuovo bottone player-facing** in Pack X
- Home continua a usare `BottomNav` custom

## 4. Sezione dev/admin (mai visibile ai giocatori)

- Esistente: `/dev-combat-qa-lab`, `/sprite-test`
- Futura: `/dev-readiness-panel`, `/dev-approval-matrix`

## 5. Coming soon copy rules

- Lingua: **Italiano**
- Prefisso: `"In arrivo"` o `"Prossimamente"`
- Vietato: countdown timer, fake interattività, date imminenti promesse

## 6. Dead button policy

- Locked card **non interagibili** sul percorso live
- `onPress` apre modal locked (mai chiamata endpoint 503)
- **Mai** routing implicito a endpoint disabilitati

## 7. Validator

`validate_project_x_player_safe_menu_placement_plan_v1.py` → **PASS**.
