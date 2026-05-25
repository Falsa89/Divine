# 149B — COMBAT & POST-BATTLE FLOW AUDIT

## Track B — `PROJECT_FRONTEND_B_TRACK_B`

**Verdict:** `TRACK_B_COMBAT_AND_POST_BATTLE_FLOW_AUDIT_READY`

## Routes auditate (7)

- `/(tabs)/battle` (764 LOC), `/combat` (1848 LOC)
- `/story`, `/tower`, `/pvp`, `/raid`, `/gvg`

## Flow steps (7)

1. Tab Battaglia → hub modi
2. Selezione modalità → lista capitoli/floor/avversari
3. Formazione (3 eroi attivi + supporti)
4. Lancio battaglia (`POST /api/battle/simulate`)
5. Round loop runtime
6. Post-battle rewards
7. Continue/Retry/Back

## Gap identificati (4)

| Gap | Severity |
|---|---|
| `combat.tsx` 1848 LOC, refactor in moduli necessario | **high_refactor** |
| Post-battle reward screen non uniforme tra modalità | medium |
| Mancanza indicatore "status second-slice non attivo" in PvP | low_until_prod |
| Loading skeleton tra hub e combat assente | medium |

## Vincoli

**`do_not_touch`:** `battle_engine.py` md5 `151ca35a...`, `battle_core.py`, combat logic core (refactor solo strutturale dei componenti UI).

## Validator

`validate_project_frontend_b_combat_flow_audit_v1.py` → **PASS**. `battle_engine.py` integrity verified.
