# 127B — PROJECT_E Track B — HOUSING PHASE 3 INTEGRATION DESIGN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_B_HOUSING_PHASE3_INTEGRATION_DESIGN_READY`  
**Rollback**: N/A (design + validator only)

## Scopo

Portare Housing dalla phase2 unit validation (V_D) alla **phase3 integration design** con definizione del futuro endpoint preview e 6 UT addizionali. NESSUN runtime live bonus.

## Endpoint design (DESIGN_ONLY_NOT_IMPLEMENTED in V_E)

```
GET /api/housing/preview     (authn required, future runtime pack)
  -> { user_id, housing_bonus (zero envelope), caps_applied, mode_context, preview:true, dry_run:true }
```

DB writes 0; battle/account stat mutation 0; route assente in V_E (validator verifica 404).

## Resolver input bundle contract

| Campo | Tipo |
|---|---|
| `user_id` | str |
| `housing_rooms` | list[dict] (room_id, level) |
| `objects` | list[dict] (object_id, room_id, category) |
| `residents` | list[dict] (hero_id, room_id, position) |
| `caps_override` | None \| dict (opzionale) |
| `mode_context` | PvE \| PvP |

## 6 UT addizionali (UT_HOUSING_PHASE3_1..6)

1. `master_cap >= every secondary cap` — ordine cap rispettato
2. `empty inventory -> zero envelope`
3. `duplicate residents -> zero envelope identico`
4. `VIP/Vault secondary cap <= master`
5. `no official hero leak` (Borea / Primordial Gaia non emersi)
6. `PvE vs PvP mode context -> envelope stub identico` (modalità governata da caps, non da stub)

## Forbidden scope rispettato

Live housing route ❌, battle/account stat mutation ❌, DB writes ❌, frontend ❌, runtime import of stub ❌.
