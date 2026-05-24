# 147F — SAFE MENU ENTRY / DEV PANEL

## Track F — `PROJECT_Y_TRACK_F`

**Verdict:** `TRACK_F_SAFE_MENU_ENTRY_OR_DEV_PANEL_READY`

## 1. Strategia adottata

```
create_routes_only_no_menu_mutation
```

## 2. Razionale

Il Pack Y crea **3 nuove route preview** raggiungibili via **deep link expo-router** (`/artifacts-preview`, `/housing-preview`, `/status-codex`). **Nessuna mutazione del menu** (`/app/frontend/app/(tabs)/menu.tsx`) **e nessuna mutazione del tab layout** (`/app/frontend/app/(tabs)/_layout.tsx`) per evitare ogni risk di broad navigation refactor. Il cablaggio delle voci in menu e l'eventuale aggiunta in sezioni dedicate sono **rimandati al Pack Z** dopo QA mobile / Expo Go.

## 3. Stato attuale

| Voce | Valore |
|---|---|
| Nuove tab bottom | 0 |
| Voci menu aggiunte | 0 |
| Cambiamenti navigation player-facing | 0 |
| Broad navigation refactor | ❌ |
| Dev panel creato | ❌ (deferred) |
| Deep link route raggiungibili | 3 |

## 4. Deep link disponibili

```
/artifacts-preview
/housing-preview
/status-codex
```

Queste route saranno cablate nel menu/dev hub in `PROJECT_Z_FRONTEND_SAFE_PREVIEW_POLISH_AND_MOBILE_QA_PACK`.

## 5. Validator

`validate_project_y_safe_menu_entry_dev_panel_v1.py` → **PASS**.
