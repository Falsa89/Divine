# 134A — BATTLE RUNTIME SEAM AUDIT AND CONTRACT

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track A
**Verdict**: `TRACK_A_BATTLE_RUNTIME_SEAM_AUDIT_READY`
**Classificazione seam**: `SEAM_SAFE_NOW_INERT`
**Marker JSON**: `/app/data/design/status_effects/project_l_battle_runtime_seam_audit_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_battle_runtime_seam_audit_v1.py`

---

## Obiettivo

Audit *read-only* del runtime battle del backend per identificare il punto più sicuro dove ospitare il futuro cablaggio first-slice (`buff_offensive`, `buff_defensive`) tramite il resolver puro.

## Reality check

A differenza di quanto controllato dal Pack K (che cercava i moduli sotto `/app/backend/game_logic/`), una scansione esaustiva del backend ha rilevato che il battle runtime layer **esiste** ma vive direttamente sotto `/app/backend/`:

| File | Stato | Ruolo |
|------|-------|-------|
| `/app/backend/battle_engine.py` | ESISTE (≈1249 LOC) | source-of-truth: `simulate_battle`, `execute_skill`, `generate_enemy_team` |
| `/app/backend/battle_core.py` | ESISTE (33 LOC) | thin proxy che riesporta da `battle_engine.py` |
| `/app/backend/routes/combat.py` | ESISTE | route /api/combat (⊃3 LOC) |
| `/app/backend/server.py` | ESISTE | registra l'endpoint `simulate_battle_endpoint` |

## Decisione di sicurezza

Intervenire direttamente su `battle_engine.py` (1249 LOC) sarebbe classificato `broad battle refactor` — esplicitamente vietato dal Pack L. La spec autorizza un **fallback isolato**:

> *«or inert module under `/app/backend/game_logic/status_prefight_runtime_seam.py` if no battle file safe»*

Quindi la classifica corretta è **`SEAM_SAFE_NOW_INERT`**, attuata mediante creazione di un nuovo modulo *isolato* sotto `/app/backend/game_logic/`, **non importato** da `battle_engine.py`, `battle_core.py`, `server.py`, né da alcuna route.

## Conformità ai guardrail

- ✅ Audit read-only.
- ✅ Nessuna mutazione runtime in Track A.
- ✅ Nessun broad refactor.
- ✅ Nessun cambio battle behavior.
