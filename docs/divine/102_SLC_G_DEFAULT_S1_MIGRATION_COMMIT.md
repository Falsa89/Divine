# 102 · SLC-G — DEFAULT S1 MIGRATION COMMIT (COMMIT-A)

**Stato finale**: ✅ `SLC_G_COMMIT_APPLIED_SAFE`
**Modalità**: `GATED DB WRITE / BACKUP-FIRST / ROLLBACK-READY / NO RUNTIME PATCH`
**Approvazione esplicita**: ✅ marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true` rilevato
**`migration_id`**: `slc_g_commit_a_20260523T143803Z_4600ac04`
**SLC-G combo `final_status`**: ✅ `MIGRATION_APPLIED`
**Suite globale**: `RM1.31-B` → **330 PASS / 0 FAIL / 0 MISS** (329 → 330, +1 post-apply validator)
**Baseline diff RM1.32-PRE**: ✅ PASS

---

## 1. Obiettivo raggiunto

Eseguito il **commit gated della migrazione default legacy `s1`** sulle collection
server-bound classificate da SLC-F/SLC-G, dopo che:
- SLC-G pre-commit aveva chiuso 10/12 gate;
- G10 era stato sbloccato da SLC-G-GUILDS-UNSAFE-CLEANUP-B (`unsafe_unknown==0`);
- G11 è stato esplicitamente autorizzato in questo prompt.

**`migration_applied=true`**, **route NON patchata, nessun secondo server aperto,
nessuna feature flag attiva, nessun Phase 11, nessun runtime change.**

---

## 2. Pre-flight verificato prima della scrittura

| Check | Risultato |
|---|---|
| Marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true` presente | ✅ |
| Nessun `unsafe_unknown` in qualsiasi server-bound collection | ✅ (post cleanup-B) |
| AF2-N pre-state catturato: 2500/502/1914 | ✅ |
| Nessuna collection server-bound presente fuori dallo scope contratto | ✅ |

---

## 3. Backup pre-write (rollback-ready)

Backup completo creato **prima** di ogni write:

**Root**: `/app/data/design/system_safety/backups/slc_g_commit_a_pre_backup_20260523T143803Z/`

| Collection | Doc count (pre) | File | SHA-256 |
|---|---|---|---|
| `user_heroes` | 1971 | `user_heroes.json` | per-collection |
| `teams` | 21 | `teams.json` | per-collection |
| `inventory` | 10 | `inventory.json` | per-collection |
| `story_progress` | 1 | `story_progress.json` | per-collection |
| `guilds` | 2 | `guilds.json` | per-collection |
| `user_affinity_state` | 1914 | `user_affinity_state.json` | per-collection |
| `gift_transaction_ledger` | 502 | `gift_transaction_ledger.json` | per-collection |
| `user_gift_inventory` | 2500 | `user_gift_inventory.json` | per-collection |
| `users` | 25 | `users.json` | per-collection |

Manifest aggregato con SHA-256 finale: `backup_manifest_sha256` salvato nel
marker file di migrazione.

---

## 4. Write applicato — `set_only_if_missing`

Tutte le scritture sono state effettuate con semantica strettamente set-only-if-missing.
Nessun campo esistente è stato sovrascritto.

### 4.1 Server-bound collections (8 presenti)

| Collection | `server_id=s1` set | `account_id=user_id` set | Totale doc | Note |
|---|---|---|---|---|
| `user_heroes` | 1971 | 1971 | 1971 | tutti puliti |
| `teams` | 21 | 21 | 21 | tutti puliti |
| `inventory` | 10 | 10 | 10 | tutti puliti |
| `story_progress` | 1 | 1 | 1 | tutti puliti |
| `guilds` | 0 | 0 | 2 | già puliti da cleanup-B (markers preservati) |
| `user_affinity_state` | 1914 | 1914 | 1914 | AF2-N row count preservato |
| `gift_transaction_ledger` | 502 | 502 | 502 | AF2-N row count preservato |
| `user_gift_inventory` | 2500 | 2500 | 2500 | AF2-N row count preservato |

