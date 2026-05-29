# 176 — PROJECT ARTIFACT INVENTORY LIVE APPLY (Stage 8 — Canary Live Apply Autorizzato)

> 📌 **PATH CANONICO**. Questo file è il documento Stage 8 di riferimento.
> Il path `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md` è mantenuto solo come alias/redirect (vedi cleanup pack `PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP` → doc 177).

## Verdetto locale
**`PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY_CANARY_APPLIED_INTERNAL_ONLY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `_COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo che l'utente ha eseguito **Save to GitHub → branch `main` → PUSH** e verificato manualmente la repo pubblica.

---

## Obiettivo (Stage 8)
Eseguire l'**apply DB canary autorizzato** del nuovo sistema "Artifact Inventory" SOLO per i due canary user interni:

- `sfqa@test.com`
- `test@test.com`

senza toccare:

- gacha rates / pity / pool / shop / IAP / Battle Pass / VIP / Soul Forge
- battle runtime / Character Bible
- legacy POST artifact/constellation (restano `HTTP 423`)
- frontend player UI (artifacts-preview.tsx, artifacts.tsx, (tabs)/gacha.tsx)
- `backend/battle_engine.py` / `backend/.env`

---

## Canary user effettivamente risolti

| email          | user_id                                | server_id | server_profile_id                                  |
|----------------|----------------------------------------|-----------|----------------------------------------------------|
| sfqa@test.com  | e15599e2-fe11-4d2e-86c9-10b9eab88acf   | s1        | e15599e2-fe11-4d2e-86c9-10b9eab88acf@s1            |
| test@test.com  | 651253e2-da8d-466b-98f3-82f008d158ed   | eu_1      | 651253e2-da8d-466b-98f3-82f008d158ed@eu_1          |

**Nessun altro user** è stato toccato. Nessun matching su `users` per qualunque altra email è stato eseguito.

---

## DB writes esatti eseguiti (40 totali, budget 52 → 12 sotto budget)

| Collection                      | Operazione | Count |
|---------------------------------|------------|-------|
| `artifact_catalog_snapshot`     | inserts    | 32    |
| `user_artifact_inventory`       | inserts    | 2     |
| `artifact_inventory_ledger`     | appends    | 2     |
| `artifact_collection_state`     | upserts    | 2     |
| `artifact_idempotency_registry` | inserts    | 2     |
| **TOTALE**                      |            | **40**|

### Counts post-apply (live DB read-only verify)
```
artifact_catalog_snapshot:     32
user_artifact_inventory:       2
artifact_inventory_ledger:     2
artifact_collection_state:     2
artifact_idempotency_registry: 2
```

### Source tag univoco
`artifact_inventory_live_apply_stage8_canary_2026_05_27`

### Artifact unico granted (locked=True)
`relic_aurora_eterna` × 1 → status `owned`, `locked: true` per entrambi i canary user.

---

## Collection NON toccate da Stage 8 (verificato live)

```
users:               0 writes Stage 8  (28 totali pre-esistenti, intatti)
teams:               0 writes Stage 8  (intatti)
user_heroes:         0 writes Stage 8  (intatti)
user_artifacts:      0 writes con source_id stage8  (legacy collection — intatta)
user_constellations: 0 writes con source_id stage8  (legacy collection — intatta)
```

### Idempotency check
Re-resolve della chiave `(user_id, server_profile_id, artifact_id, source_id)` produrrebbe **no-op** in tutte e 5 le collection target — registrato in `artifact_idempotency_registry`.

---

## Lock surfaces ancora attivi (verifica esplicita)

### Legacy POST artifact/constellation → ancora `HTTP 423`
`backend/routes/artifacts.py` MD5 = `893f244d85fd45cbe825996463995293`
- `ARTIFACT_MUTATION_LOCK_STATUS = 423` ✅
- Tutti gli handler POST legacy (equip/fuse/craft/pull) raise `HTTPException(423,...)` ✅

### Gacha banners artifact/constellation → ancora **hidden**
`data/design/artifacts/live_apply/artifact_live_apply_runtime_lock_guard_v1.json`:
```
"hidden_banners_v2_state": {"artifact": "hidden", "constellation": "hidden"}
"gacha_unchanged": true
```

