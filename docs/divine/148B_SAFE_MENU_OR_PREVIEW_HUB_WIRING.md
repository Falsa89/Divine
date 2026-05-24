# 148B — SAFE MENU / PREVIEW HUB WIRING

## Track B — `PROJECT_Z_TRACK_B`

**Verdict:** `TRACK_B_SAFE_MENU_OR_PREVIEW_HUB_WIRED_SAFE`

## 1. Strategia applicata

```
dedicated_safe_preview_hub_single_menu_entry
```

## 2. File creati

- `/app/frontend/app/safe-previews.tsx` — hub centralizzato (read-only, nessuna live action)

## 3. File modificati (1 entry aggiunta)

- `/app/frontend/app/(tabs)/menu.tsx` — aggiunta voce **“Sistemi in preparazione”** nella sezione **Altro**
  - Label: “Sistemi in preparazione”
  - Icon: ✨
  - Route: `/safe-previews`
  - Gradient: `['#FF6B35', '#3D5AFE']`

## 4. Contenuto hub

3 entry (tutte navigabili, tutte read-only, **nessuna live action**):

| Route | Label | Badge |
|---|---|---|
| `/status-codex` | Codex Status Effects | “Anteprima” |
| `/artifacts-preview` | Anteprima Artefatti | “In arrivo” |
| `/housing-preview` | Dimora Divina | “In arrivo” |

## 5. Sicurezza

| Voce | Stato |
|---|---|
| Nuova bottom tab | ❌ no |
| Broad navigation refactor | ❌ no |
| Live action label in menu | ❌ no |
| Hub live actions | **0** |
| Hub solo `router.push` (no API mutativi) | ✅ |

## 6. Validator

`validate_project_z_safe_menu_or_preview_hub_wiring_v1.py` → **PASS**.
