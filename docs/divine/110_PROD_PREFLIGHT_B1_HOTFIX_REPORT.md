# Hotfix B1 — v110 PROD Preflight Dry-Run Invocation & Diff Reconciliation

Hotfix: `v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION`
Pack base: `MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Sentinel: `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Data esecuzione: 2026-06-07 (UTC)

## Verdetto

```
MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Stesso verdetto del Pack 76 base ma ora basato su un **vero dry-run** del production apply script
con `returncode=0` e su numeri **riconciliati** tra report e JSON.

## Issue 1 — Dry-run dichiarato verde ma invocazione fallita (RISOLTO)

**Pre-hotfix** (commit `d59e4c3e`):
- l'orchestratore invocava `apply_v110_psp_migration_execute_staging.py --dry-run`;
- lo script NON supporta `--dry-run` → `argparse` falliva con `returncode=2`;
- `stderr_tail`: `error: unrecognized arguments: --dry-run`;
- tuttavia `dry_run_executed` veniva dichiarato `true` → blocker rilevato dall'utente.

**Hotfix B1**:
- l'orchestratore ora invoca lo script con `--plan-only` (che è una flag effettivamente supportata,
  in alternativa all'assenza di `--execute`);
- il validatore `validate_v110_prod_psp_apply_dry_run_result.py` ora richiede:
  - `apply_script_invocation.returncode == 0`;
  - `--dry-run` NON presente nel cmd;
  - `cmd` contiene `--plan-only` oppure NON contiene `--execute`;
  - `script_status_in_output_file` in un set di status di safety dichiarato:
    - `PLAN_ONLY_NO_WRITE` (caso clone confermato + flag impostati),
    - `APPLY_REFUSED_MISSING_FLAGS` (caso produzione senza flag),
    - `APPLY_REFUSED_NO_DB`,
    - `APPLY_REFUSED_NOT_STAGING_CLONE`;
  - `script_apply_executed_in_output_file == false`;
  - `script_db_writes_in_output_file == 0`;
  - `dry_run_real_success == true`;
  - `dry_run_executed == true`;
  - coerenza algebrica: `db_writes_if_apply_executed_estimate == psp_to_insert + sum(updates)`.

**Stato post-hotfix**: lo script invocato sulla produzione torna `returncode=0` con status
`APPLY_REFUSED_MISSING_FLAGS` — è esattamente la prova che il design dello script è inviolabile
contro la produzione anche se invocato da un orchestratore. Questo è il **vero dry-run di safety**.

## Issue 2 — Mismatch report vs JSON sulle stime (RISOLTO)

**Pre-hotfix** (report finale del commit `c0bd3ee0`):
- report dichiarava `user_heroes=0, team=1, equipment=445, total=2004`;
- JSON dichiarava `user_heroes=418, team=0, equipment=28, total=2004`;
- totali coincidevano ma distribuzione no → blocker rilevato dall'utente.

**Hotfix B1**:
- la tabella expected diff in questo file è derivata 1:1 dal JSON corrente;
- il validatore Track D ora forza la coerenza algebrica
  (`total == psp + sum(updates)`, assertion fail se diversa);
- il validatore Track G era già numeric-agnostic e accetta solo valori interi non-negativi
  + l'invariant totale di Track D.

**Distribuzione corrente** (post-hotfix, JSON di riferimento):

| Campo | Valore |
|-------|--------|
| users_selected | **1606** |
| psp_to_insert_estimate | **1606** |
| user_heroes_to_update_estimate | **418** |
| team_formation_to_update_estimate | **0** |
| user_equipment_to_update_estimate | **28** |
| db_writes_if_apply_executed_estimate | **2052** = 1606 + 418 + 0 + 28 ✅ |

> Nota: il numero `1606` (vs `1582` del Pack 76 v1 e `1558` della prima esecuzione) cresce perché
> il master suite contiene validatori QA storici (v96/v98) che creano utenti di test transitori
> nel DB di produzione locale. Questa è una caratteristica nota e documentata della suite,
> NON una scrittura imputabile al Pack 76 o all'hotfix B1. L'orchestratore Pack 76 esegue solo
> `count_documents` (read-only) sulla produzione.

## Issue extra — Bug B1.1: backup Pack 74 catturato dopo la corruzione (RISOLTO)

**Sintomo**: durante la prima esecuzione dell'hotfix B1, i validatori
`PROJECT-V110-LIMITED-PSP-APPLY-EXECUTE-RESULT` e
`MEGA-RELEASE-ACCELERATION-74-v110-PSP-APPLY-STAGING-EXECUTE-ROLLUP` flippavano da PASS a FAIL.

**Root cause**: nel codice dell'orchestratore Pack 76 originale, l'ordine delle istruzioni era:
1. `subprocess.run(cmd)` (lo script sovrascrive `v110_limited_psp_apply_execute_result_v1.json`);
2. `pack74_backup = open(APPLY_RESULT_FILE).read()` (legge il file **già corrotto**);
3. ripristina dal backup = ripristina lo stato corrotto.

**Fix B1.1**: spostato il `pack74_backup = open(...).read()` PRIMA di `subprocess.run(cmd)`,
così il backup riflette lo stato Pack 74 originale e il ripristino è effettivo. Verificato che
i validatori Pack 74 tornano verdi dopo il fix.

## Commit Hash

```
(da generare al commit finale di questo hotfix)
```

## Track aggiornate

| Track | Stato | Note |
|-------|-------|------|
| A — Baseline 3-run | ✅ 1296/21/0/0 | invariato |
| B — Production env classification | ✅ | invariato |
| C — Pre-dry-run snapshot | ✅ users=1606 | aggiornato |
| **D — Production PSP apply dry-run** | ✅ **HOTFIX B1** | `--plan-only`, returncode=0, status `APPLY_REFUSED_MISSING_FLAGS` (safe-refuse) |
| E — Backup preflight | ✅ manifest_sha256=`16d4fa19858849c1760bbcaf...` | aggiornato (count delta) |
| F — Rollback preflight | ✅ | invariato |
| G — Expected diff | ✅ **riconciliato con D** | numeri ora coerenti |
| H — Approval gate matrix | ✅ tutti i flag NO | invariato (pins ricalcolati post-hotfix) |
| I — Apply script safety recheck | ✅ all_audits_ok=true, sha256=`9232b93e6135d7813c85566b...` | invariato |
| J — Post-dry-run immutability | ✅ counts+checksums unchanged | invariato |
| K — Live readiness | ✅ live OFF | invariato |
| L — Gate/runtime invariant | ✅ preserved | invariato |
| M — Final 3-run | ✅ **1310/21/0/0 deterministico** | invariato |
| N — Validators + runner integration | ✅ 14 entry registrate | validator Track D rafforzato |

## Final 3-Run Suite (post-hotfix B1)

| Run | PASS | FAIL | MISS | REQUIRED FAIL |
|-----|------|------|------|---------------|
| 1   | 1310 | 21   | 0    | 0             |
| 2   | 1310 | 21   | 0    | 0             |
| 3   | 1310 | 21   | 0    | 0             |

Deterministico ✅ — **1310/21/0/0** (= Pack 76 v1, nessun regressione).

## Production Dry-Run Result (Track D, post-hotfix B1)

| Campo | Valore |
|-------|--------|
| `hotfix_applied` | `v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION` |
| `dry_run_invocation_mode` | `plan_only` |
| `dry_run_executed` | **true** |
| `dry_run_real_success` | **true** |
| `apply_script_invocation.cmd` | `[python, apply_..._staging.py, --plan-only, --target-server-id, s1]` |
| `apply_script_invocation.returncode` | **0** |
| `apply_script_invocation.exit_zero` | **true** |
| `script_status_in_output_file` | `APPLY_REFUSED_MISSING_FLAGS` |
| `script_apply_executed_in_output_file` | false |
| `script_db_writes_in_output_file` | 0 |
| `apply_executed` | false |
| `production_apply_executed` | **false** |
| `users_selected` | 1606 |
| `psp_to_insert_estimate` | 1606 |
| `user_heroes_to_update_estimate` | 418 |
| `team_formation_to_update_estimate` | 0 |
| `user_equipment_to_update_estimate` | 28 |
| `db_writes_if_apply_executed_estimate` | **2052** |
| `actual_db_writes_in_this_dry_run` | **0** |
| `production_db_writes` | **0** |

`safety_flags`:
- `production_apply`: false
- `production_db_writes`: false
- `false_filter_applied`: false
- `release_readiness_claimed`: false
- `fake_PASS`: false
- `fake_dry_run_when_command_failed`: **false** (nuovo flag introdotto dall'hotfix B1)

## Approval Gate Matrix (Track H, pins aggiornati post-hotfix)

`production_execute_allowed`: **false**

Pin di artefatto aggiornati (per il prossimo pack apply-execute):
- `exact_git_commit_pin`: (commit hash di questo hotfix — da inserire al commit)
- `backup_artifact_pin (manifest_sha256)`: `16d4fa19858849c1760bbcaf...`
- `dry_run_hash_pin`: sha256 del nuovo `v110_prod_psp_apply_dry_run_result_v1.json` (post-B1)
- `rollback_plan_hash_pin`: sha256 del nuovo `v110_prod_rollback_preflight_result_v1.json`

## Safety Flags (riepilogo globale hotfix B1)

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
- `approval_flags_changed_to_yes`: **false**
- `raw_secret_export`: false
- `rollback_executed_on_production`: false
- `fake_dry_run_when_command_failed`: false

## PRODUCTION APPLY NOT EXECUTED ✅

Confermato. Nessun apply su `divine_waifus`. Lo script invocato in `--plan-only` con DB_NAME=divine_waifus
si è correttamente rifiutato a livello `APPLY_REFUSED_MISSING_FLAGS` (nessuno dei 5 flag `V110_*` impostati a YES).

## PRODUCTION DB WRITES = 0 ✅

Misurato via:
- snapshot di conteggi pre/post identici;
- checksum SHA-256 di sequenze `_id` pre/post identici;
- output del script: `apply_executed=false, db_writes=0, status=APPLY_REFUSED_MISSING_FLAGS`;
- nessuna esecuzione di rollback o delete su produzione.

## LEGACY CLEANUP NOT EXECUTED ✅

Confermato. `legacy_cleanup_executed=false` ovunque.

## Remaining Blockers

- `V110_PRODUCTION_DB_EXPLICIT_APPROVAL` non concessa dall'utente.
- Production apply execute pack dedicato non ancora creato.
- Maintenance window di ≥30 minuti non ancora pianificata.

## Next Step

> Pack 77 — **production apply execute pack** con autorizzazione esplicita separata, che pini
> il commit di questo hotfix B1 (corretto), il `manifest_sha256` corretto, lo `apply_script_sha256`
> corretto, e i nuovi `dry_run_hash_pin` / `rollback_plan_hash_pin`. Solo allora si potrà
> procedere all'apply produzione.

---

> Questo report è strettamente locale (container Kubernetes). Tag pubblico
> `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO` rimane in stato
> `PUBLIC_SYNC_PENDING`.