### Frontend player UI per inventory → **non esiste** (zero esposizione live)
Verificato MD5 file frontend protetti vs `git HEAD` → **MATCH** su tutti:
```
frontend/app/artifacts-preview.tsx   0e75c94e00899af773dbc9faf7326a15  MATCH
frontend/app/(tabs)/gacha.tsx        f68b9239cec04ea54879f0be381e772a  MATCH
frontend/app/artifacts.tsx           8849e21c44207fc1d0074cae2cdc6879  MATCH
```
Nessun nuovo screen inventory esposto al player. Nessuna entry-point UI verso le nuove collection.

---

## 🔒 Invarianti MD5 rispettati

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅ UNCHANGED (zero live marker injected)
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅ (locked POST legacy intatto)
```

---

## Suite custom Python — risultato finale

**Comando:**
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel \
  --json-out /app/backend/reports/stage8_canary_apply_suite_run.json
```

**Risultato:**
```
Overall: PASS  (pass=707, fail=0, miss=0)
EXIT=0
```

✅ **707/707 PASS** (target raggiunto: 706 baseline 175 + 1 nuovo Stage 8 validator)

### Nuovo validator Stage 8
- `backend/scripts/validate_project_artifact_inventory_live_apply_v1.py` → **PASS**
- Registrato come **OPTIONAL** nel suite runner alla tupla:
  ```python
  ('PROJECT-ARTIFACT-INVENTORY-LIVE-APPLY', 'validate_project_artifact_inventory_live_apply_v1.py')
  ```

### Refresh pin MD5 (autorizzato dall'utente)
Un solo validator OPTIONAL pre-esistente (`PROJECT-BETA-HARNESS-PUBLIC-REPO-SYNC-AND-MINOR-UI-HYGIENE-FIX`) era FAIL a causa di un drift MD5 di `frontend/package.json` causato da auto-commit piattaforma (`dc068e4a` "Auto-generated changes" → bump patch `expo ~54.0.34→~54.0.35` + `expo-router ~6.0.23→~6.0.24`).

Su esplicita autorizzazione dell'utente è stato refreshato il **solo pin** `p1_a_playwright_yarn_alignment.package_json_md5_post` in:
```
data/design/testing/beta_harness_public_repo_sync_and_minor_ui_hygiene_fix_v1.json
  7fb50b6042864f7159ae3d0bd4eb2ede  →  bf8117614d334d7cd74115e1f9dfa038
```
Nota esplicita aggiunta in `delta_from_stage8_context_explanation` con motivazione completa. **Nessun validator weakening, nessuna modifica a `package.json`, nessun `yarn install`, nessun downgrade Expo.**

---

## Strategia tripled-sentinel anti stale-push (suite runner)

Per evitare il bug recurrente di stale push del suite runner (175 + precedenti), sono stati applicati **tre marcatori** distinti:

### 1) PUBLIC_SYNC_TAG fresco in header
`backend/scripts/run_hero_skill_kit_validator_suite.py` riga 4:
```python
# PUBLIC_SYNC_TAG_RESYNC_v5: suite_runner_stage_8_canary_apply_v5_2026_05_27
```

### 2) Sentinella inline sopra la riga di registrazione Stage 8
```python
# STAGE_8_CANARY_LIVE_APPLY_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
# Sentinella inline Stage 8 — registrazione canary live apply autorizzata SOLO per sfqa@test.com e test@test.com.
# Proof marker dedicato (tripled-sentinel): data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json
('PROJECT-ARTIFACT-INVENTORY-LIVE-APPLY', 'validate_project_artifact_inventory_live_apply_v1.py'),
```

### 3) Proof marker JSON in directory separata
`data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json` contiene il testo esatto della riga attesa, della sentinella inline e del top-sentinel v5.

---

## File creati / modificati (Stage 8)

### Validator + suite registration
- ✅ **NEW** `backend/scripts/validate_project_artifact_inventory_live_apply_v1.py` (211 righe)
- 🔧 **MOD** `backend/scripts/run_hero_skill_kit_validator_suite.py` — solo header comments + 1 riga tupla + 3 righe sentinelle inline (zero modifiche logica)

