# 148A — SAFE MENU WIRING TARGET AUDIT

## Track A — `PROJECT_Z_TRACK_A`

**Verdict:** `TRACK_A_SAFE_MENU_WIRING_TARGET_AUDIT_READY`

## 1. Obiettivo

Identificare il punto d'inserimento più sicuro per le 3 route Project Y (`/artifacts-preview`, `/housing-preview`, `/status-codex`) senza broad navigation refactor.

## 2. Opzioni valutate (4)

| Opzione | Fattibile | Risk | Note |
|---|---|---|---|
| Pannello dev/admin esistente | ❌ | n/a | Nessun gate dev runtime presente |
| Voci separate in menu Altro | ✅ | medium | 3 modifiche a `menu.tsx`, superficie più ampia |
| **Hub dedicato + 1 voce menu** | ✅ | **low** | **SCELTA** — 1 sola entry in menu, hub centralizzato |
| Solo deep link (nessun cablaggio) | ✅ | none | Visibilità utente sub-ottimale |

## 3. Strategia selezionata

```
dedicated_safe_preview_hub_single_menu_entry
```

Questa strategia minimizza la mutazione del file `menu.tsx` (1 sola riga aggiunta) e centralizza l'accesso alle 3 anteprime tramite un hub dedicato `/safe-previews`.

## 4. Vincoli rispettati

- `broad_navigation_refactor`: ❌ no
- `new_bottom_tab`: ❌ no
- `audit_only` in Track A: ✅ nessuna modifica UI eseguita qui

## 5. Validator

`validate_project_z_safe_menu_wiring_target_audit_v1.py` → **PASS**.