### 4.2 Mixed collection

| Collection | `server_id` | `account_id=id` set | Note |
|---|---|---|---|
| `users` | **mai toccato** | 25 | account_id derivato da `users.id`, conforme al contratto SLC-C |

### 4.3 Marker doc-level

A ciascun documento toccato è stato aggiunto `_slc_g_commit_marker` contenente:
```
{ task, version, migration_id, applied_at_utc }
```
**Totale documenti con marker commit-A: 6944** (1971+21+10+1+1914+502+2500+25). I 2 documenti `guilds` non hanno il marker commit-A perché erano già stati bonificati da cleanup-B (hanno invece `_slc_g_guilds_cleanup_marker`).

### 4.4 Conteggio operativo totale
- `server_id` set: **6919**
- `account_id` set: **6944**
- **Total field-set operations**: **13 863**
- **Documenti modificati**: **6 944**
- **Documenti eliminati**: **0** ✅
- **Insert eseguiti**: **0** ✅

---

## 5. Post-commit verification

### 5.1 Dry-run rieseguito

```
SLC-G-BACKFILL-DRYRUN PASS missing_sid=0 missing_aid=0 unsafe_unknown=0
```

### 5.2 SLC-G commit-A post-apply validator

```
SLC-G-COMMIT-A-POST-APPLY PASS errors=0
```

Verifiche specifiche tutte ✅:
- `migration_applied=true` nel marker file
- `route_patch_applied=false`
- `second_server_opening_allowed=false`
- `feature_flag_enabled=false`
- `phase_11_executed=false`
- AF2-N pre/post counts uguali
- Tutte le server-bound: `missing_server_id=0`, `unsafe_unknown=0`, `missing_aid_with_uid=0`
- `users.account_id` presente su tutti i 25 documenti
- Guild cleanup-B marker preservato su 2 documenti

### 5.3 SLC-G combo final status

```
[slc_g_combo_v1] PASS final_status=MIGRATION_APPLIED
  PASS   preflight
  PASS   backfill_dryrun
  PASS   write_gate_contract
  PASS   rollback_plan
  PASS   idempotency_contract
```

---

## 6. API smoke + baseline diff