### Deliverable JSON (7 file in `data/design/artifacts/live_apply/`)
- ✅ `artifact_live_apply_authorized_gate_preflight_v1.json`
- ✅ `artifact_live_apply_canary_user_resolution_writeset_v1.json`
- ✅ `artifact_live_apply_canary_execution_v1.json`
- ✅ `artifact_live_apply_rollback_idempotency_v1.json`
- ✅ `artifact_live_apply_runtime_lock_guard_v1.json`
- ✅ `artifact_live_apply_completion_v1.json`
- ✅ `artifact_live_apply_suite_registration_proof_marker_v1.json` (tripled-sentinel proof marker)

### Pin refresh (autorizzato esplicitamente)
- 🔧 **MOD** `data/design/testing/beta_harness_public_repo_sync_and_minor_ui_hygiene_fix_v1.json` — solo `p1_a_playwright_yarn_alignment.package_json_md5_post` + nota `delta_from_stage8_context_explanation`

### Documentazione
- ✅ **NEW** `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md` (questo file)

### Report suite generato
- ✅ **NEW** `backend/reports/stage8_canary_apply_suite_run.json` (707/707 PASS)

---

## ❌ NON eseguito (vincoli rispettati)

- ❌ Nessuna scrittura DB oltre ai 40 canary write già autorizzati
- ❌ Nessuna mutazione a `users` / `teams` / `user_heroes` / `user_artifacts` / `user_constellations`
- ❌ Nessuna modifica a `backend/battle_engine.py`
- ❌ Nessuna modifica a `backend/.env` (zero live marker injected per public users)
- ❌ Nessuna modifica a `backend/routes/artifacts.py` (legacy POST restano 423)
- ❌ Nessuna modifica a `frontend/app/artifacts-preview.tsx` / `frontend/app/artifacts.tsx` / `frontend/app/(tabs)/gacha.tsx`
- ❌ Nessuna esposizione frontend live del nuovo inventory
- ❌ Nessuno sblocco di banner artifact/constellation in gacha
- ❌ Nessuno sblocco di equip/fuse/craft/pull artifact/constellation
- ❌ Nessun touch a IAP / Battle Pass / VIP / Soul Forge / Combat / Character Bible
- ❌ Nessuna modifica a gacha rates / pity / pools / shop prices / shop items
- ❌ Nessun validator weakening / bypass / fake PASS
- ❌ Nessun `yarn install` / `yarn add` / downgrade Expo

---

## Public Repo Sync Verification (PENDING)

### Stato locale ✅
- Suite custom Python: **707/707 PASS**
- MD5 invarianti: ✅ tutti rispettati
- DB live: ✅ 40 canary write totali, 0 forbidden writes
- Commit locale: vedi sezione successiva

### Azione richiesta all'utente per chiudere il pack
1. **Aprire il pannello Emergent → tasto "Save to GitHub"**
2. Selezionare branch **`main`**
3. **PUSH**
4. Su GitHub.com aprire `backend/scripts/run_hero_skill_kit_validator_suite.py` e verificare:
   - ✅ Top sentinel presente: `# PUBLIC_SYNC_TAG_RESYNC_v5: suite_runner_stage_8_canary_apply_v5_2026_05_27`
   - ✅ Sentinella inline presente: `# STAGE_8_CANARY_LIVE_APPLY_REGISTRATION_SENTINEL`
   - ✅ Tupla presente: `('PROJECT-ARTIFACT-INVENTORY-LIVE-APPLY', 'validate_project_artifact_inventory_live_apply_v1.py'),`
5. Su GitHub.com aprire `data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json` e confermarne la presenza
6. Solo dopo questa verifica manuale, il verdetto può promuoversi a `_COMPLETE_PUBLIC_REPO_VERIFIED`

> Se il push pubblico non aggiorna il blob del suite runner (recurrent stale-push bug), la presenza del proof marker JSON in directory separata (tripled-sentinel) consente di diagnosticare immediatamente l'eventuale skip del blob runner.

---

## Verdict finale

**`PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY_CANARY_APPLIED_INTERNAL_ONLY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**
