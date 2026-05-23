# 106 — SLC-F APPLY BATCH-1B (server-bound a basso rischio, write-time scoping)

> **Verdict finale:** `SLC_F_BATCH_1B_APPLIED_SAFE`
> **Progress globale:** **88% → ~90%**
> **Modalità:** APPLY GATED — BATCH-1B SOLO. Nessuna espansione di scope. Nessuna apertura del secondo server. AF2-N completamente preservato.

---

## 1. Executive Verdict

✅ **PASS** — La Batch-1B della migrazione SLC-F è stata applicata in modo sicuro e idempotente alle 7 route server-bound a basso rischio identificate dall'audit. Tutte le route esterne allo scope (combat / battle / gacha / AF2-N / Character Bible / housing / secondo server) sono rimaste **intatte**. La suite master di validazione è **verde a 342/342** e tutti gli invarianti runtime sono confermati.

**Risultato in sintesi**

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Suite master `run_hero_skill_kit_validator_suite.py` | PASS | PASS (342/342) | ✅ |
| Nuovo validator `SLC-F-BATCH-1B-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| `/api/heroes` count | 100 | 100 | ✅ |
| `/api/heroes/primordial_gaia` | 404 | 404 | ✅ |
| `/api/heroes/borea` | 200 (catalog-only inert) | 200 | ✅ |
| `/api/heroes/greek_borea` | 200 (catalog-only inert) | 200 | ✅ |
| Env `SERVER_PROFILES_RUNTIME_ENABLED` | unset | unset | ✅ |
| Env `SECOND_SERVER_OPENING_ENABLED` | unset | unset | ✅ |
| AF2-N canary state | preservato | preserved (V28 scope S1, allowlist=2500, cap=50000) | ✅ |

---

## 2. Validator Suite Integration Result

- **File modificato:** `/app/backend/scripts/run_hero_skill_kit_validator_suite.py`
- **Inserimento:** chiave `('SLC-F-BATCH-1B-POST-APPLY', 'validate_slc_f_batch_1b_post_apply_v1.py')` aggiunta in coda alla lista `OPTIONAL`, subito dopo `SLC-F-BATCH-0-1-POST-APPLY`.
- **Esito integrazione:** ✅ il runner orchestratore esegue il nuovo validator come optional task, esce con `0` e contribuisce ai totali PASS.
- **Nessuna voce REQUIRED modificata** — nessun validator ACTIVE_REQUIRED rimosso, indebolito o riordinato.

---

## 3. Master Suite Result

```
Overall: PASS  (pass=342, fail=0, miss=0)
JSON report: /tmp/slc_f_batch_1b_suite.json
```

- Nessun FAIL.
- Nessun MISS.
- Nessun validator SUPERSEDED inatteso (la lista SUPERSEDED riflette correttamente lo stato AF2-N corrente: canary attivo, inventory writes attivi, stage2/3/4 applicati, rate-limit attivo, scope S1 a 2500).

---

## 4. API Smoke Result (read-only)

| Endpoint | HTTP | Verifica |
|---|---|---|
| `GET /api/heroes` → length | 200, 100 elementi | ✅ catalogo intatto |
| `GET /api/heroes/primordial_gaia` | 404 | ✅ esclusione preservata |
| `GET /api/heroes/borea` | 200 | ✅ catalog-only inert baseline preservato |
| `GET /api/heroes/greek_borea` | 200 | ✅ catalog-only inert baseline preservato |
| `GET /api/affinity/gift-spend/canary-status` | 200 | ✅ AF2-N invariato |

---

## 5. Invariants

- ✅ `/api/heroes` length **= 100** (Character Bible canonica).
- ✅ `primordial_gaia` → **404** (rimane escluso).
- ✅ `borea` / `greek_borea` → **200** in modalità **catalog-only inert** (nessuna attivazione runtime).
- ✅ `SERVER_PROFILES_RUNTIME_ENABLED` **unset**.
- ✅ `SECOND_SERVER_OPENING_ENABLED` **unset**.
- ✅ AF2-N: `feature_flag_currently_enabled=True`, `inventory_mutation_enabled=True`, `rate_limit_enabled=True`, `canary_allowlist_size=2500`, `canary_ledger_cap=50000` — **identico** al pre-apply.
- ✅ Nessuna rotta `/api/housing`, `/api/servers`, `/api/account/server-profiles`, `/api/account/active-server` presente nel codice (verificato dal validator post-apply).

---

## 6. Files Changed (final list)

### File di codice (route patchate)
1. `backend/routes/forge.py`
2. `backend/routes/achievements.py`
3. `backend/routes/level_sharing.py`
4. `backend/routes/social.py`
5. `backend/routes/soul_forge.py`
6. `backend/routes/artifacts.py`
7. `backend/routes/guild.py`

> Nota: `backend/routes/items.py` risulta nella whitelist `ALLOWED_CHANGED` ma era già stato patchato in Batch-0/1; la Batch-1B non lo ritocca. Non vi è alcuna modifica aggiuntiva su quel file in questo apply.

### Helper (riusato, non modificato)
- `backend/utils/server_scope.py` — già presente da Batch-0, esporta `ensure_server_scope()` e `LEGACY_DEFAULT_SERVER_ID = "s1"`.

### Script di sicurezza generati
- `backend/scripts/validate_slc_f_batch_1b_post_apply_v1.py` (post-apply validator, READ-ONLY).
- `backend/scripts/rollback_slc_f_batch_1b.py` (rollback gated, richiede `SLC_F_BATCH_1B_ROLLBACK_APPROVAL=true` + `SLC_F_BATCH_1B_ROLLBACK_ID=slc_f_batch_1b_20260523T175058Z_2cf0584c`).

### Markers / artifacts
- `data/design/system_safety/slc_f_batch_1b_apply_marker_v1.json` (apply marker firmato).
- `data/design/server_lifecycle/_slc_f_batch_1b_post_apply_v1_result.json` (output validator, verdict `PASS`).
- `/tmp/slc_f_batch_1b_suite.json` (report JSON suite master, verdict `PASS`).

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunta UNA riga in `OPTIONAL`.

---

## 7. Routes Patched / Skipped

### ✅ Patchate (7 famiglie route, scoping write-time)
| Famiglia | File | Collections write-time interessate |
|---|---|---|
| forge | `forge.py` | `user_runes`, `inventory` |
| achievements | `achievements.py` | `achievement_claims` |
| level_sharing | `level_sharing.py` | `level_sharing` |
| social | `social.py` | `plaza_chat`, `friends` |
| soul_forge | `soul_forge.py` | `wallets`, `retirement_history`, `shop_purchases_special` |
| artifacts | `artifacts.py` | `user_materials`, `user_fragments`, `user_artifacts`, `user_constellations` |
| guild | `guild.py` | `teams`, `guilds` |

**Semantica patch:** `ensure_server_scope(doc, current_user)` viene applicato sull'oggetto candidato all'`insert_one` / `update_one(..., upsert=True)`. Su upsert si usa `$setOnInsert` ⇒ **set-only-if-missing**, idempotente e retro-compatibile con i documenti legacy `s1`.

### ⛔ Saltate per design (audit pre-apply)
| Famiglia | Motivo |
|---|---|
| `sanctuary` | Scrive su `db.heroes` ⇒ **Character Bible**: fuori scope assoluto. |
| `player_faction_v2` | Nessuna `insert_one` / `upsert` trovata: nulla da patchare. |

### ⛔ Famiglie esplicitamente FUORI scope Batch-1B (intoccate)
- `combat.py`, `battle_engine.py`, `battle_core.py` — Batch-4 futuro.
- `affinity_gift_spend.py`, `affinity_gifts.py` — AF2-N: gestito da pipeline separata.
- `heroes.py` — Character Bible read.
- Tutto Phase 11 / second server opening / SLC-H live wiring / housing runtime.

---

## 8. Forbidden Scope Verification

Verificato da `validate_slc_f_batch_1b_post_apply_v1.py` (sezione `FORBIDDEN_UNCHANGED`):

| File / area | Diff su HEAD | Esito |
|---|---|---|
| `backend/battle_engine.py` | nessuno | ✅ intatto |
| `backend/battle_core.py` | nessuno | ✅ intatto |
| `frontend/app/combat.tsx` | nessuno | ✅ intatto |
| `backend/routes/affinity_gift_spend.py` | nessuno | ✅ intatto |
| `backend/routes/affinity_gifts.py` | nessuno | ✅ intatto |
| `backend/routes/heroes.py` | nessuno | ✅ intatto |
| `backend/routes/combat.py` | nessuno | ✅ intatto |
| `backend/routes/sanctuary.py` | nessuno | ✅ saltata correttamente |
| `backend/routes/player_faction_v2.py` | nessuno | ✅ saltata correttamente |
| Route `/api/housing` | non presente | ✅ |
| Route `/api/servers` | non presente | ✅ |
| Route `/api/account/server-profiles` | non presente | ✅ |
| Route `/api/account/active-server` | non presente | ✅ |

---

## 9. Borea / Gaia Safety

- ✅ `primordial_gaia` continua a restituire `404` (rimosso storicamente; nessuna re-introduzione).
- ✅ `borea` e `greek_borea` restano in stato **catalog-only inert**:
  - presenti nel catalogo (HTTP 200 sull'endpoint singolo);
  - **nessuna** attivazione runtime, **nessun** kit attivo, **nessun** trigger/flag abilitato;
  - Character Bible non modificata (zero diff in `sanctuary.py`, `heroes.py`, `db.heroes`).
- ✅ Nessuna feature `BOREA_ACTIVATION_*` introdotta o ribaltata.

---

## 10. AF2-N Preservation

| Voce | Pre-apply | Post-apply | Esito |
|---|---|---|---|
| `feature_flag_currently_enabled` | True | True | ✅ |
| `inventory_mutation_enabled` | True | True | ✅ |
| `rate_limit_enabled` | True | True | ✅ |
| `canary_allowlist_size` | 2500 | 2500 | ✅ |
| `canary_ledger_cap` | 50000 | 50000 | ✅ |
| Validator family AF2-N (V12–V30) | PASS | PASS | ✅ |
| Diff su `affinity_gift_spend.py` / `affinity_gifts.py` | 0 | 0 | ✅ |

**Conclusione:** la canary AF2-N e l'intera pipeline V12–V30 sono **identiche** allo stato pre-Batch-1B. Nessuna interferenza laterale.

---

## 11. Known Drift Docs Status

Per istruzione esplicita dell'utente: i 7 documenti di drift provenienti dal famiglia `gacha/summon` **NON sono stati corretti** in questo job.

- Stato: **DRIFT KNOWN, NON-BLOCKING, INTENZIONALMENTE NON CORRETTO IN BATCH-1B**.
- Tutti i validator AF2-N / suite master restano verdi nonostante il drift dichiarato (è documentazione, non runtime).
- Da affrontare in un job dedicato successivo (suggerito post-Batch-2 o come task indipendente di housekeeping documentale).

---

## 12. Rollback Path

In caso di necessità di rollback:

```bash
export SLC_F_BATCH_1B_ROLLBACK_APPROVAL=true
export SLC_F_BATCH_1B_ROLLBACK_ID=slc_f_batch_1b_20260523T175058Z_2cf0584c
python3 /app/backend/scripts/rollback_slc_f_batch_1b.py
```

Caratteristiche del rollback:
- **Gated**: senza entrambi i marker rifiuta l'esecuzione (exit ≠ 0).
- **Code-only revert**: rimuove la riga `ensure_server_scope(...)` dalle 7 route patchate; non tocca `users` / `db.heroes` / `dm_*` / AF2-N.
- **Idempotente**: ri-eseguito su uno stato già rolled-back è no-op.
- **Apply marker preserved**: il file `slc_f_batch_1b_apply_marker_v1.json` rimane on-disk per audit, ma viene aggiornato un `_rollback_marker_v1.json` parallelo.
- **No DB touch**: nessuna scrittura su MongoDB durante il rollback (le scritture future torneranno a non avere `server_id`, ma quelle già scritte con `server_id="s1"` restano legali per la legacy compatibility policy SLC-G).

---

## 13. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| Drift docs gacha/summon non corretti (7 file) | bassa | Solo documentazione; runtime non impattato. Da chiudere in job housekeeping dedicato. |
| Redis rate-limit binary può crashare nel container | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina; SAFETY-ROLLUP-T,U,V,W,X,Y restano PASS. |
| Le route fuori Batch-1B (sanctuary write su Character Bible, player_faction_v2, e l'intero Batch-2/3/4) restano NON scoped | bassa | Atteso e desiderato. Batch-2/3/4 in backlog gated. |
| Le scritture legacy ancora a `server_id="s1"` esistenti | informativa | Coperto da SLC-G commit-A (`slc_g_commit_a_20260523T143803Z_4600ac04`) + write-gate + idempotency contract. |

Nessun rischio di severità **media-alta o alta** identificato.

---

## 14. Recommended Next Step

🔵 **Prossimo job suggerito (NON in questo apply):**

1. **(P1) SLC-F APPLY BATCH-2 ONLY** — Route mixed/account-wide a rischio medio (es. `users` profile updates non legati a Character Bible, `wallets` cross-shard, ecc.). Richiede nuova analisi pre-apply + nuovo set di marker autorizzativi (`SLC_F_BATCH_2_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=BATCH_2_ONLY`).
2. **(P2) Housekeeping drift docs gacha/summon** — job indipendente per correggere i 7 documenti di drift; nessun impatto runtime atteso.
3. **(P2) SLC-H live wiring (design-only → contract test)** — solo dopo che Batch-2 è applicata e stabilizzata.
4. **(P3) Phase 11 / secondo server / Batch-3 (AF2-N routing) / Batch-4 (combat-battle)** — restano in backlog gated; richiederanno apply pack dedicati e marker espliciti per ciascuna fase.

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server.
- Attivazione runtime `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare `combat`/`battle`/`gacha`/`AF2-N` routing.

---

## 15. Updated Progress Estimate

| Fase | Stato pre-Batch-1B | Stato post-Batch-1B |
|---|---|---|
| SLC-F Design / Dry-run / Combo | ✅ done | ✅ done |
| SLC-F Apply Prep + Housing Addendum | ✅ done | ✅ done |
| SLC-F Batch-0/1 (helper + items.py) | ✅ done | ✅ done |
| **SLC-F Batch-1B (7 route low-risk)** | 🟡 pending | ✅ **done** |
| SLC-F Batch-2 (mixed / account-wide) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 (AF2-N routing) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 (combat / battle) | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **88% → ~90%** (incremento atteso confermato dopo PASS della suite master e del nuovo validator dedicato).

---

## 16. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `applied_at_utc`: `2026-05-23T18:00:29.368257+00:00`
- `git_head_before`: `e86d821`
- `git_head_now`: `fa44754` (auto-commit post-apply)
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `verdict_target`: `SLC_F_BATCH_1B_APPLIED_SAFE` → ✅ **RAGGIUNTO**

---

**FINE REPORT 106_SLC_F_APPLY_BATCH_1B.md**