| Check | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` | 200, count=100 | **200, 100** ✅ |
| `GET /api/heroes/primordial_gaia` | 404 | **404** ✅ |
| `GET /api/heroes/borea` | 200 catalog-only | **200** ✅ |
| `GET /api/heroes/greek_borea` | 200 catalog-only | **200** ✅ |
| AF2-N cap | 50000 | **50000** ✅ |
| AF2-N allowlist | 2500 | **2500** ✅ |
| AF2-N user_gift_inventory rows | 2500 | **2500** ✅ |
| AF2-N gift_transaction_ledger rows | 502 | **502** ✅ |
| AF2-N user_affinity_state rows | 1914 | **1914** ✅ |
| Baseline diff RM1.32-PRE | PASS | **PASS** ✅ |

---

## 7. File creati e modificati

### 7.1 Script Python creati

| File | Funzione |
|---|---|
| `/app/backend/scripts/apply_slc_g_commit_a.py` | Apply script gated (env-marker richiesto) |
| `/app/backend/scripts/rollback_slc_g_commit_a.py` | Rollback per `migration_id` (gated, env separato) |
| `/app/backend/scripts/validate_slc_g_commit_a_post_apply_v1.py` | Post-apply validator read-only |

### 7.2 Script modificati

| File | Modifica |
|---|---|
| `/app/backend/scripts/validate_slc_g_combo_v1.py` | Detect del marker file `slc_g_default_s1_migration_apply_result_v1.json` → flip a `final_status=MIGRATION_APPLIED` quando applicata |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Registrato OPTIONAL: `SLC-G-COMMIT-A-POST-APPLY` |

### 7.3 File generati a runtime

| File | Contenuto |
|---|---|
| `/app/data/design/system_safety/slc_g_default_s1_migration_apply_result_v1.json` | Marker file: `migration_applied=true`, `migration_id`, write_log, pre/post counts, AF2-N pre/post, backup root, rollback script path |
| `/app/backend/reports/slc_g_commit_a_apply_result.json` | Report dettagliato apply |
| `/app/backend/reports/slc_g_commit_a_suite_run.json` | Snapshot suite finale |
| `/app/data/design/system_safety/backups/slc_g_commit_a_pre_backup_20260523T143803Z/` | Backup completo pre-write (9 file JSON + manifest) |

---

## 8. Rollback path

Disponibile in qualsiasi momento via:

```bash
SLC_G_COMMIT_A_ROLLBACK_APPROVAL=true \
SLC_G_COMMIT_A_ROLLBACK_MIGRATION_ID=slc_g_commit_a_20260523T143803Z_4600ac04 \
python3 /app/backend/scripts/rollback_slc_g_commit_a.py
```

Il rollback usa il `migration_id` per `$unset` di `server_id`, `account_id` e
`_slc_g_commit_marker` ESCLUSIVAMENTE sui documenti taggati con quel preciso
`migration_id`. Nessun altro documento verrà mai toccato.

Fallback escalato: ripristino dai backup JSON in
`/app/data/design/system_safety/backups/slc_g_commit_a_pre_backup_20260523T143803Z/`.

---

## 9. Conta finale suite + invarianti

| Metrica | Valore |
|---|---|
| Suite globale | **330 PASS / 0 FAIL / 0 MISS** |
| Baseline diff RM1.32-PRE | **PASS** |
| Validator SLC-G OPTIONAL totali | 9 (6 originali + 1 post-cleanup-B + 1 cleanup-B post-apply + 1 commit-A post-apply) |
| Progress percent (per spec): 72 → **80** | ✅ |

---

## 10. Guardrail rispettati

- ✅ NO route runtime patch
- ✅ NO server selection endpoint live
- ✅ NO secondo server aperto
- ✅ NO feature flag enable (`SERVER_PROFILES_RUNTIME_ENABLED` + `SECOND_SERVER_OPENING_ENABLED` ancora unset)
- ✅ NO legacy fallback removal (S1 fallback ancora attivo)
- ✅ NO Phase 11
- ✅ NO UI changes
- ✅ NO modifiche a `battle_engine.py` / `battle_core.py` / `combat.tsx`
- ✅ NO modifiche a `affinity_gift_spend.py` / AF2-N / Stage4 / Redis runtime
- ✅ NO modifiche a gacha / roster / Character Bible / cataloghi / asset
- ✅ NO broad rollout / public spend UI / STACK-G wiring
- ✅ NO delete operations
- ✅ NO validator weakening
- ✅ AF2-N row counts esattamente preservati: 2500 / 502 / 1914

---

## 11. Verdict finale

> ## ✅ `SLC_G_COMMIT_APPLIED_SAFE`
> - **`migration_applied=true`**
> - **`migration_id=slc_g_commit_a_20260523T143803Z_4600ac04`**
> - 6944 documenti modificati esclusivamente in modalità set-only-if-missing
> - 0 documenti eliminati, 0 documenti creati
> - AF2-N invariants preservate al byte
> - SLC-G combo: `final_status=MIGRATION_APPLIED`
> - SLC-G migration ora compatibile con il futuro `server_id`/`account_id` model
>   senza alcuna modifica runtime/routing/UI: la migrazione dati è applicata
>   in modo trasparente al runtime corrente legacy.

---

## 12. Prossimi passi (gated, NON eseguiti)

- **SLC-H** (P1): server selection endpoint design-only
- **COSMETIC-B/C/D/E** (P2): read-only/inert
- **Managed Redis Live / Alerting Sink Live** (P3): pending env vars
- **Route patch runtime (SLC-F apply)** (P3): strettamente gated da approvazione successiva
- **Broad Rollout / Public Spend UI / STACK-G** (P4): strettamente OFF

Nessuno di questi è oggetto del task corrente.
