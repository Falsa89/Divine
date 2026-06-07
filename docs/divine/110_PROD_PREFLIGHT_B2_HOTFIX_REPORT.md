# Micro-Hotfix B2 — Approval Gate Commit Pin Fix

Hotfix: `v110_PROD_PREFLIGHT_B2_APPROVAL_GATE_COMMIT_PIN_FIX`
Pack base: `MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Pack precedente (B1): `v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION`
Sentinel: `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Data esecuzione: 2026-06-07 (UTC)

## Verdetto

```
MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

## Issue rilevato dall'utente

Nel file pubblico
`data/design/v110_prod_preflight/v110_production_approval_gate_matrix_v1.json`,
il campo `exact_git_commit_pin.pinned_value` era `null`. Per Pack 77 non può restare `null`:
deve essere pinnato al commit hotfix B1 `fc13fa32ef91530eca031fbeec283bea66bb21d9`.

## Fix applicato

1. **Orchestratore** (`orchestrate_v110_prod_preflight.py`):
   - rimosso `pinned_value: None` come stato di default;
   - hard-coded del commit hotfix B1 `fc13fa32ef91530eca031fbeec283bea66bb21d9` come pin di riferimento per il Pack 77;
   - aggiunto `pinned_at_utc`, `hotfix_chain`, `pin_source`, `pin_rationale`, `current_head_at_orchestrator_run`;
   - eventuali auto-commit successivi al B1 NON spostano il pin (vengono tracciati separatamente in `current_head_at_orchestrator_run` per audit, ma non sovrascrivono `pinned_value`).
2. **Validator** (`validate_v110_production_approval_gate_matrix.py`):
   - asserisce che `pinned_value` non sia null;
   - asserisce lunghezza 40 e formato esadecimale (git sha-1);
   - asserisce che il valore sia ESATTAMENTE il commit B1 `fc13fa32ef91530eca031fbeec283bea66bb21d9`;
   - asserisce che `pin_source == "hard_coded_at_pack_76_hotfix_b2"`;
   - asserisce che `pin_rationale` sia non-vuoto;
   - asserisce che la `hotfix_chain` contenga sia B1 che B2.

## Stato `exact_git_commit_pin` post-hotfix B2

```json
{
  "description": "commit hash della preflight chain (Pack 76 + hotfix B1 + B2) — pinnato per il Pack 77 production apply execute",
  "pinned_value": "fc13fa32ef91530eca031fbeec283bea66bb21d9",
  "pinned_at_utc": "2026-06-07T19:31:47.522109Z",
  "hotfix_chain": [
    "v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION",
    "v110_PROD_PREFLIGHT_B2_APPROVAL_GATE_COMMIT_PIN_FIX"
  ],
  "pin_source": "hard_coded_at_pack_76_hotfix_b2",
  "pin_rationale": "Il pin riferisce il commit dell'hotfix B1 (fc13fa32) che ha reso il dry-run reale e riconciliato i diff. Eventuali auto-commit successivi non spostano questo pin.",
  "current_head_at_orchestrator_run": "(git HEAD del momento — audit only, non sostituisce pinned_value)"
}
```

## Rollup marker rigenerato

Stesso verdetto del Pack 76 v1 e dell'hotfix B1. La chain dei pin è ora completa e validata.

## Final 3-Run Suite (post-hotfix B2)

| Run | PASS | FAIL | MISS | REQUIRED FAIL |
|-----|------|------|------|---------------|
| 1   | 1310 | 21   | 0    | 0             |
| 2   | 1310 | 21   | 0    | 0             |
| 3   | 1310 | 21   | 0    | 0             |

Deterministico ✅ — **1310/21/0/0** (invariato vs Pack 76 v1 e hotfix B1).

> Nota operativa: durante l'esecuzione del rollup B2 è stato rilevato che il binario di Redis era nuovamente scomparso dal container (sintomo noto e ricorrente). Reinstallato via `apt-get install --reinstall redis-server` + symlink + restart via supervisor. Master suite tornata a baseline 1310/21/0/0 prima di generare il rollup finale B2.

## Track aggiornate

| Track | Stato |
|-------|-------|
| H — Approval gate matrix | ✅ **HOTFIX B2** — `exact_git_commit_pin.pinned_value = fc13fa32...`, validator rinforzato |
| tutte le altre | ✅ invariate vs B1 |

## Estimates correnti (Track D)

| Campo | Valore |
|-------|--------|
| users_selected | 1630 |
| psp_to_insert_estimate | 1630 |
| user_heroes_to_update_estimate | 422 |
| team_formation_to_update_estimate | 0 |
| user_equipment_to_update_estimate | 28 |
| db_writes_if_apply_executed_estimate | **2080** = 1630 + 422 + 0 + 28 ✅ |
| backup_manifest_sha256 | `f68574c39c89...` |
| apply_script_sha256 | `9232b93e6135...` |

> Nota: il numero di utenti aumenta organicamente durante le rotazioni del master suite (validatori QA storici v96/v98 creano utenti di test sul DB locale). Lo orchestratore Pack 76 esegue solo `count_documents` (read-only) sulla produzione.

## Safety Flags (riepilogo globale hotfix B2)

- `fake_PASS`: false
- `validator_weakening`: false
- `silent_validator_deletion`: false
- `release_readiness_claimed`: false
- `production_apply_executed`: false
- `production_db_writes`: false
- `destructive_migration`: false
- `delete_on_production`: false
- `premium_grant`: false
- `reward_live`: false
- `progress_live`: false
- `legacy_cleanup_executed`: false
- `battle_engine_formula_rewrite`: false
- `postqa_d_unlocked`: false
- `approval_flags_changed_to_yes`: false
- `raw_secret_export`: false
- `rollback_executed_on_production`: false
- `fake_dry_run_when_command_failed`: false

## PRODUCTION APPLY NOT EXECUTED ✅
## PRODUCTION DB WRITES = 0 ✅
## LEGACY CLEANUP NOT EXECUTED ✅

## Pin definitivi per Pack 77

| Pin | Valore |
|-----|--------|
| `exact_git_commit_pin` | **`fc13fa32ef91530eca031fbeec283bea66bb21d9`** |
| `backup_artifact_pin (manifest_sha256)` | `f68574c39c89...` (vedi JSON corrente) |
| `apply_script_sha256` | `9232b93e6135...` (vedi JSON corrente) |
| `dry_run_hash_pin` | sha256 del JSON `v110_prod_psp_apply_dry_run_result_v1.json` |
| `rollback_plan_hash_pin` | sha256 del JSON `v110_prod_rollback_preflight_result_v1.json` |

## Next Step

> Hotfix B2 chiuso. Tutti i pin coerenti e non-null. Pronto per ricevere il **Pack 77 — production apply execute pack** con autorizzazione utente esplicita separata, pinato sul commit B1 `fc13fa32...`.

---

> Questo report è strettamente locale (container Kubernetes). Tag pubblico
> `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO` rimane in stato
> `PUBLIC_SYNC_PENDING`.
